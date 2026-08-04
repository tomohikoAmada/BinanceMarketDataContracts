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


def test_accepted_types_importable():
    from binance_market_data_contracts import (  # noqa: F401
        AggTrade,
        BookTicker,
        ContractError,
        ContractModel,
        ContractStatus,
        DepthUpdate,
        EventMetadata,
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
        SchemaVersionError,
        Stream,
        Symbol,
        ValidationError,
        Venue,
    )


def test_registry_importable():
    from binance_market_data_contracts import CONTRACT_REGISTRY, get_contract_status

    assert isinstance(CONTRACT_REGISTRY, dict)
    assert callable(get_contract_status)


def test_no_internal_leakage():
    """Verify that no internal implementation classes leak into __all__."""
    import binance_market_data_contracts as pkg

    forbidden = {"ReplayQuery", "HistoricalDatasetDescriptor", "TelemetryEnvelope", "ControlCommand", "CommandResult"}
    for name in forbidden:
        assert hasattr(pkg, name) is False or name not in __all__, f"{name} should not be in __all__"
