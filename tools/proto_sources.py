"""Authoritative source-derived C++ message proto expectations."""

from __future__ import annotations

from pathlib import Path

SERVICE_PROTO = "binance_market_data/gateway/v1/gateway_service.proto"


def collect_message_protos(source_root: Path) -> list[str]:
    """Return sorted relative paths of all non-service .proto files under proto root."""
    proto_root = source_root / "src" / "binance_market_data_contracts" / "proto"
    protos = sorted(path.relative_to(proto_root).as_posix() for path in proto_root.rglob("*.proto"))
    if SERVICE_PROTO not in protos:
        raise RuntimeError(f"expected service proto {SERVICE_PROTO} under {proto_root}")
    message_protos = [proto for proto in protos if proto != SERVICE_PROTO]
    if not message_protos:
        raise RuntimeError(f"no message .proto files found under {proto_root}")
    return message_protos


def expected_cpp_headers(source_root: Path) -> set[str]:
    """Return expected installed .pb.h paths relative to include/binance_market_data."""
    return {
        Path(proto).relative_to("binance_market_data").with_suffix(".pb.h").as_posix()
        for proto in collect_message_protos(source_root)
    }


def expected_cpp_objects(source_root: Path) -> set[str]:
    """Return expected static-archive .pb.cc.o member names from message protos."""
    message_protos = collect_message_protos(source_root)
    objects = {f"{Path(proto).stem}.pb.cc.o" for proto in message_protos}
    if len(objects) != len(message_protos):
        raise RuntimeError(f"duplicate proto basename among message protos: {message_protos}")
    return objects
