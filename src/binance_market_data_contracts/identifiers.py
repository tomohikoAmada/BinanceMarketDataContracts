"""Identifier types for BinanceMarketData contracts.

All identifier types use StringConstraints to ensure JSON Schema output
includes minLength, maxLength, and pattern where applicable.
"""

from typing import Annotated

from pydantic import StringConstraints

from binance_market_data_contracts.common import IDENTIFIER_PATTERN

Symbol = Annotated[
    str,
    StringConstraints(min_length=2, max_length=20, pattern=r"^[A-Z0-9]+$", strip_whitespace=False),
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
