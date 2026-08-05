"""BinanceMarketDataContracts — versioned public contracts for BinanceMarketData.

All contracts are in PROPOSED or DRAFT status pending architecture review.

Model validation errors use pydantic.ValidationError.
"""

__version__ = "0.2.0a1"

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import (
    ConnectionState,
    ConsumerGapReason,
    ContractStatus,
    DeliveryMode,
    HealthState,
    InitialSnapshotMode,
    Market,
    QualityFlag,
    ReasonCode,
    RecoveryAction,
    ReliabilityState,
    ResyncState,
    SnapshotSource,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.errors import ContractError, SchemaVersionError
from binance_market_data_contracts.identifiers import ConnectionId, GatewayInstanceId, RequestId, SubscriptionId, Symbol
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
from binance_market_data_contracts.versions import (
    CONTRACT_REGISTRY,
    WIRE_CONTRACT_REGISTRY,
    ContractEntry,
    WireContractEntry,
    get_contract_status,
)

__all__ = [
    "CONTRACT_REGISTRY",
    "WIRE_CONTRACT_REGISTRY",
    "AggTrade",
    "AggTradeMetadata",
    "BookTicker",
    "BookTickerMetadata",
    "ConnectionId",
    "ConnectionState",
    "ConsumerGapReason",
    "ContractEntry",
    "ContractError",
    "ContractModel",
    "ContractStatus",
    "DataHealthSnapshot",
    "DeliveryMode",
    "DepthUpdate",
    "DepthUpdateMetadata",
    "ExchangeDepthSnapshot",
    "GapDescriptor",
    "GatewayInstanceId",
    "HealthState",
    "InitialSnapshotMode",
    "LatencySummary",
    "LocalOrderBookSnapshot",
    "Market",
    "MarketStateSnapshot",
    "PriceLevel",
    "QualityFlag",
    "ReasonCode",
    "RecoveryAction",
    "ReliabilityState",
    "RequestId",
    "ResyncState",
    "SchemaVersionError",
    "SnapshotSource",
    "Stream",
    "StreamLifecycleState",
    "SubscriptionId",
    "Symbol",
    "Venue",
    "WireContractEntry",
    "__version__",
    "get_contract_status",
]
