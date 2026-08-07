#!/usr/bin/env python3
"""Canonical M4 descriptor fingerprint, Algorithm Version 1."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import google.protobuf
from google.protobuf import descriptor_pb2

if TYPE_CHECKING:
    from collections.abc import Iterable

    from google.protobuf.message import Message

ALGORITHM_VERSION = 1
ROOTS = (
    "binance_market_data/market/v1/market_events.proto",
    "binance_market_data/projection/v1/snapshots.proto",
)
EXPECTED_CLOSURE = frozenset(
    {
        "binance_market_data/common/v1/enums.proto",
        "binance_market_data/common/v1/metadata.proto",
        *ROOTS,
    }
)

_GENERATOR_ONLY_OPTIONS: dict[str, frozenset[str]] = {
    "google.protobuf.FileOptions": frozenset(
        {
            "java_package",
            "java_outer_classname",
            "java_multiple_files",
            "java_generate_equals_and_hash",
            "java_string_check_utf8",
            "optimize_for",
            "go_package",
            "cc_generic_services",
            "java_generic_services",
            "py_generic_services",
            "php_generic_services",
            "cc_enable_arenas",
            "objc_class_prefix",
            "csharp_namespace",
            "swift_prefix",
            "php_class_prefix",
            "php_namespace",
            "php_metadata_namespace",
            "ruby_package",
        }
    ),
    "google.protobuf.MessageOptions": frozenset({"no_standard_descriptor_accessor"}),
    "google.protobuf.FieldOptions": frozenset({"ctype", "jstype", "lazy", "unverified_lazy"}),
}


class FingerprintError(ValueError):
    """Descriptor input is outside Algorithm Version 1."""


def _serialized(message: Message) -> bytes:
    return message.SerializeToString(deterministic=True)


def _normalize_name(name: str) -> str:
    if not name or "\\" in name or name.startswith("./") or "//" in name:
        raise FingerprintError(f"non-canonical proto filename: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise FingerprintError(f"unsafe proto filename: {name!r}")
    normalized = path.as_posix()
    if normalized != name:
        raise FingerprintError(f"proto filename is not normalized: {name!r}")
    return normalized


def _message_tree(message: Message) -> Iterable[Message]:
    yield message
    for field, value in message.ListFields():
        if field.type != field.TYPE_MESSAGE:
            continue
        if field.is_repeated:
            for child in value:
                yield from _message_tree(child)
        else:
            yield from _message_tree(value)


def _reject_unclassified_options(file_proto: descriptor_pb2.FileDescriptorProto) -> None:
    for message in _message_tree(file_proto):
        descriptor = message.DESCRIPTOR
        if not descriptor.full_name.endswith("Options"):
            continue
        before = _serialized(message)
        known = message.__class__()
        known.CopyFrom(message)
        known.DiscardUnknownFields()
        if _serialized(known) != before:
            raise FingerprintError(f"unknown/unclassified option in {descriptor.full_name}")
        uninterpreted = descriptor.fields_by_name.get("uninterpreted_option")
        if uninterpreted is not None and len(getattr(message, uninterpreted.name)):
            raise FingerprintError(f"uninterpreted option in {descriptor.full_name}")


def _clear_generator_options(file_proto: descriptor_pb2.FileDescriptorProto) -> None:
    for message in _message_tree(file_proto):
        removable = _GENERATOR_ONLY_OPTIONS.get(message.DESCRIPTOR.full_name, frozenset())
        for name in removable:
            field = message.DESCRIPTOR.fields_by_name.get(name)
            if field is not None:
                message.ClearField(name)


def _closure(files: dict[str, descriptor_pb2.FileDescriptorProto]) -> set[str]:
    pending = list(ROOTS)
    selected: set[str] = set()
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        file_proto = files.get(name)
        if file_proto is None:
            raise FingerprintError(f"dependency closure is missing {name}")
        selected.add(name)
        pending.extend(file_proto.dependency)
    if selected != EXPECTED_CLOSURE:
        raise FingerprintError(
            f"dependency closure mismatch: expected {sorted(EXPECTED_CLOSURE)}, got {sorted(selected)}"
        )
    return selected


def canonicalize(descriptor_set: descriptor_pb2.FileDescriptorSet) -> bytes:
    files: dict[str, descriptor_pb2.FileDescriptorProto] = {}
    for original in descriptor_set.file:
        name = _normalize_name(original.name)
        if name in files:
            raise FingerprintError(f"duplicate descriptor filename: {name}")
        clone = descriptor_pb2.FileDescriptorProto()
        clone.CopyFrom(original)
        clone.name = name
        for index, dependency in enumerate(clone.dependency):
            clone.dependency[index] = _normalize_name(dependency)
        files[name] = clone

    selected_names = _closure(files)
    canonical = descriptor_pb2.FileDescriptorSet()
    for name in sorted(selected_names):
        file_proto = files[name]
        _reject_unclassified_options(file_proto)
        file_proto.DiscardUnknownFields()
        file_proto.ClearField("source_code_info")
        old_dependencies = list(file_proto.dependency)
        sorted_dependencies = sorted(old_dependencies)
        old_to_new = {old_index: sorted_dependencies.index(dep) for old_index, dep in enumerate(old_dependencies)}
        public = [old_to_new[index] for index in file_proto.public_dependency]
        weak = [old_to_new[index] for index in file_proto.weak_dependency]
        del file_proto.dependency[:]
        file_proto.dependency.extend(sorted_dependencies)
        del file_proto.public_dependency[:]
        file_proto.public_dependency.extend(sorted(public))
        del file_proto.weak_dependency[:]
        file_proto.weak_dependency.extend(sorted(weak))
        _clear_generator_options(file_proto)
        canonical.file.add().CopyFrom(file_proto)
    return _serialized(canonical)


def fingerprint(descriptor_set: descriptor_pb2.FileDescriptorSet) -> tuple[str, bytes]:
    canonical = canonicalize(descriptor_set)
    return hashlib.sha256(canonical).hexdigest(), canonical


def validate_runtime(expected: str) -> None:
    if google.protobuf.__version__ != expected:
        raise FingerprintError(
            f"protobuf runtime identity mismatch: expected {expected}, got {google.protobuf.__version__}"
        )


def load_descriptor(path: Path) -> descriptor_pb2.FileDescriptorSet:
    descriptor_set = descriptor_pb2.FileDescriptorSet()
    descriptor_set.ParseFromString(path.read_bytes())
    return descriptor_set


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--descriptor-set", type=Path, required=True)
    parser.add_argument("--expected-runtime", default="6.33.5")
    parser.add_argument("--canonical-output", type=Path)
    args = parser.parse_args()
    try:
        validate_runtime(args.expected_runtime)
        digest, canonical = fingerprint(load_descriptor(args.descriptor_set))
        if args.canonical_output:
            args.canonical_output.parent.mkdir(parents=True, exist_ok=True)
            args.canonical_output.write_bytes(canonical)
        print(digest)
        return 0
    except (FingerprintError, OSError) as exc:
        print(f"fingerprint error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
