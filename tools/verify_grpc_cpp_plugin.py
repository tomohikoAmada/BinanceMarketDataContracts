#!/usr/bin/env python3
"""Fail-closed validation for the locked build-context gRPC C++ plugin."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def verify_plugin(
    executable: Path,
    package_folder: Path,
    actual_provenance: str,
    expected_provenance: str,
) -> str:
    if actual_provenance != expected_provenance:
        raise ValueError(
            f"grpc_cpp_plugin provenance mismatch: expected {expected_provenance!r}, got {actual_provenance!r}"
        )
    resolved_package = package_folder.resolve(strict=True)
    resolved_executable = executable.resolve(strict=True)
    expected_executable = resolved_package / "bin" / executable.name
    if resolved_executable != expected_executable:
        raise ValueError(
            "grpc_cpp_plugin is not the executable from the locked Conan package folder: "
            f"expected {expected_executable}, got {resolved_executable}"
        )
    if not resolved_executable.is_file() or not os.access(resolved_executable, os.X_OK):
        raise ValueError(f"grpc_cpp_plugin is not an executable file: {resolved_executable}")
    return str(resolved_executable)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--package-folder", type=Path, required=True)
    parser.add_argument("--actual-provenance", required=True)
    parser.add_argument("--expected-provenance", required=True)
    args = parser.parse_args()
    try:
        print(
            verify_plugin(
                args.executable,
                args.package_folder,
                args.actual_provenance,
                args.expected_provenance,
            )
        )
    except (OSError, ValueError) as exc:
        print(f"grpc_cpp_plugin identity error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
