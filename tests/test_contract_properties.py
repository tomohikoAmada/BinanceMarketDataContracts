"""Test contract model properties: frozen, strict, extra=forbid."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.enums import (
    ContractStatus,
    HealthState,
    Market,
    QualityFlag,
    ReasonCode,
    ReliabilityState,
    Stream,
    Venue,
)
from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate, EventMetadata, PriceLevel
from binance_market_data_contracts.snapshots import (
    DataHealthSnapshot,
    ExchangeDepthSnapshot,
    GapDescriptor,
    LatencySummary,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)

ALL_PUBLIC_MODELS = [
    EventMetadata,
    PriceLevel,
    DepthUpdate,
    AggTrade,
    BookTicker,
    ExchangeDepthSnapshot,
    GapDescriptor,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
    LatencySummary,
    DataHealthSnapshot,
]


class TestFrozen:
    @pytest.mark.parametrize("model_cls", ALL_PUBLIC_MODELS)
    def test_model_is_frozen(self, model_cls):
        config = model_cls.model_config
        assert config.get("frozen") is True or config.get("frozen") is None
        instance = _make_instance(model_cls)
        with pytest.raises((ValidationError, TypeError, ValueError, AttributeError, RuntimeError)):
            if isinstance(instance, PriceLevel):
                instance.price = "999"  # type: ignore[misc]
            elif isinstance(instance, EventMetadata):
                instance.venue = Venue.BINANCE  # type: ignore[misc]
            elif isinstance(instance, DepthUpdate):
                instance.first_update_id = 9999  # type: ignore[misc]
            elif isinstance(instance, AggTrade):
                instance.aggregate_trade_id = 9999  # type: ignore[misc]
            elif isinstance(instance, BookTicker):
                instance.best_bid_price = "999"  # type: ignore[misc]
            elif isinstance(instance, ExchangeDepthSnapshot):
                instance.last_update_id = 9999  # type: ignore[misc]
            elif isinstance(instance, LocalOrderBookSnapshot):
                instance.synchronized = False  # type: ignore[misc]
            elif isinstance(instance, MarketStateSnapshot):
                instance.mid_price = "999"  # type: ignore[misc]
            elif isinstance(instance, LatencySummary):
                instance.count = 999  # type: ignore[misc]
            elif isinstance(instance, DataHealthSnapshot):
                instance.overall_state = HealthState.UNRELIABLE  # type: ignore[misc]
            elif isinstance(instance, GapDescriptor):
                instance.stream = Stream.BOOK_TICKER  # type: ignore[misc]


class TestExtraForbid:
    def test_extra_field_rejected(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "stream": "DIFF_DEPTH",
            "producer": "test",
            "producer_version": "0.1.0",
            "schema_version": "depth-update.v1",
            "connection_id": "conn-1",
            "extra_field": "should fail",
        }
        with pytest.raises(ValidationError, match="extra"):
            EventMetadata(**data)


class TestEnumStringValues:
    @pytest.mark.parametrize(
        "enum_cls", [Venue, Market, Stream, HealthState, ReliabilityState, QualityFlag, ReasonCode, ContractStatus]
    )
    def test_enum_values_are_strings(self, enum_cls):
        for member in enum_cls:
            assert isinstance(member.value, str), f"{enum_cls.__name__}.{member.name} value is not str"
            assert member.value == member.value.upper(), (
                f"{enum_cls.__name__}.{member.name} value not uppercase: {member.value}"
            )


def _make_instance(model_cls):
    if model_cls is EventMetadata:
        return EventMetadata(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            stream="DIFF_DEPTH",
            producer="test",
            producer_version="0.1.0",
            schema_version="depth-update.v1",
            connection_id="conn-1",
        )
    elif model_cls is PriceLevel:
        return PriceLevel(price="100.00", quantity="1.0")
    elif model_cls is DepthUpdate:
        return DepthUpdate(
            metadata=_make_metadata("DIFF_DEPTH", "depth-update.v1"),
            first_update_id=1,
            final_update_id=2,
            bids=[],
            asks=[],
        )
    elif model_cls is AggTrade:
        return AggTrade(
            metadata=_make_metadata("AGG_TRADE", "agg-trade.v1"),
            aggregate_trade_id=1,
            price="100.00",
            quantity="1.0",
            first_trade_id=1,
            last_trade_id=1,
            trade_time_ms=1000,
            buyer_is_maker=False,
        )
    elif model_cls is BookTicker:
        return BookTicker(
            metadata=_make_metadata("BOOK_TICKER", "book-ticker.v1"),
            update_id=None,
            best_bid_price="100.00",
            best_bid_quantity="1.0",
            best_ask_price="101.00",
            best_ask_quantity="1.0",
        )
    elif model_cls is ExchangeDepthSnapshot:
        return ExchangeDepthSnapshot(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            schema_version="v1",
            producer="test",
            producer_version="0.1.0",
            request_id="req-1",
            last_update_id=1,
            bids=[],
            asks=[],
            quality_flags=[],
        )
    elif model_cls is GapDescriptor:
        return GapDescriptor(stream="DIFF_DEPTH", detected_at_utc_ns=1000)
    elif model_cls is LocalOrderBookSnapshot:
        return LocalOrderBookSnapshot(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            schema_version="v1",
            producer="test",
            producer_version="0.1.0",
            source="test",
            last_update_id=1,
            synchronized=True,
            quality_flags=[],
        )
    elif model_cls is MarketStateSnapshot:
        return MarketStateSnapshot(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            schema_version="v1",
            producer="test",
            producer_version="0.1.0",
        )
    elif model_cls is LatencySummary:
        return LatencySummary(
            count=1,
            min_ms=10.0,
            max_ms=20.0,
            p50_ms=15.0,
            p95_ms=18.0,
            p99_ms=20.0,
            window_start_utc_ns=1000,
            window_end_utc_ns=2000,
        )
    elif model_cls is DataHealthSnapshot:
        return DataHealthSnapshot(
            overall_state="HEALTHY",
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            schema_version="v1",
            sequence_gap_count=0,
        )
    raise ValueError(f"No factory for {model_cls}")


def _make_metadata(stream: str, schema_version: str) -> EventMetadata:
    return EventMetadata(
        venue="BINANCE",
        market="SPOT",
        symbol="BTCUSDT",
        stream=stream,
        producer="test",
        producer_version="0.1.0",
        schema_version=schema_version,
        connection_id="conn-1",
    )
