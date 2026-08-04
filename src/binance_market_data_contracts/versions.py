"""Contract registry and version management.

The registry is the single source of truth for all contracts, their statuses,
and their corresponding Python types. Tests enforce consistency between the
registry, __all__, generated schemas, and fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from binance_market_data_contracts.enums import ContractStatus

if TYPE_CHECKING:
    from pydantic import BaseModel


@dataclass(frozen=True)
class ContractEntry:
    name: str  # e.g. "depth-update.v1"
    status: ContractStatus
    python_type: type[BaseModel]
    producer: str | None = None
    consumer: str | None = None
    replaces: str | None = None
    replaced_by: str | None = None


CONTRACT_REGISTRY: dict[str, ContractEntry] = {}


def _register(
    name: str,
    status: ContractStatus,
    python_type: type[BaseModel],
    producer: str | None = None,
    consumer: str | None = None,
    replaces: str | None = None,
    replaced_by: str | None = None,
) -> None:
    CONTRACT_REGISTRY[name] = ContractEntry(
        name=name,
        status=status,
        python_type=python_type,
        producer=producer,
        consumer=consumer,
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
    "depth-update.v1", ContractStatus.PROPOSED, DepthUpdate, producer="recorder or gateway", consumer="all modules"
)
_register("agg-trade.v1", ContractStatus.PROPOSED, AggTrade, producer="recorder or gateway", consumer="all modules")
_register("book-ticker.v1", ContractStatus.PROPOSED, BookTicker, producer="recorder or gateway", consumer="all modules")
_register(
    "exchange-depth-snapshot.v1",
    ContractStatus.PROPOSED,
    ExchangeDepthSnapshot,
    producer="recorder or gateway",
    consumer="order book, history",
)
_register(
    "local-order-book-snapshot.v1",
    ContractStatus.PROPOSED,
    LocalOrderBookSnapshot,
    producer="gateway or replay",
    consumer="view, health",
)
_register(
    "market-state-snapshot.v1",
    ContractStatus.PROPOSED,
    MarketStateSnapshot,
    producer="projection or gateway",
    consumer="view, strategy",
)
_register(
    "data-health-snapshot.v1",
    ContractStatus.PROPOSED,
    DataHealthSnapshot,
    producer="health",
    consumer="view, control, risk",
)

# -- Draft Contracts --

from binance_market_data_contracts.control import CommandResult, ControlCommand  # noqa: E402
from binance_market_data_contracts.history import HistoricalDatasetDescriptor, ReplayQuery  # noqa: E402
from binance_market_data_contracts.telemetry import TelemetryEnvelope  # noqa: E402

_register("historical-dataset-descriptor.v1", ContractStatus.DRAFT, HistoricalDatasetDescriptor)
_register("replay-query.v1", ContractStatus.DRAFT, ReplayQuery)
_register("telemetry.v1", ContractStatus.DRAFT, TelemetryEnvelope)
_register("control-command.v1", ContractStatus.DRAFT, ControlCommand)
_register("command-result.v1", ContractStatus.DRAFT, CommandResult)
