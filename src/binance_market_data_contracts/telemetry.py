"""DRAFT — Telemetry contract.

Type consistency: telemetry_type must match metrics.type.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import ContractModel, NonEmptyText
from binance_market_data_contracts.enums import Market, QualityFlag, Stream
from binance_market_data_contracts.identifiers import ConnectionId, InstanceId, Symbol


class TelemetryType(StrEnum):
    CONNECTION = "CONNECTION"
    SEQUENCE = "SEQUENCE"
    LATENCY = "LATENCY"
    QUEUE = "QUEUE"
    BOOK = "BOOK"
    SYSTEM = "SYSTEM"


_TELEMETRY_METRIC_TYPES: dict[TelemetryType, str] = {
    TelemetryType.CONNECTION: "connection",
    TelemetryType.SEQUENCE: "sequence",
    TelemetryType.LATENCY: "latency",
    TelemetryType.QUEUE: "queue",
    TelemetryType.BOOK: "book",
    TelemetryType.SYSTEM: "system",
}


class ConnectionMetrics(ContractModel):
    type: Literal["connection"] = "connection"
    connected: bool
    last_message_age_ms: int | None = Field(default=None, ge=0)
    reconnect_count: int = Field(default=0, ge=0)


class SequenceMetrics(ContractModel):
    type: Literal["sequence"] = "sequence"
    last_update_id: int | None = Field(default=None, ge=0)
    duplicate_count: int = Field(default=0, ge=0)
    out_of_order_count: int = Field(default=0, ge=0)


class LatencyMetrics(ContractModel):
    type: Literal["latency"] = "latency"
    receive_lag_ms: int | None = Field(default=None, ge=0)
    publish_lag_ms: int | None = Field(default=None, ge=0)
    consumer_delivery_lag_ms: int | None = Field(default=None, ge=0)


class QueueMetrics(ContractModel):
    type: Literal["queue"] = "queue"
    queue_depth: int = Field(default=0, ge=0)
    queue_capacity: int = Field(default=0, ge=0)
    queue_utilization: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    oldest_message_age_ms: int | None = Field(default=None, ge=0)
    dropped: int = Field(default=0, ge=0)
    disconnect_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _validate_queue(self) -> QueueMetrics:
        if self.queue_capacity > 0 and self.queue_depth > self.queue_capacity:
            raise ValueError(f"queue_depth ({self.queue_depth}) must not exceed queue_capacity ({self.queue_capacity})")
        if self.queue_utilization is not None and self.queue_capacity > 0:
            expected = self.queue_depth / self.queue_capacity
            if abs(self.queue_utilization - expected) > 0.001:
                raise ValueError(
                    f"queue_utilization ({self.queue_utilization}) inconsistent with "
                    f"depth/capacity ({self.queue_depth}/{self.queue_capacity} = {expected:.4f})"
                )
        if self.queue_utilization is not None and self.queue_utilization > 1.0:
            raise ValueError(f"queue_utilization must be <= 1.0, got {self.queue_utilization}")
        return self


class BookMetrics(ContractModel):
    type: Literal["book"] = "book"
    synchronized: bool
    sync_latency_ms: int | None = Field(default=None, ge=0)


class SystemMetrics(ContractModel):
    type: Literal["system"] = "system"
    cpu_percent: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    memory_mb: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    disk_free_gb: float | None = Field(default=None, ge=0, allow_inf_nan=False)


MetricsPayload = Annotated[
    ConnectionMetrics | SequenceMetrics | LatencyMetrics | QueueMetrics | BookMetrics | SystemMetrics,
    Field(discriminator="type"),
]


class TelemetryEnvelope(ContractModel):
    """DRAFT — Telemetry envelope for Gateway and Recorder."""

    schema_version: Literal["telemetry.v1"]
    telemetry_type: TelemetryType
    source_module: NonEmptyText
    source_instance_id: InstanceId
    observed_time_utc_ns: int = Field(..., ge=0)
    market: Market | None = None
    symbol: Symbol | None = None
    metrics: MetricsPayload | None = None
    quality_flags: tuple[QualityFlag, ...] = ()
    stream: Stream | None = None
    connection_id: ConnectionId | None = None
    connection_generation: int | None = Field(default=None, ge=1)
    subscription_id: InstanceId | None = None

    @model_validator(mode="after")
    def _validate_metric_type(self) -> TelemetryEnvelope:
        if self.metrics is not None:
            expected = _TELEMETRY_METRIC_TYPES[self.telemetry_type]
            if self.metrics.type != expected:
                raise ValueError(
                    f"metrics.type '{self.metrics.type}' must match "
                    f"telemetry_type '{self.telemetry_type.value}' (expected '{expected}')"
                )
        return self
