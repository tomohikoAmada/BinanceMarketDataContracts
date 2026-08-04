"""Test Draft contracts: history, telemetry, control."""

from binance_market_data_contracts.control import CommandResult, CommandStatus, CommandType, ControlCommand
from binance_market_data_contracts.history import HistoricalDatasetDescriptor, ReplayQuery
from binance_market_data_contracts.telemetry import (
    ConnectionMetrics,
    LatencyMetrics,
    QueueMetrics,
    SequenceMetrics,
    TelemetryEnvelope,
    TelemetryType,
)


class TestHistoricalDatasetDescriptor:
    def test_minimal_descriptor(self):
        d = HistoricalDatasetDescriptor(
            dataset_id="ds-001",
            market="SPOT",
            symbol="BTCUSDT",
            streams=["DIFF_DEPTH", "AGG_TRADE"],
            schema_version="historical-dataset-descriptor.v1",
            producer_version="0.1.0",
        )
        assert d.dataset_id == "ds-001"
        assert len(d.streams) == 2
        assert d.gap_count == 0

    def test_with_gap_intervals(self):
        d = HistoricalDatasetDescriptor(
            dataset_id="ds-002",
            market="SPOT",
            symbol="ETHUSDT",
            streams=["DIFF_DEPTH"],
            schema_version="historical-dataset-descriptor.v1",
            producer_version="0.1.0",
            gap_count=2,
            gap_intervals=["2024-01-01T00:00:00Z/2024-01-01T00:05:00Z"],
        )
        assert d.gap_count == 2


class TestReplayQuery:
    def test_minimal_query(self):
        q = ReplayQuery(dataset_id="ds-001")
        assert q.dataset_id == "ds-001"
        assert q.clock == "receive_time"
        assert q.gap_policy == "report"

    def test_custom_policies(self):
        q = ReplayQuery(
            dataset_id="ds-001",
            clock="exchange_time",
            missing_exchange_time_policy="use_receive_time",
            gap_policy="skip_gap",
        )
        assert q.clock == "exchange_time"
        assert q.missing_exchange_time_policy == "use_receive_time"


class TestTelemetry:
    def test_connection_metrics(self):
        m = ConnectionMetrics(connected=True, last_message_age_ms=100)
        assert m.type == "connection"
        assert m.connected is True

    def test_sequence_metrics(self):
        m = SequenceMetrics(last_update_id=500, duplicate_count=2)
        assert m.type == "sequence"
        assert m.last_update_id == 500

    def test_latency_metrics(self):
        m = LatencyMetrics(receive_lag_ms=45)
        assert m.type == "latency"
        assert m.receive_lag_ms == 45

    def test_queue_metrics(self):
        m = QueueMetrics(queue_depth=10, dropped=2)
        assert m.queue_depth == 10

    def test_telemetry_envelope(self):
        metrics = ConnectionMetrics(connected=True)
        e = TelemetryEnvelope(
            telemetry_type="CONNECTION",
            source_module="gateway",
            source_instance_id="gw-001",
            market="SPOT",
            symbol="BTCUSDT",
            metrics=metrics,
        )
        assert e.telemetry_type == TelemetryType.CONNECTION
        assert e.metrics.connected is True

    def test_discriminated_union(self):
        e = TelemetryEnvelope(
            telemetry_type="SEQUENCE",
            source_module="recorder",
            source_instance_id="rec-001",
            metrics={"type": "sequence", "last_update_id": 100, "duplicate_count": 0, "out_of_order_count": 0},
        )
        assert e.metrics.type == "sequence"


class TestControl:
    def test_control_command(self):
        cmd = ControlCommand(
            command_id="cmd-001",
            command_type="GET_STATUS",
            target="gateway",
            requested_at="2024-01-01T00:00:00Z",
            requester="admin",
        )
        assert cmd.command_type == CommandType.GET_STATUS
        assert cmd.schema_version == "control-command.v1"

    def test_control_command_with_idempotency(self):
        cmd = ControlCommand(
            command_id="cmd-002",
            command_type="TRIGGER_ARCHIVE",
            target="recorder",
            requested_at="2024-01-01T00:00:00Z",
            requester="system",
            idempotency_key="key-123",
            parameters={"target_date": "2024-01-01"},
        )
        assert cmd.idempotency_key == "key-123"
        assert cmd.parameters == {"target_date": "2024-01-01"}

    def test_command_result_success(self):
        result = CommandResult(
            command_id="cmd-001",
            status="COMPLETED",
            result_summary="Status retrieved",
            requested_at="2024-01-01T00:00:00Z",
            executed_at="2024-01-01T00:00:01Z",
        )
        assert result.status == CommandStatus.COMPLETED
        assert result.error_code is None

    def test_command_result_failure(self):
        result = CommandResult(
            command_id="cmd-002",
            status="FAILED",
            error_code="TIMEOUT",
            error_message="Command timed out after 30s",
            requested_at="2024-01-01T00:00:00Z",
        )
        assert result.status == CommandStatus.FAILED
        assert result.error_code == "TIMEOUT"
