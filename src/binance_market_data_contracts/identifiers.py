"""Identifier types for BinanceMarketData contracts.

Provides strict, validated types for identifiers used across contracts.
"""

import re
from typing import Annotated

from pydantic import PlainValidator


def _validate_symbol(v: object) -> str:
    if not isinstance(v, str):
        raise ValueError(f"symbol must be a string, got {type(v).__name__}")
    if not re.match(r"^[A-Z0-9]{2,20}$", v):
        raise ValueError(f"Invalid symbol format '{v}'. Must be 2-20 uppercase alphanumeric characters.")
    return v


def _validate_connection_id(v: object) -> str:
    if not isinstance(v, str):
        raise ValueError(f"connection_id must be a string, got {type(v).__name__}")
    stripped = v.strip()
    if not stripped:
        raise ValueError("connection_id must not be empty")
    if len(stripped) > 128:
        raise ValueError(f"connection_id too long ({len(stripped)} > 128)")
    return stripped


def _validate_request_id(v: object) -> str:
    if not isinstance(v, str):
        raise ValueError(f"request_id must be a string, got {type(v).__name__}")
    stripped = v.strip()
    if not stripped:
        raise ValueError("request_id must not be empty")
    if len(stripped) > 128:
        raise ValueError(f"request_id too long ({len(stripped)} > 128)")
    return stripped


Symbol = Annotated[str, PlainValidator(_validate_symbol)]
ConnectionId = Annotated[str, PlainValidator(_validate_connection_id)]
RequestId = Annotated[str, PlainValidator(_validate_request_id)]
