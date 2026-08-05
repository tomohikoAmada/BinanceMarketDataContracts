"""Exercise the Buf baseline script against the real Buf binary."""

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_buf_breaking.sh"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def write_contract(proto: Path, *, count_type: str = "int64") -> None:
    proto.write_text(
        'syntax = "proto3";\n'
        "package baseline.v1;\n"
        "message Widget {\n"
        "  string name = 1;\n"
        f"  {count_type} count = 2;\n"
        "}\n",
        encoding="utf-8",
    )


def main() -> None:
    with TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        proto_dir = repo / "proto" / "nested"
        proto_dir.mkdir(parents=True)
        (repo / "buf.yaml").write_text("version: v2\nmodules:\n  - path: proto\n", encoding="utf-8")
        proto = proto_dir / "contract.proto"
        write_contract(proto)
        run("git", "init", "-q", cwd=repo)
        run("git", "config", "user.name", "Buf Integration", cwd=repo)
        run("git", "config", "user.email", "buf-integration@example.invalid", cwd=repo)
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-qm", "baseline", cwd=repo)
        baseline = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()

        with proto.open("a", encoding="utf-8") as handle:
            handle.write("message CompatibleAddition { string value = 1; }\n")
        compatible = run("bash", str(SCRIPT), baseline, cwd=repo, check=False)
        if compatible.returncode != 0:
            raise RuntimeError(f"compatible Buf comparison failed:\n{compatible.stdout}\n{compatible.stderr}")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-qm", "compatible change", cwd=repo)

        write_contract(proto, count_type="string")
        breaking = run("bash", str(SCRIPT), baseline, cwd=repo, check=False)
        if breaking.returncode == 0:
            raise RuntimeError("real Buf breaking comparison unexpectedly accepted a field type change")
        print("real Buf breaking integration passed")


if __name__ == "__main__":
    main()
