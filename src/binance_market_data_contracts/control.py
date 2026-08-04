"""DRAFT — Control contracts.

Defines operational control commands and their results.
These are read-only operational commands — no trading, account, or strategy commands.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from binance_market_data_contracts.common import ContractModel


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


class ControlCommand(ContractModel):
    """DRAFT — Operational control command.

    Commands are limited to operational actions:
    status queries, data validation, archive triggering, resync, and diagnostics.

    Trading, account, position, and strategy commands are FORBIDDEN.
    """

    command_id: str = Field(..., description="Unique command identifier")
    command_type: CommandType
    target: str = Field(..., description="Target module or resource")
    requested_at: str = Field(..., description="ISO-8601 UTC timestamp when the command was requested")
    requester: str = Field(..., description="Identity of the requester (user or system)")
    schema_version: str = Field(default="control-command.v1", description="Contract schema version")
    parameters: dict[str, str] | None = Field(
        default=None,
        description="Command parameters as key-value pairs. Values are strings for schema stability.",
    )
    idempotency_key: str | None = Field(
        default=None, description="Idempotency key — duplicated commands with same key have no effect"
    )
    timeout_seconds: int | None = Field(default=None, ge=1, description="Command timeout in seconds")


class CommandResult(ContractModel):
    """DRAFT — Result of a control command execution."""

    command_id: str = Field(..., description="Command identifier matching the request")
    status: CommandStatus
    error_code: str | None = Field(default=None, description="Machine-readable error code on failure")
    error_message: str | None = Field(default=None, description="Human-readable error description on failure")
    result_summary: str | None = Field(default=None, description="Summary of the command result")
    requested_at: str
    executed_at: str | None = Field(default=None, description="ISO-8601 UTC timestamp when the command completed")
    schema_version: str = Field(default="command-result.v1", description="Contract schema version")
    audit_metadata: dict[str, str] | None = Field(
        default=None,
        description="Audit trail metadata (keys and values are strings for schema stability)",
    )
