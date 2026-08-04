"""DRAFT — History contracts.

Describes historical datasets and replay queries.
All time fields use explicit unit suffixes.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from binance_market_data_contracts.common import ContractModel, NonEmptyText
from binance_market_data_contracts.enums import (
    GapPolicy,
    Market,
    MissingExchangeTimePolicy,
    ReliabilityState,
    ReplayClock,
    Stream,
)
from binance_market_data_contracts.identifiers import DatasetId, Symbol


class HistoricalDatasetDescriptor(ContractModel):
    """DRAFT — Describes a queryable, replayable historical dataset."""

    dataset_id: DatasetId
    market: Market
    symbol: Symbol
    streams: tuple[Stream, ...] = ()
    start_time_utc_ns: int | None = Field(default=None, ge=0)
    end_time_utc_ns: int | None = Field(default=None, ge=0)
    schema_version: Literal["historical-dataset-descriptor.v1"] = "historical-dataset-descriptor.v1"
    producer: NonEmptyText = "recorder"
    producer_version: NonEmptyText
    source_manifests: tuple[str, ...] = ()
    gap_count: int = Field(default=0, ge=0)
    gap_intervals: tuple[str, ...] = ()
    partitions: int = Field(default=1, ge=1)
    manifest_hash: str | None = None
    query_capabilities: tuple[str, ...] = ()
    replay_capabilities: tuple[str, ...] = ()
    reliability_state: ReliabilityState = ReliabilityState.UNKNOWN

    @model_validator(mode="after")
    def _validate_times(self) -> HistoricalDatasetDescriptor:
        if self.start_time_utc_ns is not None and self.end_time_utc_ns is not None:
            if self.start_time_utc_ns > self.end_time_utc_ns:
                raise ValueError("start_time_utc_ns must be <= end_time_utc_ns")
        return self


class ReplayQuery(ContractModel):
    """DRAFT — Describes a historical replay request.

    Ordering rules are versioned via ordering_version.
    """

    dataset_id: DatasetId
    start_time_utc_ns: int | None = Field(default=None, ge=0)
    end_time_utc_ns: int | None = Field(default=None, ge=0)
    clock: ReplayClock = ReplayClock.RECEIVE_TIME
    missing_exchange_time_policy: MissingExchangeTimePolicy = MissingExchangeTimePolicy.EXCLUDE
    gap_policy: GapPolicy = GapPolicy.INCLUDE
    streams: tuple[Stream, ...] | None = None
    ordering_version: NonEmptyText = "1"

    @model_validator(mode="after")
    def _validate_times(self) -> ReplayQuery:
        if self.start_time_utc_ns is not None and self.end_time_utc_ns is not None:
            if self.start_time_utc_ns > self.end_time_utc_ns:
                raise ValueError("start_time_utc_ns must be <= end_time_utc_ns")
        return self
