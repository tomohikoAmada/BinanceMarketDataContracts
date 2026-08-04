"""Base contract model and decimal string types.

All public contracts inherit from ContractModel which enforces:
- frozen (immutable)
- strict (no type coercion)
- extra="forbid" (no unknown fields)
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainValidator


def _validate_price_string(v: object) -> str:
    """Validate a price decimal string: positive (>0), strict format, no scientific notation."""
    if not isinstance(v, str):
        raise ValueError(f"price must be a string, got {type(v).__name__}")
    if not re.match(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", v):
        raise ValueError(
            f"Invalid price format '{v}'. Must match '^(0|[1-9][0-9]*)(\\\\.[0-9]+)?$' "
            f"with value > 0. No leading zeros, trailing dot, leading dot, scientific notation, or whitespace."
        )
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d <= 0:
        raise ValueError(f"price must be > 0, got '{v}'")
    return v


def _validate_quantity_string(v: object) -> str:
    """Validate a quantity decimal string: non-negative (>=0), strict format, no scientific notation."""
    if not isinstance(v, str):
        raise ValueError(f"quantity must be a string, got {type(v).__name__}")
    if not re.match(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", v):
        raise ValueError(
            f"Invalid quantity format '{v}'. Must match '^(0|[1-9][0-9]*)(\\\\.[0-9]+)?$' "
            f"with value >= 0. No leading zeros, trailing dot, leading dot, scientific notation, or whitespace."
        )
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d < 0:
        raise ValueError(f"quantity must be >= 0, got '{v}'")
    return v


def _validate_positive_decimal_string(v: object) -> str:
    """Validate a positive (>0) decimal string."""
    if not isinstance(v, str):
        raise ValueError(f"value must be a string, got {type(v).__name__}")
    if not re.match(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", v):
        raise ValueError(f"Invalid format '{v}'. Must match '^(0|[1-9][0-9]*)(\\\\.[0-9]+)?$' with value > 0.")
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d <= 0:
        raise ValueError(f"value must be > 0, got '{v}'")
    return v


def _validate_non_negative_decimal_string(v: object) -> str:
    """Validate a non-negative (>=0) decimal string."""
    if not isinstance(v, str):
        raise ValueError(f"value must be a string, got {type(v).__name__}")
    if not re.match(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", v):
        raise ValueError(f"Invalid format '{v}'. Must match '^(0|[1-9][0-9]*)(\\\\.[0-9]+)?$' with value >= 0.")
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d < 0:
        raise ValueError(f"value must be >= 0, got '{v}'")
    return v


PriceString = Annotated[str, PlainValidator(_validate_price_string)]
QuantityString = Annotated[str, PlainValidator(_validate_quantity_string)]
PositiveDecimalString = Annotated[str, PlainValidator(_validate_positive_decimal_string)]
NonNegativeDecimalString = Annotated[str, PlainValidator(_validate_non_negative_decimal_string)]


class ContractModel(BaseModel):
    """Base class for all public contracts.

    Enforces:
    - frozen=True: instances are immutable
    - strict=True: no type coercion (str won't accept int)
    - extra="forbid": unknown fields rejected
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )
