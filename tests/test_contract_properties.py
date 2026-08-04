"""Test contract model properties: frozen, strict, extra=forbid across registry."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.enums import Market, Venue
from binance_market_data_contracts.market_events import (
    DepthUpdate,
    PriceLevel,
    _BaseEventMetadata,
)
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


class TestRegistryModelProperties:
    """Check all registry models have required config."""

    def test_all_models_frozen(self):
        for entry in CONTRACT_REGISTRY.values():
            config = entry.python_type.model_config
            assert config.get("frozen") is True, f"{entry.name} not frozen"

    def test_all_models_extra_forbid(self):
        for entry in CONTRACT_REGISTRY.values():
            config = entry.python_type.model_config
            assert config.get("extra") == "forbid", f"{entry.name} does not forbid extra"

    def test_all_models_strict(self):
        for entry in CONTRACT_REGISTRY.values():
            config = entry.python_type.model_config
            assert config.get("strict") is True, f"{entry.name} not strict"


class TestRegistryUniqueness:
    def test_no_duplicate_names(self):
        names = list(CONTRACT_REGISTRY.keys())
        assert len(names) == len(set(names))

    def test_duplicate_register_raises(self):
        from binance_market_data_contracts.enums import ContractStatus
        from binance_market_data_contracts.versions import _register

        with pytest.raises(RuntimeError):
            _register("depth-update.v1", ContractStatus.PROPOSED, DepthUpdate)


class TestProducerConsumer:
    def test_proposed_have_producers_consumers(self):
        from binance_market_data_contracts.enums import ContractStatus

        for entry in CONTRACT_REGISTRY.values():
            if entry.status == ContractStatus.PROPOSED:
                assert len(entry.producers) > 0, f"PROPOSED {entry.name} has no producers"
                assert len(entry.consumers) > 0, f"PROPOSED {entry.name} has no consumers"


class TestSchemaVersionLiteral:
    def test_schema_version_matches_registry(self):
        from binance_market_data_contracts.time import walk_models

        for name, entry in CONTRACT_REGISTRY.items():
            found = False
            for model_type in walk_models(entry.python_type):
                fields = model_type.model_fields
                if "schema_version" in fields:
                    field_info = fields["schema_version"]
                    assert field_info.is_required(), f"{model_type.__name__}.schema_version must be required"
                    ann = str(field_info.annotation)
                    assert name in ann.replace("'", "").replace('"', ""), (
                        f"schema_version Literal mismatch for {name} "
                        f"in {model_type.__name__}: {field_info.annotation!r}"
                    )
                    found = True
            assert found, f"Registered contract {name} has no schema_version field in any nested model"


class TestExtraForbid:
    def test_extra_field_rejected(self):
        from binance_market_data_contracts.market_events import _BaseEventMetadata

        with pytest.raises(ValidationError, match="extra"):
            _BaseEventMetadata.model_validate(
                {
                    "venue": "BINANCE",
                    "market": "SPOT",
                    "symbol": "BTCUSDT",
                    "producer": "test",
                    "producer_version": "0.1.0",
                    "connection_id": "conn-1",
                    "extra_field": "should fail",
                }
            )


class TestFrozen:
    def test_frozen_prevents_mutation(self):
        m = _BaseEventMetadata(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol="BTCUSDT",
            producer="test",
            producer_version="0.1.0",
            connection_id="conn-1",
        )
        with pytest.raises((ValidationError, TypeError, AttributeError)):
            m.venue = Venue.BINANCE  # type: ignore[misc]

    def test_collection_is_tuple_not_list(self):
        price_level = PriceLevel(price="100.00", quantity="1.0")
        assert not hasattr(price_level, "__setitem__")
