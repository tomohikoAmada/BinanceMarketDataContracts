"""Test that all public imports resolve correctly."""

import binance_market_data_contracts as pkg
from binance_market_data_contracts import __all__


def test_package_version():
    assert pkg.__version__ == "0.1.0a1"


def test_all_exports_exist():
    for name in __all__:
        if name == "__version__":
            continue
        obj = getattr(pkg, name)
        assert obj is not None, f"{name} is None"


def test_proposed_types_importable():
    from binance_market_data_contracts import (  # noqa: F401
        AggTrade,
        AggTradeMetadata,
        BookTicker,
        BookTickerMetadata,
        ConnectionId,
        ConnectionState,
        ContractError,
        ContractModel,
        ContractStatus,
        DataHealthSnapshot,
        DepthUpdate,
        DepthUpdateMetadata,
        ExchangeDepthSnapshot,
        GapDescriptor,
        HealthState,
        LatencySummary,
        LocalOrderBookSnapshot,
        Market,
        MarketStateSnapshot,
        PriceLevel,
        QualityFlag,
        ReasonCode,
        ReliabilityState,
        RequestId,
        ResyncState,
        SchemaVersionError,
        SnapshotSource,
        Stream,
        Symbol,
        Venue,
    )


def test_registry_importable():
    from binance_market_data_contracts import CONTRACT_REGISTRY, get_contract_status

    assert isinstance(CONTRACT_REGISTRY, dict)
    assert callable(get_contract_status)


def test_no_internal_leakage():
    import binance_market_data_contracts as pkg

    draft_names = {"HistoricalDatasetDescriptor", "ReplayQuery", "TelemetryEnvelope", "ControlCommand", "CommandResult"}
    for name in draft_names:
        assert not hasattr(pkg, name) or name not in __all__, f"{name} should not be in __all__"
