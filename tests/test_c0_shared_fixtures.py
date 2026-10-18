"""Source-time and binary-presence oracles for producer repositories to reuse."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from binance_market_data.gateway.v1 import gateway_messages_pb2
from binance_market_data.market.v1 import market_events_pb2
from binance_market_data_contracts import DepthUpdate
from binance_market_data_contracts.wire import adapters

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
TIMES = json.loads((FIXTURES / "integration/usdm-depth-time.v1.json").read_text())
PRESENCE = json.loads((FIXTURES / "integration/consumer-gap-presence.v1.json").read_text())


def _domain_payload(metadata):
    payload = json.loads((FIXTURES / "valid/depth-update.v1.usdm.json").read_text())
    payload["metadata"].update(metadata)
    raw = TIMES["raw"]
    payload.update(first_update_id=raw["U"], final_update_id=raw["u"], previous_final_update_id=raw["pu"])
    payload["bids"] = [dict(zip(("price", "quantity"), level, strict=True)) for level in raw["b"]]
    payload["asks"] = [dict(zip(("price", "quantity"), level, strict=True)) for level in raw["a"]]
    return payload


@pytest.mark.parametrize("case", TIMES["cases"], ids=lambda c: c["name"])
def test_transaction_time_fixture_roundtrips_without_trade_time(case):
    raw = copy.deepcopy(TIMES["raw"])
    raw.update(case["source_patch"])
    for field in case["remove_source_fields"]:
        del raw[field]
    expected = case["expected_metadata"]
    assert expected["exchange_event_time_ms"] == raw["E"]
    assert expected["exchange_transaction_time_ms"] == raw.get("T")
    assert expected["exchange_trade_time_ms"] is None
    value = DepthUpdate.model_validate_json(json.dumps(_domain_payload(expected)))
    wire = adapters.depth_update_to_pb(value)
    decoded = market_events_pb2.DepthUpdate.FromString(wire.SerializeToString())
    assert decoded.metadata.HasField("exchange_transaction_time_ms") == ("T" in raw)
    assert not decoded.metadata.HasField("exchange_trade_time_ms")
    assert adapters.depth_update_from_pb(decoded) == value
    assert value.asks[0].quantity == "0.00000000"


@pytest.mark.parametrize("wrong", TIMES["invalid_metadata"])
def test_wrong_mapping_is_structurally_valid_but_fails_source_oracle(wrong):
    # Domain validation cannot recover the raw exchange field's origin.
    value = DepthUpdate.model_validate_json(json.dumps(_domain_payload(wrong)))
    decoded = adapters.depth_update_from_pb(adapters.depth_update_to_pb(value))
    actual = {field: getattr(decoded.metadata, field) for field in TIMES["expected_metadata"]}
    assert actual != TIMES["expected_metadata"]


@pytest.mark.parametrize("patch", [patch for patch in TIMES["invalid_source_patches"] if patch["T"] is not None])
def test_invalid_transaction_values_cannot_be_domain_integers(patch):
    expected = dict(TIMES["expected_metadata"], exchange_transaction_time_ms=patch["T"])
    with pytest.raises(ValidationError):
        DepthUpdate.model_validate_json(json.dumps(_domain_payload(expected)))


@pytest.mark.parametrize("case", PRESENCE["cases"], ids=lambda c: c["name"])
def test_binary_symbol_presence_fixture(case):
    wire = gateway_messages_pb2.ConsumerGapNotice.FromString(bytes.fromhex(case["protobuf_hex"]))
    assert wire.HasField("symbol") == case["symbol_present"]
    assert wire.symbol == (case["symbol"] if case["symbol_present"] else "")
    if not case["domain_valid"]:
        with pytest.raises(ValidationError) as error:
            adapters.consumer_gap_notice_from_pb(wire)
        assert any(e["loc"] == ("symbol",) and e["type"] == "string_too_short" for e in error.value.errors())
    else:
        value = adapters.consumer_gap_notice_from_pb(wire)
        assert value.symbol == case["symbol"]
        assert (
            adapters.consumer_gap_notice_to_pb(value).SerializeToString(deterministic=True).hex()
            == case["protobuf_hex"]
        )


@pytest.mark.parametrize(
    "wrapper,payload_name,from_pb",
    (
        (gateway_messages_pb2.GatewayEventEnvelope, "consumer_gap", adapters.gateway_event_envelope_from_pb),
        (gateway_messages_pb2.OrderBookStreamItem, "consumer_gap", adapters.order_book_stream_item_from_pb),
    ),
)
def test_nested_present_empty_symbol_is_rejected(wrapper, payload_name, from_pb):
    empty = next(case for case in PRESENCE["cases"] if case["name"] == "present-empty")
    gap = gateway_messages_pb2.ConsumerGapNotice.FromString(bytes.fromhex(empty["protobuf_hex"]))
    wire = wrapper()
    wire.delivery_metadata.protocol_version = "gateway-stream.v1"
    wire.delivery_metadata.gateway_instance_id = "gw-c0"
    wire.delivery_metadata.subscription_id = gap.subscription_id
    wire.delivery_metadata.session_sequence = 1
    getattr(wire, payload_name).CopyFrom(gap)
    with pytest.raises(ValidationError):
        from_pb(wrapper.FromString(wire.SerializeToString()))
