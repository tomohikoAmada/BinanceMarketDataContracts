"""Test that the public API surface is clean and consistent."""

from binance_market_data_contracts import __all__
from binance_market_data_contracts.enums import ContractStatus
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


def test_registry_proposed_contracts_in_all():
    registry_names = {entry.name for entry in CONTRACT_REGISTRY.values() if entry.status == ContractStatus.PROPOSED}
    for name in registry_names:
        python_type = CONTRACT_REGISTRY[name].python_type
        type_name = python_type.__name__
        assert type_name in __all__, f"PROPOSED contract {name} Python type '{type_name}' not in __all__"


def test_no_internal_types_in_all():
    internal_patterns = ["BaseModel", "ConfigDict", "PlainValidator", "Annotated", "Field"]
    for name in __all__:
        assert name not in internal_patterns, f"Internal pattern '{name}' in __all__"


def test_no_draft_contracts_in_all():
    draft_names = {"HistoricalDatasetDescriptor", "ReplayQuery", "TelemetryEnvelope", "ControlCommand", "CommandResult"}
    for name in draft_names:
        assert name not in __all__, f"DRAFT contract '{name}' should not be in __all__"


def test_version_accessible():
    from binance_market_data_contracts import __version__

    assert __version__ == "0.1.0a1"


def test_contract_registry_is_complete():
    assert len(CONTRACT_REGISTRY) >= 7, f"Expected at least 7 contracts, got {len(CONTRACT_REGISTRY)}"
    proposed = [e for e in CONTRACT_REGISTRY.values() if e.status == ContractStatus.PROPOSED]
    draft = [e for e in CONTRACT_REGISTRY.values() if e.status == ContractStatus.DRAFT]
    assert len(proposed) >= 7
    assert len(draft) >= 5
