"""Tests for the opaque UTF-8 Symbol identity contract."""

import pytest
from jsonschema import Draft202012Validator
from pydantic import TypeAdapter, ValidationError

from binance_market_data_contracts.enums import DeliveryMode, Market, Stream, Venue
from binance_market_data_contracts.gateway import EventSubscriptionRequest, StreamSelector
from binance_market_data_contracts.identifiers import RequestId, Symbol
from binance_market_data_contracts.wire.adapters import (
    event_subscription_request_from_pb,
    event_subscription_request_to_pb,
)

_SYMBOL_ADAPTER = TypeAdapter(Symbol)

_VALID_SYMBOLS = (
    "A",
    "BTCUSDT",
    "bTcUsdt",
    "X" * 21,
    "\uff11\uff12\uff13\uff14\uff15\uff16",
    "这是测试币456",
    "¢",
    "\U0001f4b1",
    "\U0010ffff",
    "\u0080",
    "\u00a0",
    "\u3000",
    "\u00e9",
    "e\u0301",
)


@pytest.mark.parametrize("symbol", _VALID_SYMBOLS)
def test_valid_symbol_is_preserved_exactly(symbol: str) -> None:
    assert _SYMBOL_ADAPTER.validate_python(symbol) == symbol
    assert _SYMBOL_ADAPTER.validate_json(_SYMBOL_ADAPTER.dump_json(symbol)) == symbol


@pytest.mark.parametrize("code_point", range(0x21))
def test_symbol_rejects_ascii_c0_controls_and_whitespace(code_point: int) -> None:
    with pytest.raises(ValidationError, match="String should match pattern"):
        _SYMBOL_ADAPTER.validate_python(f"BTC{chr(code_point)}USDT")


def test_symbol_rejects_empty_and_del() -> None:
    for symbol in ("", "BTC\u007fUSDT"):
        with pytest.raises(ValidationError):
            _SYMBOL_ADAPTER.validate_python(symbol)


@pytest.mark.parametrize("symbol", ("\ud800", "\udfff", "BTC\ud800USDT"))
def test_symbol_rejects_lone_surrogates(symbol: str) -> None:
    with pytest.raises(ValidationError, match="Unicode scalar values"):
        _SYMBOL_ADAPTER.validate_python(symbol)


@pytest.mark.parametrize("payload", (b'"\\ud800"', b'"\\udfff"'))
def test_symbol_json_rejects_escaped_lone_surrogates(payload: bytes) -> None:
    with pytest.raises(ValidationError) as exc_info:
        _SYMBOL_ADAPTER.validate_json(payload)

    assert exc_info.value.errors()[0]["type"] == "json_invalid"


def test_symbol_json_accepts_escaped_surrogate_pair() -> None:
    assert _SYMBOL_ADAPTER.validate_json(b'"\\ud83d\\udcb1"') == "\U0001f4b1"


def test_symbol_json_schema_exposes_portable_constraints() -> None:
    schema = _SYMBOL_ADAPTER.json_schema()

    assert schema["minLength"] == 1
    assert "maxLength" not in schema
    assert schema["pattern"] == r"^(?![\s\S]*[\u0000-\u0020\u007F])[\s\S]+$"

    validator = Draft202012Validator(schema)
    for symbol in _VALID_SYMBOLS:
        assert not list(validator.iter_errors(symbol))
    for symbol in ("", "BTC USDT", "BTC\tUSDT", "BTC\nUSDT", "BTC\n", "BTC\u007fUSDT"):
        assert list(validator.iter_errors(symbol))


@pytest.mark.parametrize("symbol", _VALID_SYMBOLS)
def test_symbol_pydantic_protobuf_roundtrip_preserves_identity(symbol: str) -> None:
    request = EventSubscriptionRequest(
        request_id=RequestId("symbol-roundtrip"),
        schema_version="event-subscription-request.v1",
        selectors=(
            StreamSelector(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol=symbol,
                stream=Stream.DIFF_DEPTH,
            ),
        ),
        delivery_mode=DeliveryMode.CONTIGUOUS_EVENTS,
        supported_payload_schema_versions=("depth-update.v1",),
    )

    wire_request = event_subscription_request_to_pb(request)
    assert wire_request.selectors[0].symbol == symbol
    serialized = wire_request.SerializeToString()
    parsed_wire_request = wire_request.__class__()
    parsed_wire_request.ParseFromString(serialized)
    restored = event_subscription_request_from_pb(parsed_wire_request)

    assert restored.selectors[0].symbol == symbol
