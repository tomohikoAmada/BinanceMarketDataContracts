#!/usr/bin/env python3
"""Prove that a non-exported Git commit cannot change the base Conan RREV."""

from __future__ import annotations

import argparse
import os
import re
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


def commit(tree: Path, message: str) -> str:
    run(["git", "add", "."], cwd=tree)
    run(["git", "commit", "-m", message], cwd=tree)
    return run(["git", "rev-parse", "HEAD"], cwd=tree).strip()


def exported_rrev(conan: str, tree: Path, conan_home: Path, revision: str) -> str:
    env = os.environ.copy()
    env["CONAN_HOME"] = str(conan_home)
    env["BMD_CONTRACTS_SOURCE_REVISION"] = revision
    output = run([conan, "export", "."], cwd=tree, env=env)
    match = re.search(
        r"Exported:\s+binance-market-data-contracts-cpp/0\.1\.0#([0-9a-f]+)",
        output,
    )
    if match is None:
        raise RuntimeError(f"unable to parse exported base RREV:\n{output}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--conan", required=True)
    args = parser.parse_args()
    conan = shutil.which(args.conan)
    if conan is None:
        candidate = Path(args.conan).resolve()
        if not candidate.is_file():
            raise RuntimeError(f"Conan executable not found: {args.conan}")
        conan = str(candidate)
    else:
        conan = str(Path(conan).resolve())

    ignored = shutil.ignore_patterns(
        ".git",
        ".venv",
        "build",
        "dist",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    )
    with tempfile.TemporaryDirectory(prefix="bmd-contracts-rrev-") as temporary:
        root = Path(temporary)
        tree = root / "tree"
        shutil.copytree(args.source_root.resolve(), tree, ignore=ignored)
        run(["git", "init", "--quiet"], cwd=tree)
        run(["git", "config", "user.name", "RREV Stability Test"], cwd=tree)
        run(["git", "config", "user.email", "rrev-stability.invalid"], cwd=tree)
        first_revision = commit(tree, "first")
        first_rrev = exported_rrev(conan, tree, root / "conan-home", first_revision)

        marker = tree / "RREV_STABILITY_NON_EXPORTED.md"
        marker.write_text(
            "This committed file is intentionally outside the base recipe exports.\n",
            encoding="utf-8",
        )
        second_revision = commit(tree, "second")
        second_rrev = exported_rrev(conan, tree, root / "conan-home", second_revision)
        if first_revision == second_revision:
            raise RuntimeError("experiment did not change Git HEAD")
        if first_rrev != second_rrev:
            raise RuntimeError(
                "base Conan RREV depends on Git HEAD and cannot be pinned by the sibling gRPC "
                f"lock: {first_rrev} != {second_rrev}"
            )
    print(f"base Conan RREV is stable across non-exported Git commits: {first_rrev}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
