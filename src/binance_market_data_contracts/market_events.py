"""Core Binance market event contracts.

Defines the standard event envelope (EventMetadata) and the primary
market data event types: DepthUpdate, AggTrade, BookTicker.

All events use nested metadata — changing to flat fields is a BREAKING change.
Each event restricts its metadata.stream to the correct value.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from binance_market_data_contracts.common import ContractModel, PriceString, QuantityString
from binance_market_data_contracts.enums import Market, QualityFlag, Stream, Venue
from binance_market_data_contracts.identifiers import ConnectionId, Symbol  # noqa: TC001


class EventMetadata(ContractModel):
    """Metadata envelope for all market events.

    All times use the unit-embedded naming convention.
    Missing exchange times use None, never 0.
    """

    venue: Venue
    market: Market
    symbol: Symbol
    stream: Stream
    producer: str = Field(..., description="Producer module name (e.g. 'recorder', 'gateway')")
    producer_version: str = Field(..., description="Producer module version")
    schema_version: str = Field(..., description="Contract version (e.g. 'depth-update.v1')")
    connection_id: ConnectionId = Field(..., description="Unique identifier for this connection session")
    exchange_event_time_ms: int | None = Field(
        default=None,
        description="Exchange-assigned event time in milliseconds",
        ge=0,
    )
    exchange_trade_time_ms: int | None = Field(
        default=None,
        description="Exchange-assigned trade time in milliseconds",
        ge=0,
    )
    exchange_transaction_time_ms: int | None = Field(
        default=None,
        description="Exchange-assigned transaction time in milliseconds",
        ge=0,
    )
    receive_time_utc_ns: int | None = Field(
        default=None,
        description="UTC wall clock receive time in nanoseconds",
        ge=0,
    )
    receive_monotonic_ns: int | None = Field(
        default=None,
        description="Monotonic clock receive time in nanoseconds",
        ge=0,
    )
    quality_flags: list[QualityFlag] = Field(
        default_factory=list,
        description="Quality flags describing observed data facts",
    )


class PriceLevel(ContractModel):
    """A single price level in the order book.

    quantity represents the absolute quantity at this price level after the update.
    quantity == "0" means this price level should be removed.
    """

    price: PriceString
    quantity: QuantityString


class DepthUpdate(ContractModel):
    """Binance order book depth update.

    Represents a diff depth event with bids and asks at updated price levels.
    The metadata.stream MUST be DIFF_DEPTH.
    """

    metadata: EventMetadata
    first_update_id: int = Field(..., ge=0, description="First update ID in this event")
    final_update_id: int = Field(..., ge=0, description="Final update ID in this event")
    previous_final_update_id: int | None = Field(
        default=None,
        ge=0,
        description="Previous final update ID (available in USD-M Diff Depth as 'pu')",
    )
    bids: list[PriceLevel] = Field(
        default_factory=list,
        description="Updated bid price levels",
    )
    asks: list[PriceLevel] = Field(
        default_factory=list,
        description="Updated ask price levels",
    )

    @model_validator(mode="after")
    def _validate_ids(self) -> DepthUpdate:
        if self.final_update_id < self.first_update_id:
            raise ValueError(
                f"final_update_id ({self.final_update_id}) must be >= first_update_id ({self.first_update_id})"
            )
        return self

    @model_validator(mode="after")
    def _validate_stream(self) -> DepthUpdate:
        if self.metadata.stream != Stream.DIFF_DEPTH:
            raise ValueError(f"DepthUpdate metadata.stream must be DIFF_DEPTH, got {self.metadata.stream.value}")
        return self


class AggTrade(ContractModel):
    """Binance aggregated trade.

    Represents an aggregated trade where a taker order was filled
    against one or more resting orders at the same price.

    The metadata.stream MUST be AGG_TRADE.
    """

    metadata: EventMetadata
    aggregate_trade_id: int = Field(..., ge=0, description="Aggregate trade ID from the exchange")
    price: PriceString
    quantity: QuantityString = Field(..., description="Total quantity of the aggregate trade (> 0)")
    first_trade_id: int = Field(..., ge=0, description="First individual trade ID in this aggregate")
    last_trade_id: int = Field(..., ge=0, description="Last individual trade ID in this aggregate")
    trade_time_ms: int = Field(..., ge=0, description="Trade time in milliseconds")
    buyer_is_maker: bool = Field(
        ...,
        description="True if the buyer was the maker (trade initiated by seller)",
    )

    @model_validator(mode="after")
    def _validate_trade_ids(self) -> AggTrade:
        if self.last_trade_id < self.first_trade_id:
            raise ValueError(f"last_trade_id ({self.last_trade_id}) must be >= first_trade_id ({self.first_trade_id})")
        return self

    @model_validator(mode="after")
    def _validate_stream(self) -> AggTrade:
        if self.metadata.stream != Stream.AGG_TRADE:
            raise ValueError(f"AggTrade metadata.stream must be AGG_TRADE, got {self.metadata.stream.value}")
        return self


class BookTicker(ContractModel):
    """Binance book ticker — best bid and ask with quantities.

    Accepts crossed books (best_bid_price >= best_ask_price).
    Crossed state is reported by Health through QualityFlag.CROSSED_BOOK,
    not rejected at contract construction.

    update_id is None when the exchange product does not provide it.

    The metadata.stream MUST be BOOK_TICKER.
    """

    metadata: EventMetadata
    update_id: int | None = Field(
        default=None,
        ge=0,
        description="Update ID from the exchange, or None if not provided",
    )
    best_bid_price: PriceString
    best_bid_quantity: QuantityString
    best_ask_price: PriceString
    best_ask_quantity: QuantityString

    @model_validator(mode="after")
    def _validate_stream(self) -> BookTicker:
        if self.metadata.stream != Stream.BOOK_TICKER:
            raise ValueError(f"BookTicker metadata.stream must be BOOK_TICKER, got {self.metadata.stream.value}")
        return self
