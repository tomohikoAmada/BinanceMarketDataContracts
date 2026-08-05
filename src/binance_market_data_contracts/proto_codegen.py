"""Proto code generation tool.

Generates Python protobuf and gRPC stubs from .proto files.
Uses grpc_tools.protoc for compilation.

Usage:
    python -m binance_market_data_contracts.proto_codegen           # generate
    python -m binance_market_data_contracts.proto_codegen --check    # drift check
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT = PACKAGE_DIR.parent
PROTO_ROOT = PACKAGE_DIR / "proto"
GENERATED_DIR = ROOT / "binance_market_data"


def _find_protoc() -> list[str]:
    """Find the grpc_tools protoc compiler."""
    try:
        subprocess.run(
            [sys.executable, "-m", "grpc_tools.protoc", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [sys.executable, "-m", "grpc_tools.protoc"]
    except (subprocess.CalledProcessError, ImportError) as e:
        print(f"grpc_tools.protoc not available: {e}", file=sys.stderr)
        print("Install it with: pip install grpcio-tools", file=sys.stderr)
        sys.exit(1)


def _collect_proto_files() -> list[Path]:
    return sorted(PROTO_ROOT.rglob("*.proto"))


def _add_init_files(base_dir: Path) -> None:
    """Add __init__.py files to all directories under base_dir."""
    for path in base_dir.rglob("*"):
        if path.is_dir():
            init_file = path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")


def _collect_tracked_files(base_dir: Path) -> set[str]:
    files: set[str] = set()
    for f in base_dir.rglob("*"):
        if f.is_file() and "__pycache__" not in f.parts:
            files.add(str(f.relative_to(base_dir)))
    return files


def _safe_clean_target(target: Path, gen_package: str = "binance_market_data") -> None:
    """Remove only the generated package directory."""
    pkg_dir = target / gen_package
    if not pkg_dir.exists():
        return
    for path in sorted(pkg_dir.rglob("*"), reverse=True):
        if path.is_dir():
            with suppress(OSError):
                path.rmdir()
    if pkg_dir.exists():
        pkg_dir.rmdir()


def _generate(output_dir: Path) -> None:
    _safe_clean_target(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    protoc = _find_protoc()
    proto_files = _collect_proto_files()
    if not proto_files:
        print("No .proto files found", file=sys.stderr)
        return

    args: list[str] = [str(pf) for pf in proto_files]
    args.extend(
        [
            f"--proto_path={PROTO_ROOT}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
        ]
    )

    result = subprocess.run([*protoc, *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"protoc failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    _add_init_files(output_dir)

    # Remove empty _pb2_grpc.py stubs for files that have no services
    for grpc_file in sorted(output_dir.rglob("*_pb2_grpc.py")):
        content = grpc_file.read_text()
        if "Servicer" not in content and "Stub" not in content:
            grpc_file.unlink()

    print(f"Generated {len(proto_files)} proto files to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate protobuf Python stubs")
    parser.add_argument("--check", action="store_true", help="Check for drift (exit non-zero if dirty)")
    args_cli = parser.parse_args()

    if args_cli.check:
        with TemporaryDirectory() as tmp:
            tmp_src = Path(tmp) / "src"
            _generate(tmp_src)

            repo_pkg = GENERATED_DIR
            tmp_pkg = tmp_src / "binance_market_data"

            repo_files = _collect_tracked_files(repo_pkg) if repo_pkg.exists() else set()
            tmp_files = _collect_tracked_files(tmp_pkg)

            all_files = repo_files | tmp_files
            dirty = False

            for fname in sorted(all_files):
                repo_path = repo_pkg / fname
                tmp_path = tmp_pkg / fname
                if not repo_path.exists():
                    print(f"  MISSING in repo: {fname}")
                    dirty = True
                elif not tmp_path.exists():
                    print(f"  EXTRA in repo: {fname}")
                    dirty = True
                elif repo_path.read_bytes() != tmp_path.read_bytes():
                    print(f"  DRIFT: {fname}")
                    dirty = True

            if dirty:
                print("\nGenerated code has drifted. Run: python -m binance_market_data_contracts.proto_codegen")
                sys.exit(1)
            print("Generated code matches .proto sources.")
            sys.exit(0)

    _generate(ROOT)
    print(f"Proto code generation complete: {GENERATED_DIR}")


if __name__ == "__main__":
    main()
