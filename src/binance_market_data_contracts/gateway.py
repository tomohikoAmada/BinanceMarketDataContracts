"""DRAFT — Gateway protocol contracts.

All gateway contracts use ContractModel (frozen=True, strict=True, extra="forbid").
These contracts define the subscription, lifecycle, and streaming shapes for the Gateway.
Network I/O and server implementation are not part of this module.
"""

from __future__ import annotations

import re
from typing import Final, Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import (
    INT32_MAX,
    NON_EMPTY_TEXT_PATTERN,
    UINT64_MAX,
    ContractModel,
    NonEmptyText,
    QuantityString,
)
from binance_market_data_contracts.enums import (
    ConsumerGapReason,
    DeliveryMode,
    InitialSnapshotMode,
    Market,
    ReasonCode,
    RecoveryAction,
    ReferenceObservationStatus,
    ReferenceSourceKind,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.identifiers import GatewayInstanceId, RequestId, SubscriptionId, Symbol
from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate, Liquidation, MarkPrice
from binance_market_data_contracts.snapshots import ExchangeDepthSnapshot, LocalOrderBookSnapshot, MarketStateSnapshot


def _validate_schema_version_tuple(versions: tuple[str, ...], field_name: str) -> None:
    non_empty = re.compile(NON_EMPTY_TEXT_PATTERN)
    seen: set[str] = set()
    for v in versions:
        if not non_empty.match(v):
            raise ValueError(f"{field_name} must contain non-empty, non-whitespace strings, got {v!r}")
        if v in seen:
            raise ValueError(f"{field_name} must not contain duplicates, got {v!r}")
        seen.add(v)


_CONSUMER_GAP_RECOVERY_ACTION_BY_REASON: Final = {
    ConsumerGapReason.SLOW_CONSUMER: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.RESUME_NOT_AVAILABLE: RecoveryAction.REQUEST_NEW_SNAPSHOT,
    ConsumerGapReason.UPSTREAM_SEQUENCE_GAP: RecoveryAction.REQUEST_NEW_SNAPSHOT,
    ConsumerGapReason.GATEWAY_RESTART: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.CONNECTION_GENERATION_CHANGED: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.SUBSCRIPTION_RECONFIGURED: RecoveryAction.RESUBSCRIBE,
}


class StreamSelector(ContractModel):
    """Identifies a specific market data stream to subscribe to."""

    venue: Venue
    market: Market
    symbol: Symbol
    stream: Stream


class EventSubscriptionRequest(ContractModel):
    """Request to subscribe to a contiguous event stream."""

    request_id: RequestId
    schema_version: Literal["event-subscription-request.v1"]
    selectors: tuple[StreamSelector, ...] = Field(..., min_length=1)
    delivery_mode: Literal[DeliveryMode.CONTIGUOUS_EVENTS]
    supported_payload_schema_versions: tuple[str, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_selectors(self) -> EventSubscriptionRequest:
        seen: set[tuple[Venue, Market, str, Stream]] = set()
        for sel in self.selectors:
            key = (sel.venue, sel.market, sel.symbol, sel.stream)
            if key in seen:
                raise ValueError(f"Duplicate selector: {sel}")
            seen.add(key)
        return self

    @model_validator(mode="after")
    def _validate_supported_payload_schema_versions(self) -> EventSubscriptionRequest:
        _validate_schema_version_tuple(self.supported_payload_schema_versions, "supported_payload_schema_versions")
        return self

    @model_validator(mode="after")
    def _validate_no_snapshot_selectors(self) -> EventSubscriptionRequest:
        for sel in self.selectors:
            if sel.stream == Stream.DEPTH_SNAPSHOT:
                raise ValueError("DEPTH_SNAPSHOT cannot be subscribed via event stream (REST snapshot only)")
        return self


class OrderBookSubscriptionRequest(ContractModel):
    """Request to subscribe to an order book snapshot + diff stream."""

    request_id: RequestId
    schema_version: Literal["order-book-subscription-request.v1"]
    venue: Venue
    market: Market
    symbol: Symbol
    depth_limit: int | None = Field(default=None, gt=0, le=INT32_MAX)
    initial_snapshot_mode: Literal[InitialSnapshotMode.REQUIRED]
    supported_snapshot_schema_versions: tuple[str, ...] = Field(..., min_length=1)
    supported_update_schema_versions: tuple[str, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_supported_snapshot_schema_versions(self) -> OrderBookSubscriptionRequest:
        _validate_schema_version_tuple(self.supported_snapshot_schema_versions, "supported_snapshot_schema_versions")
        return self

    @model_validator(mode="after")
    def _validate_supported_update_schema_versions(self) -> OrderBookSubscriptionRequest:
        _validate_schema_version_tuple(self.supported_update_schema_versions, "supported_update_schema_versions")
        return self


class MarketStateSubscriptionRequest(ContractModel):
    """Request to subscribe to latest market state updates."""

    request_id: RequestId
    schema_version: Literal["market-state-subscription-request.v1"]
    venue: Venue
    market: Market
    symbol: Symbol
    delivery_mode: Literal[DeliveryMode.LATEST_STATE]
    depth_limit: int | None = Field(default=None, gt=0)
    minimum_publish_interval_ms: int | None = Field(default=None, ge=0)
    supported_schema_versions: tuple[str, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_supported_schema_versions(self) -> MarketStateSubscriptionRequest:
        _validate_schema_version_tuple(self.supported_schema_versions, "supported_schema_versions")
        return self


class SubscriptionAccepted(ContractModel):
    """Confirms a subscription was accepted by the Gateway."""

    request_id: RequestId
    subscription_id: SubscriptionId
    schema_version: Literal["subscription-accepted.v1"]
    gateway_instance_id: GatewayInstanceId
    accepted_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    negotiated_payload_schema_versions: tuple[str, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_negotiated_payload_schema_versions(self) -> SubscriptionAccepted:
        _validate_schema_version_tuple(self.negotiated_payload_schema_versions, "negotiated_payload_schema_versions")
        return self


class ConsumerGapNotice(ContractModel):
    """Informs the consumer that a gap has been detected in their stream."""

    schema_version: Literal["consumer-gap-notice.v1"]
    subscription_id: SubscriptionId
    detected_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    last_delivered_session_sequence: int | None = Field(default=None, gt=0, le=UINT64_MAX)
    next_available_session_sequence: int | None = Field(default=None, gt=0, le=UINT64_MAX)
    reason: ConsumerGapReason
    recovery_action: RecoveryAction
    market: Market | None = None
    symbol: Symbol | None = None
    stream: Stream | None = None

    @model_validator(mode="after")
    def _validate_sequences(self) -> ConsumerGapNotice:
        if (
            self.last_delivered_session_sequence is not None
            and self.next_available_session_sequence is not None
            and self.next_available_session_sequence <= self.last_delivered_session_sequence
        ):
            raise ValueError(
                f"next_available_session_sequence ({self.next_available_session_sequence}) "
                f"must be > last_delivered_session_sequence ({self.last_delivered_session_sequence})"
            )
        return self

    @model_validator(mode="after")
    def _validate_recovery_action(self) -> ConsumerGapNotice:
        expected_action = _CONSUMER_GAP_RECOVERY_ACTION_BY_REASON[self.reason]
        if self.recovery_action != expected_action:
            raise ValueError(
                f"Gap reason '{self.reason.value}' requires recovery action "
                f"'{expected_action.value}', got '{self.recovery_action.value}'"
            )
        return self


class StreamStatus(ContractModel):
    """Reports the lifecycle state of a consumer subscription stream."""

    schema_version: Literal["stream-status.v1"]
    subscription_id: SubscriptionId
    state: StreamLifecycleState
    observed_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    reason_code: ReasonCode | None = None
    message: NonEmptyText | None = None
    reference_source_kind: ReferenceSourceKind | None = None


class OpenInterest(ContractModel):
    open_interest: QuantityString
    source_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)


class LongShortRatio(ContractModel):
    long_short_ratio: QuantityString
    long_account: QuantityString
    short_account: QuantityString
    source_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    period: NonEmptyText


class TakerBuySellVolume(ContractModel):
    buy_sell_ratio: QuantityString
    buy_volume: QuantityString
    sell_volume: QuantityString
    source_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    period: NonEmptyText


class InstrumentFilter(ContractModel):
    filter_type: NonEmptyText
    price: str | None = None
    quantity: str | None = None
    notional: QuantityString | None = None
    limit: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    min_price: QuantityString | None = None
    max_price: QuantityString | None = None
    tick_size: QuantityString | None = None
    min_quantity: QuantityString | None = None
    max_quantity: QuantityString | None = None
    step_size: QuantityString | None = None
    multiplier_up: QuantityString | None = None
    multiplier_down: QuantityString | None = None
    multiplier_decimal: QuantityString | None = None
    position_control_side: NonEmptyText | None = None


class RateLimit(ContractModel):
    rate_limit_type: NonEmptyText
    interval: NonEmptyText
    interval_num: int = Field(..., ge=0, le=INT32_MAX)
    limit: int = Field(..., ge=0, le=UINT64_MAX)


class InstrumentReference(ContractModel):
    symbol_present: bool
    contract_type: NonEmptyText
    trading_status: NonEmptyText
    base_asset: NonEmptyText
    quote_asset: NonEmptyText
    margin_asset: NonEmptyText
    price_precision: int = Field(..., ge=0, le=INT32_MAX)
    quantity_precision: int = Field(..., ge=0, le=INT32_MAX)
    onboard_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    delivery_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    filters: tuple[InstrumentFilter, ...] = ()
    rate_limits: tuple[RateLimit, ...] = ()
    server_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)


class ReferenceObservation(ContractModel):
    """One typed low-frequency REST observation."""

    schema_version: Literal["reference-observation.v1"]
    venue: Venue
    market: Market
    symbol: Symbol
    request_id: RequestId
    source_kind: ReferenceSourceKind
    receive_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    source_time_ms: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    status: ReferenceObservationStatus
    error_code: NonEmptyText | None = None

    open_interest: OpenInterest | None = None
    top_long_short_account_ratio: LongShortRatio | None = None
    top_long_short_position_ratio: LongShortRatio | None = None
    global_long_short_account_ratio: LongShortRatio | None = None
    taker_buy_sell_volume: TakerBuySellVolume | None = None
    instrument: InstrumentReference | None = None
    depth_baseline: ExchangeDepthSnapshot | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> ReferenceObservation:
        mapping = {
            ReferenceSourceKind.OPEN_INTEREST: self.open_interest,
            ReferenceSourceKind.TOP_LONG_SHORT_ACCOUNT_RATIO: self.top_long_short_account_ratio,
            ReferenceSourceKind.TOP_LONG_SHORT_POSITION_RATIO: self.top_long_short_position_ratio,
            ReferenceSourceKind.GLOBAL_LONG_SHORT_ACCOUNT_RATIO: self.global_long_short_account_ratio,
            ReferenceSourceKind.TAKER_BUY_SELL_VOLUME: self.taker_buy_sell_volume,
            ReferenceSourceKind.INSTRUMENT: self.instrument,
            ReferenceSourceKind.DEPTH_BASELINE: self.depth_baseline,
        }
        payload = mapping[self.source_kind]
        if self.status == ReferenceObservationStatus.VALID and payload is None:
            raise ValueError("VALID reference observation requires its typed payload")
        if self.status in {ReferenceObservationStatus.EMPTY, ReferenceObservationStatus.ERROR} and payload is not None:
            raise ValueError("EMPTY/ERROR reference observation must not carry a payload")
        present = [key for key, value in mapping.items() if value is not None]
        if len(present) > 1:
            raise ValueError("reference observation must have exactly one payload")
        if present and present[0] != self.source_kind:
            raise ValueError("reference observation payload does not match source_kind")
        return self


class GatewayEnvelopeMetadata(ContractModel):
    """Canonical M6 Gateway delivery metadata."""

    protocol_version: Literal["gateway-stream.v1"]
    gateway_instance_id: GatewayInstanceId
    subscription_id: SubscriptionId
    connection_generation: int | None = Field(default=None, ge=1, le=UINT64_MAX)
    session_sequence: int = Field(..., ge=1, le=UINT64_MAX)
    publish_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    publish_monotonic_ns: int | None = Field(default=None, ge=0, le=UINT64_MAX)


def _validate_stream_item_identity(
    *,
    delivery_metadata: GatewayEnvelopeMetadata,
    subscription_accepted: SubscriptionAccepted | None,
    consumer_gap: ConsumerGapNotice | None,
    stream_status: StreamStatus | None,
) -> None:
    """Validate lifecycle payload identity consistently across all stream envelopes."""
    lifecycle_payload = subscription_accepted or consumer_gap or stream_status
    if lifecycle_payload is not None and lifecycle_payload.subscription_id != delivery_metadata.subscription_id:
        raise ValueError(
            f"Identity conflict: payload subscription_id ({lifecycle_payload.subscription_id}) "
            f"!= delivery_metadata.subscription_id ({delivery_metadata.subscription_id})"
        )
    if (
        subscription_accepted is not None
        and subscription_accepted.gateway_instance_id != delivery_metadata.gateway_instance_id
    ):
        raise ValueError(
            f"Identity conflict: SubscriptionAccepted gateway_instance_id "
            f"({subscription_accepted.gateway_instance_id}) != delivery_metadata.gateway_instance_id "
            f"({delivery_metadata.gateway_instance_id})"
        )


class GatewayEventEnvelope(ContractModel):
    """Wraps a single event for the contiguous event stream.

    Exactly one payload field must be set.
    """

    delivery_metadata: GatewayEnvelopeMetadata

    subscription_accepted: SubscriptionAccepted | None = None
    depth_update: DepthUpdate | None = None
    agg_trade: AggTrade | None = None
    book_ticker: BookTicker | None = None
    mark_price: MarkPrice | None = None
    liquidation: Liquidation | None = None
    reference_observation: ReferenceObservation | None = None
    consumer_gap: ConsumerGapNotice | None = None
    stream_status: StreamStatus | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> GatewayEventEnvelope:
        payloads = [
            self.subscription_accepted,
            self.depth_update,
            self.agg_trade,
            self.book_ticker,
            self.mark_price,
            self.liquidation,
            self.reference_observation,
            self.consumer_gap,
            self.stream_status,
        ]
        non_none = [p for p in payloads if p is not None]
        if len(non_none) == 0:
            raise ValueError("GatewayEventEnvelope must have exactly one payload, got none")
        if len(non_none) > 1:
            raise ValueError(f"GatewayEventEnvelope must have exactly one payload, got {len(non_none)}")
        return self

    @model_validator(mode="after")
    def _validate_identity_consistency(self) -> GatewayEventEnvelope:
        _validate_stream_item_identity(
            delivery_metadata=self.delivery_metadata,
            subscription_accepted=self.subscription_accepted,
            consumer_gap=self.consumer_gap,
            stream_status=self.stream_status,
        )
        return self


class OrderBookStreamItem(ContractModel):
    """Wraps a single item for the order book stream.

    Exactly one payload field must be set.
    """

    delivery_metadata: GatewayEnvelopeMetadata

    subscription_accepted: SubscriptionAccepted | None = None
    snapshot: LocalOrderBookSnapshot | None = None
    depth_update: DepthUpdate | None = None
    consumer_gap: ConsumerGapNotice | None = None
    stream_status: StreamStatus | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> OrderBookStreamItem:
        payloads = [
            self.subscription_accepted,
            self.snapshot,
            self.depth_update,
            self.consumer_gap,
            self.stream_status,
        ]
        non_none = [p for p in payloads if p is not None]
        if len(non_none) == 0:
            raise ValueError("OrderBookStreamItem must have exactly one payload, got none")
        if len(non_none) > 1:
            raise ValueError(f"OrderBookStreamItem must have exactly one payload, got {len(non_none)}")
        return self

    @model_validator(mode="after")
    def _validate_identity_consistency(self) -> OrderBookStreamItem:
        _validate_stream_item_identity(
            delivery_metadata=self.delivery_metadata,
            subscription_accepted=self.subscription_accepted,
            consumer_gap=self.consumer_gap,
            stream_status=self.stream_status,
        )
        return self


class MarketStateStreamItem(ContractModel):
    """Wraps a single item for the market state stream.

    Exactly one payload field must be set.
    """

    delivery_metadata: GatewayEnvelopeMetadata

    subscription_accepted: SubscriptionAccepted | None = None
    market_state: MarketStateSnapshot | None = None
    consumer_gap: ConsumerGapNotice | None = None
    stream_status: StreamStatus | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> MarketStateStreamItem:
        payloads = [
            self.subscription_accepted,
            self.market_state,
            self.consumer_gap,
            self.stream_status,
        ]
        non_none = [p for p in payloads if p is not None]
        if len(non_none) == 0:
            raise ValueError("MarketStateStreamItem must have exactly one payload, got none")
        if len(non_none) > 1:
            raise ValueError(f"MarketStateStreamItem must have exactly one payload, got {len(non_none)}")
        return self

    @model_validator(mode="after")
    def _validate_identity_consistency(self) -> MarketStateStreamItem:
        _validate_stream_item_identity(
            delivery_metadata=self.delivery_metadata,
            subscription_accepted=self.subscription_accepted,
            consumer_gap=self.consumer_gap,
            stream_status=self.stream_status,
        )
        return self


class GatewayStatusRequest(ContractModel):
    """One-shot request for Gateway operational status."""

    request_id: RequestId
    schema_version: Literal["gateway-status-request.v1"]


class MarketRuntimeStatus(ContractModel):
    """Per-market aggregate runtime status within a Gateway instance.

    Connection generation is optional because an aggregate market status may not
    have one uniquely applicable upstream source.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    state: StreamLifecycleState
    last_event_utc_ns: int | None = Field(default=None, ge=0, le=UINT64_MAX)
    connection_generation: int | None = Field(default=None, ge=1, le=UINT64_MAX)
    active_subscription_count: int = Field(default=0, ge=0, le=UINT64_MAX)


class GatewayStatusSnapshot(ContractModel):
    """Snapshot of Gateway operational status."""

    schema_version: Literal["gateway-status-snapshot.v1"]
    gateway_instance_id: GatewayInstanceId
    observed_time_utc_ns: int = Field(..., ge=0, le=UINT64_MAX)
    uptime_seconds: int = Field(..., ge=0, le=UINT64_MAX)
    markets: tuple[MarketRuntimeStatus, ...] = ()
    total_active_subscriptions: int = Field(default=0, ge=0, le=UINT64_MAX)
