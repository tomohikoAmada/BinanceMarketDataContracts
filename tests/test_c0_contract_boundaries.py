"""Current consumer surface: Domain limits must match the actual wire descriptors."""

import json
import re
from pathlib import Path

import pytest
from google.protobuf.descriptor import FieldDescriptor
from pydantic import ConfigDict, TypeAdapter, ValidationError

from binance_market_data.common.v1 import metadata_pb2
from binance_market_data.gateway.v1 import gateway_messages_pb2
from binance_market_data.market.v1 import market_events_pb2
from binance_market_data.projection.v1 import snapshots_pb2
from binance_market_data_contracts import gateway, market_events, snapshots
from binance_market_data_contracts.versions import CONTRACT_REGISTRY, WIRE_CONTRACT_REGISTRY
from binance_market_data_contracts.wire import adapters

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PAIRS = (
    (market_events.DepthUpdateMetadata, metadata_pb2.EventMetadata),
    (market_events.AggTradeMetadata, metadata_pb2.EventMetadata),
    (market_events.BookTickerMetadata, metadata_pb2.EventMetadata),
    (market_events.DepthUpdate, market_events_pb2.DepthUpdate),
    (market_events.AggTrade, market_events_pb2.AggTrade),
    (market_events.BookTicker, market_events_pb2.BookTicker),
    (snapshots.ExchangeDepthSnapshot, market_events_pb2.ExchangeDepthSnapshot),
    (snapshots.GapDescriptor, snapshots_pb2.GapDescriptor),
    (snapshots.LocalOrderBookSnapshot, snapshots_pb2.LocalOrderBookSnapshot),
    (gateway.OrderBookSubscriptionRequest, gateway_messages_pb2.OrderBookSubscriptionRequest),
    (gateway.SubscriptionAccepted, gateway_messages_pb2.SubscriptionAccepted),
    (gateway.ConsumerGapNotice, gateway_messages_pb2.ConsumerGapNotice),
    (gateway.StreamStatus, gateway_messages_pb2.StreamStatus),
    (gateway.GatewayEnvelopeMetadata, gateway_messages_pb2.GatewayEnvelopeMetadata),
    (gateway.MarketRuntimeStatus, gateway_messages_pb2.MarketRuntimeStatus),
    (gateway.GatewayStatusSnapshot, gateway_messages_pb2.GatewayStatusSnapshot),
)
INTEGER_FIELDS = [
    pytest.param(model, proto, field, id=f"{model.__name__}.{field.name}")
    for model, proto in PAIRS
    for field in proto.DESCRIPTOR.fields
    if field.type in (FieldDescriptor.TYPE_UINT64, FieldDescriptor.TYPE_INT32)
]


@pytest.mark.parametrize("model,proto,field", INTEGER_FIELDS)
def test_integer_range_and_presence_match_descriptor(model, proto, field):
    validator = TypeAdapter(model.model_fields[field.name].rebuild_annotation(), config=ConfigDict(strict=True))
    upper = (1 << (64 if field.type == FieldDescriptor.TYPE_UINT64 else 31)) - 1
    schema = validator.json_schema()
    integer_schema = next(s for s in schema.get("anyOf", [schema]) if s.get("type") == "integer")
    assert integer_schema["maximum"] == upper
    lower = integer_schema.get("minimum", integer_schema.get("exclusiveMinimum", -1) + 1)
    assert lower in (0, 1)
    for value in (lower, upper):
        assert validator.validate_python(value) == value
        assert validator.validate_json(json.dumps(value)) == value
        wire = proto(**{field.name: value})
        decoded = proto.FromString(wire.SerializeToString())
        assert getattr(decoded, field.name) == value
        if field.has_presence:
            assert decoded.HasField(field.name)
    for value in (lower - 1, upper + 1, True, 1.0, "1"):
        with pytest.raises(ValidationError):
            validator.validate_python(value)
        with pytest.raises(ValidationError):
            validator.validate_json(json.dumps(value))
    if field.has_presence:
        assert validator.validate_python(None) is None
        assert validator.validate_json("null") is None
        assert not proto.FromString(proto().SerializeToString()).HasField(field.name)


def _adapter_pair(model):
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", model.__name__).lower()
    return getattr(adapters, name + "_to_pb"), getattr(adapters, name + "_from_pb")


MANIFEST = json.loads((FIXTURES / "manifest.json").read_text())["fixtures"]
WIRE_VALID_FIXTURES = [
    entry for entry in MANIFEST if entry["valid"] and entry["contract_name"] in WIRE_CONTRACT_REGISTRY
]


@pytest.mark.parametrize("entry", WIRE_VALID_FIXTURES, ids=lambda e: e["path"])
def test_existing_and_boundary_fixtures_roundtrip(entry):
    model = CONTRACT_REGISTRY[entry["contract_name"]].python_type
    value = model.model_validate_json((FIXTURES / entry["path"]).read_text())
    to_pb, from_pb = _adapter_pair(model)
    wire = to_pb(value)
    assert from_pb(wire.__class__.FromString(wire.SerializeToString())) == value


CURRENT_NUMERIC_CONTRACTS = (
    "depth-update.v1.spot",
    "agg-trade.v1",
    "book-ticker.v1",
    "exchange-depth-snapshot.v1",
    "local-order-book-snapshot.v1.with-gap",
    "order-book-subscription-request.v1",
    "subscription-accepted.v1",
    "consumer-gap-notice.v1",
    "stream-status.v1",
    "gateway-event-envelope.v1",
    "order-book-stream-item.v1",
    "gateway-status-snapshot.v1.with-generation",
)


def _at_boundary(model, payload, use_maximum):
    """Mutate real model input recursively, including shared metadata and gaps."""
    schema = model.model_json_schema()
    for name, field in model.model_fields.items():
        properties = schema["properties"][name]
        integer = next((s for s in properties.get("anyOf", [properties]) if s.get("type") == "integer"), None)
        if integer is not None:
            payload[name] = integer["maximum"] if use_maximum else integer.get("minimum", 1)
        elif isinstance(payload.get(name), dict):
            nested = field.annotation
            if hasattr(nested, "model_fields"):
                _at_boundary(nested, payload[name], use_maximum)
    if model is gateway.ConsumerGapNotice:
        payload["last_delivered_session_sequence"] = payload["next_available_session_sequence"] - 1
        if not use_maximum:
            payload["last_delivered_session_sequence"] = 1
            payload["next_available_session_sequence"] = 2
    if model is snapshots.LocalOrderBookSnapshot and not use_maximum:
        payload["bids"] = payload["asks"] = []
    return payload


@pytest.mark.parametrize("fixture", CURRENT_NUMERIC_CONTRACTS)
@pytest.mark.parametrize("use_maximum", (False, True), ids=("minimum", "maximum"))
def test_current_messages_roundtrip_at_boundaries(fixture, use_maximum):
    entry = next(e for e in MANIFEST if e["path"] == f"valid/{fixture}.json")
    model = CONTRACT_REGISTRY[entry["contract_name"]].python_type
    payload = json.loads((FIXTURES / entry["path"]).read_text())
    # Validate optional nested models and repeated runtime statuses separately.
    if payload.get("last_gap"):
        _at_boundary(snapshots.GapDescriptor, payload["last_gap"], use_maximum)
    for status in payload.get("markets", []):
        _at_boundary(gateway.MarketRuntimeStatus, status, use_maximum)
    if payload.get("delivery_metadata"):
        _at_boundary(gateway.GatewayEnvelopeMetadata, payload["delivery_metadata"], use_maximum)
    value = model.model_validate_json(json.dumps(_at_boundary(model, payload, use_maximum)))
    to_pb, from_pb = _adapter_pair(model)
    wire = to_pb(value)
    assert from_pb(wire.__class__.FromString(wire.SerializeToString())) == value
