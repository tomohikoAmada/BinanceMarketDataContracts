#!/usr/bin/env python3
"""Verify that the message and gRPC Conan artifacts have distinct dependency graphs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

BASE_REFERENCE = "binance-market-data-contracts-cpp/0.1.0"
GRPC_CONTRACTS_REFERENCE = "binance-market-data-contracts-grpc-cpp/0.1.0"
GRPC_REFERENCE = "grpc/1.83.0"

GRPC_PLUGIN_OPTIONS = (
    "csharp_ext",
    "csharp_plugin",
    "node_plugin",
    "objective_c_plugin",
    "php_plugin",
    "python_plugin",
    "ruby_plugin",
    "otel_plugin",
)


def _reference(node: dict[str, Any]) -> str:
    return str(node.get("ref") or "").split("#", maxsplit=1)[0]


def _matching_nodes(nodes: list[dict[str, Any]], reference: str, context: str) -> list[dict[str, Any]]:
    return [node for node in nodes if _reference(node) == reference and node.get("context") == context]


def verify_base_graph(nodes: list[dict[str, Any]]) -> None:
    grpc_nodes = [node for node in nodes if _reference(node).startswith("grpc/")]
    if grpc_nodes:
        raise RuntimeError(f"message artifact graph contains gRPC: {grpc_nodes}")
    contracts_grpc_nodes = [
        node for node in nodes if _reference(node).startswith("binance-market-data-contracts-grpc-cpp/")
    ]
    if contracts_grpc_nodes:
        raise RuntimeError(f"message artifact graph contains the gRPC Contracts artifact: {contracts_grpc_nodes}")
    base_nodes = _matching_nodes(nodes, BASE_REFERENCE, "host")
    protobuf_nodes = _matching_nodes(nodes, "protobuf/6.33.5", "host")
    if len(base_nodes) == 1 and len(protobuf_nodes) == 1:
        if _bool_option(base_nodes[0], "shared") != _bool_option(protobuf_nodes[0], "shared"):
            raise RuntimeError("base Contracts shared option does not drive Protobuf linkage")


def _bool_option(node: dict[str, Any], name: str) -> bool:
    value = node.get("options", {}).get(name)
    if value is None:
        raise RuntimeError(f"missing gRPC option {name!r} in graph node")
    return str(value).lower() == "true"


def verify_grpc_graph(nodes: list[dict[str, Any]]) -> None:
    base_nodes = _matching_nodes(nodes, BASE_REFERENCE, "host")
    if len(base_nodes) != 1:
        raise RuntimeError(f"expected exactly one host base Contracts artifact, got {base_nodes}")
    if _matching_nodes(nodes, BASE_REFERENCE, "build"):
        raise RuntimeError("base Contracts artifact must not appear in the build context")

    grpc_contracts_nodes = _matching_nodes(nodes, GRPC_CONTRACTS_REFERENCE, "host")
    if len(grpc_contracts_nodes) > 1:
        raise RuntimeError("duplicate gRPC Contracts artifact nodes")

    host_grpc = _matching_nodes(nodes, GRPC_REFERENCE, "host")
    build_grpc = _matching_nodes(nodes, GRPC_REFERENCE, "build")
    if len(host_grpc) != 1 or len(build_grpc) != 1:
        raise RuntimeError(
            f"expected one host and one build-context gRPC node, got host={host_grpc}, build={build_grpc}"
        )
    if _bool_option(host_grpc[0], "codegen") or _bool_option(host_grpc[0], "cpp_plugin"):
        raise RuntimeError("host gRPC runtime unexpectedly enables code generation")
    if not _bool_option(build_grpc[0], "codegen") or not _bool_option(build_grpc[0], "cpp_plugin"):
        raise RuntimeError("build-context gRPC must enable only C++ code generation")
    if _bool_option(build_grpc[0], "shared"):
        raise RuntimeError("build-context grpc_cpp_plugin must use the static tool package")
    if grpc_contracts_nodes:
        selected_shared = _bool_option(grpc_contracts_nodes[0], "shared")
        if _bool_option(base_nodes[0], "shared") != selected_shared:
            raise RuntimeError("gRPC artifact shared option does not drive the base artifact")
        if _bool_option(host_grpc[0], "shared") != selected_shared:
            raise RuntimeError("gRPC artifact shared option does not drive the host gRPC runtime")
    for option in GRPC_PLUGIN_OPTIONS:
        if _bool_option(host_grpc[0], option) or _bool_option(build_grpc[0], option):
            raise RuntimeError(f"unrelated gRPC plugin is enabled: {option}")


def _run_graph(command: list[str], cwd: Path) -> list[dict[str, Any]]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}{result.stderr}")
    return list(json.loads(result.stdout)["graph"]["nodes"].values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--profile-host", type=Path, required=True)
    parser.add_argument("--profile-build", type=Path, required=True)
    parser.add_argument("--conan", default="conan")
    parser.add_argument("--no-remote", action="store_true")
    args = parser.parse_args()
    root = args.source_root.resolve()
    common = [
        f"--profile:host={args.profile_host.resolve()}",
        f"--profile:build={args.profile_build.resolve()}",
        "--format=json",
    ]
    if args.no_remote:
        common.append("--no-remote")
    for shared in (False, True):
        linkage = f"&:shared={shared}"
        base_nodes = _run_graph(
            [
                args.conan,
                "graph",
                "info",
                ".",
                "--lockfile=conan.lock",
                "--options:host",
                linkage,
                *common,
            ],
            root,
        )
        verify_base_graph(base_nodes)
        grpc_nodes = _run_graph(
            [
                args.conan,
                "graph",
                "info",
                "conanfile_grpc.py",
                "--lockfile=grpc/conan.lock",
                "--options:host",
                linkage,
                *common,
            ],
            root,
        )
        verify_grpc_graph(grpc_nodes)
    print(
        "static/shared message graphs exclude gRPC; gRPC host/build contexts, linkage, and plugin options are isolated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
