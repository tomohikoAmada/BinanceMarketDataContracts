"""Tests for repeatable and narrowly scoped protobuf generation."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

import binance_market_data_contracts.proto_codegen as proto_codegen
from binance_market_data_contracts.proto_codegen import (
    _collect_proto_files,
    _generate,
    _safe_clean_generated_package,
    expected_proto_artifacts,
)
from tools.proto_sources import collect_message_protos, expected_cpp_headers, expected_cpp_objects

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
    assert (output / "binance_market_data" / "py.typed").is_file()


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


def test_missing_proto_sources_preserve_generated_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output = tmp_path / "src"
    package = output / "binance_market_data"
    package.mkdir(parents=True)
    sentinel = package / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    empty_proto_root = tmp_path / "empty-proto"
    empty_proto_root.mkdir()
    monkeypatch.setattr(proto_codegen, "PROTO_ROOT", empty_proto_root)

    with pytest.raises(RuntimeError, match=r"No \.proto files found.*refusing to delete"):
        _generate(output)

    assert package.is_dir()
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_expected_proto_artifacts_derive_from_source_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    protos, pb2, pyi = expected_proto_artifacts()
    count = len(_collect_proto_files())
    assert count > 0
    assert len(protos) == len(pb2) == len(pyi) == count
    assert "binance_market_data_contracts/proto/binance_market_data/gateway/v1/gateway_service.proto" in protos
    assert "binance_market_data/gateway/v1/gateway_service_pb2.py" in pb2

    fake_root = tmp_path / "repo"
    fake_proto_root = fake_root / "src" / "binance_market_data_contracts" / "proto"
    shutil.copytree(proto_codegen.PROTO_ROOT, fake_proto_root)
    extra_proto = fake_proto_root / "binance_market_data" / "market" / "v1" / "extra_fixture.proto"
    extra_proto.write_text('syntax = "proto3";\npackage binance_market_data.market.v1;\n', encoding="utf-8")

    monkeypatch.setattr(proto_codegen, "PROTO_ROOT", fake_proto_root)
    new_protos, new_pb2, new_pyi = expected_proto_artifacts()
    assert new_protos - protos == {
        "binance_market_data_contracts/proto/binance_market_data/market/v1/extra_fixture.proto"
    }
    assert new_pb2 - pb2 == {"binance_market_data/market/v1/extra_fixture_pb2.py"}
    assert new_pyi - pyi == {"binance_market_data/market/v1/extra_fixture_pb2.pyi"}
    assert pb2 != new_pb2

    msg_protos = collect_message_protos(fake_root)
    assert len(msg_protos) == len(new_protos) - 1
    assert "binance_market_data/market/v1/extra_fixture.proto" in msg_protos
    assert "binance_market_data/gateway/v1/gateway_service.proto" not in msg_protos
    assert "market/v1/extra_fixture.pb.h" in expected_cpp_headers(fake_root)
    assert "extra_fixture.pb.cc.o" in expected_cpp_objects(fake_root)
