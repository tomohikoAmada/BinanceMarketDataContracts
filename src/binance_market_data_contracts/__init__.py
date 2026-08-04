"""BinanceMarketDataContracts — versioned public contracts for BinanceMarketData.

All contracts are in PROPOSED or DRAFT status pending architecture review.
"""

__version__ = "0.1.0a1"

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import (
    ContractStatus,
    HealthState,
    Market,
    QualityFlag,
    ReasonCode,
    ReliabilityState,
    Stream,
    Venue,
)
from binance_market_data_contracts.errors import ContractError, SchemaVersionError, ValidationError
from binance_market_data_contracts.identifiers import ConnectionId, RequestId, Symbol
from binance_market_data_contracts.market_events import (
    AggTrade,
    BookTicker,
    DepthUpdate,
    EventMetadata,
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
    "BookTicker",
    "ConnectionId",
    "ContractEntry",
    "ContractError",
    "ContractModel",
    "ContractStatus",
    "DataHealthSnapshot",
    "DepthUpdate",
    "EventMetadata",
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
    "SchemaVersionError",
    "Stream",
    "Symbol",
    "ValidationError",
    "Venue",
    "__version__",
    "get_contract_status",
]
