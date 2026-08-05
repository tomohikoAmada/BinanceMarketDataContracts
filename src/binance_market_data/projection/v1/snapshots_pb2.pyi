from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from binance_market_data.common.v1 import metadata_pb2 as _metadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GapDescriptor(_message.Message):
    __slots__ = ("stream", "detected_at_utc_ns", "previous_sequence", "next_sequence", "reason_code", "recovery_state")
    STREAM_FIELD_NUMBER: _ClassVar[int]
    DETECTED_AT_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NEXT_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REASON_CODE_FIELD_NUMBER: _ClassVar[int]
    RECOVERY_STATE_FIELD_NUMBER: _ClassVar[int]
    stream: _enums_pb2.Stream
    detected_at_utc_ns: int
    previous_sequence: int
    next_sequence: int
    reason_code: _enums_pb2.ReasonCode
    recovery_state: _enums_pb2.ResyncState
    def __init__(self, stream: _Optional[_Union[_enums_pb2.Stream, str]] = ..., detected_at_utc_ns: _Optional[int] = ..., previous_sequence: _Optional[int] = ..., next_sequence: _Optional[int] = ..., reason_code: _Optional[_Union[_enums_pb2.ReasonCode, str]] = ..., recovery_state: _Optional[_Union[_enums_pb2.ResyncState, str]] = ...) -> None: ...

class LocalOrderBookSnapshot(_message.Message):
    __slots__ = ("venue", "market", "symbol", "schema_version", "producer", "producer_version", "source", "last_update_id", "bids", "asks", "depth_limit", "generated_time_utc_ns", "generated_monotonic_ns", "synchronized", "last_gap", "quality_flags")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    ASKS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_MONOTONIC_NS_FIELD_NUMBER: _ClassVar[int]
    SYNCHRONIZED_FIELD_NUMBER: _ClassVar[int]
    LAST_GAP_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    schema_version: str
    producer: str
    producer_version: str
    source: _enums_pb2.SnapshotSource
    last_update_id: int
    bids: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    asks: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    depth_limit: int
    generated_time_utc_ns: int
    generated_monotonic_ns: int
    synchronized: bool
    last_gap: GapDescriptor
    quality_flags: _containers.RepeatedScalarFieldContainer[_enums_pb2.QualityFlag]
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., schema_version: _Optional[str] = ..., producer: _Optional[str] = ..., producer_version: _Optional[str] = ..., source: _Optional[_Union[_enums_pb2.SnapshotSource, str]] = ..., last_update_id: _Optional[int] = ..., bids: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., asks: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., depth_limit: _Optional[int] = ..., generated_time_utc_ns: _Optional[int] = ..., generated_monotonic_ns: _Optional[int] = ..., synchronized: _Optional[bool] = ..., last_gap: _Optional[_Union[GapDescriptor, _Mapping]] = ..., quality_flags: _Optional[_Iterable[_Union[_enums_pb2.QualityFlag, str]]] = ...) -> None: ...

class MarketStateSnapshot(_message.Message):
    __slots__ = ("venue", "market", "symbol", "schema_version", "producer", "producer_version", "best_bid_price", "best_bid_quantity", "best_ask_price", "best_ask_quantity", "mid_price", "spread", "microprice", "top_bids", "top_asks", "depth_limit", "mark_price", "index_price", "funding_rate", "next_funding_time_ms", "open_interest", "generated_time_utc_ns", "data_freshness_ms", "book_synchronized", "source_book_update_id", "source_trade_id")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_VERSION_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    MID_PRICE_FIELD_NUMBER: _ClassVar[int]
    SPREAD_FIELD_NUMBER: _ClassVar[int]
    MICROPRICE_FIELD_NUMBER: _ClassVar[int]
    TOP_BIDS_FIELD_NUMBER: _ClassVar[int]
    TOP_ASKS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    MARK_PRICE_FIELD_NUMBER: _ClassVar[int]
    INDEX_PRICE_FIELD_NUMBER: _ClassVar[int]
    FUNDING_RATE_FIELD_NUMBER: _ClassVar[int]
    NEXT_FUNDING_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    GENERATED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    DATA_FRESHNESS_MS_FIELD_NUMBER: _ClassVar[int]
    BOOK_SYNCHRONIZED_FIELD_NUMBER: _ClassVar[int]
    SOURCE_BOOK_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    schema_version: str
    producer: str
    producer_version: str
    best_bid_price: str
    best_bid_quantity: str
    best_ask_price: str
    best_ask_quantity: str
    mid_price: str
    spread: str
    microprice: str
    top_bids: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    top_asks: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    depth_limit: int
    mark_price: str
    index_price: str
    funding_rate: str
    next_funding_time_ms: int
    open_interest: str
    generated_time_utc_ns: int
    data_freshness_ms: int
    book_synchronized: bool
    source_book_update_id: int
    source_trade_id: int
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., schema_version: _Optional[str] = ..., producer: _Optional[str] = ..., producer_version: _Optional[str] = ..., best_bid_price: _Optional[str] = ..., best_bid_quantity: _Optional[str] = ..., best_ask_price: _Optional[str] = ..., best_ask_quantity: _Optional[str] = ..., mid_price: _Optional[str] = ..., spread: _Optional[str] = ..., microprice: _Optional[str] = ..., top_bids: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., top_asks: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., depth_limit: _Optional[int] = ..., mark_price: _Optional[str] = ..., index_price: _Optional[str] = ..., funding_rate: _Optional[str] = ..., next_funding_time_ms: _Optional[int] = ..., open_interest: _Optional[str] = ..., generated_time_utc_ns: _Optional[int] = ..., data_freshness_ms: _Optional[int] = ..., book_synchronized: _Optional[bool] = ..., source_book_update_id: _Optional[int] = ..., source_trade_id: _Optional[int] = ...) -> None: ...

class LatencySummary(_message.Message):
    __slots__ = ("count", "min_ms", "max_ms", "p50_ms", "p95_ms", "p99_ms", "window_start_utc_ns", "window_end_utc_ns")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    MIN_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_MS_FIELD_NUMBER: _ClassVar[int]
    P50_MS_FIELD_NUMBER: _ClassVar[int]
    P95_MS_FIELD_NUMBER: _ClassVar[int]
    P99_MS_FIELD_NUMBER: _ClassVar[int]
    WINDOW_START_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    WINDOW_END_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    count: int
    min_ms: float
    max_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    window_start_utc_ns: int
    window_end_utc_ns: int
    def __init__(self, count: _Optional[int] = ..., min_ms: _Optional[float] = ..., max_ms: _Optional[float] = ..., p50_ms: _Optional[float] = ..., p95_ms: _Optional[float] = ..., p99_ms: _Optional[float] = ..., window_start_utc_ns: _Optional[int] = ..., window_end_utc_ns: _Optional[int] = ...) -> None: ...

class DataHealthSnapshot(_message.Message):
    __slots__ = ("health_snapshot_id", "overall_state", "venue", "market", "symbol", "schema_version", "producer", "producer_version", "source_instance_id", "stream", "connection_state", "last_message_age_ms", "receive_latency", "publish_latency", "sequence_gap_count", "resync_state", "book_synchronized", "recorder_alive", "gateway_alive", "reason_codes", "observed_time_utc_ns", "quality_flags", "consumer_delivery_latency")
    HEALTH_SNAPSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    OVERALL_STATE_FIELD_NUMBER: _ClassVar[int]
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_AGE_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_LATENCY_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_LATENCY_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_GAP_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESYNC_STATE_FIELD_NUMBER: _ClassVar[int]
    BOOK_SYNCHRONIZED_FIELD_NUMBER: _ClassVar[int]
    RECORDER_ALIVE_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ALIVE_FIELD_NUMBER: _ClassVar[int]
    REASON_CODES_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_DELIVERY_LATENCY_FIELD_NUMBER: _ClassVar[int]
    health_snapshot_id: str
    overall_state: _enums_pb2.HealthState
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    schema_version: str
    producer: str
    producer_version: str
    source_instance_id: str
    stream: _enums_pb2.Stream
    connection_state: _enums_pb2.ConnectionState
    last_message_age_ms: int
    receive_latency: LatencySummary
    publish_latency: LatencySummary
    sequence_gap_count: int
    resync_state: _enums_pb2.ResyncState
    book_synchronized: bool
    recorder_alive: bool
    gateway_alive: bool
    reason_codes: _containers.RepeatedScalarFieldContainer[_enums_pb2.ReasonCode]
    observed_time_utc_ns: int
    quality_flags: _containers.RepeatedScalarFieldContainer[_enums_pb2.QualityFlag]
    consumer_delivery_latency: LatencySummary
    def __init__(self, health_snapshot_id: _Optional[str] = ..., overall_state: _Optional[_Union[_enums_pb2.HealthState, str]] = ..., venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., schema_version: _Optional[str] = ..., producer: _Optional[str] = ..., producer_version: _Optional[str] = ..., source_instance_id: _Optional[str] = ..., stream: _Optional[_Union[_enums_pb2.Stream, str]] = ..., connection_state: _Optional[_Union[_enums_pb2.ConnectionState, str]] = ..., last_message_age_ms: _Optional[int] = ..., receive_latency: _Optional[_Union[LatencySummary, _Mapping]] = ..., publish_latency: _Optional[_Union[LatencySummary, _Mapping]] = ..., sequence_gap_count: _Optional[int] = ..., resync_state: _Optional[_Union[_enums_pb2.ResyncState, str]] = ..., book_synchronized: _Optional[bool] = ..., recorder_alive: _Optional[bool] = ..., gateway_alive: _Optional[bool] = ..., reason_codes: _Optional[_Iterable[_Union[_enums_pb2.ReasonCode, str]]] = ..., observed_time_utc_ns: _Optional[int] = ..., quality_flags: _Optional[_Iterable[_Union[_enums_pb2.QualityFlag, str]]] = ..., consumer_delivery_latency: _Optional[_Union[LatencySummary, _Mapping]] = ...) -> None: ...
