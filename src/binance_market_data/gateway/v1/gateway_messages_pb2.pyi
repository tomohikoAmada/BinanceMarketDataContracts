from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from binance_market_data.common.v1 import identifiers_pb2 as _identifiers_pb2
from binance_market_data.common.v1 import metadata_pb2 as _metadata_pb2
from binance_market_data.market.v1 import market_events_pb2 as _market_events_pb2
from binance_market_data.projection.v1 import snapshots_pb2 as _snapshots_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventSubscriptionRequest(_message.Message):
    __slots__ = ("request_id", "schema_version", "selectors", "delivery_mode", "supported_payload_schema_versions")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    SELECTORS_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_MODE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_PAYLOAD_SCHEMA_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    schema_version: str
    selectors: _containers.RepeatedCompositeFieldContainer[_identifiers_pb2.StreamSelector]
    delivery_mode: _enums_pb2.DeliveryMode
    supported_payload_schema_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., selectors: _Optional[_Iterable[_Union[_identifiers_pb2.StreamSelector, _Mapping]]] = ..., delivery_mode: _Optional[_Union[_enums_pb2.DeliveryMode, str]] = ..., supported_payload_schema_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class OrderBookSubscriptionRequest(_message.Message):
    __slots__ = ("request_id", "schema_version", "venue", "market", "symbol", "depth_limit", "initial_snapshot_mode", "supported_snapshot_schema_versions", "supported_update_schema_versions")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DEPTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SNAPSHOT_MODE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SNAPSHOT_SCHEMA_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_UPDATE_SCHEMA_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    schema_version: str
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    depth_limit: int
    initial_snapshot_mode: _enums_pb2.InitialSnapshotMode
    supported_snapshot_schema_versions: _containers.RepeatedScalarFieldContainer[str]
    supported_update_schema_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., depth_limit: _Optional[int] = ..., initial_snapshot_mode: _Optional[_Union[_enums_pb2.InitialSnapshotMode, str]] = ..., supported_snapshot_schema_versions: _Optional[_Iterable[str]] = ..., supported_update_schema_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class MarketStateSubscriptionRequest(_message.Message):
    __slots__ = ("request_id", "schema_version", "venue", "market", "symbol", "delivery_mode", "depth_limit", "minimum_publish_interval_ms", "supported_schema_versions")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_MODE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_PUBLISH_INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SCHEMA_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    schema_version: str
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    delivery_mode: _enums_pb2.DeliveryMode
    depth_limit: int
    minimum_publish_interval_ms: int
    supported_schema_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., delivery_mode: _Optional[_Union[_enums_pb2.DeliveryMode, str]] = ..., depth_limit: _Optional[int] = ..., minimum_publish_interval_ms: _Optional[int] = ..., supported_schema_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class SubscriptionAccepted(_message.Message):
    __slots__ = ("request_id", "subscription_id", "schema_version", "gateway_instance_id", "accepted_time_utc_ns", "negotiated_payload_schema_versions")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    NEGOTIATED_PAYLOAD_SCHEMA_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    subscription_id: str
    schema_version: str
    gateway_instance_id: str
    accepted_time_utc_ns: int
    negotiated_payload_schema_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., subscription_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., gateway_instance_id: _Optional[str] = ..., accepted_time_utc_ns: _Optional[int] = ..., negotiated_payload_schema_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class ConsumerGapNotice(_message.Message):
    __slots__ = ("schema_version", "subscription_id", "detected_time_utc_ns", "last_delivered_session_sequence", "next_available_session_sequence", "reason", "recovery_action", "market", "symbol", "stream")
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    DETECTED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    LAST_DELIVERED_SESSION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NEXT_AVAILABLE_SESSION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    RECOVERY_ACTION_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    schema_version: str
    subscription_id: str
    detected_time_utc_ns: int
    last_delivered_session_sequence: int
    next_available_session_sequence: int
    reason: _enums_pb2.ConsumerGapReason
    recovery_action: _enums_pb2.RecoveryAction
    market: _enums_pb2.Market
    symbol: str
    stream: _enums_pb2.Stream
    def __init__(self, schema_version: _Optional[str] = ..., subscription_id: _Optional[str] = ..., detected_time_utc_ns: _Optional[int] = ..., last_delivered_session_sequence: _Optional[int] = ..., next_available_session_sequence: _Optional[int] = ..., reason: _Optional[_Union[_enums_pb2.ConsumerGapReason, str]] = ..., recovery_action: _Optional[_Union[_enums_pb2.RecoveryAction, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., stream: _Optional[_Union[_enums_pb2.Stream, str]] = ...) -> None: ...

class StreamStatus(_message.Message):
    __slots__ = ("schema_version", "subscription_id", "state", "observed_time_utc_ns", "reason_code", "message")
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    REASON_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    schema_version: str
    subscription_id: str
    state: _enums_pb2.StreamLifecycleState
    observed_time_utc_ns: int
    reason_code: _enums_pb2.ReasonCode
    message: str
    def __init__(self, schema_version: _Optional[str] = ..., subscription_id: _Optional[str] = ..., state: _Optional[_Union[_enums_pb2.StreamLifecycleState, str]] = ..., observed_time_utc_ns: _Optional[int] = ..., reason_code: _Optional[_Union[_enums_pb2.ReasonCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class GatewayEnvelopeMetadata(_message.Message):
    __slots__ = ("protocol_version", "gateway_instance_id", "subscription_id", "connection_generation", "session_sequence", "publish_time_utc_ns", "publish_monotonic_ns")
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_GENERATION_FIELD_NUMBER: _ClassVar[int]
    SESSION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_MONOTONIC_NS_FIELD_NUMBER: _ClassVar[int]
    protocol_version: str
    gateway_instance_id: str
    subscription_id: str
    connection_generation: int
    session_sequence: int
    publish_time_utc_ns: int
    publish_monotonic_ns: int
    def __init__(self, protocol_version: _Optional[str] = ..., gateway_instance_id: _Optional[str] = ..., subscription_id: _Optional[str] = ..., connection_generation: _Optional[int] = ..., session_sequence: _Optional[int] = ..., publish_time_utc_ns: _Optional[int] = ..., publish_monotonic_ns: _Optional[int] = ...) -> None: ...

class GatewayEventEnvelope(_message.Message):
    __slots__ = ("envelope_metadata", "delivery_metadata", "subscription_accepted", "depth_update", "agg_trade", "book_ticker", "consumer_gap", "stream_status")
    ENVELOPE_METADATA_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_METADATA_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    DEPTH_UPDATE_FIELD_NUMBER: _ClassVar[int]
    AGG_TRADE_FIELD_NUMBER: _ClassVar[int]
    BOOK_TICKER_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_GAP_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATUS_FIELD_NUMBER: _ClassVar[int]
    envelope_metadata: _metadata_pb2.EnvelopeMetadata
    delivery_metadata: GatewayEnvelopeMetadata
    subscription_accepted: SubscriptionAccepted
    depth_update: _market_events_pb2.DepthUpdate
    agg_trade: _market_events_pb2.AggTrade
    book_ticker: _market_events_pb2.BookTicker
    consumer_gap: ConsumerGapNotice
    stream_status: StreamStatus
    def __init__(self, envelope_metadata: _Optional[_Union[_metadata_pb2.EnvelopeMetadata, _Mapping]] = ..., delivery_metadata: _Optional[_Union[GatewayEnvelopeMetadata, _Mapping]] = ..., subscription_accepted: _Optional[_Union[SubscriptionAccepted, _Mapping]] = ..., depth_update: _Optional[_Union[_market_events_pb2.DepthUpdate, _Mapping]] = ..., agg_trade: _Optional[_Union[_market_events_pb2.AggTrade, _Mapping]] = ..., book_ticker: _Optional[_Union[_market_events_pb2.BookTicker, _Mapping]] = ..., consumer_gap: _Optional[_Union[ConsumerGapNotice, _Mapping]] = ..., stream_status: _Optional[_Union[StreamStatus, _Mapping]] = ...) -> None: ...

class OrderBookStreamItem(_message.Message):
    __slots__ = ("envelope_metadata", "delivery_metadata", "subscription_accepted", "snapshot", "depth_update", "consumer_gap", "stream_status")
    ENVELOPE_METADATA_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_METADATA_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_UPDATE_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_GAP_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATUS_FIELD_NUMBER: _ClassVar[int]
    envelope_metadata: _metadata_pb2.EnvelopeMetadata
    delivery_metadata: GatewayEnvelopeMetadata
    subscription_accepted: SubscriptionAccepted
    snapshot: _snapshots_pb2.LocalOrderBookSnapshot
    depth_update: _market_events_pb2.DepthUpdate
    consumer_gap: ConsumerGapNotice
    stream_status: StreamStatus
    def __init__(self, envelope_metadata: _Optional[_Union[_metadata_pb2.EnvelopeMetadata, _Mapping]] = ..., delivery_metadata: _Optional[_Union[GatewayEnvelopeMetadata, _Mapping]] = ..., subscription_accepted: _Optional[_Union[SubscriptionAccepted, _Mapping]] = ..., snapshot: _Optional[_Union[_snapshots_pb2.LocalOrderBookSnapshot, _Mapping]] = ..., depth_update: _Optional[_Union[_market_events_pb2.DepthUpdate, _Mapping]] = ..., consumer_gap: _Optional[_Union[ConsumerGapNotice, _Mapping]] = ..., stream_status: _Optional[_Union[StreamStatus, _Mapping]] = ...) -> None: ...

class MarketStateStreamItem(_message.Message):
    __slots__ = ("envelope_metadata", "delivery_metadata", "subscription_accepted", "market_state", "consumer_gap", "stream_status")
    ENVELOPE_METADATA_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_METADATA_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    MARKET_STATE_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_GAP_FIELD_NUMBER: _ClassVar[int]
    STREAM_STATUS_FIELD_NUMBER: _ClassVar[int]
    envelope_metadata: _metadata_pb2.EnvelopeMetadata
    delivery_metadata: GatewayEnvelopeMetadata
    subscription_accepted: SubscriptionAccepted
    market_state: _snapshots_pb2.MarketStateSnapshot
    consumer_gap: ConsumerGapNotice
    stream_status: StreamStatus
    def __init__(self, envelope_metadata: _Optional[_Union[_metadata_pb2.EnvelopeMetadata, _Mapping]] = ..., delivery_metadata: _Optional[_Union[GatewayEnvelopeMetadata, _Mapping]] = ..., subscription_accepted: _Optional[_Union[SubscriptionAccepted, _Mapping]] = ..., market_state: _Optional[_Union[_snapshots_pb2.MarketStateSnapshot, _Mapping]] = ..., consumer_gap: _Optional[_Union[ConsumerGapNotice, _Mapping]] = ..., stream_status: _Optional[_Union[StreamStatus, _Mapping]] = ...) -> None: ...

class GatewayStatusRequest(_message.Message):
    __slots__ = ("request_id", "schema_version")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    schema_version: str
    def __init__(self, request_id: _Optional[str] = ..., schema_version: _Optional[str] = ...) -> None: ...

class MarketRuntimeStatus(_message.Message):
    __slots__ = ("venue", "market", "symbol", "state", "last_event_utc_ns", "connection_generation", "active_subscription_count")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_EVENT_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_GENERATION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SUBSCRIPTION_COUNT_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    state: _enums_pb2.StreamLifecycleState
    last_event_utc_ns: int
    connection_generation: int
    active_subscription_count: int
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., state: _Optional[_Union[_enums_pb2.StreamLifecycleState, str]] = ..., last_event_utc_ns: _Optional[int] = ..., connection_generation: _Optional[int] = ..., active_subscription_count: _Optional[int] = ...) -> None: ...

class GatewayStatusSnapshot(_message.Message):
    __slots__ = ("schema_version", "gateway_instance_id", "observed_time_utc_ns", "uptime_seconds", "markets", "total_active_subscriptions")
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ACTIVE_SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    schema_version: str
    gateway_instance_id: str
    observed_time_utc_ns: int
    uptime_seconds: int
    markets: _containers.RepeatedCompositeFieldContainer[MarketRuntimeStatus]
    total_active_subscriptions: int
    def __init__(self, schema_version: _Optional[str] = ..., gateway_instance_id: _Optional[str] = ..., observed_time_utc_ns: _Optional[int] = ..., uptime_seconds: _Optional[int] = ..., markets: _Optional[_Iterable[_Union[MarketRuntimeStatus, _Mapping]]] = ..., total_active_subscriptions: _Optional[int] = ...) -> None: ...
