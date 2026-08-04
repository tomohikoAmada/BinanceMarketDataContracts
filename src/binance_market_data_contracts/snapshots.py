"""Snapshot contracts for BinanceMarketData.

Includes exchange snapshots, local order book state, market state,
gap descriptors, latency summaries, and data health snapshots.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from binance_market_data_contracts.common import ContractModel, NonNegativeDecimalString, PriceString, QuantityString
from binance_market_data_contracts.enums import (  # noqa: TC001
    HealthState,
    Market,
    QualityFlag,
    ReasonCode,
    Stream,
    Venue,
)
from binance_market_data_contracts.identifiers import RequestId, Symbol  # noqa: TC001
from binance_market_data_contracts.market_events import PriceLevel  # noqa: TC001


class ExchangeDepthSnapshot(ContractModel):
    """REST depth snapshot from Binance.

    A point-in-time limited-depth snapshot used for initialization,
    recovery, and validation. This is NOT a continuous full-depth stream.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: str = Field(..., description="Contract version (e.g. 'exchange-depth-snapshot.v1')")
    producer: str
    producer_version: str
    request_id: RequestId
    last_update_id: int = Field(..., ge=0, description="Last update ID at time of snapshot")
    bids: list[PriceLevel] = Field(default_factory=list, description="Snapshot bid levels")
    asks: list[PriceLevel] = Field(default_factory=list, description="Snapshot ask levels")
    exchange_transaction_time_ms: int | None = Field(
        default=None, ge=0, description="Exchange transaction time in milliseconds"
    )
    receive_time_utc_ns: int | None = Field(default=None, ge=0, description="UTC receive time in nanoseconds")
    receive_monotonic_ns: int | None = Field(default=None, ge=0, description="Monotonic receive time in nanoseconds")
    quality_flags: list[QualityFlag] = Field(default_factory=list, description="Quality flags for this snapshot")


class GapDescriptor(ContractModel):
    """Structured description of a sequence gap.

    Records what stream was affected, when the gap was detected,
    the gap boundaries, the reason, and the recovery state.
    """

    stream: Stream = Field(..., description="The stream in which the gap was detected")
    detected_at_utc_ns: int = Field(..., ge=0, description="UTC time when the gap was detected (ns)")
    previous_sequence: int | None = Field(default=None, ge=0, description="Last known sequence before the gap")
    next_sequence: int | None = Field(default=None, ge=0, description="First known sequence after the gap")
    reason_code: ReasonCode | None = Field(default=None, description="Reason for the gap")
    recovery_state: str | None = Field(
        default=None, description="Current recovery state (e.g. 'RESYNC_IN_PROGRESS', 'RECOVERED')"
    )


class LocalOrderBookSnapshot(ContractModel):
    """Locally reconstructed order book snapshot.

    Represents the state of a locally-reconstructed order book at a point in time,
    built from an ExchangeDepthSnapshot and subsequent DepthUpdate events.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: str = Field(..., description="Contract version (e.g. 'local-order-book-snapshot.v1')")
    producer: str
    producer_version: str
    source: str = Field(..., description="Source of the snapshot (e.g. 'gateway', 'replay')")
    last_update_id: int = Field(..., ge=0, description="Last applied update ID")
    bids: list[PriceLevel] = Field(default_factory=list, description="Current bid levels")
    asks: list[PriceLevel] = Field(default_factory=list, description="Current ask levels")
    depth_limit: int | None = Field(default=None, ge=0, description="Depth limit applied, if any")
    generated_time_utc_ns: int | None = Field(
        default=None, ge=0, description="UTC time when this snapshot was generated (ns)"
    )
    generated_monotonic_ns: int | None = Field(
        default=None, ge=0, description="Monotonic time when this snapshot was generated (ns)"
    )
    synchronized: bool = Field(..., description="Whether the order book is currently synchronized with the exchange")
    last_gap: GapDescriptor | None = Field(default=None, description="The most recent gap, if one exists")
    quality_flags: list[QualityFlag] = Field(
        default_factory=list, description="Quality flags for this order book state"
    )


class MarketStateSnapshot(ContractModel):
    """Strategy-independent market state projection.

    Contains derived market facts: best bid/ask, mid, spread, microprice,
    recent trades, top-N depth, mark/index, funding, OI.
    Does NOT contain predictions, alpha, or trading signals.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: str = Field(..., description="Contract version (e.g. 'market-state-snapshot.v1')")
    producer: str
    producer_version: str
    best_bid_price: PriceString | None = None
    best_bid_quantity: QuantityString | None = None
    best_ask_price: PriceString | None = None
    best_ask_quantity: QuantityString | None = None
    mid_price: PriceString | None = None
    spread: NonNegativeDecimalString | None = None
    microprice: PriceString | None = None
    top_n_depth: list[PriceLevel] = Field(default_factory=list, description="Top-N depth levels")
    mark_price: PriceString | None = None
    index_price: PriceString | None = None
    funding_rate: str | None = Field(default=None, description="Current funding rate as a string (e.g. '0.0001')")
    funding_time: int | None = Field(default=None, ge=0, description="Next funding time in milliseconds")
    open_interest: QuantityString | None = None
    generated_time_utc_ns: int | None = Field(
        default=None, ge=0, description="UTC time when this snapshot was generated (ns)"
    )
    data_freshness_ms: int | None = Field(default=None, ge=0, description="Age of the underlying data in milliseconds")
    book_synchronized: bool | None = Field(default=None, description="Whether the order book is synchronized")


class LatencySummary(ContractModel):
    """Statistical summary of latency measurements.

    When count == 0, all percentile fields must be None.
    When count > 0, min, max, p50, p95, p99 must all be present.
    """

    count: int = Field(..., ge=0, description="Number of measurements in the window")
    min_ms: float | None = Field(default=None, ge=0, description="Minimum latency in milliseconds")
    max_ms: float | None = Field(default=None, ge=0, description="Maximum latency in milliseconds")
    p50_ms: float | None = Field(default=None, ge=0, description="50th percentile latency in milliseconds")
    p95_ms: float | None = Field(default=None, ge=0, description="95th percentile latency in milliseconds")
    p99_ms: float | None = Field(default=None, ge=0, description="99th percentile latency in milliseconds")
    window_start_utc_ns: int = Field(..., ge=0, description="Window start UTC time in nanoseconds")
    window_end_utc_ns: int = Field(..., ge=0, description="Window end UTC time in nanoseconds")

    @model_validator(mode="after")
    def _validate_latency_fields(self) -> LatencySummary:
        if self.count > 0:
            missing = [f for f in ["min_ms", "max_ms", "p50_ms", "p95_ms", "p99_ms"] if getattr(self, f) is None]
            if missing:
                raise ValueError(f"When count > 0, these fields must not be None: {', '.join(missing)}")
            if self.min_ms is not None and self.max_ms is not None and self.min_ms > self.max_ms:
                raise ValueError(f"min_ms ({self.min_ms}) must be <= max_ms ({self.max_ms})")
        else:
            pct_fields = ["min_ms", "max_ms", "p50_ms", "p95_ms", "p99_ms"]
            non_none = [f for f in pct_fields if getattr(self, f) is not None]
            if non_none:
                raise ValueError(f"When count == 0, these fields must be None: {', '.join(non_none)}")
        return self

    @model_validator(mode="after")
    def _validate_ordering(self) -> LatencySummary:
        values = [self.min_ms, self.p50_ms, self.p95_ms, self.p99_ms, self.max_ms]
        values = [v for v in values if v is not None]
        for i in range(len(values) - 1):
            if values[i] > values[i + 1]:  # type: ignore[operator]
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
    """Data health assessment for a market data stream.

    Provides an overall health state with supporting metrics for
    connection, latency, sequence, and synchronization health.
    """

    overall_state: HealthState
    venue: Venue
    market: Market
    symbol: Symbol
    schema_version: str = Field(..., description="Contract version (e.g. 'data-health-snapshot.v1')")
    connection_state: str | None = Field(
        default=None, description="Current connection state (e.g. 'CONNECTED', 'DISCONNECTED')"
    )
    last_message_age_ms: int | None = Field(
        default=None, ge=0, description="Age of last received message in milliseconds"
    )
    receive_latency: LatencySummary | None = Field(default=None, description="Receive latency summary")
    publish_latency: LatencySummary | None = Field(default=None, description="Publish latency summary")
    sequence_gap_count: int = Field(default=0, ge=0, description="Number of sequence gaps detected")
    resync_state: str | None = Field(
        default=None, description="Current resync state (e.g. 'SYNCED', 'RESYNC_IN_PROGRESS')"
    )
    book_synchronized: bool | None = Field(default=None, description="Whether the order book is synchronized")
    recorder_alive: bool | None = Field(default=None, description="Whether the Recorder process is alive")
    gateway_alive: bool | None = Field(default=None, description="Whether the Gateway process is alive")
    reason_codes: list[ReasonCode] = Field(default_factory=list, description="Reason codes explaining the health state")
    observed_time_utc_ns: int | None = Field(
        default=None, ge=0, description="UTC time when this health snapshot was observed (ns)"
    )
