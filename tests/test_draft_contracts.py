"""Test Draft contracts: history, telemetry, control."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.control import (
    CommandResult,
    CommandStatus,
    CommandType,
    ControlCommand,
    GetStatusParameters,
)
from binance_market_data_contracts.enums import Market
from binance_market_data_contracts.history import HistoricalDatasetDescriptor, ReplayQuery
from binance_market_data_contracts.telemetry import ConnectionMetrics, TelemetryEnvelope, TelemetryType


class TestHistoricalDatasetDescriptor:
    def test_minimal_descriptor(self):
        d = HistoricalDatasetDescriptor(
            dataset_id="ds-001",
            market=Market.SPOT,
            symbol="BTCUSDT",
            producer_version="0.1.0",
        )
        assert d.dataset_id == "ds-001"

    def test_start_after_end_rejected(self):
        with pytest.raises(ValidationError):
            HistoricalDatasetDescriptor(
                dataset_id="ds-001",
                market=Market.SPOT,
                symbol="BTCUSDT",
                producer_version="0.1.0",
                start_time_utc_ns=2000,
                end_time_utc_ns=1000,
            )


class TestReplayQuery:
    def test_minimal_query(self):
        q = ReplayQuery(dataset_id="ds-001")
        assert q.dataset_id == "ds-001"
        assert q.clock == "RECEIVE_TIME"


class TestTelemetry:
    def test_envelope(self):
        metrics = ConnectionMetrics(connected=True)
        e = TelemetryEnvelope(
            telemetry_type=TelemetryType.CONNECTION,
            source_module="gateway",
            source_instance_id="gw-001",
            metrics=metrics,
        )
        assert e.telemetry_type == TelemetryType.CONNECTION


class TestControl:
    def test_control_command(self):
        cmd = ControlCommand(
            command_id="cmd-001",
            command_type=CommandType.GET_STATUS,
            target="gateway",
            requested_at_utc_ns=1000,
            requester="admin",
            parameters=GetStatusParameters(),
        )
        assert cmd.command_type == CommandType.GET_STATUS

    def test_command_result(self):
        result = CommandResult(
            command_id="cmd-001",
            status=CommandStatus.COMPLETED,
            result_summary="OK",
            requested_at_utc_ns=1000,
            executed_at_utc_ns=2000,
        )
        assert result.status == CommandStatus.COMPLETED

    def test_command_failure(self):
        result = CommandResult(
            command_id="cmd-002",
            status=CommandStatus.FAILED,
            error_code="TIMEOUT",
            error_message="Timed out",
            requested_at_utc_ns=1000,
        )
        assert result.error_code == "TIMEOUT"
