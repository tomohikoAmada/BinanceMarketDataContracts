"""Tests for repeatable and narrowly scoped protobuf generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from binance_market_data_contracts.proto_codegen import _generate, _safe_clean_generated_package

if TYPE_CHECKING:
    from pathlib import Path


def test_generation_is_repeatable_and_removes_only_stale_package_files(tmp_path: Path) -> None:
    output = tmp_path / "src"
    output.mkdir()
    preserved = output / "keep.txt"
    preserved.write_text("keep", encoding="utf-8")

    _generate(output)
    _generate(output)
    stale = output / "binance_market_data" / "stale.txt"
    stale.write_text("stale", encoding="utf-8")
    _generate(output)

    assert not stale.exists()
    assert preserved.read_text(encoding="utf-8") == "keep"
    assert list((output / "binance_market_data").rglob("*.pyi"))


def test_generated_package_symlink_is_rejected(tmp_path: Path) -> None:
    output = tmp_path / "src"
    output.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    package = output / "binance_market_data"
    package.symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="symlink"):
        _safe_clean_generated_package(output)
    assert outside.exists()
