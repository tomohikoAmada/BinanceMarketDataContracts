"""BinanceMarketDataContracts — versioned public contracts for BinanceMarketData.

All contracts are in PROPOSED or DRAFT status pending architecture review.

Model validation errors use pydantic.ValidationError.
"""

__version__ = "0.1.0a1"

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import (
    ConnectionState,
    ContractStatus,
    HealthState,
    Market,
    QualityFlag,
    ReasonCode,
    ReliabilityState,
    ResyncState,
    SnapshotSource,
    Stream,
    Venue,
)
from binance_market_data_contracts.errors import ContractError, SchemaVersionError
from binance_market_data_contracts.identifiers import ConnectionId, RequestId, Symbol
from binance_market_data_contracts.market_events import (
    AggTrade,
    AggTradeMetadata,
    BookTicker,
    BookTickerMetadata,
    DepthUpdate,
    DepthUpdateMetadata,
    PriceLevel,
)
from binance_market_data_contracts.snapshots import (
    DataHealthSnapshot,
    ExchangeDepthSnapshot,
    GapDescriptor,
    LatencySummary,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)
from binance_market_data_contracts.versions import CONTRACT_REGISTRY, ContractEntry, get_contract_status

__all__ = [
    "CONTRACT_REGISTRY",
    "AggTrade",
    "AggTradeMetadata",
    "BookTicker",
    "BookTickerMetadata",
    "ConnectionId",
    "ConnectionState",
    "ContractEntry",
    "ContractError",
    "ContractModel",
    "ContractStatus",
    "DataHealthSnapshot",
    "DepthUpdate",
    "DepthUpdateMetadata",
    "ExchangeDepthSnapshot",
    "GapDescriptor",
    "HealthState",
    "LatencySummary",
    "LocalOrderBookSnapshot",
    "Market",
    "MarketStateSnapshot",
    "PriceLevel",
    "QualityFlag",
    "ReasonCode",
    "ReliabilityState",
    "RequestId",
    "ResyncState",
    "SchemaVersionError",
    "SnapshotSource",
    "Stream",
    "Symbol",
    "Venue",
    "__version__",
    "get_contract_status",
]
