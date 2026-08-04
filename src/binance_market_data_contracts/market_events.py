"""Core Binance market event contracts.

Defines base event metadata and specific metadata per event type.
Each event type fixes its stream and schema_version via Literal.

All events use nested metadata — changing to flat fields is a BREAKING change.
All collections use tuples for deep immutability.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import (
    ContractModel,
    NonEmptyText,
    PositiveQuantityString,
    PriceString,
    QuantityString,
)
from binance_market_data_contracts.enums import Market, QualityFlag, Stream, Venue
from binance_market_data_contracts.identifiers import ConnectionId, Symbol


class BaseEventMetadata(ContractModel):
    """Base metadata fields shared by all market events.

    Concrete event types use specific metadata subclasses that fix
    stream and schema_version via Literal.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    producer: NonEmptyText
    producer_version: NonEmptyText
    connection_id: ConnectionId
    exchange_event_time_ms: int | None = Field(default=None, ge=0)
    exchange_trade_time_ms: int | None = Field(default=None, ge=0)
    exchange_transaction_time_ms: int | None = Field(default=None, ge=0)
    receive_time_utc_ns: int | None = Field(default=None, ge=0)
    receive_monotonic_ns: int | None = Field(default=None, ge=0)
    quality_flags: tuple[QualityFlag, ...] = ()


class DepthUpdateMetadata(BaseEventMetadata):
    """Metadata specific to DepthUpdate events."""

    stream: Literal[Stream.DIFF_DEPTH] = Stream.DIFF_DEPTH
    schema_version: Literal["depth-update.v1"] = "depth-update.v1"


class AggTradeMetadata(BaseEventMetadata):
    """Metadata specific to AggTrade events."""

    stream: Literal[Stream.AGG_TRADE] = Stream.AGG_TRADE
    schema_version: Literal["agg-trade.v1"] = "agg-trade.v1"


class BookTickerMetadata(BaseEventMetadata):
    """Metadata specific to BookTicker events."""

    stream: Literal[Stream.BOOK_TICKER] = Stream.BOOK_TICKER
    schema_version: Literal["book-ticker.v1"] = "book-ticker.v1"


class PriceLevel(ContractModel):
    """A single price level in the order book.

    quantity represents the absolute quantity at this price level after the update.
    quantity == "0" means this price level should be removed.
    """

    price: PriceString
    quantity: QuantityString


class DepthUpdate(ContractModel):
    """Binance order book depth update.

    Uses DepthUpdateMetadata which fixes stream=DIFF_DEPTH and schema_version.
    """

    metadata: DepthUpdateMetadata
    first_update_id: int = Field(..., ge=0)
    final_update_id: int = Field(..., ge=0)
    previous_final_update_id: int | None = Field(default=None, ge=0)
    bids: tuple[PriceLevel, ...] = ()
    asks: tuple[PriceLevel, ...] = ()

    @model_validator(mode="after")
    def _validate_ids(self) -> DepthUpdate:
        if self.final_update_id < self.first_update_id:
            raise ValueError(
                f"final_update_id ({self.final_update_id}) must be >= first_update_id ({self.first_update_id})"
            )
        return self


class AggTrade(ContractModel):
    """Binance aggregated trade.

    Uses AggTradeMetadata which fixes stream=AGG_TRADE and schema_version.
    quantity MUST be > 0 (quantity="0" is not valid for trades).
    """

    metadata: AggTradeMetadata
    aggregate_trade_id: int = Field(..., ge=0)
    price: PriceString
    quantity: PositiveQuantityString = Field(..., description="Total quantity of the aggregate trade (> 0)")
    first_trade_id: int = Field(..., ge=0)
    last_trade_id: int = Field(..., ge=0)
    trade_time_ms: int = Field(..., ge=0)
    buyer_is_maker: bool

    @model_validator(mode="after")
    def _validate_trade_ids(self) -> AggTrade:
        if self.last_trade_id < self.first_trade_id:
            raise ValueError(f"last_trade_id ({self.last_trade_id}) must be >= first_trade_id ({self.first_trade_id})")
        return self


class BookTicker(ContractModel):
    """Binance book ticker — best bid and ask with quantities.

    Uses BookTickerMetadata which fixes stream=BOOK_TICKER and schema_version.
    Accepts crossed books (best_bid_price >= best_ask_price).
    Crossed state is reported by Health through QualityFlag.CROSSED_BOOK.
    """

    metadata: BookTickerMetadata
    update_id: int | None = Field(default=None, ge=0)
    best_bid_price: PriceString
    best_bid_quantity: QuantityString
    best_ask_price: PriceString
    best_ask_quantity: QuantityString
