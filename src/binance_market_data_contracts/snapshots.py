"""Snapshot contracts for BinanceMarketData.

All snapshot types use Literal schema_version (required, no default).
Bids are in descending price order, asks in ascending price order.
All collections use tuples for deep immutability.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import (
    ContractModel,
    NonEmptyText,
    PriceString,
    QuantityString,
    SignedDecimalString,
)
from binance_market_data_contracts.enums import (
    ConnectionState,
    HealthState,
    Market,
    QualityFlag,
    ReasonCode,
    ResyncState,
    SnapshotSource,
    Stream,
    Venue,
)
from binance_market_data_contracts.identifiers import InstanceId, RequestId, SnapshotId, Symbol
from binance_market_data_contracts.market_events import PriceLevel


class ExchangeDepthSnapshot(ContractModel):
    """REST depth snapshot from Binance."""

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: Literal["exchange-depth-snapshot.v1"]
    producer: NonEmptyText
    producer_version: NonEmptyText
    request_id: RequestId
    last_update_id: int = Field(..., ge=0)
    bids: tuple[PriceLevel, ...] = ()
    asks: tuple[PriceLevel, ...] = ()
    exchange_transaction_time_ms: int | None = Field(default=None, ge=0)
    receive_time_utc_ns: int | None = Field(default=None, ge=0)
    receive_monotonic_ns: int | None = Field(default=None, ge=0)
    quality_flags: tuple[QualityFlag, ...] = ()

    @model_validator(mode="after")
    def _validate_order(self) -> ExchangeDepthSnapshot:
        _validate_bids_descending(self.bids)
        _validate_asks_ascending(self.asks)
        return self


class GapDescriptor(ContractModel):
    """Structured description of a sequence gap."""

    stream: Stream
    detected_at_utc_ns: int = Field(..., ge=0)
    previous_sequence: int | None = Field(default=None, ge=0)
    next_sequence: int | None = Field(default=None, ge=0)
    reason_code: ReasonCode | None = None
    recovery_state: ResyncState | None = None


class LocalOrderBookSnapshot(ContractModel):
    """Locally reconstructed order book snapshot."""

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: Literal["local-order-book-snapshot.v1"]
    producer: NonEmptyText
    producer_version: NonEmptyText
    source: SnapshotSource
    last_update_id: int = Field(..., ge=0)
    bids: tuple[PriceLevel, ...] = ()
    asks: tuple[PriceLevel, ...] = ()
    depth_limit: int | None = Field(default=None, gt=0)
    generated_time_utc_ns: int = Field(..., ge=0)
    generated_monotonic_ns: int | None = Field(default=None, ge=0)
    synchronized: bool
    last_gap: GapDescriptor | None = None
    quality_flags: tuple[QualityFlag, ...] = ()

    @model_validator(mode="after")
    def _validate_order(self) -> LocalOrderBookSnapshot:
        _validate_bids_descending(self.bids)
        _validate_asks_ascending(self.asks)
        if self.depth_limit is not None:
            if len(self.bids) > self.depth_limit:
                raise ValueError(f"bids count ({len(self.bids)}) exceeds depth_limit ({self.depth_limit})")
            if len(self.asks) > self.depth_limit:
                raise ValueError(f"asks count ({len(self.asks)}) exceeds depth_limit ({self.depth_limit})")
        return self


class MarketStateSnapshot(ContractModel):
    """Strategy-independent market state projection."""

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: Literal["market-state-snapshot.v1"]
    producer: NonEmptyText
    producer_version: NonEmptyText
    best_bid_price: PriceString | None = None
    best_bid_quantity: QuantityString | None = None
    best_ask_price: PriceString | None = None
    best_ask_quantity: QuantityString | None = None
    mid_price: PriceString | None = None
    spread: QuantityString | None = None
    microprice: PriceString | None = None
    top_bids: tuple[PriceLevel, ...] = ()
    top_asks: tuple[PriceLevel, ...] = ()
    depth_limit: int | None = Field(default=None, gt=0)
    mark_price: PriceString | None = None
    index_price: PriceString | None = None
    funding_rate: SignedDecimalString | None = None
    next_funding_time_ms: int | None = Field(default=None, ge=0)
    open_interest: QuantityString | None = None
    generated_time_utc_ns: int = Field(..., ge=0)
    data_freshness_ms: int | None = Field(default=None, ge=0)
    book_synchronized: bool | None = None
    source_book_update_id: int | None = Field(default=None, ge=0)
    source_trade_id: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_order(self) -> MarketStateSnapshot:
        _validate_bids_descending(self.top_bids)
        _validate_asks_ascending(self.top_asks)
        if self.depth_limit is not None:
            if len(self.top_bids) > self.depth_limit:
                raise ValueError(f"top_bids count ({len(self.top_bids)}) exceeds depth_limit ({self.depth_limit})")
            if len(self.top_asks) > self.depth_limit:
                raise ValueError(f"top_asks count ({len(self.top_asks)}) exceeds depth_limit ({self.depth_limit})")
        return self


class LatencySummary(ContractModel):
    """Statistical summary of latency measurements.

    When count == 0, all percentile fields must be None.
    When count > 0, min, max, p50, p95, p99 must all be present.
    Must satisfy: min <= p50 <= p95 <= p99 <= max and window_start <= window_end.
    """

    count: int = Field(..., ge=0)
    min_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    max_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    p50_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    p95_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    p99_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    window_start_utc_ns: int = Field(..., ge=0)
    window_end_utc_ns: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _validate_latency_fields(self) -> LatencySummary:
        pct_fields = ["min_ms", "max_ms", "p50_ms", "p95_ms", "p99_ms"]
        if self.count > 0:
            missing = [f for f in pct_fields if getattr(self, f) is None]
            if missing:
                raise ValueError(f"When count > 0, these fields must not be None: {', '.join(missing)}")
        else:
            non_none = [f for f in pct_fields if getattr(self, f) is not None]
            if non_none:
                raise ValueError(f"When count == 0, these fields must be None: {', '.join(non_none)}")
        return self

    @model_validator(mode="after")
    def _validate_ordering(self) -> LatencySummary:
        if self.min_ms is not None and self.max_ms is not None and self.min_ms > self.max_ms:
            raise ValueError(f"min_ms ({self.min_ms}) must be <= max_ms ({self.max_ms})")
        values: list[float] = [
            v for v in [self.min_ms, self.p50_ms, self.p95_ms, self.p99_ms, self.max_ms] if v is not None
        ]
        for i in range(len(values) - 1):
            if values[i] > values[i + 1]:
                raise ValueError("Latency values must be non-decreasing: min <= p50 <= p95 <= p99 <= max")
        return self

    @model_validator(mode="after")
    def _validate_window(self) -> LatencySummary:
        if self.window_start_utc_ns > self.window_end_utc_ns:
            raise ValueError(
                f"window_start ({self.window_start_utc_ns}) must be <= window_end ({self.window_end_utc_ns})"
            )
        return self


class DataHealthSnapshot(ContractModel):
    """Data health assessment for a market data stream."""

    health_snapshot_id: SnapshotId
    overall_state: HealthState
    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: Literal["data-health-snapshot.v1"]
    producer: NonEmptyText
    producer_version: NonEmptyText
    source_instance_id: InstanceId
    stream: Stream | None = Field(default=None, description="Stream scope (None = market-level aggregate Health)")
    connection_state: ConnectionState | None = None
    last_message_age_ms: int | None = Field(default=None, ge=0)
    receive_latency: LatencySummary | None = None
    publish_latency: LatencySummary | None = None
    sequence_gap_count: int = Field(default=0, ge=0)
    resync_state: ResyncState | None = None
    book_synchronized: bool | None = None
    recorder_alive: bool | None = None
    gateway_alive: bool | None = None
    consumer_delivery_latency: LatencySummary | None = None
    reason_codes: tuple[ReasonCode, ...] = ()
    observed_time_utc_ns: int = Field(..., ge=0)
    quality_flags: tuple[QualityFlag, ...] = ()


def _validate_bids_descending(bids: tuple[PriceLevel, ...]) -> None:
    if len(bids) <= 1:
        return
    prev = None
    for level in bids:
        p = Decimal(level.price)
        if prev is not None and p >= prev:
            raise ValueError(f"bids must be in strictly descending price order: {level.price}")
        prev = p


def _validate_asks_ascending(asks: tuple[PriceLevel, ...]) -> None:
    if len(asks) <= 1:
        return
    prev = None
    for level in asks:
        p = Decimal(level.price)
        if prev is not None and p <= prev:
            raise ValueError(f"asks must be in strictly ascending price order: {level.price}")
        prev = p
