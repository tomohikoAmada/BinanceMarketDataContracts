#!/usr/bin/env python3
"""Fail-closed validation for the production C++ Protobuf generator."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def verify_protoc(
    protoc: Path,
    expected_version: str,
    actual_provenance: str,
    expected_provenance: str,
) -> str:
    if actual_provenance != expected_provenance:
        raise ValueError(f"protoc provenance mismatch: expected {expected_provenance!r}, got {actual_provenance!r}")
    result = subprocess.run(
        [str(protoc), "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    version = result.stdout.strip()
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        raise ValueError(f"protoc execution failed: {detail}")
    if version != expected_version:
        raise ValueError(f"protoc version mismatch: expected {expected_version!r}, got {version!r}")
    return version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protoc", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--actual-provenance", required=True)
    parser.add_argument("--expected-provenance", required=True)
    args = parser.parse_args()
    try:
        print(
            verify_protoc(
                args.protoc,
                args.expected_version,
                args.actual_provenance,
                args.expected_provenance,
            )
        )
    except (OSError, ValueError) as exc:
        print(f"protoc identity error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
