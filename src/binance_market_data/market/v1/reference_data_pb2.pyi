from binance_market_data.common.v1 import enums_pb2 as _enums_pb2
from binance_market_data.market.v1 import market_events_pb2 as _market_events_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReferenceObservation(_message.Message):
    __slots__ = ("venue", "market", "symbol", "request_id", "source_kind", "receive_time_utc_ns", "source_time_ms", "status", "error_code", "schema_version", "open_interest", "top_long_short_account_ratio", "top_long_short_position_ratio", "global_long_short_account_ratio", "taker_buy_sell_volume", "instrument", "depth_baseline")
    VENUE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_KIND_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_TIME_UTC_NS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    TOP_LONG_SHORT_ACCOUNT_RATIO_FIELD_NUMBER: _ClassVar[int]
    TOP_LONG_SHORT_POSITION_RATIO_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_LONG_SHORT_ACCOUNT_RATIO_FIELD_NUMBER: _ClassVar[int]
    TAKER_BUY_SELL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_BASELINE_FIELD_NUMBER: _ClassVar[int]
    venue: _enums_pb2.Venue
    market: _enums_pb2.Market
    symbol: str
    request_id: str
    source_kind: _enums_pb2.ReferenceSourceKind
    receive_time_utc_ns: int
    source_time_ms: int
    status: _enums_pb2.ReferenceObservationStatus
    error_code: str
    schema_version: str
    open_interest: OpenInterest
    top_long_short_account_ratio: LongShortRatio
    top_long_short_position_ratio: LongShortRatio
    global_long_short_account_ratio: LongShortRatio
    taker_buy_sell_volume: TakerBuySellVolume
    instrument: InstrumentReference
    depth_baseline: _market_events_pb2.ExchangeDepthSnapshot
    def __init__(self, venue: _Optional[_Union[_enums_pb2.Venue, str]] = ..., market: _Optional[_Union[_enums_pb2.Market, str]] = ..., symbol: _Optional[str] = ..., request_id: _Optional[str] = ..., source_kind: _Optional[_Union[_enums_pb2.ReferenceSourceKind, str]] = ..., receive_time_utc_ns: _Optional[int] = ..., source_time_ms: _Optional[int] = ..., status: _Optional[_Union[_enums_pb2.ReferenceObservationStatus, str]] = ..., error_code: _Optional[str] = ..., schema_version: _Optional[str] = ..., open_interest: _Optional[_Union[OpenInterest, _Mapping]] = ..., top_long_short_account_ratio: _Optional[_Union[LongShortRatio, _Mapping]] = ..., top_long_short_position_ratio: _Optional[_Union[LongShortRatio, _Mapping]] = ..., global_long_short_account_ratio: _Optional[_Union[LongShortRatio, _Mapping]] = ..., taker_buy_sell_volume: _Optional[_Union[TakerBuySellVolume, _Mapping]] = ..., instrument: _Optional[_Union[InstrumentReference, _Mapping]] = ..., depth_baseline: _Optional[_Union[_market_events_pb2.ExchangeDepthSnapshot, _Mapping]] = ...) -> None: ...

class OpenInterest(_message.Message):
    __slots__ = ("open_interest", "source_time_ms")
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    open_interest: str
    source_time_ms: int
    def __init__(self, open_interest: _Optional[str] = ..., source_time_ms: _Optional[int] = ...) -> None: ...

class LongShortRatio(_message.Message):
    __slots__ = ("long_short_ratio", "long_account", "short_account", "source_time_ms", "period")
    LONG_SHORT_RATIO_FIELD_NUMBER: _ClassVar[int]
    LONG_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    SHORT_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    long_short_ratio: str
    long_account: str
    short_account: str
    source_time_ms: int
    period: str
    def __init__(self, long_short_ratio: _Optional[str] = ..., long_account: _Optional[str] = ..., short_account: _Optional[str] = ..., source_time_ms: _Optional[int] = ..., period: _Optional[str] = ...) -> None: ...

class TakerBuySellVolume(_message.Message):
    __slots__ = ("buy_sell_ratio", "buy_volume", "sell_volume", "source_time_ms", "period")
    BUY_SELL_RATIO_FIELD_NUMBER: _ClassVar[int]
    BUY_VOLUME_FIELD_NUMBER: _ClassVar[int]
    SELL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    buy_sell_ratio: str
    buy_volume: str
    sell_volume: str
    source_time_ms: int
    period: str
    def __init__(self, buy_sell_ratio: _Optional[str] = ..., buy_volume: _Optional[str] = ..., sell_volume: _Optional[str] = ..., source_time_ms: _Optional[int] = ..., period: _Optional[str] = ...) -> None: ...

class InstrumentFilter(_message.Message):
    __slots__ = ("filter_type", "price", "quantity", "notional", "limit", "min_price", "max_price", "tick_size", "min_quantity", "max_quantity", "step_size", "multiplier_up", "multiplier_down", "multiplier_decimal", "position_control_side")
    FILTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    NOTIONAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    MIN_PRICE_FIELD_NUMBER: _ClassVar[int]
    MAX_PRICE_FIELD_NUMBER: _ClassVar[int]
    TICK_SIZE_FIELD_NUMBER: _ClassVar[int]
    MIN_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    MAX_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STEP_SIZE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_UP_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_DOWN_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_DECIMAL_FIELD_NUMBER: _ClassVar[int]
    POSITION_CONTROL_SIDE_FIELD_NUMBER: _ClassVar[int]
    filter_type: str
    price: str
    quantity: str
    notional: str
    limit: int
    min_price: str
    max_price: str
    tick_size: str
    min_quantity: str
    max_quantity: str
    step_size: str
    multiplier_up: str
    multiplier_down: str
    multiplier_decimal: str
    position_control_side: str
    def __init__(self, filter_type: _Optional[str] = ..., price: _Optional[str] = ..., quantity: _Optional[str] = ..., notional: _Optional[str] = ..., limit: _Optional[int] = ..., min_price: _Optional[str] = ..., max_price: _Optional[str] = ..., tick_size: _Optional[str] = ..., min_quantity: _Optional[str] = ..., max_quantity: _Optional[str] = ..., step_size: _Optional[str] = ..., multiplier_up: _Optional[str] = ..., multiplier_down: _Optional[str] = ..., multiplier_decimal: _Optional[str] = ..., position_control_side: _Optional[str] = ...) -> None: ...

class RateLimit(_message.Message):
    __slots__ = ("rate_limit_type", "interval", "interval_num", "limit")
    RATE_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_NUM_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    rate_limit_type: str
    interval: str
    interval_num: int
    limit: int
    def __init__(self, rate_limit_type: _Optional[str] = ..., interval: _Optional[str] = ..., interval_num: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class InstrumentReference(_message.Message):
    __slots__ = ("symbol_present", "contract_type", "trading_status", "base_asset", "quote_asset", "margin_asset", "price_precision", "quantity_precision", "onboard_time_ms", "delivery_time_ms", "filters", "rate_limits", "server_time_ms")
    SYMBOL_PRESENT_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRADING_STATUS_FIELD_NUMBER: _ClassVar[int]
    BASE_ASSET_FIELD_NUMBER: _ClassVar[int]
    QUOTE_ASSET_FIELD_NUMBER: _ClassVar[int]
    MARGIN_ASSET_FIELD_NUMBER: _ClassVar[int]
    PRICE_PRECISION_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_PRECISION_FIELD_NUMBER: _ClassVar[int]
    ONBOARD_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    SERVER_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    symbol_present: bool
    contract_type: str
    trading_status: str
    base_asset: str
    quote_asset: str
    margin_asset: str
    price_precision: int
    quantity_precision: int
    onboard_time_ms: int
    delivery_time_ms: int
    filters: _containers.RepeatedCompositeFieldContainer[InstrumentFilter]
    rate_limits: _containers.RepeatedCompositeFieldContainer[RateLimit]
    server_time_ms: int
    def __init__(self, symbol_present: _Optional[bool] = ..., contract_type: _Optional[str] = ..., trading_status: _Optional[str] = ..., base_asset: _Optional[str] = ..., quote_asset: _Optional[str] = ..., margin_asset: _Optional[str] = ..., price_precision: _Optional[int] = ..., quantity_precision: _Optional[int] = ..., onboard_time_ms: _Optional[int] = ..., delivery_time_ms: _Optional[int] = ..., filters: _Optional[_Iterable[_Union[InstrumentFilter, _Mapping]]] = ..., rate_limits: _Optional[_Iterable[_Union[RateLimit, _Mapping]]] = ..., server_time_ms: _Optional[int] = ...) -> None: ...
