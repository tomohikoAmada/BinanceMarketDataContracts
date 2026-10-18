"""Binary protobuf evolution does not imply strict Domain/JSON compatibility."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from binance_market_data.market.v1 import market_events_pb2
from binance_market_data_contracts import DepthUpdate
from binance_market_data_contracts.wire.adapters import UnknownEnumValueError, depth_update_from_pb, depth_update_to_pb

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/valid/depth-update.v1.spot.json"


def test_unknown_binary_field_survives_binary_roundtrip_but_not_domain_conversion():
    value = DepthUpdate.model_validate_json(FIXTURE.read_text())
    wire = depth_update_to_pb(value)
    # Unknown field 99, varint value 1. This is test data, not a schema addition.
    binary = wire.SerializeToString() + b"\x98\x06\x01"
    decoded = market_events_pb2.DepthUpdate.FromString(binary)
    reserialized = decoded.SerializeToString()
    without_unknown = market_events_pb2.DepthUpdate.FromString(reserialized)
    without_unknown.DiscardUnknownFields()
    assert reserialized != without_unknown.SerializeToString()
    assert depth_update_from_pb(decoded) == value
    assert depth_update_to_pb(depth_update_from_pb(decoded)).SerializeToString() == wire.SerializeToString()


def test_unknown_quality_enum_is_preserved_on_binary_wire_and_rejected_by_adapter():
    wire = depth_update_to_pb(DepthUpdate.model_validate_json(FIXTURE.read_text()))
    wire.metadata.quality_flags.append(999)
    decoded = market_events_pb2.DepthUpdate.FromString(wire.SerializeToString())
    assert list(decoded.metadata.quality_flags) == [999]
    assert list(market_events_pb2.DepthUpdate.FromString(decoded.SerializeToString()).metadata.quality_flags) == [999]
    with pytest.raises(UnknownEnumValueError, match=r"QualityFlag value 999 in DepthUpdate\.metadata\.quality_flags"):
        depth_update_from_pb(decoded)


@pytest.mark.parametrize("flag", ("FUTURE_FLAG", 999))
def test_unknown_quality_flag_in_domain_json_is_rejected(flag):
    payload = json.loads(FIXTURE.read_text())
    payload["metadata"]["quality_flags"] = [flag]
    with pytest.raises(ValidationError):
        DepthUpdate.model_validate_json(json.dumps(payload))


def test_extra_domain_json_field_is_rejected():
    payload = json.loads(FIXTURE.read_text())
    payload["future_field"] = 1
    with pytest.raises(ValidationError) as error:
        DepthUpdate.model_validate_json(json.dumps(payload))
    assert error.value.errors()[0]["type"] == "extra_forbidden"
