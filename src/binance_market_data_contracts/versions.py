"""Contract registry and version management.

The registry is the single source of truth for all contracts, their statuses,
and their corresponding Python types. Duplicate names are rejected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from binance_market_data_contracts.enums import ContractStatus

if TYPE_CHECKING:
    from pydantic import BaseModel


@dataclass(frozen=True)
class ContractEntry:
    name: str
    status: ContractStatus
    python_type: type[BaseModel]
    producers: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()
    replaces: str | None = None
    replaced_by: str | None = None


CONTRACT_REGISTRY: dict[str, ContractEntry] = {}


def _register(
    name: str,
    status: ContractStatus,
    python_type: type[BaseModel],
    producers: tuple[str, ...] = (),
    consumers: tuple[str, ...] = (),
    replaces: str | None = None,
    replaced_by: str | None = None,
) -> None:
    if name in CONTRACT_REGISTRY:
        raise RuntimeError(f"Contract '{name}' is already registered")
    CONTRACT_REGISTRY[name] = ContractEntry(
        name=name,
        status=status,
        python_type=python_type,
        producers=producers,
        consumers=consumers,
        replaces=replaces,
        replaced_by=replaced_by,
    )


def get_contract_status(name: str) -> ContractStatus | None:
    entry = CONTRACT_REGISTRY.get(name)
    return entry.status if entry else None


def get_accepted_contracts() -> dict[str, ContractEntry]:
    return {k: v for k, v in CONTRACT_REGISTRY.items() if v.status == ContractStatus.ACCEPTED}


def get_proposed_contracts() -> dict[str, ContractEntry]:
    return {k: v for k, v in CONTRACT_REGISTRY.items() if v.status == ContractStatus.PROPOSED}


def get_draft_contracts() -> dict[str, ContractEntry]:
    return {k: v for k, v in CONTRACT_REGISTRY.items() if v.status == ContractStatus.DRAFT}


# -- Core Market Contracts (PROPOSED) --

from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate  # noqa: E402
from binance_market_data_contracts.snapshots import (  # noqa: E402
    DataHealthSnapshot,
    ExchangeDepthSnapshot,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)

_register(
    "depth-update.v1",
    ContractStatus.PROPOSED,
    DepthUpdate,
    producers=("recorder-adapter", "gateway-adapter"),
    consumers=("projection", "health", "history-replay", "live-strategy"),
)
_register(
    "agg-trade.v1",
    ContractStatus.PROPOSED,
    AggTrade,
    producers=("recorder-adapter", "gateway-adapter"),
    consumers=("projection", "health", "history-replay", "live-strategy"),
)
_register(
    "book-ticker.v1",
    ContractStatus.PROPOSED,
    BookTicker,
    producers=("recorder-adapter", "gateway-adapter"),
    consumers=("projection", "health", "history-replay", "live-strategy"),
)
_register(
    "exchange-depth-snapshot.v1",
    ContractStatus.PROPOSED,
    ExchangeDepthSnapshot,
    producers=("recorder-adapter", "gateway-adapter"),
    consumers=("order-book", "history"),
)
_register(
    "local-order-book-snapshot.v1",
    ContractStatus.PROPOSED,
    LocalOrderBookSnapshot,
    producers=("gateway-adapter", "replay"),
    consumers=("view", "health"),
)
_register(
    "market-state-snapshot.v1",
    ContractStatus.PROPOSED,
    MarketStateSnapshot,
    producers=("projection", "gateway-adapter"),
    consumers=("view", "live-strategy"),
)
_register(
    "data-health-snapshot.v1",
    ContractStatus.PROPOSED,
    DataHealthSnapshot,
    producers=("health",),
    consumers=("view", "control", "risk"),
)

# -- Draft Contracts --

from binance_market_data_contracts.control import CommandResult, ControlCommand  # noqa: E402
from binance_market_data_contracts.gateway import (  # noqa: E402
    ConsumerGapNotice,
    EventSubscriptionRequest,
    GatewayEventEnvelope,
    GatewayStatusSnapshot,
    MarketStateStreamItem,
    MarketStateSubscriptionRequest,
    OrderBookStreamItem,
    OrderBookSubscriptionRequest,
    StreamStatus,
    SubscriptionAccepted,
)
from binance_market_data_contracts.history import HistoricalDatasetDescriptor, ReplayQuery  # noqa: E402
from binance_market_data_contracts.telemetry import TelemetryEnvelope  # noqa: E402

_register("historical-dataset-descriptor.v1", ContractStatus.DRAFT, HistoricalDatasetDescriptor)
_register("replay-query.v1", ContractStatus.DRAFT, ReplayQuery)
_register("telemetry.v1", ContractStatus.DRAFT, TelemetryEnvelope)
_register("control-command.v1", ContractStatus.DRAFT, ControlCommand)
_register("command-result.v1", ContractStatus.DRAFT, CommandResult)

# -- Gateway Contracts (DRAFT) --

_register(
    "event-subscription-request.v1",
    ContractStatus.DRAFT,
    EventSubscriptionRequest,
    producers=("gateway-consumer",),
    consumers=("gateway",),
)
_register(
    "order-book-subscription-request.v1",
    ContractStatus.DRAFT,
    OrderBookSubscriptionRequest,
    producers=("gateway-consumer",),
    consumers=("gateway",),
)
_register(
    "market-state-subscription-request.v1",
    ContractStatus.DRAFT,
    MarketStateSubscriptionRequest,
    producers=("gateway-consumer",),
    consumers=("gateway",),
)
_register(
    "subscription-accepted.v1",
    ContractStatus.DRAFT,
    SubscriptionAccepted,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "consumer-gap-notice.v1",
    ContractStatus.DRAFT,
    ConsumerGapNotice,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "stream-status.v1",
    ContractStatus.DRAFT,
    StreamStatus,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "gateway-event-envelope.v1",
    ContractStatus.DRAFT,
    GatewayEventEnvelope,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "order-book-stream-item.v1",
    ContractStatus.DRAFT,
    OrderBookStreamItem,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "market-state-stream-item.v1",
    ContractStatus.DRAFT,
    MarketStateStreamItem,
    producers=("gateway",),
    consumers=("gateway-consumer",),
)
_register(
    "gateway-status-snapshot.v1",
    ContractStatus.DRAFT,
    GatewayStatusSnapshot,
    producers=("gateway",),
    consumers=("control", "view", "health"),
)

# -- Wire Contract Registry --

from dataclasses import dataclass as _dataclass  # noqa: E402


@_dataclass(frozen=True)
class WireContractEntry:
    schema_version: str
    pydantic_type: type[BaseModel] | None
    proto_full_name: str
    status: ContractStatus
    producers: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()


WIRE_CONTRACT_REGISTRY: dict[str, WireContractEntry] = {
    # Core market events
    "depth-update.v1": WireContractEntry(
        schema_version="depth-update.v1",
        pydantic_type=DepthUpdate,
        proto_full_name="binance_market_data.market.v1.DepthUpdate",
        status=ContractStatus.PROPOSED,
        producers=("recorder-adapter", "gateway-adapter"),
        consumers=("projection", "health", "history-replay", "live-strategy"),
    ),
    "agg-trade.v1": WireContractEntry(
        schema_version="agg-trade.v1",
        pydantic_type=AggTrade,
        proto_full_name="binance_market_data.market.v1.AggTrade",
        status=ContractStatus.PROPOSED,
        producers=("recorder-adapter", "gateway-adapter"),
        consumers=("projection", "health", "history-replay", "live-strategy"),
    ),
    "book-ticker.v1": WireContractEntry(
        schema_version="book-ticker.v1",
        pydantic_type=BookTicker,
        proto_full_name="binance_market_data.market.v1.BookTicker",
        status=ContractStatus.PROPOSED,
        producers=("recorder-adapter", "gateway-adapter"),
        consumers=("projection", "health", "history-replay", "live-strategy"),
    ),
    "exchange-depth-snapshot.v1": WireContractEntry(
        schema_version="exchange-depth-snapshot.v1",
        pydantic_type=ExchangeDepthSnapshot,
        proto_full_name="binance_market_data.market.v1.ExchangeDepthSnapshot",
        status=ContractStatus.PROPOSED,
        producers=("recorder-adapter", "gateway-adapter"),
        consumers=("order-book", "history"),
    ),
    # Projection snapshots
    "local-order-book-snapshot.v1": WireContractEntry(
        schema_version="local-order-book-snapshot.v1",
        pydantic_type=LocalOrderBookSnapshot,
        proto_full_name="binance_market_data.projection.v1.LocalOrderBookSnapshot",
        status=ContractStatus.PROPOSED,
        producers=("gateway-adapter", "replay"),
        consumers=("view", "health"),
    ),
    "market-state-snapshot.v1": WireContractEntry(
        schema_version="market-state-snapshot.v1",
        pydantic_type=MarketStateSnapshot,
        proto_full_name="binance_market_data.projection.v1.MarketStateSnapshot",
        status=ContractStatus.PROPOSED,
        producers=("projection", "gateway-adapter"),
        consumers=("view", "live-strategy"),
    ),
    "data-health-snapshot.v1": WireContractEntry(
        schema_version="data-health-snapshot.v1",
        pydantic_type=DataHealthSnapshot,
        proto_full_name="binance_market_data.projection.v1.DataHealthSnapshot",
        status=ContractStatus.PROPOSED,
        producers=("health",),
        consumers=("view", "control", "risk"),
    ),
    # Gateway contracts
    "event-subscription-request.v1": WireContractEntry(
        schema_version="event-subscription-request.v1",
        pydantic_type=EventSubscriptionRequest,
        proto_full_name="binance_market_data.gateway.v1.EventSubscriptionRequest",
        status=ContractStatus.DRAFT,
        producers=("gateway-consumer",),
        consumers=("gateway",),
    ),
    "order-book-subscription-request.v1": WireContractEntry(
        schema_version="order-book-subscription-request.v1",
        pydantic_type=OrderBookSubscriptionRequest,
        proto_full_name="binance_market_data.gateway.v1.OrderBookSubscriptionRequest",
        status=ContractStatus.DRAFT,
        producers=("gateway-consumer",),
        consumers=("gateway",),
    ),
    "market-state-subscription-request.v1": WireContractEntry(
        schema_version="market-state-subscription-request.v1",
        pydantic_type=MarketStateSubscriptionRequest,
        proto_full_name="binance_market_data.gateway.v1.MarketStateSubscriptionRequest",
        status=ContractStatus.DRAFT,
        producers=("gateway-consumer",),
        consumers=("gateway",),
    ),
    "subscription-accepted.v1": WireContractEntry(
        schema_version="subscription-accepted.v1",
        pydantic_type=SubscriptionAccepted,
        proto_full_name="binance_market_data.gateway.v1.SubscriptionAccepted",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "consumer-gap-notice.v1": WireContractEntry(
        schema_version="consumer-gap-notice.v1",
        pydantic_type=ConsumerGapNotice,
        proto_full_name="binance_market_data.gateway.v1.ConsumerGapNotice",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "stream-status.v1": WireContractEntry(
        schema_version="stream-status.v1",
        pydantic_type=StreamStatus,
        proto_full_name="binance_market_data.gateway.v1.StreamStatus",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "gateway-event-envelope.v1": WireContractEntry(
        schema_version="gateway-event-envelope.v1",
        pydantic_type=GatewayEventEnvelope,
        proto_full_name="binance_market_data.gateway.v1.GatewayEventEnvelope",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "order-book-stream-item.v1": WireContractEntry(
        schema_version="order-book-stream-item.v1",
        pydantic_type=OrderBookStreamItem,
        proto_full_name="binance_market_data.gateway.v1.OrderBookStreamItem",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "market-state-stream-item.v1": WireContractEntry(
        schema_version="market-state-stream-item.v1",
        pydantic_type=MarketStateStreamItem,
        proto_full_name="binance_market_data.gateway.v1.MarketStateStreamItem",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("gateway-consumer",),
    ),
    "gateway-status-snapshot.v1": WireContractEntry(
        schema_version="gateway-status-snapshot.v1",
        pydantic_type=GatewayStatusSnapshot,
        proto_full_name="binance_market_data.gateway.v1.GatewayStatusSnapshot",
        status=ContractStatus.DRAFT,
        producers=("gateway",),
        consumers=("control", "view", "health"),
    ),
    # Telemetry
    "telemetry.v1": WireContractEntry(
        schema_version="telemetry.v1",
        pydantic_type=TelemetryEnvelope,
        proto_full_name="binance_market_data.telemetry.v1.TelemetryEnvelope",
        status=ContractStatus.DRAFT,
        producers=("gateway", "recorder"),
        consumers=("health",),
    ),
}
