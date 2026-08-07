from __future__ import annotations

import os
from pathlib import Path

import pytest
from google.protobuf import descriptor_pb2

from tools.schema_fingerprint import (
    EXPECTED_CLOSURE,
    FingerprintError,
    canonicalize,
    fingerprint,
    load_descriptor,
    validate_runtime,
)


@pytest.fixture
def descriptor_set() -> descriptor_pb2.FileDescriptorSet:
    descriptor = os.environ.get("BMD_DESCRIPTOR_SET")
    if descriptor is None:
        pytest.skip("C++ fingerprint descriptor is produced by the CMake package build")
    path = Path(descriptor)
    return load_descriptor(path)


def _copy(value: descriptor_pb2.FileDescriptorSet) -> descriptor_pb2.FileDescriptorSet:
    result = descriptor_pb2.FileDescriptorSet()
    result.CopyFrom(value)
    return result


def test_equivalent_inputs_from_independent_paths_have_one_digest(
    descriptor_set: descriptor_pb2.FileDescriptorSet, tmp_path: Path
) -> None:
    first = tmp_path / "one" / "descriptor.pb"
    second = tmp_path / "another-root" / "descriptor.pb"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(descriptor_set.SerializeToString())
    second.write_bytes(descriptor_set.SerializeToString())
    assert fingerprint(load_descriptor(first))[0] == fingerprint(load_descriptor(second))[0]


def test_file_traversal_order_is_normalized(descriptor_set: descriptor_pb2.FileDescriptorSet) -> None:
    reordered = descriptor_pb2.FileDescriptorSet()
    for file_proto in reversed(descriptor_set.file):
        reordered.file.add().CopyFrom(file_proto)
    assert fingerprint(reordered) == fingerprint(descriptor_set)


def test_comment_only_change_is_absent_from_descriptor_identity(
    descriptor_set: descriptor_pb2.FileDescriptorSet,
) -> None:
    with_source_info = _copy(descriptor_set)
    with_source_info.file[0].source_code_info.location.add().leading_comments = "comment only"
    assert fingerprint(with_source_info) == fingerprint(descriptor_set)


def test_unrelated_proto_does_not_change_m4_fingerprint(
    descriptor_set: descriptor_pb2.FileDescriptorSet,
) -> None:
    unrelated = _copy(descriptor_set)
    extra = unrelated.file.add()
    extra.name = "binance_market_data/telemetry/v1/unrelated.proto"
    extra.package = "binance_market_data.telemetry.v1"
    assert fingerprint(unrelated) == fingerprint(descriptor_set)


def test_selected_schema_change_changes_digest(descriptor_set: descriptor_pb2.FileDescriptorSet) -> None:
    changed = _copy(descriptor_set)
    selected = next(file for file in changed.file if file.name.endswith("market_events.proto"))
    depth = next(message for message in selected.message_type if message.name == "DepthUpdate")
    first_update = next(field for field in depth.field if field.name == "first_update_id")
    first_update.number = 101
    assert fingerprint(changed)[0] != fingerprint(descriptor_set)[0]


def test_unknown_option_fails_closed(descriptor_set: descriptor_pb2.FileDescriptorSet) -> None:
    changed = _copy(descriptor_set)
    options = changed.file[0].options
    options.ParseFromString(options.SerializeToString() + b"\xf8\x07\x01")
    with pytest.raises(FingerprintError, match="unknown/unclassified option"):
        canonicalize(changed)


def test_wrong_runtime_metadata_fails_closed() -> None:
    with pytest.raises(FingerprintError, match="runtime identity mismatch"):
        validate_runtime("0.0.0-wrong")


def test_generator_identity_change_is_not_schema_identity(
    descriptor_set: descriptor_pb2.FileDescriptorSet,
) -> None:
    digest = fingerprint(descriptor_set)[0]
    generator_metadata = {"protoc": "libprotoc 33.5", "options": "cpp_out"}
    changed_metadata = {**generator_metadata, "protoc": "libprotoc 34.0"}
    assert changed_metadata != generator_metadata
    assert fingerprint(descriptor_set)[0] == digest


def test_dependency_closure_mismatch_fails_closed(
    descriptor_set: descriptor_pb2.FileDescriptorSet,
) -> None:
    missing = descriptor_pb2.FileDescriptorSet()
    for file_proto in descriptor_set.file:
        if file_proto.name != "binance_market_data/common/v1/metadata.proto":
            missing.file.add().CopyFrom(file_proto)
    with pytest.raises(FingerprintError, match="dependency closure is missing"):
        canonicalize(missing)


def test_exact_expected_closure_and_single_package_hash(
    descriptor_set: descriptor_pb2.FileDescriptorSet, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0
    from tools import schema_fingerprint

    original = schema_fingerprint.hashlib.sha256

    def counting_sha256(value: bytes):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(schema_fingerprint.hashlib, "sha256", counting_sha256)
    digest, _ = schema_fingerprint.fingerprint(descriptor_set)
    assert len(digest) == 64
    assert calls == 1
    assert {
        "binance_market_data/common/v1/enums.proto",
        "binance_market_data/common/v1/metadata.proto",
        "binance_market_data/market/v1/market_events.proto",
        "binance_market_data/projection/v1/snapshots.proto",
    } == EXPECTED_CLOSURE
