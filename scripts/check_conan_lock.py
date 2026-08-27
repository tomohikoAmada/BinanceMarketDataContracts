#!/usr/bin/env python3
"""Compare dependency identities in two Conan 2 lockfiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def identities(path: Path) -> tuple[str, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values: list[str] = []
    for context in ("requires", "build_requires", "python_requires", "config_requires"):
        for value in payload.get(context, []):
            if value.startswith("binance-market-data-contracts-cpp/0.1.0#"):
                value = value.split("%", maxsplit=1)[0]
            values.append(f"{context}:{value}")
    return tuple(sorted(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("committed", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--expected-artifact", choices=("base", "grpc"), default="base")
    args = parser.parse_args()
    committed = identities(args.committed)
    candidate = identities(args.candidate)
    if committed != candidate:
        raise SystemExit(f"Conan dependency lock drift detected\ncommitted: {committed}\ncandidate: {candidate}")
    required = "protobuf/6.33.5#ca5ff466767b31a1b496ec60247e105c"
    protobuf_entries = [item for item in committed if item.split(":", 1)[1].startswith(required)]
    if len(protobuf_entries) != 2:
        raise SystemExit(
            "lockfile must contain the required Protobuf RREV in host and build contexts: "
            f"{required}; got {protobuf_entries}"
        )
    grpc_reference = "grpc/1.83.0#67e377a995d4a1279bffe2b941ac2f55"
    grpc_entries = [item for item in committed if item.split(":", 1)[1].startswith(grpc_reference)]
    base_reference = "binance-market-data-contracts-cpp/0.1.0#"
    base_entries = [item for item in committed if item.split(":", 1)[1].startswith(base_reference)]
    if args.expected_artifact == "base":
        if grpc_entries or base_entries:
            raise SystemExit(
                "message artifact lock must contain neither gRPC nor a self/base package entry: "
                f"grpc={grpc_entries}, base={base_entries}"
            )
    elif len(grpc_entries) != 2 or len(base_entries) != 1:
        raise SystemExit(
            "gRPC artifact lock must contain exact gRPC host/build entries and one exact base "
            f"artifact: grpc={grpc_entries}, base={base_entries}"
        )
    print("Conan dependency identities match the committed lock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
