from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from binance_market_data.common.v1 import metadata_pb2 as _metadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DepthUpdate(_message.Message):
    __slots__ = ("metadata", "first_update_id", "final_update_id", "previous_final_update_id", "bids", "asks")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FIRST_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FINAL_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    ASKS_FIELD_NUMBER: _ClassVar[int]
    metadata: _metadata_pb2.EventMetadata
    first_update_id: int
    final_update_id: int
    previous_final_update_id: int
    bids: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    asks: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    def __init__(self, metadata: _Optional[_Union[_metadata_pb2.EventMetadata, _Mapping]] = ..., first_update_id: _Optional[int] = ..., final_update_id: _Optional[int] = ..., previous_final_update_id: _Optional[int] = ..., bids: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., asks: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ...) -> None: ...

class AggTrade(_message.Message):
    __slots__ = ("metadata", "aggregate_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "trade_time_ms", "buyer_is_maker")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AGGREGATE_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FIRST_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    BUYER_IS_MAKER_FIELD_NUMBER: _ClassVar[int]
    metadata: _metadata_pb2.EventMetadata
    aggregate_trade_id: int
    price: str
    quantity: str
    first_trade_id: int
    last_trade_id: int
    trade_time_ms: int
    buyer_is_maker: bool
    def __init__(self, metadata: _Optional[_Union[_metadata_pb2.EventMetadata, _Mapping]] = ..., aggregate_trade_id: _Optional[int] = ..., price: _Optional[str] = ..., quantity: _Optional[str] = ..., first_trade_id: _Optional[int] = ..., last_trade_id: _Optional[int] = ..., trade_time_ms: _Optional[int] = ..., buyer_is_maker: _Optional[bool] = ...) -> None: ...

class BookTicker(_message.Message):
    __slots__ = ("metadata", "update_id", "best_bid_price", "best_bid_quantity", "best_ask_price", "best_ask_quantity")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    metadata: _metadata_pb2.EventMetadata
    update_id: int
    best_bid_price: str
    best_bid_quantity: str
    best_ask_price: str
    best_ask_quantity: str
    def __init__(self, metadata: _Optional[_Union[_metadata_pb2.EventMetadata, _Mapping]] = ..., update_id: _Optional[int] = ..., best_bid_price: _Optional[str] = ..., best_bid_quantity: _Optional[str] = ..., best_ask_price: _Optional[str] = ..., best_ask_quantity: _Optional[str] = ...) -> None: ...

class ExchangeDepthSnapshot(_message.Message):
    __slots__ = ("venue", "market", "symbol", "schema_version", "producer", "producer_version", "request_id", "last_update_id", "bids", "asks", "exchange_transaction_time_ms", "receive_time_utc_ns", "receive_monotonic_ns", "quality_flags")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_ID_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    ASKS_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_TRANSACTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_MONOTONIC_NS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    schema_version: str
    producer: str
    producer_version: str
    request_id: str
    last_update_id: int
    bids: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    asks: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.PriceLevel]
    exchange_transaction_time_ms: int
    receive_time_utc_ns: int
    receive_monotonic_ns: int
    quality_flags: _containers.RepeatedScalarFieldContainer[_enums_pb2.QualityFlag]
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., schema_version: _Optional[str] = ..., producer: _Optional[str] = ..., producer_version: _Optional[str] = ..., request_id: _Optional[str] = ..., last_update_id: _Optional[int] = ..., bids: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., asks: _Optional[_Iterable[_Union[_metadata_pb2.PriceLevel, _Mapping]]] = ..., exchange_transaction_time_ms: _Optional[int] = ..., receive_time_utc_ns: _Optional[int] = ..., receive_monotonic_ns: _Optional[int] = ..., quality_flags: _Optional[_Iterable[_Union[_enums_pb2.QualityFlag, str]]] = ...) -> None: ...
