"""Self-tests for recursive Buf baseline detection."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_buf_breaking.sh"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def _make_repo(tmp_path: Path, *, with_proto: bool) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Buf Test")
    _git(repo, "config", "user.email", "buf-test@example.invalid")
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    if with_proto:
        nested = repo / "deep" / "nested"
        nested.mkdir(parents=True)
        (nested / "baseline.proto").write_text('syntax = "proto3";\n', encoding="utf-8")
    _git(repo, "add", "-f", ".")
    _git(repo, "commit", "-qm", "baseline")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


def _fake_buf(tmp_path: Path) -> Path:
    fake = tmp_path / "fake-buf"
    fake.write_text(
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$BUF_ARGS_FILE"\nexit "${FAKE_BUF_EXIT:-0}"\n',
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


def _run(repo: Path, fake_buf: Path, *, exit_code: int = 0) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BUF_BIN"] = str(fake_buf)
    env["BUF_ARGS_FILE"] = str(fake_buf.parent / "buf-args")
    env["FAKE_BUF_EXIT"] = str(exit_code)
    return subprocess.run(
        ["bash", str(SCRIPT), "origin/main"], cwd=repo, env=env, capture_output=True, text=True, check=False
    )


def test_nested_proto_tree_enters_breaking_check(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, with_proto=True)
    tree = _git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout
    assert "deep/nested/baseline.proto" in tree
    result = _run(repo, _fake_buf(tmp_path))
    assert result.returncode == 0
    assert "Existing Protobuf baseline detected" in result.stdout
    args = (tmp_path / "buf-args").read_text(encoding="utf-8").splitlines()
    baseline_sha = _git(repo, "rev-parse", "origin/main^{commit}").stdout.strip()
    assert len(baseline_sha) == 40
    assert args == ["breaking", "--against", f".git#ref={baseline_sha}"]
    assert ".git#branch=origin/main" not in args


def test_empty_tree_is_initial_baseline(tmp_path: Path) -> None:
    result = _run(_make_repo(tmp_path, with_proto=False), _fake_buf(tmp_path), exit_code=99)
    assert result.returncode == 0
    assert "Initial Protobuf baseline" in result.stdout


def test_breaking_error_is_not_swallowed(tmp_path: Path) -> None:
    result = _run(_make_repo(tmp_path, with_proto=True), _fake_buf(tmp_path), exit_code=23)
    assert result.returncode == 23


def test_missing_baseline_is_configuration_error(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, with_proto=False)
    env = os.environ.copy()
    env["BUF_BIN"] = str(_fake_buf(tmp_path))
    env["BUF_ARGS_FILE"] = str(tmp_path / "buf-args")
    result = subprocess.run(
        ["bash", str(SCRIPT), "refs/remotes/origin/missing"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
