"""Explicit Pydantic ↔ Protobuf adapters.

Each adapter explicitly maps fields — no reflection, no auto-mapping, no model_dump.
All Proto → Pydantic conversions validate through Pydantic strict mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Mapping

# Generated Protobuf stubs are installed as the normal top-level
# binance_market_data package. Importing wire does not modify sys.path.
from binance_market_data.common.v1 import enums_pb2 as pb_enums
from binance_market_data.common.v1 import identifiers_pb2 as pb_id
from binance_market_data.common.v1 import metadata_pb2 as pb_meta
from binance_market_data.gateway.v1 import gateway_messages_pb2 as pb_gw
from binance_market_data.market.v1 import market_events_pb2 as pb_events
from binance_market_data.projection.v1 import snapshots_pb2 as pb_snap
from binance_market_data.telemetry.v1 import telemetry_pb2 as pb_telemetry
from binance_market_data_contracts.common import PriceString, QuantityString
from binance_market_data_contracts.enums import (
    ConnectionState,
    ConsumerGapReason,
    DeliveryMode,
    HealthState,
    InitialSnapshotMode,
    Market,
    QualityFlag,
    ReasonCode,
    RecoveryAction,
    ResyncState,
    SnapshotSource,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.gateway import (
    ConsumerGapNotice,
    EnvelopeMetadata,
    EventSubscriptionRequest,
    GatewayEnvelopeMetadata,
    GatewayEventEnvelope,
    GatewayStatusRequest,
    GatewayStatusSnapshot,
    MarketRuntimeStatus,
    MarketStateStreamItem,
    MarketStateSubscriptionRequest,
    OrderBookStreamItem,
    OrderBookSubscriptionRequest,
    StreamSelector,
    StreamStatus,
    SubscriptionAccepted,
)
from binance_market_data_contracts.identifiers import (
    ConnectionId,
    GatewayInstanceId,
    InstanceId,
    RequestId,
    SnapshotId,
    SubscriptionId,
    Symbol,
)
from binance_market_data_contracts.market_events import (
    AggTrade,
    AggTradeMetadata,
    BookTicker,
    BookTickerMetadata,
    DepthUpdate,
    DepthUpdateMetadata,
    PriceLevel,
)
from binance_market_data_contracts.snapshots import (
    DataHealthSnapshot,
    ExchangeDepthSnapshot,
    GapDescriptor,
    LatencySummary,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)
from binance_market_data_contracts.telemetry import (
    BookMetrics,
    ConnectionMetrics,
    LatencyMetrics,
    QueueMetrics,
    SequenceMetrics,
    SystemMetrics,
    TelemetryEnvelope,
    TelemetryType,
)


class WireError(Exception):
    """Base error for wire conversion failures."""


class UnspecifiedEnumError(WireError):
    """A protobuf enum was UNSPECIFIED (0), which is not a legal business value."""

    def __init__(self, enum_name: str, value: int, context: str) -> None:
        super().__init__(f"{context}: Protobuf enum {enum_name} value {value} is UNSPECIFIED")


class UnsupportedSchemaVersionError(WireError):
    """A schema_version is not supported."""

    def __init__(self, expected: str, got: str) -> None:
        super().__init__(f"Unsupported schema version: expected '{expected}', got '{got}'")


class UnexpectedWireValueError(WireError):
    def __init__(self, contract: str, field: str, expected: str, got: str) -> None:
        super().__init__(f"{contract}.{field}: expected '{expected}', got '{got}'")


class UnknownEnumValueError(WireError):
    def __init__(self, enum_name: str, value: int, context: str) -> None:
        super().__init__(f"Unknown {enum_name} value {value} in {context}")


class MissingWireFieldError(WireError):
    def __init__(self, contract: str, field: str) -> None:
        super().__init__(f"{contract}: missing required field '{field}'")


def _require_exact_string(*, contract: str, field: str, actual: str, expected: str) -> None:
    if actual != expected:
        raise UnexpectedWireValueError(contract, field, expected, actual)


TEnum = TypeVar("TEnum")


def _mapped_enum_from_pb(
    *,
    value: int,
    mapping: Mapping[int, TEnum],
    enum_name: str,
    context: str,
    unspecified_value: int,
    allow_unspecified_none: bool = False,
) -> TEnum | None:
    """Map a protobuf enum while preserving optional presence semantics."""
    if value == unspecified_value:
        if allow_unspecified_none:
            return None
        raise UnspecifiedEnumError(enum_name, value, context)
    try:
        return mapping[value]
    except KeyError:
        raise UnknownEnumValueError(enum_name, value, context) from None


# ---------------------------------------------------------------------------
# Enum mapping dictionaries
# ---------------------------------------------------------------------------

_VENUE_PB_TO_PY: Mapping[int, Venue] = {
    pb_enums.Venue.VENUE_BINANCE: Venue.BINANCE,
}

_VENUE_PY_TO_PB: Mapping[Venue, int] = {v: k for k, v in _VENUE_PB_TO_PY.items()}


def _venue_from_pb(v: int, context: str = "WireContract.venue") -> Venue:
    result = _mapped_enum_from_pb(
        value=v,
        mapping=_VENUE_PB_TO_PY,
        enum_name="Venue",
        context=context,
        unspecified_value=pb_enums.Venue.VENUE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _venue_to_pb(v: Venue) -> Any:
    return _VENUE_PY_TO_PB[v]


_MARKET_PB_TO_PY: Mapping[int, Market] = {
    pb_enums.Market.MARKET_SPOT: Market.SPOT,
    pb_enums.Market.MARKET_USD_M_PERPETUAL: Market.USD_M_PERPETUAL,
}

_MARKET_PY_TO_PB: Mapping[Market, int] = {v: k for k, v in _MARKET_PB_TO_PY.items()}


def _market_from_pb(v: int, context: str = "WireContract.market") -> Market:
    result = _mapped_enum_from_pb(
        value=v,
        mapping=_MARKET_PB_TO_PY,
        enum_name="Market",
        context=context,
        unspecified_value=pb_enums.Market.MARKET_UNSPECIFIED,
    )
    assert result is not None
    return result


def _market_to_pb(v: Market) -> Any:
    return _MARKET_PY_TO_PB[v]


_STREAM_PB_TO_PY: Mapping[int, Stream] = {
    pb_enums.Stream.STREAM_DIFF_DEPTH: Stream.DIFF_DEPTH,
    pb_enums.Stream.STREAM_AGG_TRADE: Stream.AGG_TRADE,
    pb_enums.Stream.STREAM_BOOK_TICKER: Stream.BOOK_TICKER,
    pb_enums.Stream.STREAM_DEPTH_SNAPSHOT: Stream.DEPTH_SNAPSHOT,
}

_STREAM_PY_TO_PB: Mapping[Stream, int] = {v: k for k, v in _STREAM_PB_TO_PY.items()}


def _stream_from_pb(v: int, context: str = "WireContract.stream") -> Stream:
    result = _mapped_enum_from_pb(
        value=v,
        mapping=_STREAM_PB_TO_PY,
        enum_name="Stream",
        context=context,
        unspecified_value=pb_enums.Stream.STREAM_UNSPECIFIED,
    )
    assert result is not None
    return result


def _stream_to_pb(v: Stream) -> Any:
    return _STREAM_PY_TO_PB[v]


_QUALITY_FLAG_PB_TO_PY: Mapping[int, QualityFlag] = {
    pb_enums.QualityFlag.QUALITY_FLAG_DUPLICATE: QualityFlag.DUPLICATE,
    pb_enums.QualityFlag.QUALITY_FLAG_OUT_OF_ORDER: QualityFlag.OUT_OF_ORDER,
    pb_enums.QualityFlag.QUALITY_FLAG_SEQUENCE_GAP: QualityFlag.SEQUENCE_GAP,
    pb_enums.QualityFlag.QUALITY_FLAG_ORDERBOOK_RESYNC: QualityFlag.ORDERBOOK_RESYNC,
    pb_enums.QualityFlag.QUALITY_FLAG_SNAPSHOT_BRIDGE_PENDING: QualityFlag.SNAPSHOT_BRIDGE_PENDING,
    pb_enums.QualityFlag.QUALITY_FLAG_SNAPSHOT_TOO_OLD: QualityFlag.SNAPSHOT_TOO_OLD,
    pb_enums.QualityFlag.QUALITY_FLAG_BOOTSTRAP_BUFFER_OVERFLOW: QualityFlag.BOOTSTRAP_BUFFER_OVERFLOW,
    pb_enums.QualityFlag.QUALITY_FLAG_RECOVERED_TAIL: QualityFlag.RECOVERED_TAIL,
    pb_enums.QualityFlag.QUALITY_FLAG_MALFORMED_PAYLOAD: QualityFlag.MALFORMED_PAYLOAD,
    pb_enums.QualityFlag.QUALITY_FLAG_EXCHANGE_TIME_MISSING: QualityFlag.EXCHANGE_TIME_MISSING,
    pb_enums.QualityFlag.QUALITY_FLAG_RECEIVE_CLOCK_DISCONTINUITY: QualityFlag.RECEIVE_CLOCK_DISCONTINUITY,
    pb_enums.QualityFlag.QUALITY_FLAG_SLOW_CONSUMER_GAP: QualityFlag.SLOW_CONSUMER_GAP,
    pb_enums.QualityFlag.QUALITY_FLAG_PRODUCER_RESTART: QualityFlag.PRODUCER_RESTART,
    pb_enums.QualityFlag.QUALITY_FLAG_OVERLAP: QualityFlag.OVERLAP,
    pb_enums.QualityFlag.QUALITY_FLAG_IDENTITY_CONFLICT: QualityFlag.IDENTITY_CONFLICT,
    pb_enums.QualityFlag.QUALITY_FLAG_CROSSED_BOOK: QualityFlag.CROSSED_BOOK,
}

_QUALITY_FLAG_PY_TO_PB: Mapping[QualityFlag, int] = {v: k for k, v in _QUALITY_FLAG_PB_TO_PY.items()}


def _quality_from_pb(flags: list[int], context: str = "WireContract.quality_flags") -> tuple[QualityFlag, ...]:
    result: list[QualityFlag] = []
    for f in flags:
        mapped = _mapped_enum_from_pb(
            value=f,
            mapping=_QUALITY_FLAG_PB_TO_PY,
            enum_name="QualityFlag",
            context=context,
            unspecified_value=pb_enums.QualityFlag.QUALITY_FLAG_UNSPECIFIED,
        )
        assert mapped is not None
        result.append(mapped)
    return tuple(result)


def _quality_to_pb(flags: tuple[QualityFlag, ...]) -> list[Any]:
    return [_QUALITY_FLAG_PY_TO_PB[f] for f in flags]


def _optional_uint64(v: int | None) -> int | None:
    """Return None if the value represents 'not set', else the value."""
    return v if v is not None else None


# ---------------------------------------------------------------------------
# PriceLevel adapters
# ---------------------------------------------------------------------------


def price_level_from_pb(pl: pb_meta.PriceLevel) -> PriceLevel:
    return PriceLevel(price=PriceString(pl.price), quantity=QuantityString(pl.quantity))


def price_level_to_pb(pl: PriceLevel) -> pb_meta.PriceLevel:
    return pb_meta.PriceLevel(price=pl.price, quantity=pl.quantity)


# ---------------------------------------------------------------------------
# EventMetadata adapters
# ---------------------------------------------------------------------------


def _event_metadata_from_pb(m: pb_meta.EventMetadata, contract: str) -> dict[str, Any]:
    return {
        "venue": _venue_from_pb(m.venue, f"{contract}.metadata.venue"),
        "market": _market_from_pb(m.market, f"{contract}.metadata.market"),
        "symbol": Symbol(m.symbol),
        "producer": m.producer,
        "producer_version": m.producer_version,
        "connection_id": ConnectionId(m.connection_id),
        "exchange_event_time_ms": _optional_uint64(m.exchange_event_time_ms)
        if m.HasField("exchange_event_time_ms")
        else None,
        "exchange_trade_time_ms": _optional_uint64(m.exchange_trade_time_ms)
        if m.HasField("exchange_trade_time_ms")
        else None,
        "exchange_transaction_time_ms": _optional_uint64(m.exchange_transaction_time_ms)
        if m.HasField("exchange_transaction_time_ms")
        else None,
        "receive_time_utc_ns": _optional_uint64(m.receive_time_utc_ns) if m.HasField("receive_time_utc_ns") else None,
        "receive_monotonic_ns": _optional_uint64(m.receive_monotonic_ns)
        if m.HasField("receive_monotonic_ns")
        else None,
        "quality_flags": _quality_from_pb(list(m.quality_flags), f"{contract}.metadata.quality_flags"),
    }


def _event_metadata_to_pb(m: AggTradeMetadata | DepthUpdateMetadata | BookTickerMetadata) -> pb_meta.EventMetadata:
    mdl = pb_meta.EventMetadata()
    mdl.venue = _venue_to_pb(m.venue)
    mdl.market = _market_to_pb(m.market)
    mdl.symbol = m.symbol
    mdl.producer = m.producer
    mdl.producer_version = m.producer_version
    mdl.connection_id = m.connection_id
    mdl.stream = _stream_to_pb(m.stream)
    mdl.schema_version = m.schema_version
    if m.exchange_event_time_ms is not None:
        mdl.exchange_event_time_ms = m.exchange_event_time_ms
    if m.exchange_trade_time_ms is not None:
        mdl.exchange_trade_time_ms = m.exchange_trade_time_ms
    if m.exchange_transaction_time_ms is not None:
        mdl.exchange_transaction_time_ms = m.exchange_transaction_time_ms
    if m.receive_time_utc_ns is not None:
        mdl.receive_time_utc_ns = m.receive_time_utc_ns
    if m.receive_monotonic_ns is not None:
        mdl.receive_monotonic_ns = m.receive_monotonic_ns
    mdl.quality_flags.extend(_quality_to_pb(m.quality_flags))
    return mdl


# ---------------------------------------------------------------------------
# DepthUpdate adapters
# ---------------------------------------------------------------------------


def depth_update_from_pb(du: pb_events.DepthUpdate) -> DepthUpdate:
    stream = _stream_from_pb(du.metadata.stream, "DepthUpdate.metadata.stream")
    if stream != Stream.DIFF_DEPTH:
        raise UnexpectedWireValueError("DepthUpdate", "stream", "DIFF_DEPTH", stream.value)
    _require_exact_string(
        contract="DepthUpdate", field="schema_version", actual=du.metadata.schema_version, expected="depth-update.v1"
    )
    meta = _event_metadata_from_pb(du.metadata, "DepthUpdate")
    meta["stream"] = stream
    meta["schema_version"] = du.metadata.schema_version
    return DepthUpdate(
        metadata=DepthUpdateMetadata(**meta),
        first_update_id=du.first_update_id,
        final_update_id=du.final_update_id,
        previous_final_update_id=_optional_uint64(du.previous_final_update_id)
        if du.HasField("previous_final_update_id")
        else None,
        bids=tuple(price_level_from_pb(b) for b in du.bids),
        asks=tuple(price_level_from_pb(a) for a in du.asks),
    )


def depth_update_to_pb(du: DepthUpdate) -> pb_events.DepthUpdate:
    pb = pb_events.DepthUpdate()
    pb.metadata.CopyFrom(_event_metadata_to_pb(du.metadata))
    pb.first_update_id = du.first_update_id
    pb.final_update_id = du.final_update_id
    if du.previous_final_update_id is not None:
        pb.previous_final_update_id = du.previous_final_update_id
    pb.bids.extend(price_level_to_pb(b) for b in du.bids)
    pb.asks.extend(price_level_to_pb(a) for a in du.asks)
    return pb


# ---------------------------------------------------------------------------
# AggTrade adapters
# ---------------------------------------------------------------------------


def agg_trade_from_pb(at: pb_events.AggTrade) -> AggTrade:
    stream = _stream_from_pb(at.metadata.stream, "AggTrade.metadata.stream")
    if stream != Stream.AGG_TRADE:
        raise UnexpectedWireValueError("AggTrade", "stream", "AGG_TRADE", stream.value)
    _require_exact_string(
        contract="AggTrade", field="schema_version", actual=at.metadata.schema_version, expected="agg-trade.v1"
    )
    meta = _event_metadata_from_pb(at.metadata, "AggTrade")
    meta["stream"] = stream
    meta["schema_version"] = at.metadata.schema_version
    return AggTrade(
        metadata=AggTradeMetadata(**meta),
        aggregate_trade_id=at.aggregate_trade_id,
        price=PriceString(at.price),
        quantity=QuantityString(at.quantity),
        first_trade_id=at.first_trade_id,
        last_trade_id=at.last_trade_id,
        trade_time_ms=at.trade_time_ms,
        buyer_is_maker=at.buyer_is_maker,
    )


def agg_trade_to_pb(at: AggTrade) -> pb_events.AggTrade:
    pb = pb_events.AggTrade()
    pb.metadata.CopyFrom(_event_metadata_to_pb(at.metadata))
    pb.aggregate_trade_id = at.aggregate_trade_id
    pb.price = at.price
    pb.quantity = at.quantity
    pb.first_trade_id = at.first_trade_id
    pb.last_trade_id = at.last_trade_id
    pb.trade_time_ms = at.trade_time_ms
    pb.buyer_is_maker = at.buyer_is_maker
    return pb


# ---------------------------------------------------------------------------
# BookTicker adapters
# ---------------------------------------------------------------------------


def book_ticker_from_pb(bt: pb_events.BookTicker) -> BookTicker:
    stream = _stream_from_pb(bt.metadata.stream, "BookTicker.metadata.stream")
    if stream != Stream.BOOK_TICKER:
        raise UnexpectedWireValueError("BookTicker", "stream", "BOOK_TICKER", stream.value)
    _require_exact_string(
        contract="BookTicker", field="schema_version", actual=bt.metadata.schema_version, expected="book-ticker.v1"
    )
    meta = _event_metadata_from_pb(bt.metadata, "BookTicker")
    meta["stream"] = stream
    meta["schema_version"] = bt.metadata.schema_version
    return BookTicker(
        metadata=BookTickerMetadata(**meta),
        update_id=_optional_uint64(bt.update_id) if bt.HasField("update_id") else None,
        best_bid_price=PriceString(bt.best_bid_price),
        best_bid_quantity=QuantityString(bt.best_bid_quantity),
        best_ask_price=PriceString(bt.best_ask_price),
        best_ask_quantity=QuantityString(bt.best_ask_quantity),
    )


def book_ticker_to_pb(bt: BookTicker) -> pb_events.BookTicker:
    pb = pb_events.BookTicker()
    pb.metadata.CopyFrom(_event_metadata_to_pb(bt.metadata))
    if bt.update_id is not None:
        pb.update_id = bt.update_id
    pb.best_bid_price = bt.best_bid_price
    pb.best_bid_quantity = bt.best_bid_quantity
    pb.best_ask_price = bt.best_ask_price
    pb.best_ask_quantity = bt.best_ask_quantity
    return pb


# ---------------------------------------------------------------------------
# ExchangeDepthSnapshot adapters
# ---------------------------------------------------------------------------


def exchange_depth_snapshot_from_pb(es: pb_events.ExchangeDepthSnapshot) -> ExchangeDepthSnapshot:
    _require_exact_string(
        contract="ExchangeDepthSnapshot",
        field="schema_version",
        actual=es.schema_version,
        expected="exchange-depth-snapshot.v1",
    )
    return ExchangeDepthSnapshot(
        venue=_venue_from_pb(es.venue, "ExchangeDepthSnapshot.venue"),
        market=_market_from_pb(es.market, "ExchangeDepthSnapshot.market"),
        symbol=Symbol(es.symbol),
        schema_version="exchange-depth-snapshot.v1",
        producer=es.producer,
        producer_version=es.producer_version,
        request_id=RequestId(es.request_id),
        last_update_id=es.last_update_id,
        bids=tuple(price_level_from_pb(b) for b in es.bids),
        asks=tuple(price_level_from_pb(a) for a in es.asks),
        exchange_transaction_time_ms=_optional_uint64(es.exchange_transaction_time_ms)
        if es.HasField("exchange_transaction_time_ms")
        else None,
        receive_time_utc_ns=_optional_uint64(es.receive_time_utc_ns) if es.HasField("receive_time_utc_ns") else None,
        receive_monotonic_ns=_optional_uint64(es.receive_monotonic_ns) if es.HasField("receive_monotonic_ns") else None,
        quality_flags=_quality_from_pb(list(es.quality_flags), "ExchangeDepthSnapshot.quality_flags"),
    )


def exchange_depth_snapshot_to_pb(es: ExchangeDepthSnapshot) -> pb_events.ExchangeDepthSnapshot:
    pb = pb_events.ExchangeDepthSnapshot()
    pb.venue = _venue_to_pb(es.venue)
    pb.market = _market_to_pb(es.market)
    pb.symbol = es.symbol
    pb.schema_version = es.schema_version
    pb.producer = es.producer
    pb.producer_version = es.producer_version
    pb.request_id = es.request_id
    pb.last_update_id = es.last_update_id
    pb.bids.extend(price_level_to_pb(b) for b in es.bids)
    pb.asks.extend(price_level_to_pb(a) for a in es.asks)
    if es.exchange_transaction_time_ms is not None:
        pb.exchange_transaction_time_ms = es.exchange_transaction_time_ms
    if es.receive_time_utc_ns is not None:
        pb.receive_time_utc_ns = es.receive_time_utc_ns
    if es.receive_monotonic_ns is not None:
        pb.receive_monotonic_ns = es.receive_monotonic_ns
    pb.quality_flags.extend(_quality_to_pb(es.quality_flags))
    return pb


# ---------------------------------------------------------------------------
# GapDescriptor adapters
# ---------------------------------------------------------------------------


def _reason_code_from_pb(v: int, context: str = "WireContract.reason_code") -> ReasonCode | None:
    mapping: dict[int, ReasonCode] = {
        pb_enums.ReasonCode.REASON_CODE_CONNECTION_LOST: ReasonCode.CONNECTION_LOST,
        pb_enums.ReasonCode.REASON_CODE_CONNECTION_RESUMED: ReasonCode.CONNECTION_RESUMED,
        pb_enums.ReasonCode.REASON_CODE_PING_TIMEOUT: ReasonCode.PING_TIMEOUT,
        pb_enums.ReasonCode.REASON_CODE_LAST_MESSAGE_AGE_HIGH: ReasonCode.LAST_MESSAGE_AGE_HIGH,
        pb_enums.ReasonCode.REASON_CODE_RECEIVE_LATENCY_HIGH: ReasonCode.RECEIVE_LATENCY_HIGH,
        pb_enums.ReasonCode.REASON_CODE_PUBLISH_LATENCY_HIGH: ReasonCode.PUBLISH_LATENCY_HIGH,
        pb_enums.ReasonCode.REASON_CODE_SEQUENCE_GAP_DETECTED: ReasonCode.SEQUENCE_GAP_DETECTED,
        pb_enums.ReasonCode.REASON_CODE_SEQUENCE_GAP_TOO_LARGE: ReasonCode.SEQUENCE_GAP_TOO_LARGE,
        pb_enums.ReasonCode.REASON_CODE_RESYNC_IN_PROGRESS: ReasonCode.RESYNC_IN_PROGRESS,
        pb_enums.ReasonCode.REASON_CODE_RESYNC_FAILED: ReasonCode.RESYNC_FAILED,
        pb_enums.ReasonCode.REASON_CODE_BOOK_NOT_SYNCHRONIZED: ReasonCode.BOOK_NOT_SYNCHRONIZED,
        pb_enums.ReasonCode.REASON_CODE_BOOK_CROSSED: ReasonCode.BOOK_CROSSED,
        pb_enums.ReasonCode.REASON_CODE_BOOK_EMPTY: ReasonCode.BOOK_EMPTY,
        pb_enums.ReasonCode.REASON_CODE_RECORDER_STALLED: ReasonCode.RECORDER_STALLED,
        pb_enums.ReasonCode.REASON_CODE_GATEWAY_STALLED: ReasonCode.GATEWAY_STALLED,
        pb_enums.ReasonCode.REASON_CODE_DIVERGENCE_DETECTED: ReasonCode.DIVERGENCE_DETECTED,
        pb_enums.ReasonCode.REASON_CODE_DISK_SPACE_LOW: ReasonCode.DISK_SPACE_LOW,
        pb_enums.ReasonCode.REASON_CODE_QUEUE_BACKLOG: ReasonCode.QUEUE_BACKLOG,
        pb_enums.ReasonCode.REASON_CODE_ARCHIVE_BACKLOG: ReasonCode.ARCHIVE_BACKLOG,
        pb_enums.ReasonCode.REASON_CODE_CONFIGURATION_ERROR: ReasonCode.CONFIGURATION_ERROR,
    }
    return _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="ReasonCode",
        context=context,
        unspecified_value=pb_enums.ReasonCode.REASON_CODE_UNSPECIFIED,
        allow_unspecified_none=True,
    )


def _reason_code_to_pb(v: ReasonCode | None) -> Any:
    if v is None:
        return 0
    mapping: dict[ReasonCode, int] = {
        ReasonCode.CONNECTION_LOST: pb_enums.ReasonCode.REASON_CODE_CONNECTION_LOST,
        ReasonCode.CONNECTION_RESUMED: pb_enums.ReasonCode.REASON_CODE_CONNECTION_RESUMED,
        ReasonCode.PING_TIMEOUT: pb_enums.ReasonCode.REASON_CODE_PING_TIMEOUT,
        ReasonCode.LAST_MESSAGE_AGE_HIGH: pb_enums.ReasonCode.REASON_CODE_LAST_MESSAGE_AGE_HIGH,
        ReasonCode.RECEIVE_LATENCY_HIGH: pb_enums.ReasonCode.REASON_CODE_RECEIVE_LATENCY_HIGH,
        ReasonCode.PUBLISH_LATENCY_HIGH: pb_enums.ReasonCode.REASON_CODE_PUBLISH_LATENCY_HIGH,
        ReasonCode.SEQUENCE_GAP_DETECTED: pb_enums.ReasonCode.REASON_CODE_SEQUENCE_GAP_DETECTED,
        ReasonCode.SEQUENCE_GAP_TOO_LARGE: pb_enums.ReasonCode.REASON_CODE_SEQUENCE_GAP_TOO_LARGE,
        ReasonCode.RESYNC_IN_PROGRESS: pb_enums.ReasonCode.REASON_CODE_RESYNC_IN_PROGRESS,
        ReasonCode.RESYNC_FAILED: pb_enums.ReasonCode.REASON_CODE_RESYNC_FAILED,
        ReasonCode.BOOK_NOT_SYNCHRONIZED: pb_enums.ReasonCode.REASON_CODE_BOOK_NOT_SYNCHRONIZED,
        ReasonCode.BOOK_CROSSED: pb_enums.ReasonCode.REASON_CODE_BOOK_CROSSED,
        ReasonCode.BOOK_EMPTY: pb_enums.ReasonCode.REASON_CODE_BOOK_EMPTY,
        ReasonCode.RECORDER_STALLED: pb_enums.ReasonCode.REASON_CODE_RECORDER_STALLED,
        ReasonCode.GATEWAY_STALLED: pb_enums.ReasonCode.REASON_CODE_GATEWAY_STALLED,
        ReasonCode.DIVERGENCE_DETECTED: pb_enums.ReasonCode.REASON_CODE_DIVERGENCE_DETECTED,
        ReasonCode.DISK_SPACE_LOW: pb_enums.ReasonCode.REASON_CODE_DISK_SPACE_LOW,
        ReasonCode.QUEUE_BACKLOG: pb_enums.ReasonCode.REASON_CODE_QUEUE_BACKLOG,
        ReasonCode.ARCHIVE_BACKLOG: pb_enums.ReasonCode.REASON_CODE_ARCHIVE_BACKLOG,
        ReasonCode.CONFIGURATION_ERROR: pb_enums.ReasonCode.REASON_CODE_CONFIGURATION_ERROR,
    }
    return mapping[v]


def _resync_state_from_pb(v: int, context: str = "WireContract.resync_state") -> ResyncState | None:
    mapping: dict[int, ResyncState] = {
        pb_enums.ResyncState.RESYNC_STATE_SYNCHRONIZED: ResyncState.SYNCHRONIZED,
        pb_enums.ResyncState.RESYNC_STATE_RESYNC_REQUIRED: ResyncState.RESYNC_REQUIRED,
        pb_enums.ResyncState.RESYNC_STATE_RESYNC_IN_PROGRESS: ResyncState.RESYNC_IN_PROGRESS,
        pb_enums.ResyncState.RESYNC_STATE_RECOVERED: ResyncState.RECOVERED,
        pb_enums.ResyncState.RESYNC_STATE_RESYNC_FAILED: ResyncState.RESYNC_FAILED,
    }
    return _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="ResyncState",
        context=context,
        unspecified_value=pb_enums.ResyncState.RESYNC_STATE_UNSPECIFIED,
        allow_unspecified_none=True,
    )


def _resync_state_to_pb(v: ResyncState | None) -> Any:
    if v is None:
        return 0
    mapping: dict[ResyncState, int] = {
        ResyncState.SYNCHRONIZED: pb_enums.ResyncState.RESYNC_STATE_SYNCHRONIZED,
        ResyncState.RESYNC_REQUIRED: pb_enums.ResyncState.RESYNC_STATE_RESYNC_REQUIRED,
        ResyncState.RESYNC_IN_PROGRESS: pb_enums.ResyncState.RESYNC_STATE_RESYNC_IN_PROGRESS,
        ResyncState.RECOVERED: pb_enums.ResyncState.RESYNC_STATE_RECOVERED,
        ResyncState.RESYNC_FAILED: pb_enums.ResyncState.RESYNC_STATE_RESYNC_FAILED,
    }
    return mapping[v]


def _snapshot_source_from_pb(v: int, context: str = "LocalOrderBookSnapshot.source") -> SnapshotSource:
    mapping: dict[int, SnapshotSource] = {
        pb_enums.SnapshotSource.SNAPSHOT_SOURCE_GATEWAY_LIVE: SnapshotSource.GATEWAY_LIVE,
        pb_enums.SnapshotSource.SNAPSHOT_SOURCE_RECORDER_REPLAY: SnapshotSource.RECORDER_REPLAY,
        pb_enums.SnapshotSource.SNAPSHOT_SOURCE_HISTORY_REPLAY: SnapshotSource.HISTORY_REPLAY,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="SnapshotSource",
        context=context,
        unspecified_value=pb_enums.SnapshotSource.SNAPSHOT_SOURCE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _snapshot_source_to_pb(v: SnapshotSource) -> Any:
    mapping: dict[SnapshotSource, int] = {
        SnapshotSource.GATEWAY_LIVE: pb_enums.SnapshotSource.SNAPSHOT_SOURCE_GATEWAY_LIVE,
        SnapshotSource.RECORDER_REPLAY: pb_enums.SnapshotSource.SNAPSHOT_SOURCE_RECORDER_REPLAY,
        SnapshotSource.HISTORY_REPLAY: pb_enums.SnapshotSource.SNAPSHOT_SOURCE_HISTORY_REPLAY,
    }
    return mapping[v]


def gap_descriptor_from_pb(g: pb_snap.GapDescriptor) -> GapDescriptor:
    return GapDescriptor(
        stream=_stream_from_pb(g.stream, "GapDescriptor.stream"),
        detected_at_utc_ns=g.detected_at_utc_ns,
        previous_sequence=_optional_uint64(g.previous_sequence) if g.HasField("previous_sequence") else None,
        next_sequence=_optional_uint64(g.next_sequence) if g.HasField("next_sequence") else None,
        reason_code=_reason_code_from_pb(g.reason_code, "GapDescriptor.reason_code")
        if g.HasField("reason_code")
        else None,
        recovery_state=_resync_state_from_pb(g.recovery_state, "GapDescriptor.recovery_state")
        if g.HasField("recovery_state")
        else None,
    )


def gap_descriptor_to_pb(g: GapDescriptor) -> pb_snap.GapDescriptor:
    pb = pb_snap.GapDescriptor()
    pb.stream = _stream_to_pb(g.stream)
    pb.detected_at_utc_ns = g.detected_at_utc_ns
    if g.previous_sequence is not None:
        pb.previous_sequence = g.previous_sequence
    if g.next_sequence is not None:
        pb.next_sequence = g.next_sequence
    if g.reason_code is not None:
        pb.reason_code = _reason_code_to_pb(g.reason_code)
    if g.recovery_state is not None:
        pb.recovery_state = _resync_state_to_pb(g.recovery_state)
    return pb


# ---------------------------------------------------------------------------
# LocalOrderBookSnapshot adapters
# ---------------------------------------------------------------------------


def local_order_book_snapshot_from_pb(ls: pb_snap.LocalOrderBookSnapshot) -> LocalOrderBookSnapshot:
    _require_exact_string(
        contract="LocalOrderBookSnapshot",
        field="schema_version",
        actual=ls.schema_version,
        expected="local-order-book-snapshot.v1",
    )
    return LocalOrderBookSnapshot(
        venue=_venue_from_pb(ls.venue, "LocalOrderBookSnapshot.venue"),
        market=_market_from_pb(ls.market, "LocalOrderBookSnapshot.market"),
        symbol=Symbol(ls.symbol),
        schema_version="local-order-book-snapshot.v1",
        producer=ls.producer,
        producer_version=ls.producer_version,
        source=_snapshot_source_from_pb(ls.source),
        last_update_id=ls.last_update_id,
        bids=tuple(price_level_from_pb(b) for b in ls.bids),
        asks=tuple(price_level_from_pb(a) for a in ls.asks),
        depth_limit=ls.depth_limit if ls.HasField("depth_limit") else None,
        generated_time_utc_ns=ls.generated_time_utc_ns,
        generated_monotonic_ns=_optional_uint64(ls.generated_monotonic_ns)
        if ls.HasField("generated_monotonic_ns")
        else None,
        synchronized=ls.synchronized,
        last_gap=gap_descriptor_from_pb(ls.last_gap) if ls.HasField("last_gap") else None,
        quality_flags=_quality_from_pb(list(ls.quality_flags), "LocalOrderBookSnapshot.quality_flags"),
    )


def local_order_book_snapshot_to_pb(ls: LocalOrderBookSnapshot) -> pb_snap.LocalOrderBookSnapshot:
    pb = pb_snap.LocalOrderBookSnapshot()
    pb.venue = _venue_to_pb(ls.venue)
    pb.market = _market_to_pb(ls.market)
    pb.symbol = ls.symbol
    pb.schema_version = ls.schema_version
    pb.producer = ls.producer
    pb.producer_version = ls.producer_version
    pb.source = _snapshot_source_to_pb(ls.source)
    pb.last_update_id = ls.last_update_id
    pb.bids.extend(price_level_to_pb(b) for b in ls.bids)
    pb.asks.extend(price_level_to_pb(a) for a in ls.asks)
    if ls.depth_limit is not None:
        pb.depth_limit = ls.depth_limit
    pb.generated_time_utc_ns = ls.generated_time_utc_ns
    if ls.generated_monotonic_ns is not None:
        pb.generated_monotonic_ns = ls.generated_monotonic_ns
    pb.synchronized = ls.synchronized
    if ls.last_gap is not None:
        pb.last_gap.CopyFrom(gap_descriptor_to_pb(ls.last_gap))
    pb.quality_flags.extend(_quality_to_pb(ls.quality_flags))
    return pb


# ---------------------------------------------------------------------------
# MarketStateSnapshot adapters
# ---------------------------------------------------------------------------


def market_state_snapshot_from_pb(ms: pb_snap.MarketStateSnapshot) -> MarketStateSnapshot:
    _require_exact_string(
        contract="MarketStateSnapshot",
        field="schema_version",
        actual=ms.schema_version,
        expected="market-state-snapshot.v1",
    )
    return MarketStateSnapshot(
        venue=_venue_from_pb(ms.venue, "MarketStateSnapshot.venue"),
        market=_market_from_pb(ms.market, "MarketStateSnapshot.market"),
        symbol=Symbol(ms.symbol),
        schema_version="market-state-snapshot.v1",
        producer=ms.producer,
        producer_version=ms.producer_version,
        best_bid_price=PriceString(ms.best_bid_price) if ms.HasField("best_bid_price") and ms.best_bid_price else None,
        best_bid_quantity=QuantityString(ms.best_bid_quantity)
        if ms.HasField("best_bid_quantity") and ms.best_bid_quantity
        else None,
        best_ask_price=PriceString(ms.best_ask_price) if ms.HasField("best_ask_price") and ms.best_ask_price else None,
        best_ask_quantity=QuantityString(ms.best_ask_quantity)
        if ms.HasField("best_ask_quantity") and ms.best_ask_quantity
        else None,
        mid_price=PriceString(ms.mid_price) if ms.HasField("mid_price") and ms.mid_price else None,
        spread=QuantityString(ms.spread) if ms.HasField("spread") and ms.spread else None,
        microprice=PriceString(ms.microprice) if ms.HasField("microprice") and ms.microprice else None,
        top_bids=tuple(price_level_from_pb(b) for b in ms.top_bids),
        top_asks=tuple(price_level_from_pb(a) for a in ms.top_asks),
        depth_limit=ms.depth_limit if ms.HasField("depth_limit") else None,
        mark_price=PriceString(ms.mark_price) if ms.HasField("mark_price") and ms.mark_price else None,
        index_price=PriceString(ms.index_price) if ms.HasField("index_price") and ms.index_price else None,
        funding_rate=ms.funding_rate if ms.HasField("funding_rate") and ms.funding_rate else None,
        next_funding_time_ms=_optional_uint64(ms.next_funding_time_ms) if ms.HasField("next_funding_time_ms") else None,
        open_interest=QuantityString(ms.open_interest) if ms.HasField("open_interest") and ms.open_interest else None,
        generated_time_utc_ns=ms.generated_time_utc_ns,
        data_freshness_ms=_optional_uint64(ms.data_freshness_ms) if ms.HasField("data_freshness_ms") else None,
        book_synchronized=ms.book_synchronized if ms.HasField("book_synchronized") else None,
        source_book_update_id=_optional_uint64(ms.source_book_update_id)
        if ms.HasField("source_book_update_id")
        else None,
        source_trade_id=_optional_uint64(ms.source_trade_id) if ms.HasField("source_trade_id") else None,
    )


def market_state_snapshot_to_pb(ms: MarketStateSnapshot) -> pb_snap.MarketStateSnapshot:
    pb = pb_snap.MarketStateSnapshot()
    pb.venue = _venue_to_pb(ms.venue)
    pb.market = _market_to_pb(ms.market)
    pb.symbol = ms.symbol
    pb.schema_version = ms.schema_version
    pb.producer = ms.producer
    pb.producer_version = ms.producer_version
    if ms.best_bid_price is not None:
        pb.best_bid_price = ms.best_bid_price
    if ms.best_bid_quantity is not None:
        pb.best_bid_quantity = ms.best_bid_quantity
    if ms.best_ask_price is not None:
        pb.best_ask_price = ms.best_ask_price
    if ms.best_ask_quantity is not None:
        pb.best_ask_quantity = ms.best_ask_quantity
    if ms.mid_price is not None:
        pb.mid_price = ms.mid_price
    if ms.spread is not None:
        pb.spread = ms.spread
    if ms.microprice is not None:
        pb.microprice = ms.microprice
    pb.top_bids.extend(price_level_to_pb(b) for b in ms.top_bids)
    pb.top_asks.extend(price_level_to_pb(a) for a in ms.top_asks)
    if ms.depth_limit is not None:
        pb.depth_limit = ms.depth_limit
    if ms.mark_price is not None:
        pb.mark_price = ms.mark_price
    if ms.index_price is not None:
        pb.index_price = ms.index_price
    if ms.funding_rate is not None:
        pb.funding_rate = ms.funding_rate
    if ms.next_funding_time_ms is not None:
        pb.next_funding_time_ms = ms.next_funding_time_ms
    if ms.open_interest is not None:
        pb.open_interest = ms.open_interest
    pb.generated_time_utc_ns = ms.generated_time_utc_ns
    if ms.data_freshness_ms is not None:
        pb.data_freshness_ms = ms.data_freshness_ms
    if ms.book_synchronized is not None:
        pb.book_synchronized = ms.book_synchronized
    if ms.source_book_update_id is not None:
        pb.source_book_update_id = ms.source_book_update_id
    if ms.source_trade_id is not None:
        pb.source_trade_id = ms.source_trade_id
    return pb


# ---------------------------------------------------------------------------
# DataHealthSnapshot adapters
# ---------------------------------------------------------------------------


def _health_state_from_pb(v: int, context: str = "DataHealthSnapshot.state") -> HealthState:
    mapping: dict[int, HealthState] = {
        pb_enums.HealthState.HEALTH_STATE_HEALTHY: HealthState.HEALTHY,
        pb_enums.HealthState.HEALTH_STATE_DEGRADED: HealthState.DEGRADED,
        pb_enums.HealthState.HEALTH_STATE_UNRELIABLE: HealthState.UNRELIABLE,
        pb_enums.HealthState.HEALTH_STATE_UNAVAILABLE: HealthState.UNAVAILABLE,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="HealthState",
        context=context,
        unspecified_value=pb_enums.HealthState.HEALTH_STATE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _health_state_to_pb(v: HealthState) -> Any:
    mapping: dict[HealthState, int] = {
        HealthState.HEALTHY: pb_enums.HealthState.HEALTH_STATE_HEALTHY,
        HealthState.DEGRADED: pb_enums.HealthState.HEALTH_STATE_DEGRADED,
        HealthState.UNRELIABLE: pb_enums.HealthState.HEALTH_STATE_UNRELIABLE,
        HealthState.UNAVAILABLE: pb_enums.HealthState.HEALTH_STATE_UNAVAILABLE,
    }
    return mapping[v]


def _connection_state_from_pb(v: int, context: str = "DataHealthSnapshot.connection_state") -> ConnectionState | None:
    mapping: dict[int, ConnectionState] = {
        pb_enums.ConnectionState.CONNECTION_STATE_CONNECTING: ConnectionState.CONNECTING,
        pb_enums.ConnectionState.CONNECTION_STATE_CONNECTED: ConnectionState.CONNECTED,
        pb_enums.ConnectionState.CONNECTION_STATE_RECONNECTING: ConnectionState.RECONNECTING,
        pb_enums.ConnectionState.CONNECTION_STATE_DISCONNECTED: ConnectionState.DISCONNECTED,
        pb_enums.ConnectionState.CONNECTION_STATE_FAILED: ConnectionState.FAILED,
    }
    return _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="ConnectionState",
        context=context,
        unspecified_value=pb_enums.ConnectionState.CONNECTION_STATE_UNSPECIFIED,
        allow_unspecified_none=True,
    )


def _connection_state_to_pb(v: ConnectionState | None) -> Any:
    if v is None:
        return 0
    mapping: dict[ConnectionState, int] = {
        ConnectionState.CONNECTING: pb_enums.ConnectionState.CONNECTION_STATE_CONNECTING,
        ConnectionState.CONNECTED: pb_enums.ConnectionState.CONNECTION_STATE_CONNECTED,
        ConnectionState.RECONNECTING: pb_enums.ConnectionState.CONNECTION_STATE_RECONNECTING,
        ConnectionState.DISCONNECTED: pb_enums.ConnectionState.CONNECTION_STATE_DISCONNECTED,
        ConnectionState.FAILED: pb_enums.ConnectionState.CONNECTION_STATE_FAILED,
    }
    return mapping[v]


def _latency_summary_from_pb(ls: pb_snap.LatencySummary) -> LatencySummary:
    return LatencySummary(
        count=ls.count,
        min_ms=ls.min_ms if ls.HasField("min_ms") else None,
        max_ms=ls.max_ms if ls.HasField("max_ms") else None,
        p50_ms=ls.p50_ms if ls.HasField("p50_ms") else None,
        p95_ms=ls.p95_ms if ls.HasField("p95_ms") else None,
        p99_ms=ls.p99_ms if ls.HasField("p99_ms") else None,
        window_start_utc_ns=ls.window_start_utc_ns,
        window_end_utc_ns=ls.window_end_utc_ns,
    )


def _latency_summary_to_pb(ls: LatencySummary) -> pb_snap.LatencySummary:
    pb = pb_snap.LatencySummary()
    pb.count = ls.count
    if ls.min_ms is not None:
        pb.min_ms = ls.min_ms
    if ls.max_ms is not None:
        pb.max_ms = ls.max_ms
    if ls.p50_ms is not None:
        pb.p50_ms = ls.p50_ms
    if ls.p95_ms is not None:
        pb.p95_ms = ls.p95_ms
    if ls.p99_ms is not None:
        pb.p99_ms = ls.p99_ms
    pb.window_start_utc_ns = ls.window_start_utc_ns
    pb.window_end_utc_ns = ls.window_end_utc_ns
    return pb


def data_health_snapshot_from_pb(dhs: pb_snap.DataHealthSnapshot) -> DataHealthSnapshot:
    if dhs.schema_version != "data-health-snapshot.v1":
        raise UnsupportedSchemaVersionError("data-health-snapshot.v1", dhs.schema_version)
    return DataHealthSnapshot(
        health_snapshot_id=SnapshotId(dhs.health_snapshot_id),
        overall_state=_health_state_from_pb(dhs.overall_state, "DataHealthSnapshot.overall_state"),
        venue=_venue_from_pb(dhs.venue, "DataHealthSnapshot.venue"),
        market=_market_from_pb(dhs.market, "DataHealthSnapshot.market"),
        symbol=Symbol(dhs.symbol),
        schema_version="data-health-snapshot.v1",
        producer=dhs.producer,
        producer_version=dhs.producer_version,
        source_instance_id=InstanceId(dhs.source_instance_id),
        stream=_stream_from_pb(dhs.stream, "DataHealthSnapshot.stream") if dhs.HasField("stream") else None,
        connection_state=_connection_state_from_pb(dhs.connection_state, "DataHealthSnapshot.connection_state")
        if dhs.HasField("connection_state")
        else None,
        last_message_age_ms=_optional_uint64(dhs.last_message_age_ms) if dhs.HasField("last_message_age_ms") else None,
        receive_latency=_latency_summary_from_pb(dhs.receive_latency) if dhs.HasField("receive_latency") else None,
        publish_latency=_latency_summary_from_pb(dhs.publish_latency) if dhs.HasField("publish_latency") else None,
        consumer_delivery_latency=_latency_summary_from_pb(dhs.consumer_delivery_latency)
        if dhs.HasField("consumer_delivery_latency")
        else None,
        sequence_gap_count=dhs.sequence_gap_count,
        resync_state=_resync_state_from_pb(dhs.resync_state, "DataHealthSnapshot.resync_state")
        if dhs.HasField("resync_state")
        else None,
        book_synchronized=dhs.book_synchronized if dhs.HasField("book_synchronized") else None,
        recorder_alive=dhs.recorder_alive if dhs.HasField("recorder_alive") else None,
        gateway_alive=dhs.gateway_alive if dhs.HasField("gateway_alive") else None,
        reason_codes=tuple(
            r
            for rc in dhs.reason_codes
            if (r := _reason_code_from_pb(rc, "DataHealthSnapshot.reason_codes")) is not None
        ),
        observed_time_utc_ns=dhs.observed_time_utc_ns,
        quality_flags=_quality_from_pb(list(dhs.quality_flags), "DataHealthSnapshot.quality_flags"),
    )


def data_health_snapshot_to_pb(dhs: DataHealthSnapshot) -> pb_snap.DataHealthSnapshot:
    pb = pb_snap.DataHealthSnapshot()
    pb.health_snapshot_id = dhs.health_snapshot_id
    pb.overall_state = _health_state_to_pb(dhs.overall_state)
    pb.venue = _venue_to_pb(dhs.venue)
    pb.market = _market_to_pb(dhs.market)
    pb.symbol = dhs.symbol
    pb.schema_version = dhs.schema_version
    pb.producer = dhs.producer
    pb.producer_version = dhs.producer_version
    pb.source_instance_id = dhs.source_instance_id
    if dhs.stream is not None:
        pb.stream = _stream_to_pb(dhs.stream)
    if dhs.connection_state is not None:
        pb.connection_state = _connection_state_to_pb(dhs.connection_state)
    if dhs.last_message_age_ms is not None:
        pb.last_message_age_ms = dhs.last_message_age_ms
    if dhs.receive_latency is not None:
        pb.receive_latency.CopyFrom(_latency_summary_to_pb(dhs.receive_latency))
    if dhs.publish_latency is not None:
        pb.publish_latency.CopyFrom(_latency_summary_to_pb(dhs.publish_latency))
    if dhs.consumer_delivery_latency is not None:
        pb.consumer_delivery_latency.CopyFrom(_latency_summary_to_pb(dhs.consumer_delivery_latency))
    pb.sequence_gap_count = dhs.sequence_gap_count
    if dhs.resync_state is not None:
        pb.resync_state = _resync_state_to_pb(dhs.resync_state)
    if dhs.book_synchronized is not None:
        pb.book_synchronized = dhs.book_synchronized
    if dhs.recorder_alive is not None:
        pb.recorder_alive = dhs.recorder_alive
    if dhs.gateway_alive is not None:
        pb.gateway_alive = dhs.gateway_alive
    pb.reason_codes.extend(_reason_code_to_pb(r) for r in dhs.reason_codes)
    pb.observed_time_utc_ns = dhs.observed_time_utc_ns
    pb.quality_flags.extend(_quality_to_pb(dhs.quality_flags))
    return pb


# ---------------------------------------------------------------------------
# Gateway: StreamSelector adapters
# ---------------------------------------------------------------------------


def stream_selector_from_pb(ss: pb_id.StreamSelector) -> StreamSelector:
    return StreamSelector(
        venue=_venue_from_pb(ss.venue, "StreamSelector.venue"),
        market=_market_from_pb(ss.market, "StreamSelector.market"),
        symbol=Symbol(ss.symbol),
        stream=_stream_from_pb(ss.stream, "StreamSelector.stream"),
    )


def stream_selector_to_pb(ss: StreamSelector) -> pb_id.StreamSelector:
    pb = pb_id.StreamSelector()
    pb.venue = _venue_to_pb(ss.venue)
    pb.market = _market_to_pb(ss.market)
    pb.symbol = ss.symbol
    pb.stream = _stream_to_pb(ss.stream)
    return pb


# ---------------------------------------------------------------------------
# Gateway: EnvelopeMetadata adapters
# ---------------------------------------------------------------------------


def envelope_metadata_from_pb(em: pb_meta.EnvelopeMetadata) -> EnvelopeMetadata:
    _require_exact_string(
        contract="EnvelopeMetadata", field="protocol_version", actual=em.protocol_version, expected="gateway-stream.v1"
    )
    return EnvelopeMetadata(
        protocol_version="gateway-stream.v1",
        gateway_instance_id=GatewayInstanceId(em.gateway_instance_id),
        subscription_id=SubscriptionId(em.subscription_id),
        connection_generation=em.connection_generation,
        session_sequence=em.session_sequence,
        publish_time_utc_ns=em.publish_time_utc_ns,
        publish_monotonic_ns=_optional_uint64(em.publish_monotonic_ns) if em.HasField("publish_monotonic_ns") else None,
    )


def envelope_metadata_to_pb(em: EnvelopeMetadata) -> pb_meta.EnvelopeMetadata:
    pb = pb_meta.EnvelopeMetadata()
    pb.protocol_version = em.protocol_version
    pb.gateway_instance_id = em.gateway_instance_id
    pb.subscription_id = em.subscription_id
    pb.connection_generation = em.connection_generation
    pb.session_sequence = em.session_sequence
    pb.publish_time_utc_ns = em.publish_time_utc_ns
    if em.publish_monotonic_ns is not None:
        pb.publish_monotonic_ns = em.publish_monotonic_ns
    return pb


def gateway_envelope_metadata_from_pb(em: pb_gw.GatewayEnvelopeMetadata) -> GatewayEnvelopeMetadata:
    _require_exact_string(
        contract="GatewayEnvelopeMetadata",
        field="protocol_version",
        actual=em.protocol_version,
        expected="gateway-stream.v1",
    )
    return GatewayEnvelopeMetadata(
        protocol_version="gateway-stream.v1",
        gateway_instance_id=GatewayInstanceId(em.gateway_instance_id),
        subscription_id=SubscriptionId(em.subscription_id),
        connection_generation=_optional_uint64(em.connection_generation)
        if em.HasField("connection_generation")
        else None,
        session_sequence=em.session_sequence,
        publish_time_utc_ns=em.publish_time_utc_ns,
        publish_monotonic_ns=_optional_uint64(em.publish_monotonic_ns) if em.HasField("publish_monotonic_ns") else None,
    )


def gateway_envelope_metadata_to_pb(em: GatewayEnvelopeMetadata) -> pb_gw.GatewayEnvelopeMetadata:
    pb = pb_gw.GatewayEnvelopeMetadata()
    pb.protocol_version = em.protocol_version
    pb.gateway_instance_id = em.gateway_instance_id
    pb.subscription_id = em.subscription_id
    if em.connection_generation is not None:
        pb.connection_generation = em.connection_generation
    pb.session_sequence = em.session_sequence
    pb.publish_time_utc_ns = em.publish_time_utc_ns
    if em.publish_monotonic_ns is not None:
        pb.publish_monotonic_ns = em.publish_monotonic_ns
    return pb


def _gateway_delivery_metadata_from_pb(item: Any, contract: str) -> GatewayEnvelopeMetadata:
    has_legacy = item.HasField("envelope_metadata")
    has_delivery = item.HasField("delivery_metadata")
    if has_legacy and has_delivery:
        raise WireError(f"{contract}: legacy envelope_metadata and delivery_metadata are both present")
    if has_legacy:
        raise WireError(f"{contract}: legacy envelope_metadata is not accepted")
    if not has_delivery:
        raise MissingWireFieldError(contract, "delivery_metadata")
    return gateway_envelope_metadata_from_pb(item.delivery_metadata)


# ---------------------------------------------------------------------------
# Gateway: SubscriptionAccepted adapters
# ---------------------------------------------------------------------------


def subscription_accepted_from_pb(sa: pb_gw.SubscriptionAccepted) -> SubscriptionAccepted:
    _require_exact_string(
        contract="SubscriptionAccepted",
        field="schema_version",
        actual=sa.schema_version,
        expected="subscription-accepted.v1",
    )
    return SubscriptionAccepted(
        request_id=RequestId(sa.request_id),
        subscription_id=SubscriptionId(sa.subscription_id),
        schema_version="subscription-accepted.v1",
        gateway_instance_id=GatewayInstanceId(sa.gateway_instance_id),
        accepted_time_utc_ns=sa.accepted_time_utc_ns,
        negotiated_payload_schema_versions=tuple(sa.negotiated_payload_schema_versions),
    )


def subscription_accepted_to_pb(sa: SubscriptionAccepted) -> pb_gw.SubscriptionAccepted:
    pb = pb_gw.SubscriptionAccepted()
    pb.request_id = sa.request_id
    pb.subscription_id = sa.subscription_id
    pb.schema_version = sa.schema_version
    pb.gateway_instance_id = sa.gateway_instance_id
    pb.accepted_time_utc_ns = sa.accepted_time_utc_ns
    pb.negotiated_payload_schema_versions.extend(sa.negotiated_payload_schema_versions)
    return pb


# ---------------------------------------------------------------------------
# Gateway: ConsumerGapNotice adapters
# ---------------------------------------------------------------------------


def _consumer_gap_reason_from_pb(v: int, context: str = "ConsumerGapNotice.reason") -> ConsumerGapReason:
    mapping: dict[int, ConsumerGapReason] = {
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SLOW_CONSUMER: ConsumerGapReason.SLOW_CONSUMER,
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_RESUME_NOT_AVAILABLE: ConsumerGapReason.RESUME_NOT_AVAILABLE,
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_UPSTREAM_SEQUENCE_GAP: ConsumerGapReason.UPSTREAM_SEQUENCE_GAP,
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_GATEWAY_RESTART: ConsumerGapReason.GATEWAY_RESTART,
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_CONNECTION_GENERATION_CHANGED: ConsumerGapReason.CONNECTION_GENERATION_CHANGED,  # noqa: E501
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SUBSCRIPTION_RECONFIGURED: ConsumerGapReason.SUBSCRIPTION_RECONFIGURED,  # noqa: E501
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="ConsumerGapReason",
        context=context,
        unspecified_value=pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_UNSPECIFIED,
    )
    assert result is not None
    return result


def _consumer_gap_reason_to_pb(v: ConsumerGapReason) -> Any:
    mapping: dict[ConsumerGapReason, int] = {
        ConsumerGapReason.SLOW_CONSUMER: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SLOW_CONSUMER,
        ConsumerGapReason.RESUME_NOT_AVAILABLE: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_RESUME_NOT_AVAILABLE,
        ConsumerGapReason.UPSTREAM_SEQUENCE_GAP: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_UPSTREAM_SEQUENCE_GAP,
        ConsumerGapReason.GATEWAY_RESTART: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_GATEWAY_RESTART,
        ConsumerGapReason.CONNECTION_GENERATION_CHANGED: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_CONNECTION_GENERATION_CHANGED,  # noqa: E501
        ConsumerGapReason.SUBSCRIPTION_RECONFIGURED: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SUBSCRIPTION_RECONFIGURED,  # noqa: E501
    }
    return mapping[v]


def _recovery_action_from_pb(v: int, context: str = "ConsumerGapNotice.recovery_action") -> RecoveryAction:
    mapping: dict[int, RecoveryAction] = {
        pb_enums.RecoveryAction.RECOVERY_ACTION_NONE: RecoveryAction.NONE,
        pb_enums.RecoveryAction.RECOVERY_ACTION_RESUBSCRIBE: RecoveryAction.RESUBSCRIBE,
        pb_enums.RecoveryAction.RECOVERY_ACTION_REQUEST_NEW_SNAPSHOT: RecoveryAction.REQUEST_NEW_SNAPSHOT,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="RecoveryAction",
        context=context,
        unspecified_value=pb_enums.RecoveryAction.RECOVERY_ACTION_UNSPECIFIED,
    )
    assert result is not None
    return result


def _recovery_action_to_pb(v: RecoveryAction) -> Any:
    mapping: dict[RecoveryAction, int] = {
        RecoveryAction.NONE: pb_enums.RecoveryAction.RECOVERY_ACTION_NONE,
        RecoveryAction.RESUBSCRIBE: pb_enums.RecoveryAction.RECOVERY_ACTION_RESUBSCRIBE,
        RecoveryAction.REQUEST_NEW_SNAPSHOT: pb_enums.RecoveryAction.RECOVERY_ACTION_REQUEST_NEW_SNAPSHOT,
    }
    return mapping[v]


def consumer_gap_notice_from_pb(cgn: pb_gw.ConsumerGapNotice) -> ConsumerGapNotice:
    _require_exact_string(
        contract="ConsumerGapNotice",
        field="schema_version",
        actual=cgn.schema_version,
        expected="consumer-gap-notice.v1",
    )
    return ConsumerGapNotice(
        schema_version="consumer-gap-notice.v1",
        subscription_id=SubscriptionId(cgn.subscription_id),
        detected_time_utc_ns=cgn.detected_time_utc_ns,
        last_delivered_session_sequence=_optional_uint64(cgn.last_delivered_session_sequence)
        if cgn.HasField("last_delivered_session_sequence")
        else None,
        next_available_session_sequence=_optional_uint64(cgn.next_available_session_sequence)
        if cgn.HasField("next_available_session_sequence")
        else None,
        reason=_consumer_gap_reason_from_pb(cgn.reason),
        recovery_action=_recovery_action_from_pb(cgn.recovery_action),
        market=_market_from_pb(cgn.market, "ConsumerGapNotice.market") if cgn.HasField("market") else None,
        symbol=Symbol(cgn.symbol) if cgn.HasField("symbol") and cgn.symbol else None,
        stream=_stream_from_pb(cgn.stream, "ConsumerGapNotice.stream") if cgn.HasField("stream") else None,
    )


def consumer_gap_notice_to_pb(cgn: ConsumerGapNotice) -> pb_gw.ConsumerGapNotice:
    pb = pb_gw.ConsumerGapNotice()
    pb.schema_version = cgn.schema_version
    pb.subscription_id = cgn.subscription_id
    pb.detected_time_utc_ns = cgn.detected_time_utc_ns
    if cgn.last_delivered_session_sequence is not None:
        pb.last_delivered_session_sequence = cgn.last_delivered_session_sequence
    if cgn.next_available_session_sequence is not None:
        pb.next_available_session_sequence = cgn.next_available_session_sequence
    pb.reason = _consumer_gap_reason_to_pb(cgn.reason)
    pb.recovery_action = _recovery_action_to_pb(cgn.recovery_action)
    if cgn.market is not None:
        pb.market = _market_to_pb(cgn.market)
    if cgn.symbol is not None:
        pb.symbol = cgn.symbol
    if cgn.stream is not None:
        pb.stream = _stream_to_pb(cgn.stream)
    return pb


# ---------------------------------------------------------------------------
# Gateway: StreamStatus adapters
# ---------------------------------------------------------------------------


def _stream_lifecycle_state_from_pb(v: int, context: str = "StreamStatus.state") -> StreamLifecycleState:
    mapping: dict[int, StreamLifecycleState] = {
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_ACCEPTED: StreamLifecycleState.ACCEPTED,
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_SNAPSHOT_PENDING: StreamLifecycleState.SNAPSHOT_PENDING,
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_LIVE: StreamLifecycleState.LIVE,
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_RESYNC_IN_PROGRESS: StreamLifecycleState.RESYNC_IN_PROGRESS,  # noqa: E501
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_DEGRADED: StreamLifecycleState.DEGRADED,
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_CLOSING: StreamLifecycleState.CLOSING,
        pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_CLOSED: StreamLifecycleState.CLOSED,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="StreamLifecycleState",
        context=context,
        unspecified_value=pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _stream_lifecycle_state_to_pb(v: StreamLifecycleState) -> Any:
    mapping: dict[StreamLifecycleState, int] = {
        StreamLifecycleState.ACCEPTED: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_ACCEPTED,
        StreamLifecycleState.SNAPSHOT_PENDING: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_SNAPSHOT_PENDING,
        StreamLifecycleState.LIVE: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_LIVE,
        StreamLifecycleState.RESYNC_IN_PROGRESS: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_RESYNC_IN_PROGRESS,  # noqa: E501
        StreamLifecycleState.DEGRADED: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_DEGRADED,
        StreamLifecycleState.CLOSING: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_CLOSING,
        StreamLifecycleState.CLOSED: pb_enums.StreamLifecycleState.STREAM_LIFECYCLE_STATE_CLOSED,
    }
    return mapping[v]


def stream_status_from_pb(ss: pb_gw.StreamStatus) -> StreamStatus:
    _require_exact_string(
        contract="StreamStatus", field="schema_version", actual=ss.schema_version, expected="stream-status.v1"
    )
    return StreamStatus(
        schema_version="stream-status.v1",
        subscription_id=SubscriptionId(ss.subscription_id),
        state=_stream_lifecycle_state_from_pb(ss.state),
        observed_time_utc_ns=ss.observed_time_utc_ns,
        reason_code=_reason_code_from_pb(ss.reason_code, "StreamStatus.reason_code")
        if ss.HasField("reason_code")
        else None,
        message=ss.message if ss.HasField("message") and ss.message else None,
    )


def stream_status_to_pb(ss: StreamStatus) -> pb_gw.StreamStatus:
    pb = pb_gw.StreamStatus()
    pb.schema_version = ss.schema_version
    pb.subscription_id = ss.subscription_id
    pb.state = _stream_lifecycle_state_to_pb(ss.state)
    pb.observed_time_utc_ns = ss.observed_time_utc_ns
    if ss.reason_code is not None:
        pb.reason_code = _reason_code_to_pb(ss.reason_code)
    if ss.message is not None:
        pb.message = ss.message
    return pb


# ---------------------------------------------------------------------------
# Gateway: Event Envelope adapters
# ---------------------------------------------------------------------------


def gateway_event_envelope_from_pb(env: pb_gw.GatewayEventEnvelope) -> GatewayEventEnvelope:
    kwargs: dict[str, Any] = {
        "delivery_metadata": _gateway_delivery_metadata_from_pb(env, "GatewayEventEnvelope"),
    }
    which = env.WhichOneof("payload")
    if which == "subscription_accepted":
        kwargs["subscription_accepted"] = subscription_accepted_from_pb(env.subscription_accepted)
    elif which == "depth_update":
        kwargs["depth_update"] = depth_update_from_pb(env.depth_update)
    elif which == "agg_trade":
        kwargs["agg_trade"] = agg_trade_from_pb(env.agg_trade)
    elif which == "book_ticker":
        kwargs["book_ticker"] = book_ticker_from_pb(env.book_ticker)
    elif which == "consumer_gap":
        kwargs["consumer_gap"] = consumer_gap_notice_from_pb(env.consumer_gap)
    elif which == "stream_status":
        kwargs["stream_status"] = stream_status_from_pb(env.stream_status)
    else:
        raise WireError("GatewayEventEnvelope has no payload set")
    return GatewayEventEnvelope(**kwargs)


def gateway_event_envelope_to_pb(env: GatewayEventEnvelope) -> pb_gw.GatewayEventEnvelope:
    pb = pb_gw.GatewayEventEnvelope()
    pb.delivery_metadata.CopyFrom(gateway_envelope_metadata_to_pb(env.delivery_metadata))
    if env.subscription_accepted is not None:
        pb.subscription_accepted.CopyFrom(subscription_accepted_to_pb(env.subscription_accepted))
    elif env.depth_update is not None:
        pb.depth_update.CopyFrom(depth_update_to_pb(env.depth_update))
    elif env.agg_trade is not None:
        pb.agg_trade.CopyFrom(agg_trade_to_pb(env.agg_trade))
    elif env.book_ticker is not None:
        pb.book_ticker.CopyFrom(book_ticker_to_pb(env.book_ticker))
    elif env.consumer_gap is not None:
        pb.consumer_gap.CopyFrom(consumer_gap_notice_to_pb(env.consumer_gap))
    elif env.stream_status is not None:
        pb.stream_status.CopyFrom(stream_status_to_pb(env.stream_status))
    return pb


# ---------------------------------------------------------------------------
# Gateway: OrderBookStreamItem adapters
# ---------------------------------------------------------------------------


def order_book_stream_item_from_pb(item: pb_gw.OrderBookStreamItem) -> OrderBookStreamItem:
    kwargs: dict[str, Any] = {
        "delivery_metadata": _gateway_delivery_metadata_from_pb(item, "OrderBookStreamItem"),
    }
    which = item.WhichOneof("payload")
    if which == "subscription_accepted":
        kwargs["subscription_accepted"] = subscription_accepted_from_pb(item.subscription_accepted)
    elif which == "snapshot":
        kwargs["snapshot"] = local_order_book_snapshot_from_pb(item.snapshot)
    elif which == "depth_update":
        kwargs["depth_update"] = depth_update_from_pb(item.depth_update)
    elif which == "consumer_gap":
        kwargs["consumer_gap"] = consumer_gap_notice_from_pb(item.consumer_gap)
    elif which == "stream_status":
        kwargs["stream_status"] = stream_status_from_pb(item.stream_status)
    else:
        raise WireError("OrderBookStreamItem has no payload set")
    return OrderBookStreamItem(**kwargs)


def order_book_stream_item_to_pb(item: OrderBookStreamItem) -> pb_gw.OrderBookStreamItem:
    pb = pb_gw.OrderBookStreamItem()
    pb.delivery_metadata.CopyFrom(gateway_envelope_metadata_to_pb(item.delivery_metadata))
    if item.subscription_accepted is not None:
        pb.subscription_accepted.CopyFrom(subscription_accepted_to_pb(item.subscription_accepted))
    elif item.snapshot is not None:
        pb.snapshot.CopyFrom(local_order_book_snapshot_to_pb(item.snapshot))
    elif item.depth_update is not None:
        pb.depth_update.CopyFrom(depth_update_to_pb(item.depth_update))
    elif item.consumer_gap is not None:
        pb.consumer_gap.CopyFrom(consumer_gap_notice_to_pb(item.consumer_gap))
    elif item.stream_status is not None:
        pb.stream_status.CopyFrom(stream_status_to_pb(item.stream_status))
    return pb


# ---------------------------------------------------------------------------
# Gateway: MarketStateStreamItem adapters
# ---------------------------------------------------------------------------


def market_state_stream_item_from_pb(item: pb_gw.MarketStateStreamItem) -> MarketStateStreamItem:
    kwargs: dict[str, Any] = {
        "delivery_metadata": _gateway_delivery_metadata_from_pb(item, "MarketStateStreamItem"),
    }
    which = item.WhichOneof("payload")
    if which == "subscription_accepted":
        kwargs["subscription_accepted"] = subscription_accepted_from_pb(item.subscription_accepted)
    elif which == "market_state":
        kwargs["market_state"] = market_state_snapshot_from_pb(item.market_state)
    elif which == "consumer_gap":
        kwargs["consumer_gap"] = consumer_gap_notice_from_pb(item.consumer_gap)
    elif which == "stream_status":
        kwargs["stream_status"] = stream_status_from_pb(item.stream_status)
    else:
        raise WireError("MarketStateStreamItem has no payload set")
    return MarketStateStreamItem(**kwargs)


def market_state_stream_item_to_pb(item: MarketStateStreamItem) -> pb_gw.MarketStateStreamItem:
    pb = pb_gw.MarketStateStreamItem()
    pb.delivery_metadata.CopyFrom(gateway_envelope_metadata_to_pb(item.delivery_metadata))
    if item.subscription_accepted is not None:
        pb.subscription_accepted.CopyFrom(subscription_accepted_to_pb(item.subscription_accepted))
    elif item.market_state is not None:
        pb.market_state.CopyFrom(market_state_snapshot_to_pb(item.market_state))
    elif item.consumer_gap is not None:
        pb.consumer_gap.CopyFrom(consumer_gap_notice_to_pb(item.consumer_gap))
    elif item.stream_status is not None:
        pb.stream_status.CopyFrom(stream_status_to_pb(item.stream_status))
    return pb


# ---------------------------------------------------------------------------
# Gateway: GatewayStatusSnapshot adapters
# ---------------------------------------------------------------------------


def gateway_status_snapshot_from_pb(gs: pb_gw.GatewayStatusSnapshot) -> GatewayStatusSnapshot:
    _require_exact_string(
        contract="GatewayStatusSnapshot",
        field="schema_version",
        actual=gs.schema_version,
        expected="gateway-status-snapshot.v1",
    )
    return GatewayStatusSnapshot(
        schema_version="gateway-status-snapshot.v1",
        gateway_instance_id=GatewayInstanceId(gs.gateway_instance_id),
        observed_time_utc_ns=gs.observed_time_utc_ns,
        uptime_seconds=gs.uptime_seconds,
        markets=tuple(
            MarketRuntimeStatus(
                venue=_venue_from_pb(m.venue, "GatewayStatusSnapshot.markets.venue"),
                market=_market_from_pb(m.market, "GatewayStatusSnapshot.markets.market"),
                symbol=Symbol(m.symbol),
                state=_stream_lifecycle_state_from_pb(m.state, "GatewayStatusSnapshot.markets.state"),
                last_event_utc_ns=m.last_event_utc_ns if m.HasField("last_event_utc_ns") else None,
                connection_generation=m.connection_generation if m.HasField("connection_generation") else None,
                active_subscription_count=m.active_subscription_count,
            )
            for m in gs.markets
        ),
        total_active_subscriptions=gs.total_active_subscriptions,
    )


def gateway_status_snapshot_to_pb(gs: GatewayStatusSnapshot) -> pb_gw.GatewayStatusSnapshot:
    pb = pb_gw.GatewayStatusSnapshot()
    pb.schema_version = gs.schema_version
    pb.gateway_instance_id = gs.gateway_instance_id
    pb.observed_time_utc_ns = gs.observed_time_utc_ns
    pb.uptime_seconds = gs.uptime_seconds
    for m in gs.markets:
        mr = pb.markets.add()
        mr.venue = _venue_to_pb(m.venue)
        mr.market = _market_to_pb(m.market)
        mr.symbol = m.symbol
        mr.state = _stream_lifecycle_state_to_pb(m.state)
        if m.last_event_utc_ns is not None:
            mr.last_event_utc_ns = m.last_event_utc_ns
        if m.connection_generation is not None:
            mr.connection_generation = m.connection_generation
        mr.active_subscription_count = m.active_subscription_count
    pb.total_active_subscriptions = gs.total_active_subscriptions
    return pb


# ---------------------------------------------------------------------------
# EventSubscriptionRequest adapters
# ---------------------------------------------------------------------------


def _delivery_mode_from_pb(v: int, context: str = "SubscriptionRequest.delivery_mode") -> DeliveryMode:
    mapping: dict[int, DeliveryMode] = {
        pb_enums.DeliveryMode.DELIVERY_MODE_CONTIGUOUS_EVENTS: DeliveryMode.CONTIGUOUS_EVENTS,
        pb_enums.DeliveryMode.DELIVERY_MODE_LATEST_STATE: DeliveryMode.LATEST_STATE,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="DeliveryMode",
        context=context,
        unspecified_value=pb_enums.DeliveryMode.DELIVERY_MODE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _delivery_mode_to_pb(v: DeliveryMode) -> Any:
    mapping: dict[DeliveryMode, int] = {
        DeliveryMode.CONTIGUOUS_EVENTS: pb_enums.DeliveryMode.DELIVERY_MODE_CONTIGUOUS_EVENTS,
        DeliveryMode.LATEST_STATE: pb_enums.DeliveryMode.DELIVERY_MODE_LATEST_STATE,
    }
    return mapping[v]


def _initial_snapshot_mode_from_pb(
    v: int, context: str = "OrderBookSubscriptionRequest.initial_snapshot_mode"
) -> InitialSnapshotMode:
    mapping: dict[int, InitialSnapshotMode] = {
        pb_enums.InitialSnapshotMode.INITIAL_SNAPSHOT_MODE_NONE: InitialSnapshotMode.NONE,
        pb_enums.InitialSnapshotMode.INITIAL_SNAPSHOT_MODE_REQUIRED: InitialSnapshotMode.REQUIRED,
    }
    result = _mapped_enum_from_pb(
        value=v,
        mapping=mapping,
        enum_name="InitialSnapshotMode",
        context=context,
        unspecified_value=pb_enums.InitialSnapshotMode.INITIAL_SNAPSHOT_MODE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _initial_snapshot_mode_to_pb(v: InitialSnapshotMode) -> Any:
    mapping: dict[InitialSnapshotMode, int] = {
        InitialSnapshotMode.NONE: pb_enums.InitialSnapshotMode.INITIAL_SNAPSHOT_MODE_NONE,
        InitialSnapshotMode.REQUIRED: pb_enums.InitialSnapshotMode.INITIAL_SNAPSHOT_MODE_REQUIRED,
    }
    return mapping[v]


def event_subscription_request_from_pb(req: pb_gw.EventSubscriptionRequest) -> EventSubscriptionRequest:
    _require_exact_string(
        contract="EventSubscriptionRequest",
        field="schema_version",
        actual=req.schema_version,
        expected="event-subscription-request.v1",
    )
    delivery_mode = _delivery_mode_from_pb(req.delivery_mode, "EventSubscriptionRequest.delivery_mode")
    if delivery_mode != DeliveryMode.CONTIGUOUS_EVENTS:
        raise UnexpectedWireValueError(
            "EventSubscriptionRequest", "delivery_mode", "CONTIGUOUS_EVENTS", delivery_mode.value
        )
    return EventSubscriptionRequest(
        request_id=RequestId(req.request_id),
        schema_version="event-subscription-request.v1",
        selectors=tuple(stream_selector_from_pb(s) for s in req.selectors),
        delivery_mode=delivery_mode,
        supported_payload_schema_versions=tuple(req.supported_payload_schema_versions),
    )


def event_subscription_request_to_pb(req: EventSubscriptionRequest) -> pb_gw.EventSubscriptionRequest:
    pb = pb_gw.EventSubscriptionRequest()
    pb.request_id = req.request_id
    pb.schema_version = req.schema_version
    pb.selectors.extend(stream_selector_to_pb(s) for s in req.selectors)
    pb.delivery_mode = _delivery_mode_to_pb(req.delivery_mode)
    pb.supported_payload_schema_versions.extend(req.supported_payload_schema_versions)
    return pb


def order_book_subscription_request_from_pb(req: pb_gw.OrderBookSubscriptionRequest) -> OrderBookSubscriptionRequest:
    _require_exact_string(
        contract="OrderBookSubscriptionRequest",
        field="schema_version",
        actual=req.schema_version,
        expected="order-book-subscription-request.v1",
    )
    initial_snapshot_mode = _initial_snapshot_mode_from_pb(
        req.initial_snapshot_mode, "OrderBookSubscriptionRequest.initial_snapshot_mode"
    )
    if initial_snapshot_mode != InitialSnapshotMode.REQUIRED:
        raise UnexpectedWireValueError(
            "OrderBookSubscriptionRequest", "initial_snapshot_mode", "REQUIRED", initial_snapshot_mode.value
        )
    return OrderBookSubscriptionRequest(
        request_id=RequestId(req.request_id),
        schema_version="order-book-subscription-request.v1",
        venue=_venue_from_pb(req.venue, "OrderBookSubscriptionRequest.venue"),
        market=_market_from_pb(req.market, "OrderBookSubscriptionRequest.market"),
        symbol=Symbol(req.symbol),
        depth_limit=req.depth_limit if req.HasField("depth_limit") else None,
        initial_snapshot_mode=initial_snapshot_mode,
        supported_snapshot_schema_versions=tuple(req.supported_snapshot_schema_versions),
        supported_update_schema_versions=tuple(req.supported_update_schema_versions),
    )


def order_book_subscription_request_to_pb(req: OrderBookSubscriptionRequest) -> pb_gw.OrderBookSubscriptionRequest:
    pb = pb_gw.OrderBookSubscriptionRequest()
    pb.request_id = req.request_id
    pb.schema_version = req.schema_version
    pb.venue = _venue_to_pb(req.venue)
    pb.market = _market_to_pb(req.market)
    pb.symbol = req.symbol
    if req.depth_limit is not None:
        pb.depth_limit = req.depth_limit
    pb.initial_snapshot_mode = _initial_snapshot_mode_to_pb(req.initial_snapshot_mode)
    pb.supported_snapshot_schema_versions.extend(req.supported_snapshot_schema_versions)
    pb.supported_update_schema_versions.extend(req.supported_update_schema_versions)
    return pb


def market_state_subscription_request_from_pb(
    req: pb_gw.MarketStateSubscriptionRequest,
) -> MarketStateSubscriptionRequest:
    _require_exact_string(
        contract="MarketStateSubscriptionRequest",
        field="schema_version",
        actual=req.schema_version,
        expected="market-state-subscription-request.v1",
    )
    delivery_mode = _delivery_mode_from_pb(req.delivery_mode, "MarketStateSubscriptionRequest.delivery_mode")
    if delivery_mode != DeliveryMode.LATEST_STATE:
        raise UnexpectedWireValueError(
            "MarketStateSubscriptionRequest", "delivery_mode", "LATEST_STATE", delivery_mode.value
        )
    return MarketStateSubscriptionRequest(
        request_id=RequestId(req.request_id),
        schema_version="market-state-subscription-request.v1",
        venue=_venue_from_pb(req.venue, "MarketStateSubscriptionRequest.venue"),
        market=_market_from_pb(req.market, "MarketStateSubscriptionRequest.market"),
        symbol=Symbol(req.symbol),
        delivery_mode=delivery_mode,
        depth_limit=req.depth_limit if req.HasField("depth_limit") else None,
        minimum_publish_interval_ms=_optional_uint64(req.minimum_publish_interval_ms)
        if req.HasField("minimum_publish_interval_ms")
        else None,
        supported_schema_versions=tuple(req.supported_schema_versions),
    )


def market_state_subscription_request_to_pb(
    req: MarketStateSubscriptionRequest,
) -> pb_gw.MarketStateSubscriptionRequest:
    pb = pb_gw.MarketStateSubscriptionRequest()
    pb.request_id = req.request_id
    pb.schema_version = req.schema_version
    pb.venue = _venue_to_pb(req.venue)
    pb.market = _market_to_pb(req.market)
    pb.symbol = req.symbol
    pb.delivery_mode = _delivery_mode_to_pb(req.delivery_mode)
    if req.depth_limit is not None:
        pb.depth_limit = req.depth_limit
    if req.minimum_publish_interval_ms is not None:
        pb.minimum_publish_interval_ms = req.minimum_publish_interval_ms
    pb.supported_schema_versions.extend(req.supported_schema_versions)
    return pb


def gateway_status_request_from_pb(req: pb_gw.GatewayStatusRequest) -> GatewayStatusRequest:
    _require_exact_string(
        contract="GatewayStatusRequest",
        field="schema_version",
        actual=req.schema_version,
        expected="gateway-status-request.v1",
    )
    return GatewayStatusRequest(
        request_id=RequestId(req.request_id),
        schema_version="gateway-status-request.v1",
    )


def gateway_status_request_to_pb(req: GatewayStatusRequest) -> pb_gw.GatewayStatusRequest:
    pb = pb_gw.GatewayStatusRequest()
    pb.request_id = req.request_id
    pb.schema_version = req.schema_version
    return pb


# ---------------------------------------------------------------------------
# Telemetry: enum mapping
# ---------------------------------------------------------------------------

_TELEMETRY_TYPE_PB_TO_PY: Mapping[int, TelemetryType] = {
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_CONNECTION: TelemetryType.CONNECTION,
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_SEQUENCE: TelemetryType.SEQUENCE,
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_LATENCY: TelemetryType.LATENCY,
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_QUEUE: TelemetryType.QUEUE,
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_BOOK: TelemetryType.BOOK,
    pb_telemetry.TelemetryType.TELEMETRY_TYPE_SYSTEM: TelemetryType.SYSTEM,
}

_TELEMETRY_TYPE_PY_TO_PB: Mapping[TelemetryType, int] = {v: k for k, v in _TELEMETRY_TYPE_PB_TO_PY.items()}


def _telemetry_type_from_pb(v: int, context: str = "TelemetryEnvelope.telemetry_type") -> TelemetryType:
    result = _mapped_enum_from_pb(
        value=v,
        mapping=_TELEMETRY_TYPE_PB_TO_PY,
        enum_name="TelemetryType",
        context=context,
        unspecified_value=pb_telemetry.TelemetryType.TELEMETRY_TYPE_UNSPECIFIED,
    )
    assert result is not None
    return result


def _telemetry_type_to_pb(v: TelemetryType) -> Any:
    return _TELEMETRY_TYPE_PY_TO_PB[v]


# Mapping from TelemetryType → oneof field name in TelemetryEnvelope
_TELEMETRY_TYPE_ONEOF: dict[TelemetryType, str] = {
    TelemetryType.CONNECTION: "connection",
    TelemetryType.SEQUENCE: "sequence",
    TelemetryType.LATENCY: "latency",
    TelemetryType.QUEUE: "queue",
    TelemetryType.BOOK: "book",
    TelemetryType.SYSTEM: "system",
}


# ---------------------------------------------------------------------------
# Telemetry: metrics adapters
# ---------------------------------------------------------------------------


def connection_metrics_to_pb(cm: ConnectionMetrics) -> pb_telemetry.ConnectionMetrics:
    pb = pb_telemetry.ConnectionMetrics()
    pb.connected = cm.connected
    if cm.last_message_age_ms is not None:
        pb.last_message_age_ms = cm.last_message_age_ms
    pb.reconnect_count = cm.reconnect_count
    return pb


def connection_metrics_from_pb(cm: pb_telemetry.ConnectionMetrics) -> ConnectionMetrics:
    return ConnectionMetrics(
        connected=cm.connected,
        last_message_age_ms=cm.last_message_age_ms if cm.HasField("last_message_age_ms") else None,
        reconnect_count=cm.reconnect_count,
    )


def sequence_metrics_to_pb(sm: SequenceMetrics) -> pb_telemetry.SequenceMetrics:
    pb = pb_telemetry.SequenceMetrics()
    if sm.last_update_id is not None:
        pb.last_update_id = sm.last_update_id
    pb.duplicate_count = sm.duplicate_count
    pb.out_of_order_count = sm.out_of_order_count
    return pb


def sequence_metrics_from_pb(sm: pb_telemetry.SequenceMetrics) -> SequenceMetrics:
    return SequenceMetrics(
        last_update_id=sm.last_update_id if sm.HasField("last_update_id") else None,
        duplicate_count=sm.duplicate_count,
        out_of_order_count=sm.out_of_order_count,
    )


def latency_metrics_to_pb(lm: LatencyMetrics) -> pb_telemetry.LatencyMetrics:
    pb = pb_telemetry.LatencyMetrics()
    if lm.receive_lag_ms is not None:
        pb.receive_lag_ms = lm.receive_lag_ms
    if lm.publish_lag_ms is not None:
        pb.publish_lag_ms = lm.publish_lag_ms
    if lm.consumer_delivery_lag_ms is not None:
        pb.consumer_delivery_lag_ms = lm.consumer_delivery_lag_ms
    return pb


def latency_metrics_from_pb(lm: pb_telemetry.LatencyMetrics) -> LatencyMetrics:
    return LatencyMetrics(
        receive_lag_ms=lm.receive_lag_ms if lm.HasField("receive_lag_ms") else None,
        publish_lag_ms=lm.publish_lag_ms if lm.HasField("publish_lag_ms") else None,
        consumer_delivery_lag_ms=lm.consumer_delivery_lag_ms if lm.HasField("consumer_delivery_lag_ms") else None,
    )


def queue_metrics_to_pb(qm: QueueMetrics) -> pb_telemetry.QueueMetrics:
    pb = pb_telemetry.QueueMetrics()
    pb.queue_depth = qm.queue_depth
    pb.queue_capacity = qm.queue_capacity
    if qm.queue_utilization is not None:
        pb.queue_utilization = qm.queue_utilization
    if qm.oldest_message_age_ms is not None:
        pb.oldest_message_age_ms = qm.oldest_message_age_ms
    pb.dropped = qm.dropped
    pb.disconnect_count = qm.disconnect_count
    return pb


def queue_metrics_from_pb(qm: pb_telemetry.QueueMetrics) -> QueueMetrics:
    return QueueMetrics(
        queue_depth=qm.queue_depth,
        queue_capacity=qm.queue_capacity,
        queue_utilization=qm.queue_utilization if qm.HasField("queue_utilization") else None,
        oldest_message_age_ms=qm.oldest_message_age_ms if qm.HasField("oldest_message_age_ms") else None,
        dropped=qm.dropped,
        disconnect_count=qm.disconnect_count,
    )


def book_metrics_to_pb(bm: BookMetrics) -> pb_telemetry.BookMetrics:
    pb = pb_telemetry.BookMetrics()
    pb.synchronized = bm.synchronized
    if bm.sync_latency_ms is not None:
        pb.sync_latency_ms = bm.sync_latency_ms
    return pb


def book_metrics_from_pb(bm: pb_telemetry.BookMetrics) -> BookMetrics:
    return BookMetrics(
        synchronized=bm.synchronized,
        sync_latency_ms=bm.sync_latency_ms if bm.HasField("sync_latency_ms") else None,
    )


def system_metrics_to_pb(sm: SystemMetrics) -> pb_telemetry.SystemMetrics:
    pb = pb_telemetry.SystemMetrics()
    if sm.cpu_percent is not None:
        pb.cpu_percent = sm.cpu_percent
    if sm.memory_mb is not None:
        pb.memory_mb = sm.memory_mb
    if sm.disk_free_gb is not None:
        pb.disk_free_gb = sm.disk_free_gb
    return pb


def system_metrics_from_pb(sm: pb_telemetry.SystemMetrics) -> SystemMetrics:
    return SystemMetrics(
        cpu_percent=sm.cpu_percent if sm.HasField("cpu_percent") else None,
        memory_mb=sm.memory_mb if sm.HasField("memory_mb") else None,
        disk_free_gb=sm.disk_free_gb if sm.HasField("disk_free_gb") else None,
    )


# ---------------------------------------------------------------------------
# Telemetry: envelope adapter
# ---------------------------------------------------------------------------


def telemetry_envelope_to_pb(env: TelemetryEnvelope) -> pb_telemetry.TelemetryEnvelope:
    pb = pb_telemetry.TelemetryEnvelope()
    pb.schema_version = env.schema_version
    pb.telemetry_type = _telemetry_type_to_pb(env.telemetry_type)
    pb.source_module = env.source_module
    pb.source_instance_id = env.source_instance_id
    pb.observed_time_utc_ns = env.observed_time_utc_ns
    if env.market is not None:
        pb.market = _market_to_pb(env.market)
    if env.symbol is not None:
        pb.symbol = env.symbol
    if env.metrics is not None:
        if isinstance(env.metrics, ConnectionMetrics):
            pb.connection.CopyFrom(connection_metrics_to_pb(env.metrics))
        elif isinstance(env.metrics, SequenceMetrics):
            pb.sequence.CopyFrom(sequence_metrics_to_pb(env.metrics))
        elif isinstance(env.metrics, LatencyMetrics):
            pb.latency.CopyFrom(latency_metrics_to_pb(env.metrics))
        elif isinstance(env.metrics, QueueMetrics):
            pb.queue.CopyFrom(queue_metrics_to_pb(env.metrics))
        elif isinstance(env.metrics, BookMetrics):
            pb.book.CopyFrom(book_metrics_to_pb(env.metrics))
        elif isinstance(env.metrics, SystemMetrics):
            pb.system.CopyFrom(system_metrics_to_pb(env.metrics))
    pb.quality_flags.extend(_quality_to_pb(env.quality_flags))
    if env.stream is not None:
        pb.stream = _stream_to_pb(env.stream)
    if env.connection_id is not None:
        pb.connection_id = env.connection_id
    if env.connection_generation is not None:
        pb.connection_generation = env.connection_generation
    if env.subscription_id is not None:
        pb.subscription_id = env.subscription_id
    return pb


def telemetry_envelope_from_pb(env: pb_telemetry.TelemetryEnvelope) -> TelemetryEnvelope:
    _require_exact_string(
        contract="TelemetryEnvelope", field="schema_version", actual=env.schema_version, expected="telemetry.v1"
    )
    telemetry_type = _telemetry_type_from_pb(env.telemetry_type)

    which = env.WhichOneof("metrics")
    if which is None:
        raise MissingWireFieldError("TelemetryEnvelope", "metrics")

    expected_oneof = _TELEMETRY_TYPE_ONEOF[telemetry_type]
    if which != expected_oneof:
        raise UnexpectedWireValueError("TelemetryEnvelope", "metrics oneof", expected_oneof, which)

    metrics: ConnectionMetrics | SequenceMetrics | LatencyMetrics | QueueMetrics | BookMetrics | SystemMetrics
    if which == "connection":
        metrics = connection_metrics_from_pb(env.connection)
    elif which == "sequence":
        metrics = sequence_metrics_from_pb(env.sequence)
    elif which == "latency":
        metrics = latency_metrics_from_pb(env.latency)
    elif which == "queue":
        metrics = queue_metrics_from_pb(env.queue)
    elif which == "book":
        metrics = book_metrics_from_pb(env.book)
    elif which == "system":
        metrics = system_metrics_from_pb(env.system)
    else:
        raise WireError(f"TelemetryEnvelope: unexpected oneof value '{which}'")

    return TelemetryEnvelope(
        schema_version="telemetry.v1",
        telemetry_type=telemetry_type,
        source_module=env.source_module,
        source_instance_id=InstanceId(env.source_instance_id),
        observed_time_utc_ns=env.observed_time_utc_ns,
        market=_market_from_pb(env.market, "TelemetryEnvelope.market") if env.HasField("market") else None,
        symbol=Symbol(env.symbol) if env.HasField("symbol") and env.symbol else None,
        metrics=metrics,
        quality_flags=_quality_from_pb(list(env.quality_flags), "TelemetryEnvelope.quality_flags"),
        stream=_stream_from_pb(env.stream, "TelemetryEnvelope.stream") if env.HasField("stream") else None,
        connection_id=ConnectionId(env.connection_id) if env.HasField("connection_id") and env.connection_id else None,
        connection_generation=env.connection_generation if env.HasField("connection_generation") else None,
        subscription_id=SubscriptionId(env.subscription_id)
        if env.HasField("subscription_id") and env.subscription_id
        else None,
    )
