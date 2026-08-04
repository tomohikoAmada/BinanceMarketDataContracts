"""Test time semantics: recursive field naming, units, null handling."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import Market, Venue
from binance_market_data_contracts.market_events import _BaseEventMetadata
from binance_market_data_contracts.time import (
    find_invalid_time_fields,
    walk_models,
)
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


class TestRecursiveTimeFieldScan:
    def test_all_registered_time_fields_have_explicit_semantics(self):
        invalid_fields: list[str] = []
        for contract_name, entry in CONTRACT_REGISTRY.items():
            for field_id in find_invalid_time_fields(entry.python_type):
                invalid_fields.append(f"{contract_name}:{field_id}")
        assert not invalid_fields, "Ambiguous or unregistered time fields:\n" + "\n".join(sorted(invalid_fields))

    def test_no_nested_model_uses_timestamp(self):
        invalid_fields: list[str] = []
        for contract_name, entry in CONTRACT_REGISTRY.items():
            for model_type in walk_models(entry.python_type):
                if "timestamp" in model_type.model_fields:
                    invalid_fields.append(f"{contract_name}:{model_type.__name__}.timestamp")
        assert not invalid_fields, f"Found forbidden 'timestamp' field: {invalid_fields}"

    def test_walk_models_enters_nested_contracts(self):
        from binance_market_data_contracts.snapshots import DataHealthSnapshot

        models = walk_models(DataHealthSnapshot)
        model_names = {m.__name__ for m in models}
        assert "DataHealthSnapshot" in model_names
        assert "LatencySummary" in model_names

    def test_walk_models_enters_telemetry_discriminated_union(self):
        from binance_market_data_contracts.telemetry import TelemetryEnvelope

        models = walk_models(TelemetryEnvelope)
        model_names = {m.__name__ for m in models}
        assert "TelemetryEnvelope" in model_names
        assert "ConnectionMetrics" in model_names
        assert "SequenceMetrics" in model_names

    def test_walk_models_enters_control_parameters(self):
        from binance_market_data_contracts.control import ControlCommand

        models = walk_models(ControlCommand)
        model_names = {m.__name__ for m in models}
        assert "ControlCommand" in model_names
        assert "GetStatusParameters" in model_names

    def test_time_detector_reports_ambiguous_field(self):
        class InvalidTimeModel(ContractModel):
            start_time: int

        invalid = find_invalid_time_fields(InvalidTimeModel)
        assert "InvalidTimeModel.start_time" in invalid

    def test_time_detector_reports_bare_timestamp(self):
        class InvalidTimestampModel(ContractModel):
            timestamp: int

        invalid = find_invalid_time_fields(InvalidTimestampModel)
        assert "InvalidTimestampModel.timestamp" in invalid


class TestTimeFieldNaming:
    def test_no_field_named_timestamp_on_models(self):
        for entry in CONTRACT_REGISTRY.values():
            for name in entry.python_type.model_fields:
                assert name != "timestamp", f"{entry.name} has forbidden field 'timestamp'"


class TestTimeNullSemantics:
    def test_missing_exchange_time_is_null(self):
        m = _BaseEventMetadata(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol="BTCUSDT",
            producer="test",
            producer_version="0.1.0",
            connection_id="conn-1",
        )
        assert m.exchange_event_time_ms is None

    def test_time_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            _BaseEventMetadata(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol="BTCUSDT",
                producer="test",
                producer_version="0.1.0",
                connection_id="conn-1",
                receive_time_utc_ns=-1,
            )
