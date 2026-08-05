"""Keep public documentation synchronized with descriptors and registries."""

from __future__ import annotations

import re
from pathlib import Path

from binance_market_data.gateway.v1 import gateway_service_pb2
from binance_market_data_contracts import wire
from binance_market_data_contracts.enums import ContractStatus
from binance_market_data_contracts.versions import CONTRACT_REGISTRY, WIRE_CONTRACT_REGISTRY

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ARCHITECTURE = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")


def test_readme_rpc_names_match_service_descriptor() -> None:
    service = gateway_service_pb2.DESCRIPTOR.services_by_name["BinanceMarketDataGatewayService"]
    descriptor_names = {method.name for method in service.methods}
    documented_names = set(re.findall(r"^\| `([A-Za-z]+)` \|", README, flags=re.MULTILINE))
    assert documented_names == descriptor_names


def test_readme_adapter_names_exist() -> None:
    from binance_market_data_contracts.wire import adapters

    names = set(re.findall(r"`([a-z][a-z0-9_]+_(?:to|from)_pb)`", README))
    assert names
    assert not {name for name in names if not hasattr(adapters, name)}


def test_documented_generated_path_exists() -> None:
    assert "`src/binance_market_data/`" in README
    assert (ROOT / "src" / "binance_market_data").is_dir()
    assert wire.__doc__ is not None and "src/binance_market_data/" in wire.__doc__


def test_architecture_contract_names_and_statuses_match_registry() -> None:
    rows = re.findall(r"^\| ([a-z][a-z0-9-]+) \| (PROPOSED|DRAFT) \| v1 \|$", ARCHITECTURE, flags=re.MULTILINE)
    assert rows
    for contract_name, status in rows:
        registry_name = f"{contract_name}.v1"
        assert registry_name in CONTRACT_REGISTRY
        assert CONTRACT_REGISTRY[registry_name].status.value == status


def test_readme_wire_group_statuses_match_registry() -> None:
    expected_groups = {
        "Core Market Wire Contracts": (
            {"depth-update.v1", "agg-trade.v1", "book-ticker.v1", "exchange-depth-snapshot.v1"}
        ),
        "Projection Wire Contracts": (
            {"local-order-book-snapshot.v1", "market-state-snapshot.v1", "data-health-snapshot.v1"}
        ),
        "Gateway Wire Contracts": (
            {
                name
                for name in WIRE_CONTRACT_REGISTRY
                if name
                not in {
                    "depth-update.v1",
                    "agg-trade.v1",
                    "book-ticker.v1",
                    "exchange-depth-snapshot.v1",
                    "local-order-book-snapshot.v1",
                    "market-state-snapshot.v1",
                    "data-health-snapshot.v1",
                    "telemetry.v1",
                }
            }
        ),
        "Telemetry Wire Contract": ({"telemetry.v1"}),
    }
    for label, names in expected_groups.items():
        statuses = {WIRE_CONTRACT_REGISTRY[name].status for name in names}
        assert len(statuses) == 1
        status = next(iter(statuses))
        assert status in {ContractStatus.PROPOSED, ContractStatus.DRAFT}
        assert f"| {label} | {status.value} |" in README


def test_repository_sources_do_not_reference_old_generated_path() -> None:
    old_path = "src/binance_market_data_contracts/wire/" + "generated/"
    offenders = []
    excluded = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "dist", "venv"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or excluded.intersection(path.relative_to(ROOT).parts):
            continue
        if old_path in path.read_text(encoding="utf-8", errors="ignore"):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders
