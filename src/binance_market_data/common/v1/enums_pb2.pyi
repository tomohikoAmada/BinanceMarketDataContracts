from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Venue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENUE_UNSPECIFIED: _ClassVar[Venue]
    VENUE_BINANCE: _ClassVar[Venue]

class Market(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKET_UNSPECIFIED: _ClassVar[Market]
    MARKET_SPOT: _ClassVar[Market]
    MARKET_USD_M_PERPETUAL: _ClassVar[Market]

class Stream(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAM_UNSPECIFIED: _ClassVar[Stream]
    STREAM_DIFF_DEPTH: _ClassVar[Stream]
    STREAM_AGG_TRADE: _ClassVar[Stream]
    STREAM_BOOK_TICKER: _ClassVar[Stream]
    STREAM_DEPTH_SNAPSHOT: _ClassVar[Stream]

class QualityFlag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUALITY_FLAG_UNSPECIFIED: _ClassVar[QualityFlag]
    QUALITY_FLAG_DUPLICATE: _ClassVar[QualityFlag]
    QUALITY_FLAG_OUT_OF_ORDER: _ClassVar[QualityFlag]
    QUALITY_FLAG_SEQUENCE_GAP: _ClassVar[QualityFlag]
    QUALITY_FLAG_ORDERBOOK_RESYNC: _ClassVar[QualityFlag]
    QUALITY_FLAG_SNAPSHOT_BRIDGE_PENDING: _ClassVar[QualityFlag]
    QUALITY_FLAG_SNAPSHOT_TOO_OLD: _ClassVar[QualityFlag]
    QUALITY_FLAG_BOOTSTRAP_BUFFER_OVERFLOW: _ClassVar[QualityFlag]
    QUALITY_FLAG_RECOVERED_TAIL: _ClassVar[QualityFlag]
    QUALITY_FLAG_MALFORMED_PAYLOAD: _ClassVar[QualityFlag]
    QUALITY_FLAG_EXCHANGE_TIME_MISSING: _ClassVar[QualityFlag]
    QUALITY_FLAG_RECEIVE_CLOCK_DISCONTINUITY: _ClassVar[QualityFlag]
    QUALITY_FLAG_SLOW_CONSUMER_GAP: _ClassVar[QualityFlag]
    QUALITY_FLAG_PRODUCER_RESTART: _ClassVar[QualityFlag]
    QUALITY_FLAG_OVERLAP: _ClassVar[QualityFlag]
    QUALITY_FLAG_IDENTITY_CONFLICT: _ClassVar[QualityFlag]
    QUALITY_FLAG_CROSSED_BOOK: _ClassVar[QualityFlag]

class ReasonCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REASON_CODE_UNSPECIFIED: _ClassVar[ReasonCode]
    REASON_CODE_CONNECTION_LOST: _ClassVar[ReasonCode]
    REASON_CODE_CONNECTION_RESUMED: _ClassVar[ReasonCode]
    REASON_CODE_PING_TIMEOUT: _ClassVar[ReasonCode]
    REASON_CODE_LAST_MESSAGE_AGE_HIGH: _ClassVar[ReasonCode]
    REASON_CODE_RECEIVE_LATENCY_HIGH: _ClassVar[ReasonCode]
    REASON_CODE_PUBLISH_LATENCY_HIGH: _ClassVar[ReasonCode]
    REASON_CODE_SEQUENCE_GAP_DETECTED: _ClassVar[ReasonCode]
    REASON_CODE_SEQUENCE_GAP_TOO_LARGE: _ClassVar[ReasonCode]
    REASON_CODE_RESYNC_IN_PROGRESS: _ClassVar[ReasonCode]
    REASON_CODE_RESYNC_FAILED: _ClassVar[ReasonCode]
    REASON_CODE_BOOK_NOT_SYNCHRONIZED: _ClassVar[ReasonCode]
    REASON_CODE_BOOK_CROSSED: _ClassVar[ReasonCode]
    REASON_CODE_BOOK_EMPTY: _ClassVar[ReasonCode]
    REASON_CODE_RECORDER_STALLED: _ClassVar[ReasonCode]
    REASON_CODE_GATEWAY_STALLED: _ClassVar[ReasonCode]
    REASON_CODE_DIVERGENCE_DETECTED: _ClassVar[ReasonCode]
    REASON_CODE_DISK_SPACE_LOW: _ClassVar[ReasonCode]
    REASON_CODE_QUEUE_BACKLOG: _ClassVar[ReasonCode]
    REASON_CODE_ARCHIVE_BACKLOG: _ClassVar[ReasonCode]
    REASON_CODE_CONFIGURATION_ERROR: _ClassVar[ReasonCode]

class ConnectionState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONNECTION_STATE_UNSPECIFIED: _ClassVar[ConnectionState]
    CONNECTION_STATE_CONNECTING: _ClassVar[ConnectionState]
    CONNECTION_STATE_CONNECTED: _ClassVar[ConnectionState]
    CONNECTION_STATE_RECONNECTING: _ClassVar[ConnectionState]
    CONNECTION_STATE_DISCONNECTED: _ClassVar[ConnectionState]
    CONNECTION_STATE_FAILED: _ClassVar[ConnectionState]

class ResyncState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESYNC_STATE_UNSPECIFIED: _ClassVar[ResyncState]
    RESYNC_STATE_SYNCHRONIZED: _ClassVar[ResyncState]
    RESYNC_STATE_RESYNC_REQUIRED: _ClassVar[ResyncState]
    RESYNC_STATE_RESYNC_IN_PROGRESS: _ClassVar[ResyncState]
    RESYNC_STATE_RECOVERED: _ClassVar[ResyncState]
    RESYNC_STATE_RESYNC_FAILED: _ClassVar[ResyncState]

class SnapshotSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SNAPSHOT_SOURCE_UNSPECIFIED: _ClassVar[SnapshotSource]
    SNAPSHOT_SOURCE_GATEWAY_LIVE: _ClassVar[SnapshotSource]
    SNAPSHOT_SOURCE_RECORDER_REPLAY: _ClassVar[SnapshotSource]
    SNAPSHOT_SOURCE_HISTORY_REPLAY: _ClassVar[SnapshotSource]

class DeliveryMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DELIVERY_MODE_UNSPECIFIED: _ClassVar[DeliveryMode]
    DELIVERY_MODE_CONTIGUOUS_EVENTS: _ClassVar[DeliveryMode]
    DELIVERY_MODE_LATEST_STATE: _ClassVar[DeliveryMode]

class InitialSnapshotMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INITIAL_SNAPSHOT_MODE_UNSPECIFIED: _ClassVar[InitialSnapshotMode]
    INITIAL_SNAPSHOT_MODE_NONE: _ClassVar[InitialSnapshotMode]
    INITIAL_SNAPSHOT_MODE_REQUIRED: _ClassVar[InitialSnapshotMode]

class ConsumerGapReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONSUMER_GAP_REASON_UNSPECIFIED: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_SLOW_CONSUMER: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_RESUME_NOT_AVAILABLE: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_UPSTREAM_SEQUENCE_GAP: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_GATEWAY_RESTART: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_CONNECTION_GENERATION_CHANGED: _ClassVar[ConsumerGapReason]
    CONSUMER_GAP_REASON_SUBSCRIPTION_RECONFIGURED: _ClassVar[ConsumerGapReason]

class RecoveryAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RECOVERY_ACTION_UNSPECIFIED: _ClassVar[RecoveryAction]
    RECOVERY_ACTION_NONE: _ClassVar[RecoveryAction]
    RECOVERY_ACTION_RESUBSCRIBE: _ClassVar[RecoveryAction]
    RECOVERY_ACTION_REQUEST_NEW_SNAPSHOT: _ClassVar[RecoveryAction]

class StreamLifecycleState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAM_LIFECYCLE_STATE_UNSPECIFIED: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_ACCEPTED: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_SNAPSHOT_PENDING: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_LIVE: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_RESYNC_IN_PROGRESS: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_DEGRADED: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_CLOSING: _ClassVar[StreamLifecycleState]
    STREAM_LIFECYCLE_STATE_CLOSED: _ClassVar[StreamLifecycleState]

class HealthState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEALTH_STATE_UNSPECIFIED: _ClassVar[HealthState]
    HEALTH_STATE_HEALTHY: _ClassVar[HealthState]
    HEALTH_STATE_DEGRADED: _ClassVar[HealthState]
    HEALTH_STATE_UNRELIABLE: _ClassVar[HealthState]
    HEALTH_STATE_UNAVAILABLE: _ClassVar[HealthState]
VENUE_UNSPECIFIED: Venue
VENUE_BINANCE: Venue
MARKET_UNSPECIFIED: Market
MARKET_SPOT: Market
MARKET_USD_M_PERPETUAL: Market
STREAM_UNSPECIFIED: Stream
STREAM_DIFF_DEPTH: Stream
STREAM_AGG_TRADE: Stream
STREAM_BOOK_TICKER: Stream
STREAM_DEPTH_SNAPSHOT: Stream
QUALITY_FLAG_UNSPECIFIED: QualityFlag
QUALITY_FLAG_DUPLICATE: QualityFlag
QUALITY_FLAG_OUT_OF_ORDER: QualityFlag
QUALITY_FLAG_SEQUENCE_GAP: QualityFlag
QUALITY_FLAG_ORDERBOOK_RESYNC: QualityFlag
QUALITY_FLAG_SNAPSHOT_BRIDGE_PENDING: QualityFlag
QUALITY_FLAG_SNAPSHOT_TOO_OLD: QualityFlag
QUALITY_FLAG_BOOTSTRAP_BUFFER_OVERFLOW: QualityFlag
QUALITY_FLAG_RECOVERED_TAIL: QualityFlag
QUALITY_FLAG_MALFORMED_PAYLOAD: QualityFlag
QUALITY_FLAG_EXCHANGE_TIME_MISSING: QualityFlag
QUALITY_FLAG_RECEIVE_CLOCK_DISCONTINUITY: QualityFlag
QUALITY_FLAG_SLOW_CONSUMER_GAP: QualityFlag
QUALITY_FLAG_PRODUCER_RESTART: QualityFlag
QUALITY_FLAG_OVERLAP: QualityFlag
QUALITY_FLAG_IDENTITY_CONFLICT: QualityFlag
QUALITY_FLAG_CROSSED_BOOK: QualityFlag
REASON_CODE_UNSPECIFIED: ReasonCode
REASON_CODE_CONNECTION_LOST: ReasonCode
REASON_CODE_CONNECTION_RESUMED: ReasonCode
REASON_CODE_PING_TIMEOUT: ReasonCode
REASON_CODE_LAST_MESSAGE_AGE_HIGH: ReasonCode
REASON_CODE_RECEIVE_LATENCY_HIGH: ReasonCode
REASON_CODE_PUBLISH_LATENCY_HIGH: ReasonCode
REASON_CODE_SEQUENCE_GAP_DETECTED: ReasonCode
REASON_CODE_SEQUENCE_GAP_TOO_LARGE: ReasonCode
REASON_CODE_RESYNC_IN_PROGRESS: ReasonCode
REASON_CODE_RESYNC_FAILED: ReasonCode
REASON_CODE_BOOK_NOT_SYNCHRONIZED: ReasonCode
REASON_CODE_BOOK_CROSSED: ReasonCode
REASON_CODE_BOOK_EMPTY: ReasonCode
REASON_CODE_RECORDER_STALLED: ReasonCode
REASON_CODE_GATEWAY_STALLED: ReasonCode
REASON_CODE_DIVERGENCE_DETECTED: ReasonCode
REASON_CODE_DISK_SPACE_LOW: ReasonCode
REASON_CODE_QUEUE_BACKLOG: ReasonCode
REASON_CODE_ARCHIVE_BACKLOG: ReasonCode
REASON_CODE_CONFIGURATION_ERROR: ReasonCode
CONNECTION_STATE_UNSPECIFIED: ConnectionState
CONNECTION_STATE_CONNECTING: ConnectionState
CONNECTION_STATE_CONNECTED: ConnectionState
CONNECTION_STATE_RECONNECTING: ConnectionState
CONNECTION_STATE_DISCONNECTED: ConnectionState
CONNECTION_STATE_FAILED: ConnectionState
RESYNC_STATE_UNSPECIFIED: ResyncState
RESYNC_STATE_SYNCHRONIZED: ResyncState
RESYNC_STATE_RESYNC_REQUIRED: ResyncState
RESYNC_STATE_RESYNC_IN_PROGRESS: ResyncState
RESYNC_STATE_RECOVERED: ResyncState
RESYNC_STATE_RESYNC_FAILED: ResyncState
SNAPSHOT_SOURCE_UNSPECIFIED: SnapshotSource
SNAPSHOT_SOURCE_GATEWAY_LIVE: SnapshotSource
SNAPSHOT_SOURCE_RECORDER_REPLAY: SnapshotSource
SNAPSHOT_SOURCE_HISTORY_REPLAY: SnapshotSource
DELIVERY_MODE_UNSPECIFIED: DeliveryMode
DELIVERY_MODE_CONTIGUOUS_EVENTS: DeliveryMode
DELIVERY_MODE_LATEST_STATE: DeliveryMode
INITIAL_SNAPSHOT_MODE_UNSPECIFIED: InitialSnapshotMode
INITIAL_SNAPSHOT_MODE_NONE: InitialSnapshotMode
INITIAL_SNAPSHOT_MODE_REQUIRED: InitialSnapshotMode
CONSUMER_GAP_REASON_UNSPECIFIED: ConsumerGapReason
CONSUMER_GAP_REASON_SLOW_CONSUMER: ConsumerGapReason
CONSUMER_GAP_REASON_RESUME_NOT_AVAILABLE: ConsumerGapReason
CONSUMER_GAP_REASON_UPSTREAM_SEQUENCE_GAP: ConsumerGapReason
CONSUMER_GAP_REASON_GATEWAY_RESTART: ConsumerGapReason
CONSUMER_GAP_REASON_CONNECTION_GENERATION_CHANGED: ConsumerGapReason
CONSUMER_GAP_REASON_SUBSCRIPTION_RECONFIGURED: ConsumerGapReason
RECOVERY_ACTION_UNSPECIFIED: RecoveryAction
RECOVERY_ACTION_NONE: RecoveryAction
RECOVERY_ACTION_RESUBSCRIBE: RecoveryAction
RECOVERY_ACTION_REQUEST_NEW_SNAPSHOT: RecoveryAction
STREAM_LIFECYCLE_STATE_UNSPECIFIED: StreamLifecycleState
STREAM_LIFECYCLE_STATE_ACCEPTED: StreamLifecycleState
STREAM_LIFECYCLE_STATE_SNAPSHOT_PENDING: StreamLifecycleState
STREAM_LIFECYCLE_STATE_LIVE: StreamLifecycleState
STREAM_LIFECYCLE_STATE_RESYNC_IN_PROGRESS: StreamLifecycleState
STREAM_LIFECYCLE_STATE_DEGRADED: StreamLifecycleState
STREAM_LIFECYCLE_STATE_CLOSING: StreamLifecycleState
STREAM_LIFECYCLE_STATE_CLOSED: StreamLifecycleState
HEALTH_STATE_UNSPECIFIED: HealthState
HEALTH_STATE_HEALTHY: HealthState
HEALTH_STATE_DEGRADED: HealthState
HEALTH_STATE_UNRELIABLE: HealthState
HEALTH_STATE_UNAVAILABLE: HealthState
