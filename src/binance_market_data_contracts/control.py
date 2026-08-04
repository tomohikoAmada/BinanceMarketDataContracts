"""DRAFT — Control contracts.

Defines operational control commands and their results.
Uses discriminated parameter types, not unrestricted dict.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from binance_market_data_contracts.common import ContractModel, NonEmptyText
from binance_market_data_contracts.identifiers import CommandId


class CommandType(StrEnum):
    GET_STATUS = "GET_STATUS"
    VALIDATE_DATA = "VALIDATE_DATA"
    TRIGGER_ARCHIVE = "TRIGGER_ARCHIVE"
    TRIGGER_RESYNC = "TRIGGER_RESYNC"
    GENERATE_DIAGNOSTIC_BUNDLE = "GENERATE_DIAGNOSTIC_BUNDLE"


class CommandStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    TIMED_OUT = "TIMED_OUT"


class GetStatusParameters(ContractModel):
    type: Literal["GET_STATUS"] = "GET_STATUS"


class ValidateDataParameters(ContractModel):
    type: Literal["VALIDATE_DATA"] = "VALIDATE_DATA"
    market: str | None = None
    symbol: str | None = None


class TriggerArchiveParameters(ContractModel):
    type: Literal["TRIGGER_ARCHIVE"] = "TRIGGER_ARCHIVE"
    target_date: str | None = None


class TriggerResyncParameters(ContractModel):
    type: Literal["TRIGGER_RESYNC"] = "TRIGGER_RESYNC"
    market: str | None = None
    symbol: str | None = None


class GenerateDiagnosticBundleParameters(ContractModel):
    type: Literal["GENERATE_DIAGNOSTIC_BUNDLE"] = "GENERATE_DIAGNOSTIC_BUNDLE"
    include_raw: bool = False


CommandParameters = Annotated[
    GetStatusParameters
    | ValidateDataParameters
    | TriggerArchiveParameters
    | TriggerResyncParameters
    | GenerateDiagnosticBundleParameters,
    Field(discriminator="type"),
]


class AuditMetadata(ContractModel):
    requester: NonEmptyText
    source: NonEmptyText = "cli"
    trace_id: str | None = None
    correlation_id: str | None = None


class ControlCommand(ContractModel):
    """DRAFT — Operational control command."""

    command_id: CommandId
    command_type: CommandType
    target: NonEmptyText
    requested_at_utc_ns: int = Field(..., ge=0)
    requester: NonEmptyText
    schema_version: Literal["control-command.v1"] = "control-command.v1"
    parameters: CommandParameters | None = None
    idempotency_key: str | None = None
    timeout_seconds: int | None = Field(default=None, ge=1)


class CommandResult(ContractModel):
    """DRAFT — Result of a control command execution."""

    command_id: CommandId
    status: CommandStatus
    error_code: str | None = None
    error_message: str | None = None
    result_summary: str | None = None
    requested_at_utc_ns: int = Field(..., ge=0)
    executed_at_utc_ns: int | None = Field(default=None, ge=0)
    schema_version: Literal["command-result.v1"] = "command-result.v1"
    audit_metadata: AuditMetadata | None = None
