from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PriceLevel(_message.Message):
    __slots__ = ("price", "quantity")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    price: str
    quantity: str
    def __init__(self, price: _Optional[str] = ..., quantity: _Optional[str] = ...) -> None: ...

class EventMetadata(_message.Message):
    __slots__ = ("venue", "market", "symbol", "producer", "producer_version", "connection_id", "stream", "schema_version", "exchange_event_time_ms", "exchange_trade_time_ms", "exchange_transaction_time_ms", "receive_time_utc_ns", "receive_monotonic_ns", "quality_flags")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_VERSION_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_EVENT_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_TRADE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_TRANSACTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_MONOTONIC_NS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    producer: str
    producer_version: str
    connection_id: str
    stream: _enums_pb2.Stream
    schema_version: str
    exchange_event_time_ms: int
    exchange_trade_time_ms: int
    exchange_transaction_time_ms: int
    receive_time_utc_ns: int
    receive_monotonic_ns: int
    quality_flags: _containers.RepeatedScalarFieldContainer[_enums_pb2.QualityFlag]
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., producer: _Optional[str] = ..., producer_version: _Optional[str] = ..., connection_id: _Optional[str] = ..., stream: _Optional[_Union[_enums_pb2.Stream, str]] = ..., schema_version: _Optional[str] = ..., exchange_event_time_ms: _Optional[int] = ..., exchange_trade_time_ms: _Optional[int] = ..., exchange_transaction_time_ms: _Optional[int] = ..., receive_time_utc_ns: _Optional[int] = ..., receive_monotonic_ns: _Optional[int] = ..., quality_flags: _Optional[_Iterable[_Union[_enums_pb2.QualityFlag, str]]] = ...) -> None: ...

class EnvelopeMetadata(_message.Message):
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
