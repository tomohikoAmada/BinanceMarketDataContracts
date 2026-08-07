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
        values.extend(f"{context}:{value}" for value in payload.get(context, []))
    return tuple(sorted(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("committed", type=Path)
    parser.add_argument("candidate", type=Path)
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
    print("Conan dependency identities match the committed lock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
