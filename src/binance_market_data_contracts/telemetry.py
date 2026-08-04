"""DRAFT — Telemetry contract.

Provides a minimal telemetry envelope shared by Gateway and Recorder.
Uses discriminated payloads rather than unrestricted dict[str, Any].
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import Market, QualityFlag
from binance_market_data_contracts.identifiers import InstanceId, Symbol


class TelemetryType(StrEnum):
    CONNECTION = "CONNECTION"
    SEQUENCE = "SEQUENCE"
    LATENCY = "LATENCY"
    QUEUE = "QUEUE"
    BOOK = "BOOK"
    SYSTEM = "SYSTEM"


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


class QueueMetrics(ContractModel):
    type: Literal["queue"] = "queue"
    queue_depth: int = Field(default=0, ge=0)
    dropped: int = Field(default=0, ge=0)


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

    telemetry_type: TelemetryType
    source_module: str = Field(..., min_length=1)
    source_instance_id: InstanceId
    observed_time_utc_ns: int | None = Field(default=None, ge=0)
    market: Market | None = None
    symbol: Symbol | None = None
    metrics: MetricsPayload | None = None
    quality_flags: tuple[QualityFlag, ...] = ()
