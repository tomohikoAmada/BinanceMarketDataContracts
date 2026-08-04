"""Base contract model and validated string types.

All public contracts inherit from ContractModel which enforces:
- frozen=True (immutable, including nested collections via tuple)
- strict=True (no type coercion)
- extra="forbid" (no unknown fields)

Decimal string types use Pydantic StringConstraints + AfterValidator
to ensure both Python runtime validation AND rich JSON Schema output.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    StringConstraints,
)

DECIMAL_PATTERN = r"^(0|[1-9][0-9]*)(\.[0-9]+)?$"
POSITIVE_DECIMAL_PATTERN = r"^(?:[1-9][0-9]*(?:\.[0-9]+)?|0\.[0-9]*[1-9][0-9]*)$"
SIGNED_DECIMAL_PATTERN = r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$"
NON_EMPTY_TEXT_PATTERN = r"^\S(?:.*\S)?$"
IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"


def _validate_price_positive(v: str) -> str:
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d <= 0:
        raise ValueError(f"price must be > 0, got '{v}'")
    return v


def _validate_quantity_non_negative(v: str) -> str:
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d < 0:
        raise ValueError(f"quantity must be >= 0, got '{v}'")
    return v


def _validate_quantity_positive(v: str) -> str:
    try:
        d = Decimal(v)
    except InvalidOperation as e:
        raise ValueError(f"Invalid Decimal value: '{v}'") from e
    if d <= 0:
        raise ValueError(f"quantity must be > 0, got '{v}'")
    return v


def _validate_finite_signed_decimal(v: str) -> str:
    value = Decimal(v)
    if not value.is_finite():
        raise ValueError("value must be finite")
    if v.startswith("-") and value == 0:
        raise ValueError("negative zero is not allowed")
    return v


DecimalText = Annotated[
    str,
    StringConstraints(pattern=DECIMAL_PATTERN, strip_whitespace=False),
]

PositiveDecimalText = Annotated[
    str,
    StringConstraints(pattern=POSITIVE_DECIMAL_PATTERN, strip_whitespace=False),
]

SignedDecimalText = Annotated[
    str,
    StringConstraints(pattern=SIGNED_DECIMAL_PATTERN, strip_whitespace=False),
]

PriceString = Annotated[PositiveDecimalText, AfterValidator(_validate_price_positive)]
QuantityString = Annotated[DecimalText, AfterValidator(_validate_quantity_non_negative)]
PositiveQuantityString = Annotated[PositiveDecimalText, AfterValidator(_validate_quantity_positive)]
SignedDecimalString = Annotated[SignedDecimalText, AfterValidator(_validate_finite_signed_decimal)]

NonEmptyText = Annotated[
    str,
    StringConstraints(min_length=1, max_length=256, pattern=NON_EMPTY_TEXT_PATTERN, strip_whitespace=False),
]


class ContractModel(BaseModel):
    """Base class for all public contracts.

    Enforces:
    - frozen=True: instances are immutable
    - strict=True: no type coercion (e.g. str won't accept int)
    - extra="forbid": unknown fields rejected

    For JSON input, use model_validate_json() which accepts string enum values.
    For Python dict input with strict=True, use Enum instances for enum fields.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
    )
