"""Test Protobuf descriptor properties: field numbers, enum zero values, no forbidden types."""

import pytest
from google.protobuf import descriptor_pool

# Ensure all generated modules are loaded so descriptors are in the pool
from binance_market_data.common.v1 import (
    enums_pb2,  # noqa: F401
    identifiers_pb2,  # noqa: F401
    metadata_pb2,  # noqa: F401
)
from binance_market_data.gateway.v1 import (
    gateway_messages_pb2,  # noqa: F401
    gateway_service_pb2,  # noqa: F401
)
from binance_market_data.market.v1 import market_events_pb2  # noqa: F401
from binance_market_data.projection.v1 import snapshots_pb2  # noqa: F401
from binance_market_data.telemetry.v1 import telemetry_pb2  # noqa: F401

_pool = descriptor_pool.Default()


def _get_message_descriptor(full_name: str):
    try:
        return _pool.FindMessageTypeByName(full_name)
    except KeyError:
        pytest.skip(f"Message type {full_name} not found in descriptor pool")


def _get_enum_descriptor(full_name: str):
    try:
        return _pool.FindEnumTypeByName(full_name)
    except KeyError:
        pytest.skip(f"Enum type {full_name} not found in descriptor pool")


@pytest.mark.parametrize(
    "enum_full_name",
    [
        "binance_market_data.common.v1.Venue",
        "binance_market_data.common.v1.Market",
        "binance_market_data.common.v1.Stream",
        "binance_market_data.common.v1.QualityFlag",
        "binance_market_data.common.v1.ReasonCode",
        "binance_market_data.common.v1.ConnectionState",
        "binance_market_data.common.v1.ResyncState",
        "binance_market_data.common.v1.SnapshotSource",
        "binance_market_data.common.v1.DeliveryMode",
        "binance_market_data.common.v1.InitialSnapshotMode",
        "binance_market_data.common.v1.ConsumerGapReason",
        "binance_market_data.common.v1.RecoveryAction",
        "binance_market_data.common.v1.StreamLifecycleState",
        "binance_market_data.common.v1.HealthState",
        "binance_market_data.common.v1.ReferenceSourceKind",
        "binance_market_data.common.v1.ReferenceObservationStatus",
    ],
)
def test_enum_zero_is_unspecified(enum_full_name):
    enum_desc = _get_enum_descriptor(enum_full_name)
    zero_value = enum_desc.values[0]
    assert "UNSPECIFIED" in zero_value.name.upper(), (
        f"Enum {enum_full_name} zero value '{zero_value.name}' is not UNSPECIFIED"
    )


def test_enum_values_are_unique():
    enums_to_check = [
        _get_enum_descriptor("binance_market_data.common.v1.Venue"),
        _get_enum_descriptor("binance_market_data.common.v1.Market"),
        _get_enum_descriptor("binance_market_data.common.v1.Stream"),
    ]
    for ed in enums_to_check:
        values = [v.number for v in ed.values]
        assert len(values) == len(set(values)), f"Duplicate values in {ed.full_name}"


PRICE_QUANTITY_MESSAGES = [
    "binance_market_data.market.v1.DepthUpdate",
    "binance_market_data.market.v1.AggTrade",
    "binance_market_data.market.v1.BookTicker",
    "binance_market_data.market.v1.MarkPrice",
    "binance_market_data.market.v1.Liquidation",
    "binance_market_data.market.v1.ExchangeDepthSnapshot",
    "binance_market_data.market.v1.ReferenceObservation",
]


@pytest.mark.parametrize("msg_name", PRICE_QUANTITY_MESSAGES)
def test_price_fields_are_string(msg_name):
    msg = _get_message_descriptor(msg_name)
    price_quantity_fields = []
    for field in msg.fields:
        if "price" in field.name.lower() or "quantity" in field.name.lower():
            price_quantity_fields.append(field)
    for field in price_quantity_fields:
        if field.type == 11:  # TYPE_MESSAGE (nested PriceLevel)
            continue
        assert field.type == 9, (  # TYPE_STRING = 9
            f"Field {msg_name}.{field.name} should be string, got type {field.type}"
        )


ALL_MESSAGE_NAMES_TO_CHECK = [
    "binance_market_data.market.v1.DepthUpdate",
    "binance_market_data.market.v1.AggTrade",
    "binance_market_data.market.v1.BookTicker",
    "binance_market_data.market.v1.MarkPrice",
    "binance_market_data.market.v1.Liquidation",
    "binance_market_data.market.v1.ReferenceObservation",
    "binance_market_data.market.v1.ExchangeDepthSnapshot",
    "binance_market_data.projection.v1.LocalOrderBookSnapshot",
    "binance_market_data.projection.v1.MarketStateSnapshot",
    "binance_market_data.projection.v1.DataHealthSnapshot",
    "binance_market_data.gateway.v1.GatewayEventEnvelope",
    "binance_market_data.gateway.v1.OrderBookStreamItem",
    "binance_market_data.gateway.v1.MarketStateStreamItem",
    "binance_market_data.telemetry.v1.TelemetryEnvelope",
]


def test_no_timestamp_field_name():
    for msg_full_name in ALL_MESSAGE_NAMES_TO_CHECK:
        msg = _get_message_descriptor(msg_full_name)
        for field in msg.fields:
            assert field.name != "timestamp", f"Field 'timestamp' found in {msg_full_name}"


def test_no_float_double_prices():
    for msg_full_name in ALL_MESSAGE_NAMES_TO_CHECK:
        msg = _get_message_descriptor(msg_full_name)
        for field in msg.fields:
            if "price" in field.name.lower() or "quantity" in field.name.lower():
                assert field.type != 1 and field.type != 2, (  # TYPE_DOUBLE = 1, TYPE_FLOAT = 2
                    f"Field {msg_full_name}.{field.name} is float/double"
                )


def test_envelope_has_oneof():
    env = _get_message_descriptor("binance_market_data.gateway.v1.GatewayEventEnvelope")
    assert len(env.oneofs) >= 1, "GatewayEventEnvelope should have oneof payload"

    ob = _get_message_descriptor("binance_market_data.gateway.v1.OrderBookStreamItem")
    assert len(ob.oneofs) >= 1, "OrderBookStreamItem should have oneof payload"


def test_gateway_delivery_metadata_is_additive_and_canonical():
    common = _get_message_descriptor("binance_market_data.common.v1.EnvelopeMetadata")
    common_generation = common.fields_by_name["connection_generation"]
    assert not common_generation.has_presence

    delivery = _get_message_descriptor("binance_market_data.gateway.v1.GatewayEnvelopeMetadata")
    delivery_generation = delivery.fields_by_name["connection_generation"]
    assert delivery_generation.has_presence

    for message_name in ("GatewayEventEnvelope", "OrderBookStreamItem", "MarketStateStreamItem"):
        message = _get_message_descriptor(f"binance_market_data.gateway.v1.{message_name}")
        legacy = message.fields_by_name["envelope_metadata"]
        canonical = message.fields_by_name["delivery_metadata"]
        assert legacy.number == 1
        assert canonical.number == 2
        assert legacy.message_type.full_name == "binance_market_data.common.v1.EnvelopeMetadata"
        assert canonical.message_type.full_name == "binance_market_data.gateway.v1.GatewayEnvelopeMetadata"


def test_market_runtime_status_generation_is_optional():
    message = _get_message_descriptor("binance_market_data.gateway.v1.MarketRuntimeStatus")
    generation = message.fields_by_name["connection_generation"]
    assert generation.number == 6
    assert generation.has_presence


def test_c2_usdm_fields_are_additive_and_optional():
    agg_trade = _get_message_descriptor("binance_market_data.market.v1.AggTrade")
    normal_quantity = agg_trade.fields_by_name["normal_quantity"]
    assert normal_quantity.number == 9
    assert normal_quantity.has_presence

    mark_price = _get_message_descriptor("binance_market_data.market.v1.MarkPrice")
    assert mark_price.fields_by_name["next_funding_time_ms"].number == 6
    assert mark_price.fields_by_name["mark_price_moving_average"].has_presence

    snapshot = _get_message_descriptor("binance_market_data.market.v1.ExchangeDepthSnapshot")
    event_time = snapshot.fields_by_name["exchange_event_time_ms"]
    assert event_time.number == 15
    assert event_time.has_presence

    stream_status = _get_message_descriptor("binance_market_data.gateway.v1.StreamStatus")
    source_kind = stream_status.fields_by_name["reference_source_kind"]
    assert source_kind.number == 7
    assert source_kind.has_presence


def test_c2_gateway_oneof_carries_usdm_events():
    envelope = _get_message_descriptor("binance_market_data.gateway.v1.GatewayEventEnvelope")
    expected = {
        "mark_price": ("binance_market_data.market.v1.MarkPrice", 16),
        "liquidation": ("binance_market_data.market.v1.Liquidation", 17),
        "reference_observation": ("binance_market_data.market.v1.ReferenceObservation", 18),
    }
    for name, (full_name, number) in expected.items():
        field = envelope.fields_by_name[name]
        assert field.number == number
        assert field.message_type.full_name == full_name
        assert field.containing_oneof.name == "payload"


def test_reference_observation_payload_is_typed_oneof():
    message = _get_message_descriptor("binance_market_data.market.v1.ReferenceObservation")
    expected = {
        "open_interest": 20,
        "top_long_short_account_ratio": 21,
        "top_long_short_position_ratio": 22,
        "global_long_short_account_ratio": 23,
        "taker_buy_sell_volume": 24,
        "instrument": 25,
        "depth_baseline": 26,
    }
    for name, number in expected.items():
        field = message.fields_by_name[name]
        assert field.number == number
        assert field.containing_oneof.name == "payload"
