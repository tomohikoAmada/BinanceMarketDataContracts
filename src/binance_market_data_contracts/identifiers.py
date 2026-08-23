"""Identifier types for BinanceMarketData contracts."""

from typing import Annotated

from pydantic import BeforeValidator, Field, StringConstraints

from binance_market_data_contracts.common import IDENTIFIER_PATTERN

_SYMBOL_PATTERN = r"^[^\u0000-\u0020\u007F]+$"
_SYMBOL_JSON_SCHEMA_PATTERN = r"^(?![\s\S]*[\u0000-\u0020\u007F])[\s\S]+$"


def _validate_symbol_unicode_scalars(value: object) -> object:
    """Reject lone surrogates so every accepted symbol has a strict UTF-8 encoding."""
    if isinstance(value, str) and any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError("symbol must contain only Unicode scalar values")
    return value


Symbol = Annotated[
    str,
    StringConstraints(min_length=1, pattern=_SYMBOL_PATTERN, strip_whitespace=False),
    BeforeValidator(_validate_symbol_unicode_scalars),
    Field(json_schema_extra={"pattern": _SYMBOL_JSON_SCHEMA_PATTERN}),
]

NonEmptyIdentifier = Annotated[
    str,
    StringConstraints(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN, strip_whitespace=False),
]

ConnectionId = NonEmptyIdentifier
RequestId = NonEmptyIdentifier
DatasetId = NonEmptyIdentifier
CommandId = NonEmptyIdentifier
InstanceId = NonEmptyIdentifier
SnapshotId = NonEmptyIdentifier
GatewayInstanceId = NonEmptyIdentifier
SubscriptionId = NonEmptyIdentifier
