"""DRAFT — Gateway protocol contracts.

All gateway contracts use ContractModel (frozen=True, strict=True, extra="forbid").
These contracts define the subscription, lifecycle, and streaming shapes for the Gateway.
Network I/O and server implementation are not part of this module.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import ContractModel, NonEmptyText
from binance_market_data_contracts.enums import (
    ConsumerGapReason,
    DeliveryMode,
    InitialSnapshotMode,
    Market,
    ReasonCode,
    RecoveryAction,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.identifiers import GatewayInstanceId, InstanceId, RequestId, SubscriptionId, Symbol
from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate
from binance_market_data_contracts.snapshots import LocalOrderBookSnapshot, MarketStateSnapshot


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
    def _validate_delivery_mode(self) -> EventSubscriptionRequest:
        if self.delivery_mode != DeliveryMode.CONTIGUOUS_EVENTS:
            raise ValueError(f"Event subscription requires CONTIGUOUS_EVENTS, got {self.delivery_mode}")
        return self


class OrderBookSubscriptionRequest(ContractModel):
    """Request to subscribe to an order book snapshot + diff stream."""

    request_id: RequestId
    schema_version: Literal["order-book-subscription-request.v1"]
    venue: Venue
    market: Market
    symbol: Symbol
    depth_limit: int | None = Field(default=None, gt=0)
    initial_snapshot_mode: Literal[InitialSnapshotMode.REQUIRED]
    supported_snapshot_schema_versions: tuple[str, ...] = Field(..., min_length=1)
    supported_update_schema_versions: tuple[str, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_snapshot_mode(self) -> OrderBookSubscriptionRequest:
        if self.initial_snapshot_mode != InitialSnapshotMode.REQUIRED:
            raise ValueError(f"Order book V1 requires REQUIRED initial snapshot, got {self.initial_snapshot_mode}")
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
    def _validate_delivery_mode(self) -> MarketStateSubscriptionRequest:
        if self.delivery_mode != DeliveryMode.LATEST_STATE:
            raise ValueError(f"Market state subscription requires LATEST_STATE, got {self.delivery_mode}")
        return self


class SubscriptionAccepted(ContractModel):
    """Confirms a subscription was accepted by the Gateway."""

    request_id: RequestId
    subscription_id: SubscriptionId
    schema_version: Literal["subscription-accepted.v1"]
    gateway_instance_id: InstanceId
    accepted_time_utc_ns: int = Field(..., ge=0)
    negotiated_payload_schema_versions: tuple[str, ...] = Field(..., min_length=1)


class ConsumerGapNotice(ContractModel):
    """Informs the consumer that a gap has been detected in their stream."""

    schema_version: Literal["consumer-gap-notice.v1"]
    subscription_id: SubscriptionId
    detected_time_utc_ns: int = Field(..., ge=0)
    last_delivered_session_sequence: int | None = Field(default=None, gt=0)
    next_available_session_sequence: int | None = Field(default=None, gt=0)
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
        needs_recovery = {
            ConsumerGapReason.SLOW_CONSUMER,
            ConsumerGapReason.RESUME_NOT_AVAILABLE,
            ConsumerGapReason.UPSTREAM_SEQUENCE_GAP,
        }
        if self.reason in needs_recovery and self.recovery_action == RecoveryAction.NONE:
            raise ValueError(f"Gap reason '{self.reason.value}' requires a recovery action, got NONE")
        return self


class StreamStatus(ContractModel):
    """Reports the lifecycle state of a consumer subscription stream."""

    schema_version: Literal["stream-status.v1"]
    subscription_id: SubscriptionId
    state: StreamLifecycleState
    observed_time_utc_ns: int = Field(..., ge=0)
    reason_code: ReasonCode | None = None
    message: NonEmptyText | None = None


class EnvelopeMetadata(ContractModel):
    """Gateway delivery metadata for each stream item."""

    protocol_version: Literal["gateway-stream.v1"]
    gateway_instance_id: GatewayInstanceId
    subscription_id: SubscriptionId
    connection_generation: int = Field(..., ge=1)
    session_sequence: int = Field(..., ge=1)
    publish_time_utc_ns: int = Field(..., ge=0)
    publish_monotonic_ns: int | None = Field(default=None, ge=0)


class GatewayEventEnvelope(ContractModel):
    """Wraps a single event for the contiguous event stream.

    Exactly one payload field must be set.
    """

    envelope_metadata: EnvelopeMetadata

    subscription_accepted: SubscriptionAccepted | None = None
    depth_update: DepthUpdate | None = None
    agg_trade: AggTrade | None = None
    book_ticker: BookTicker | None = None
    consumer_gap: ConsumerGapNotice | None = None
    stream_status: StreamStatus | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> GatewayEventEnvelope:
        payloads = [
            self.subscription_accepted,
            self.depth_update,
            self.agg_trade,
            self.book_ticker,
            self.consumer_gap,
            self.stream_status,
        ]
        non_none = [p for p in payloads if p is not None]
        if len(non_none) == 0:
            raise ValueError("GatewayEventEnvelope must have exactly one payload, got none")
        if len(non_none) > 1:
            raise ValueError(f"GatewayEventEnvelope must have exactly one payload, got {len(non_none)}")
        return self


class OrderBookStreamItem(ContractModel):
    """Wraps a single item for the order book stream.

    Exactly one payload field must be set.
    """

    envelope_metadata: EnvelopeMetadata

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


class MarketStateStreamItem(ContractModel):
    """Wraps a single item for the market state stream.

    Exactly one payload field must be set.
    """

    envelope_metadata: EnvelopeMetadata

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


class GatewayStatusRequest(ContractModel):
    """One-shot request for Gateway operational status."""

    request_id: RequestId
    schema_version: Literal["gateway-status-request.v1"]


class MarketRuntimeStatus(ContractModel):
    """Per-market runtime status within a Gateway instance."""

    venue: Venue
    market: Market
    symbol: Symbol
    state: StreamLifecycleState
    last_event_utc_ns: int = Field(..., ge=0)
    connection_generation: int = Field(..., ge=1)
    active_subscription_count: int = Field(default=0, ge=0)


class GatewayStatusSnapshot(ContractModel):
    """Snapshot of Gateway operational status."""

    schema_version: Literal["gateway-status-snapshot.v1"]
    gateway_instance_id: GatewayInstanceId
    observed_time_utc_ns: int = Field(..., ge=0)
    uptime_seconds: int = Field(..., ge=0)
    markets: tuple[MarketRuntimeStatus, ...] = ()
    total_active_subscriptions: int = Field(default=0, ge=0)
