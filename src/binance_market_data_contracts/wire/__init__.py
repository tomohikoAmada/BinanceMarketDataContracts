"""Wire module — Pydantic ↔ Protobuf adapters.

Generated protobuf code lives in wire/generated/.
This module adjusts the import path so that 'binance_market_data' package
resolves correctly from the generated directory.
"""

import sys
from pathlib import Path

_GENERATED_DIR = str(Path(__file__).resolve().parent / "generated")
if _GENERATED_DIR not in sys.path:
    sys.path.insert(0, _GENERATED_DIR)
