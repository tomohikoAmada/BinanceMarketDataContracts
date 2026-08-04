"""DRAFT — Telemetry contract.

Provides a minimal telemetry envelope shared by Gateway and Recorder.
Uses discriminated payload rather than unrestricted dict[str, Any].
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import Market, QualityFlag  # noqa: TC001
from binance_market_data_contracts.identifiers import Symbol  # noqa: TC001


class TelemetryType(StrEnum):
    CONNECTION = "CONNECTION"
    SEQUENCE = "SEQUENCE"
    LATENCY = "LATENCY"
    QUEUE = "QUEUE"
    BOOK = "BOOK"
    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"


class ConnectionMetrics(ContractModel):
    """Connection-related telemetry data."""

    type: Literal["connection"] = "connection"
    connected: bool
    last_message_age_ms: int | None = Field(default=None, ge=0)
    reconnect_count: int = Field(default=0, ge=0)


class SequenceMetrics(ContractModel):
    """Sequence-related telemetry data."""

    type: Literal["sequence"] = "sequence"
    last_update_id: int | None = Field(default=None, ge=0)
    duplicate_count: int = Field(default=0, ge=0)
    out_of_order_count: int = Field(default=0, ge=0)


class LatencyMetrics(ContractModel):
    """Latency-related telemetry data."""

    type: Literal["latency"] = "latency"
    receive_lag_ms: int | None = Field(default=None, ge=0)
    publish_lag_ms: int | None = Field(default=None, ge=0)


class QueueMetrics(ContractModel):
    """Queue-related telemetry data."""

    type: Literal["queue"] = "queue"
    queue_depth: int = Field(default=0, ge=0)
    dropped: int = Field(default=0, ge=0)


class BookMetrics(ContractModel):
    """Order book-related telemetry data."""

    type: Literal["book"] = "book"
    synchronized: bool
    sync_latency_ms: int | None = Field(default=None, ge=0)


class SystemMetrics(ContractModel):
    """System resource telemetry data."""

    type: Literal["system"] = "system"
    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    memory_mb: float | None = Field(default=None, ge=0)
    disk_free_gb: float | None = Field(default=None, ge=0)


MetricsPayload = Annotated[
    ConnectionMetrics | SequenceMetrics | LatencyMetrics | QueueMetrics | BookMetrics | SystemMetrics,
    Field(discriminator="type"),
]


class TelemetryEnvelope(ContractModel):
    """DRAFT — Telemetry envelope for Gateway and Recorder.

    Uses a discriminated union for metrics payload. Adding a new metric type
    is generally compatible. Changing the discriminator is BREAKING.
    """

    telemetry_type: TelemetryType
    source_module: str = Field(..., description="Source module name (e.g. 'gateway', 'recorder')")
    source_instance_id: str = Field(..., description="Instance identifier")
    observed_time_utc_ns: int | None = Field(default=None, ge=0, description="UTC time of observation (ns)")
    market: Market | None = None
    symbol: Symbol | None = None
    metrics: MetricsPayload | None = Field(default=None, description="Telemetry data payload")
    quality_flags: list[QualityFlag] = Field(
        default_factory=list, description="Quality flags for this telemetry sample"
    )
