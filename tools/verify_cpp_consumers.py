#!/usr/bin/env python3
"""Verify build/install/relocation consumers and generated-symbol ownership."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{output}")
    return output


def configure_and_build(
    source: Path,
    build: Path,
    prefixes: list[Path],
    *,
    env: dict[str, str] | None = None,
) -> str:
    prefix_path = ";".join(str(path) for path in prefixes)
    output = run(
        [
            "cmake",
            "-S",
            str(source),
            "-B",
            str(build),
            "-G",
            "Ninja",
            f"-DCMAKE_PREFIX_PATH={prefix_path}",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        cwd=build.parent,
        env=env,
    )
    output += run(["cmake", "--build", str(build), "--verbose"], cwd=build.parent, env=env)
    executable = build / "contracts_isolated_consumer"
    output += run([str(executable)], cwd=build, env=env)
    return output


def assert_consumer_isolation(build: Path, output: str, source_root: Path, *, allow_build_tree: bool) -> None:
    compile_commands = json.loads((build / "compile_commands.json").read_text(encoding="utf-8"))
    consumer_commands = "\n".join(item["command"] for item in compile_commands)
    if ".pb.cc" in consumer_commands:
        raise RuntimeError("consumer compiled a generated .pb.cc source")
    if not allow_build_tree and str(source_root) in consumer_commands:
        raise RuntimeError("consumer compiler input references the Contracts source tree")
    if str(source_root / "src" / "binance_market_data_contracts" / "proto") in consumer_commands:
        raise RuntimeError("consumer compiler input references authoritative .proto sources")
    lowered = output.lower()
    if "generating the seven contracts-owned" in lowered or "protoc " in lowered:
        raise RuntimeError("consumer build invoked protoc/code generation")


def assert_installed_artifact(prefix: Path, source_root: Path) -> None:
    expected = {
        "common/v1/enums.pb.h",
        "common/v1/identifiers.pb.h",
        "common/v1/metadata.pb.h",
        "gateway/v1/gateway_messages.pb.h",
        "market/v1/market_events.pb.h",
        "projection/v1/snapshots.pb.h",
        "telemetry/v1/telemetry.pb.h",
    }
    include_root = prefix / "include" / "binance_market_data"
    actual = {str(path.relative_to(include_root)) for path in include_root.rglob("*.pb.h")}
    if actual != expected:
        raise RuntimeError(f"installed generated header set mismatch: {sorted(actual)}")
    if list(prefix.rglob("*.proto")) or list(prefix.rglob("*.pb.cc")):
        raise RuntimeError("installed package contains consumer generation inputs")
    configs = "\n".join(path.read_text(encoding="utf-8") for path in prefix.rglob("*.cmake"))
    if str(source_root) in configs:
        raise RuntimeError("installed CMake files contain an absolute build/source path")


def assert_symbol_ownership(prefix: Path) -> None:
    libraries = list((prefix / "lib").glob("*binance_market_data_contracts_protobuf*"))
    if len(libraries) != 1:
        raise RuntimeError(f"expected one Contracts library, got {libraries}")
    result = subprocess.run(["nm", "-C", str(libraries[0])], text=True, capture_output=True, check=True)
    definitions = [
        line
        for line in result.stdout.splitlines()
        if "binance_market_data::market::v1::DepthUpdate::Clear()" in line and " U " not in f" {line} "
    ]
    if len(definitions) != 1:
        raise RuntimeError(f"DepthUpdate::Clear symbol ownership is not singular: {definitions}")


def defined_symbol_lines(path: Path, symbol: str) -> list[str]:
    result = subprocess.run(["nm", "-C", str(path)], text=True, capture_output=True, check=True)
    return [
        line
        for line in result.stdout.splitlines()
        if symbol in line.replace("[abi:cxx11]", "") and " U " not in f" {line} "
    ]


def assert_final_link_participation(build: Path) -> None:
    executable = build / "contracts_isolated_consumer"
    required_consumer_symbols = {
        "serialize_depth()": build / "libconsumer_a.a",
        "serialize_snapshot()": build / "libconsumer_b.a",
    }
    for symbol, archive in required_consumer_symbols.items():
        archive_definitions = defined_symbol_lines(archive, symbol)
        executable_definitions = defined_symbol_lines(executable, symbol)
        if len(archive_definitions) != 1:
            raise RuntimeError(f"{archive.name} does not define exactly one {symbol}: {archive_definitions}")
        if len(executable_definitions) != 1:
            raise RuntimeError(
                f"{archive.name} did not participate in the final Release link for {symbol}: {executable_definitions}"
            )

    generated_symbols = (
        "binance_market_data::market::v1::DepthUpdate::Clear()",
        "binance_market_data::projection::v1::LocalOrderBookSnapshot::Clear()",
    )
    for symbol in generated_symbols:
        definitions = defined_symbol_lines(executable, symbol)
        if len(definitions) != 1:
            raise RuntimeError(f"final executable generated-symbol ownership is not singular: {symbol}: {definitions}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--dependency-prefix", type=Path, action="append", default=[])
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    build_dir = args.build_dir.resolve()

    with tempfile.TemporaryDirectory(prefix="bmd-contracts-consumers-") as temporary:
        root = Path(temporary)
        consumer_source = root / "consumer-source"
        shutil.copytree(source_root / "tests/consumers/package", consumer_source)
        build_tree_consumer = root / "build-tree-consumer"
        output = configure_and_build(
            consumer_source,
            build_tree_consumer,
            [build_dir, *args.dependency_prefix],
        )
        assert_consumer_isolation(build_tree_consumer, output, source_root, allow_build_tree=True)
        assert_final_link_participation(build_tree_consumer)

        install_prefix = root / "installed"
        run(["cmake", "--install", str(build_dir), "--prefix", str(install_prefix)], cwd=root)
        assert_installed_artifact(install_prefix, source_root)
        assert_symbol_ownership(install_prefix)

        relocated = root / "relocated-prefix"
        shutil.copytree(install_prefix, relocated)
        trap = root / "trap"
        trap.mkdir()
        protoc = trap / "protoc"
        protoc.write_text("#!/bin/sh\nexit 97\n", encoding="utf-8")
        protoc.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(trap) + os.pathsep + env["PATH"]
        install_consumer = root / "install-tree-consumer"
        output = configure_and_build(
            consumer_source,
            install_consumer,
            [relocated, *args.dependency_prefix],
            env=env,
        )
        assert_consumer_isolation(install_consumer, output, source_root, allow_build_tree=False)
        assert_final_link_participation(install_consumer)

        core_build = root / "core-like"
        core_source = root / "core-source"
        shutil.copytree(source_root / "tests/consumers/core_like", core_source)
        run(
            [
                "cmake",
                "-S",
                str(core_source),
                "-B",
                str(core_build),
                "-G",
                "Ninja",
                "-DCMAKE_DISABLE_FIND_PACKAGE_Protobuf=TRUE",
                "-DCMAKE_DISABLE_FIND_PACKAGE_BinanceMarketDataContracts=TRUE",
            ],
            cwd=root,
        )
        run(["cmake", "--build", str(core_build)], cwd=root)
    print("build-tree, install-tree, relocation, isolation, symbols, and Projection-like probes passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
