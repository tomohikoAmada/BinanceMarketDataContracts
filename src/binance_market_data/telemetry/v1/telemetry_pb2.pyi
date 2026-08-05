from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TelemetryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TELEMETRY_TYPE_UNSPECIFIED: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_CONNECTION: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_SEQUENCE: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_LATENCY: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_QUEUE: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_BOOK: _ClassVar[TelemetryType]
    TELEMETRY_TYPE_SYSTEM: _ClassVar[TelemetryType]
TELEMETRY_TYPE_UNSPECIFIED: TelemetryType
TELEMETRY_TYPE_CONNECTION: TelemetryType
TELEMETRY_TYPE_SEQUENCE: TelemetryType
TELEMETRY_TYPE_LATENCY: TelemetryType
TELEMETRY_TYPE_QUEUE: TelemetryType
TELEMETRY_TYPE_BOOK: TelemetryType
TELEMETRY_TYPE_SYSTEM: TelemetryType

class ConnectionMetrics(_message.Message):
    __slots__ = ("connected", "last_message_age_ms", "reconnect_count")
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_AGE_MS_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    connected: bool
    last_message_age_ms: int
    reconnect_count: int
    def __init__(self, connected: _Optional[bool] = ..., last_message_age_ms: _Optional[int] = ..., reconnect_count: _Optional[int] = ...) -> None: ...

class SequenceMetrics(_message.Message):
    __slots__ = ("last_update_id", "duplicate_count", "out_of_order_count")
    LAST_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    DUPLICATE_COUNT_FIELD_NUMBER: _ClassVar[int]
    OUT_OF_ORDER_COUNT_FIELD_NUMBER: _ClassVar[int]
    last_update_id: int
    duplicate_count: int
    out_of_order_count: int
    def __init__(self, last_update_id: _Optional[int] = ..., duplicate_count: _Optional[int] = ..., out_of_order_count: _Optional[int] = ...) -> None: ...

class LatencyMetrics(_message.Message):
    __slots__ = ("receive_lag_ms", "publish_lag_ms", "consumer_delivery_lag_ms")
    RECEIVE_LAG_MS_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_LAG_MS_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_DELIVERY_LAG_MS_FIELD_NUMBER: _ClassVar[int]
    receive_lag_ms: int
    publish_lag_ms: int
    consumer_delivery_lag_ms: int
    def __init__(self, receive_lag_ms: _Optional[int] = ..., publish_lag_ms: _Optional[int] = ..., consumer_delivery_lag_ms: _Optional[int] = ...) -> None: ...

class QueueMetrics(_message.Message):
    __slots__ = ("queue_depth", "queue_capacity", "queue_utilization", "oldest_message_age_ms", "dropped", "disconnect_count")
    QUEUE_DEPTH_FIELD_NUMBER: _ClassVar[int]
    QUEUE_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    QUEUE_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    OLDEST_MESSAGE_AGE_MS_FIELD_NUMBER: _ClassVar[int]
    DROPPED_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    queue_depth: int
    queue_capacity: int
    queue_utilization: float
    oldest_message_age_ms: int
    dropped: int
    disconnect_count: int
    def __init__(self, queue_depth: _Optional[int] = ..., queue_capacity: _Optional[int] = ..., queue_utilization: _Optional[float] = ..., oldest_message_age_ms: _Optional[int] = ..., dropped: _Optional[int] = ..., disconnect_count: _Optional[int] = ...) -> None: ...

class BookMetrics(_message.Message):
    __slots__ = ("synchronized", "sync_latency_ms")
    SYNCHRONIZED_FIELD_NUMBER: _ClassVar[int]
    SYNC_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    synchronized: bool
    sync_latency_ms: int
    def __init__(self, synchronized: _Optional[bool] = ..., sync_latency_ms: _Optional[int] = ...) -> None: ...

class SystemMetrics(_message.Message):
    __slots__ = ("cpu_percent", "memory_mb", "disk_free_gb")
    CPU_PERCENT_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    DISK_FREE_GB_FIELD_NUMBER: _ClassVar[int]
    cpu_percent: float
    memory_mb: float
    disk_free_gb: float
    def __init__(self, cpu_percent: _Optional[float] = ..., memory_mb: _Optional[float] = ..., disk_free_gb: _Optional[float] = ...) -> None: ...

class TelemetryEnvelope(_message.Message):
    __slots__ = ("schema_version", "telemetry_type", "source_module", "source_instance_id", "observed_time_utc_ns", "market", "symbol", "connection", "sequence", "latency", "queue", "book", "system", "quality_flags", "stream", "connection_id", "connection_generation", "subscription_id")
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    TELEMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_MODULE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    LATENCY_FIELD_NUMBER: _ClassVar[int]
    QUEUE_FIELD_NUMBER: _ClassVar[int]
    BOOK_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_GENERATION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    schema_version: str
    telemetry_type: TelemetryType
    source_module: str
    source_instance_id: str
    observed_time_utc_ns: int
    market: _enums_pb2.Market
    symbol: str
    connection: ConnectionMetrics
    sequence: SequenceMetrics
    latency: LatencyMetrics
    queue: QueueMetrics
    book: BookMetrics
    system: SystemMetrics
    quality_flags: _containers.RepeatedScalarFieldContainer[_enums_pb2.QualityFlag]
    stream: _enums_pb2.Stream
    connection_id: str
    connection_generation: int
    subscription_id: str
    def __init__(self, schema_version: _Optional[str] = ..., telemetry_type: _Optional[_Union[TelemetryType, str]] = ..., source_module: _Optional[str] = ..., source_instance_id: _Optional[str] = ..., observed_time_utc_ns: _Optional[int] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., connection: _Optional[_Union[ConnectionMetrics, _Mapping]] = ..., sequence: _Optional[_Union[SequenceMetrics, _Mapping]] = ..., latency: _Optional[_Union[LatencyMetrics, _Mapping]] = ..., queue: _Optional[_Union[QueueMetrics, _Mapping]] = ..., book: _Optional[_Union[BookMetrics, _Mapping]] = ..., system: _Optional[_Union[SystemMetrics, _Mapping]] = ..., quality_flags: _Optional[_Iterable[_Union[_enums_pb2.QualityFlag, str]]] = ..., stream: _Optional[_Union[_enums_pb2.Stream, str]] = ..., connection_id: _Optional[str] = ..., connection_generation: _Optional[int] = ..., subscription_id: _Optional[str] = ...) -> None: ...
