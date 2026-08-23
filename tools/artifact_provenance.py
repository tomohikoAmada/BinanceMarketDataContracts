#!/usr/bin/env python3
"""Generate concrete post-package provenance for one Contracts Conan binary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

CONTRACTS_REFERENCE = "binance-market-data-contracts-cpp/0.1.0"
PROTOBUF_REFERENCE = "protobuf/6.33.5"
PROTOBUF_RREV = "ca5ff466767b31a1b496ec60247e105c"


def run(command: list[str], *, env: dict[str, str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr}")
    return result.stdout


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def full_reference(node: dict[str, Any]) -> str:
    return f"{node['ref']}:{node['package_id']}#{node['prev']}"


def resolve_latest_binary(
    conan: str,
    env: dict[str, str],
    *,
    build_type: str,
    shared: bool,
) -> dict[str, str]:
    listing = json.loads(run([conan, "list", f"{CONTRACTS_REFERENCE}#*:*#*", "--format=json"], env=env))
    recipes = listing["Local Cache"][CONTRACTS_REFERENCE]["revisions"]
    candidates: list[tuple[float, float, float, str, str, str]] = []
    for rrev, recipe in recipes.items():
        for package_id, package in recipe.get("packages", {}).items():
            info = package.get("info", {})
            settings = info.get("settings", {})
            options = info.get("options", {})
            if settings.get("build_type") != build_type:
                continue
            if options.get("shared") != str(shared):
                continue
            for prev, revision in package.get("revisions", {}).items():
                candidates.append(
                    (
                        float(recipe.get("timestamp", 0)),
                        float(revision.get("timestamp", 0)),
                        float(package.get("timestamp", 0)),
                        rrev,
                        package_id,
                        prev,
                    )
                )
    if not candidates:
        raise RuntimeError(f"no {CONTRACTS_REFERENCE} {build_type=} {shared=} binary found")
    _, _, _, rrev, package_id, prev = max(candidates)
    return {"rrev": rrev, "package_id": package_id, "prev": prev}


def conan_graph(
    conan: str,
    env: dict[str, str],
    *,
    identity: dict[str, str],
    profile_host: Path,
    profile_build: Path,
    build_type: str,
    shared: bool,
) -> list[dict[str, Any]]:
    recipe = f"{CONTRACTS_REFERENCE}#{identity['rrev']}"
    with tempfile.TemporaryDirectory(prefix="bmd-contracts-graph-") as temporary:
        output = run(
            [
                conan,
                "graph",
                "info",
                f"--requires={recipe}",
                f"--profile:host={profile_host}",
                f"--profile:build={profile_build}",
                f"--settings:host=build_type={build_type}",
                f"--options:host=&:shared={shared}",
                "--format=json",
            ],
            env=env,
            cwd=Path(temporary),
        )
    graph = json.loads(output)["graph"]["nodes"]
    return list(graph.values())


def find_node(nodes: list[dict[str, Any]], reference: str, context: str) -> dict[str, Any]:
    matches = [
        node
        for node in nodes
        if str(node.get("ref", "")).startswith(reference + "#") and node.get("context") == context
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {context} graph node for {reference}, got {len(matches)}")
    return matches[0]


def cache_path(conan: str, env: dict[str, str], reference: str) -> Path:
    return Path(run([conan, "cache", "path", reference], env=env).strip()).resolve()


def package_file_manifest(package_folder: Path) -> dict[str, str]:
    excluded = {"conaninfo.txt", "conanmanifest.txt"}
    return {
        path.relative_to(package_folder).as_posix(): sha256_file(path)
        for path in sorted(package_folder.rglob("*"))
        if path.is_file() and path.name not in excluded
    }


def archive_details(package_folder: Path) -> tuple[Path, dict[str, str]]:
    archives = list((package_folder / "lib").glob("*binance_market_data_contracts_protobuf*.a"))
    if len(archives) != 1:
        raise RuntimeError(f"expected one static Contracts archive, got {archives}")
    archive = archives[0]
    members = subprocess.run(["ar", "-t", str(archive)], check=True, capture_output=True, text=True).stdout.splitlines()
    object_hashes: dict[str, str] = {}
    for member in members:
        if not member.endswith(".o"):
            continue
        content = subprocess.run(["ar", "-p", str(archive), member], check=True, capture_output=True).stdout
        object_hashes[member] = hashlib.sha256(content).hexdigest()
    if len(object_hashes) != 7:
        raise RuntimeError(f"expected seven generated object members, got {sorted(object_hashes)}")
    return archive, object_hashes


def parse_header(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    values = dict(re.findall(r'inline constexpr std::string_view\s+(\w+)\s*=\s*"([^"]*)";', text, re.MULTILINE))
    algorithm = re.search(r"schema_fingerprint_algorithm_version\s*=\s*(\d+);", text)
    if algorithm:
        values["schema_fingerprint_algorithm_version"] = algorithm.group(1)
    return values


def parse_cmake_config(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(r'set\((BinanceMarketDataContracts_\w+)\s+"([^"]*)"\)', text, re.MULTILINE))


def verify_surfaces(package_folder: Path, installed: dict[str, Any]) -> None:
    header = parse_header(package_folder / "include/binance_market_data/contracts_metadata.hpp")
    config = parse_cmake_config(
        package_folder / "lib/cmake/BinanceMarketDataContracts/BinanceMarketDataContractsConfig.cmake"
    )
    checks = {
        "schema_baseline": ("schema_baseline", "SCHEMA_BASELINE"),
        "schema_fingerprint_candidate": ("schema_fingerprint", "SCHEMA_FINGERPRINT"),
        "package_version_candidate": ("package_version", "PACKAGE_VERSION"),
        "package_revision": ("package_revision", "PACKAGE_REVISION"),
        "protoc_version": ("protoc_version", "PROTOC_VERSION"),
        "cpp_generator_options": ("cpp_generator_options", "CPP_GENERATOR_OPTIONS"),
        "protobuf_runtime_version": ("protobuf_runtime_version", "PROTOBUF_RUNTIME_VERSION"),
        "protobuf_runtime_rrev": ("protobuf_runtime_rrev", "PROTOBUF_RUNTIME_RREV"),
        "protobuf_runtime_compatibility": (
            "protobuf_runtime_compatibility",
            "PROTOBUF_RUNTIME_COMPATIBILITY",
        ),
        "protobuf_runtime_flavor": ("protobuf_runtime_flavor", "PROTOBUF_RUNTIME_FLAVOR"),
        "protobuf_runtime_linkage": ("protobuf_runtime_linkage", "PROTOBUF_RUNTIME_LINKAGE"),
        "contracts_source_revision": ("contracts_source_revision", "CONTRACTS_SOURCE_REVISION"),
    }
    for installed_name, (header_name, cmake_suffix) in checks.items():
        expected = str(installed[installed_name])
        if header.get(header_name) != expected:
            raise RuntimeError(f"C++ metadata mismatch for {installed_name}")
        cmake_name = "BinanceMarketDataContracts_" + cmake_suffix
        if config.get(cmake_name) != expected:
            raise RuntimeError(f"CMake metadata mismatch for {installed_name}")
    algorithm = str(installed["schema_fingerprint_algorithm_version"])
    if header.get("schema_fingerprint_algorithm_version") != algorithm:
        raise RuntimeError("C++ fingerprint algorithm metadata mismatch")
    if config.get("BinanceMarketDataContracts_SCHEMA_FINGERPRINT_ALGORITHM_VERSION") != algorithm:
        raise RuntimeError("CMake fingerprint algorithm metadata mismatch")


def generate_manifest(
    *,
    conan: str,
    conan_home: Path,
    profile_host: Path,
    profile_build: Path,
    build_type: str = "Release",
    shared: bool = False,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["CONAN_HOME"] = str(conan_home.resolve())
    identity = resolve_latest_binary(conan, env, build_type=build_type, shared=shared)
    nodes = conan_graph(
        conan,
        env,
        identity=identity,
        profile_host=profile_host.resolve(),
        profile_build=profile_build.resolve(),
        build_type=build_type,
        shared=shared,
    )
    unexpected_grpc = [node for node in nodes if str(node.get("ref", "")).startswith("grpc/1.83.0#")]
    if unexpected_grpc:
        raise RuntimeError("message artifact provenance graph unexpectedly contains gRPC")
    contracts = find_node(nodes, CONTRACTS_REFERENCE, "host")
    protobuf = find_node(nodes, PROTOBUF_REFERENCE, "host")
    if contracts["package_id"] != identity["package_id"] or contracts["prev"] != identity["prev"]:
        raise RuntimeError("Conan graph and cache identity disagree for Contracts")
    protobuf_rrev = str(protobuf["ref"]).split("#", maxsplit=1)[1]
    if protobuf_rrev != PROTOBUF_RREV:
        raise RuntimeError(f"Protobuf RREV drift: {protobuf_rrev}")

    package_folder = cache_path(conan, env, full_reference(contracts))
    provenance_path = package_folder / "share/BinanceMarketDataContracts/provenance.json"
    installed = json.loads(provenance_path.read_text(encoding="utf-8"))
    verify_surfaces(package_folder, installed)

    runtime_flavor = "lite" if str(protobuf["options"].get("lite")) == "True" else "full"
    runtime_linkage = "shared" if str(protobuf["options"].get("shared")) == "True" else "static"
    if installed["protobuf_runtime_flavor"] != runtime_flavor:
        raise RuntimeError("installed runtime flavor disagrees with Conan graph")
    if installed["protobuf_runtime_linkage"] != runtime_linkage:
        raise RuntimeError("installed runtime linkage disagrees with Conan graph")

    archive, objects = archive_details(package_folder)
    settings = {key: str(value) for key, value in contracts["settings"].items()}
    options = {key: str(value) for key, value in contracts["options"].items()}
    return {
        "format_version": 1,
        "contracts": {
            "source_revision": installed["contracts_source_revision"],
            "conan_reference": CONTRACTS_REFERENCE,
            "conan_recipe_revision": identity["rrev"],
            "conan_package_id": identity["package_id"],
            "conan_package_revision": identity["prev"],
            "package_version": installed["package_version_candidate"],
            "package_revision": installed["package_revision"],
            "package_revision_formal_state": installed["package_revision_formal_state"],
        },
        "schema": {
            "baseline": installed["schema_baseline"],
            "fingerprint_candidate": installed["schema_fingerprint_candidate"],
            "fingerprint_algorithm_version": installed["schema_fingerprint_algorithm_version"],
            "formal_fingerprint_approval": installed["formal_fingerprint_approval"],
        },
        "protobuf": {
            "reference": PROTOBUF_REFERENCE,
            "recipe_revision": protobuf_rrev,
            "host_package_id": protobuf["package_id"],
            "host_package_revision": protobuf["prev"],
            "generator": installed["protoc_version"],
            "generator_options": installed["cpp_generator_options"],
            "runtime_flavor": runtime_flavor,
            "runtime_linkage": runtime_linkage,
        },
        "build": {
            "compiler": settings.get("compiler"),
            "compiler_version": settings.get("compiler.version"),
            "architecture": settings.get("arch"),
            "build_type": settings.get("build_type"),
            "shared": options.get("shared"),
            "fPIC": options.get("fPIC", "not-applicable"),
            "settings": settings,
            "options": options,
            "profile_host_sha256": sha256_file(profile_host),
            "profile_build_sha256": sha256_file(profile_build),
        },
        "artifact": {
            "archive": archive.relative_to(package_folder).as_posix(),
            "archive_sha256": sha256_file(archive),
            "generated_object_sha256": objects,
            "package_files_sha256": package_file_manifest(package_folder),
        },
        "cross_surface_consistency": "PASS",
        "published": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conan", default="conan")
    parser.add_argument("--conan-home", type=Path, required=True)
    parser.add_argument("--profile-host", type=Path, required=True)
    parser.add_argument("--profile-build", type=Path, required=True)
    parser.add_argument("--build-type", default="Release")
    parser.add_argument("--shared", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = generate_manifest(
        conan=args.conan,
        conan_home=args.conan_home,
        profile_host=args.profile_host,
        profile_build=args.profile_build,
        build_type=args.build_type,
        shared=args.shared,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
