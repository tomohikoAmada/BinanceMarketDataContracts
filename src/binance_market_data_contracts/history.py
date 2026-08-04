"""DRAFT — History contracts.

These contracts describe historical datasets and replay queries.
They are in DRAFT status pending alignment with Recorder/History implementation.
"""

from __future__ import annotations

from pydantic import Field

from binance_market_data_contracts.common import ContractModel
from binance_market_data_contracts.enums import Market, ReliabilityState, Stream
from binance_market_data_contracts.identifiers import Symbol  # noqa: TC001


class HistoricalDatasetDescriptor(ContractModel):
    """DRAFT — Describes a queryable, replayable historical dataset.

    Does not expose archive mountpoints, catalog tables, or internal file paths.
    """

    dataset_id: str = Field(..., description="Unique identifier for this dataset")
    market: Market
    symbol: Symbol
    streams: list[Stream] = Field(..., description="Streams included in this dataset")
    start_time: str | None = Field(default=None, description="Dataset start time (ISO-8601 UTC)")
    end_time: str | None = Field(default=None, description="Dataset end time (ISO-8601 UTC)")
    schema_version: str = Field(..., description="Contract schema version")
    producer: str = Field(default="recorder", description="Producer module")
    producer_version: str = Field(..., description="Producer version")
    source_manifests: list[str] = Field(default_factory=list, description="Source manifest references")
    gap_count: int = Field(default=0, ge=0, description="Number of gaps in the dataset")
    gap_intervals: list[str] = Field(default_factory=list, description="Gap interval descriptions (ISO-8601 pairs)")
    partitions: int = Field(default=1, ge=1, description="Number of partitions")
    manifest_hash: str | None = Field(default=None, description="Hash of the dataset manifest")
    query_capabilities: list[str] = Field(
        default_factory=list, description="Supported query types (e.g. 'time_range', 'seek')"
    )
    replay_capabilities: list[str] = Field(
        default_factory=list, description="Supported replay modes (e.g. 'receive_time_order', 'exchange_time_order')"
    )
    reliability_state: ReliabilityState = Field(
        default=ReliabilityState.UNKNOWN, description="Overall reliability assessment"
    )


class ReplayQuery(ContractModel):
    """DRAFT — Describes a historical replay request.

    Ordering rules are versioned via ordering_version.
    """

    dataset_id: str = Field(..., description="Dataset identifier to replay")
    start: str | None = Field(default=None, description="Replay start position (ISO-8601 or seek key)")
    end: str | None = Field(default=None, description="Replay end position (ISO-8601 or seek key)")
    clock: str = Field(
        default="receive_time", description="Clock used for ordering (e.g. 'receive_time', 'exchange_time')"
    )
    missing_exchange_time_policy: str = Field(
        default="skip",
        description="Policy for events with missing exchange time: 'skip', 'error', 'use_receive_time'",
    )
    gap_policy: str = Field(
        default="report",
        description="Policy for gaps: 'report', 'skip_gap', 'abort'",
    )
    streams: list[Stream] | None = Field(default=None, description="Streams to replay (None = all available)")
    ordering_version: str = Field(default="1", description="Version of the ordering rules to apply")
