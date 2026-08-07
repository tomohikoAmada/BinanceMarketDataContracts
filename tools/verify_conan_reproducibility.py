#!/usr/bin/env python3
"""Build the same static package twice and require identical Conan artifacts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from tools.artifact_provenance import generate_manifest, sha256_file


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def build_folder(conan: str, manifest: dict[str, Any], *, cwd: Path, env: dict[str, str]) -> str:
    contracts = manifest["contracts"]
    reference = f"{contracts['conan_reference']}#{contracts['conan_recipe_revision']}:{contracts['conan_package_id']}"
    result = subprocess.run(
        [conan, "cache", "path", reference, "--folder=build"],
        cwd=cwd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return str(Path(result.stdout.strip()).resolve())


def snapshot(manifest: dict[str, Any]) -> dict[str, Any]:
    contracts = manifest["contracts"]
    artifact = manifest["artifact"]
    return {
        "input_identity": {
            "contracts_source_revision": contracts["source_revision"],
            "schema": manifest["schema"],
            "protobuf": manifest["protobuf"],
            "build": manifest["build"],
        },
        "contracts_conan_recipe_revision": contracts["conan_recipe_revision"],
        "contracts_package_id": contracts["conan_package_id"],
        "contracts_package_revision": contracts["conan_package_revision"],
        "archive_sha256": artifact["archive_sha256"],
        "generated_object_sha256": artifact["generated_object_sha256"],
        "package_files_sha256": artifact["package_files_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--conan", default="conan")
    parser.add_argument("--conan-home", type=Path, required=True)
    parser.add_argument("--profile-host", type=Path, required=True)
    parser.add_argument("--profile-build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    conan_home = args.conan_home.resolve()
    conan_home.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CONAN_HOME"] = str(conan_home)
    run([args.conan, "profile", "detect", "--force"], cwd=source_root, env=env)

    base_create = [
        args.conan,
        "create",
        ".",
        "--lockfile=conan.lock",
        f"--profile:host={args.profile_host.resolve()}",
        f"--profile:build={args.profile_build.resolve()}",
        "--settings:host=build_type=Release",
        "--options:host=&:shared=False",
    ]
    forced_build = [
        *base_create,
        "--build=missing",
        "--build=binance-market-data-contracts-cpp/*",
    ]
    run(forced_build, cwd=source_root, env=env)
    manifest_a = generate_manifest(
        conan=args.conan,
        conan_home=conan_home,
        profile_host=args.profile_host,
        profile_build=args.profile_build,
    )
    build_a = snapshot(manifest_a)
    original_build_a_folder = Path(build_folder(args.conan, manifest_a, cwd=source_root, env=env))
    retained_root = Path(tempfile.mkdtemp(prefix="c-m4-001-build-a-", dir=conan_home))
    build_a_folder = str(Path(shutil.move(str(original_build_a_folder), retained_root / "build")).resolve())

    run(forced_build, cwd=source_root, env=env)
    manifest_b = generate_manifest(
        conan=args.conan,
        conan_home=conan_home,
        profile_host=args.profile_host,
        profile_build=args.profile_build,
    )
    build_b = snapshot(manifest_b)
    build_b_folder = build_folder(args.conan, manifest_b, cwd=source_root, env=env)

    comparisons = {
        "input_identity": build_a["input_identity"] == build_b["input_identity"],
        "conan_recipe_revision": build_a["contracts_conan_recipe_revision"]
        == build_b["contracts_conan_recipe_revision"],
        "package_id": build_a["contracts_package_id"] == build_b["contracts_package_id"],
        "package_revision": build_a["contracts_package_revision"] == build_b["contracts_package_revision"],
        "archive_sha256": build_a["archive_sha256"] == build_b["archive_sha256"],
        "generated_object_sha256": build_a["generated_object_sha256"] == build_b["generated_object_sha256"],
        "package_files_sha256": build_a["package_files_sha256"] == build_b["package_files_sha256"],
        "separate_build_directories": build_a_folder != build_b_folder,
    }
    if not all(comparisons.values()):
        raise RuntimeError(
            "same-input package reproducibility failed:\n"
            + json.dumps({"build_a": build_a, "build_b": build_b, "comparisons": comparisons}, indent=2)
        )

    manifest_b["reproducibility"] = {
        "lockfile_sha256": sha256_file(source_root / "conan.lock"),
        "build_a": {**build_a, "build_folder": build_a_folder},
        "build_b": {**build_b, "build_folder": build_b_folder},
        "comparisons": comparisons,
        "match": "YES",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest_b, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"archive SHA-256: {build_b['archive_sha256']}")
    print(f"Contracts RREV: {build_b['contracts_conan_recipe_revision']}")
    print(f"package ID: {build_b['contracts_package_id']}")
    print(f"PREV: {build_b['contracts_package_revision']}")
    print("same-input reproducibility: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
