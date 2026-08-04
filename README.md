# BinanceMarketDataContracts

Versioned public contracts, schemas, fixtures and architecture decisions for BinanceMarketData.

## Status

All contracts are **PROPOSED** or **DRAFT** pending architecture review.
No contract has been formally ACCEPTED yet.

## Installation

```bash
python -m pip install -e ".[dev]"
```

## Quick start

### JSON input (recommended)

Use `model_validate_json()` to parse JSON payloads. JSON string enum values
are automatically converted to StrEnum instances:

```python
from binance_market_data_contracts import DepthUpdate

payload = """
{
  "metadata": {
    "venue": "BINANCE",
    "market": "SPOT",
    "symbol": "BTCUSDT",
    "producer": "gateway-adapter",
    "producer_version": "0.1.0",
    "connection_id": "gateway-btcusdt-001",
    "stream": "DIFF_DEPTH",
    "schema_version": "depth-update.v1",
    "exchange_event_time_ms": 1690000000123,
    "receive_time_utc_ns": 1690000000123000000,
    "receive_monotonic_ns": 1000000000,
    "quality_flags": []
  },
  "first_update_id": 1001,
  "final_update_id": 1002,
  "previous_final_update_id": 1000,
  "bids": [
    {
      "price": "65000.10",
      "quantity": "1.2500"
    }
  ],
  "asks": []
}
"""

event = DepthUpdate.model_validate_json(payload)

assert event.metadata.stream.value == "DIFF_DEPTH"
assert event.metadata.schema_version == "depth-update.v1"
assert event.bids[0].price == "65000.10"
```

### Python object input

Due to `strict=True`, Python construction requires Enum instances:

```python
from binance_market_data_contracts import DepthUpdate, DepthUpdateMetadata, Venue, Market, Stream

metadata = DepthUpdateMetadata(
    venue=Venue.BINANCE,
    market=Market.SPOT,
    symbol="BTCUSDT",
    stream=Stream.DIFF_DEPTH,
    schema_version="depth-update.v1",
    producer="gateway-adapter",
    producer_version="0.1.0",
    connection_id="gateway-btcusdt-001",
)

event = DepthUpdate(metadata=metadata, first_update_id=1001, final_update_id=1002)
```

## Contracts

| Contract | Status | Version |
|----------|--------|---------|
| DepthUpdate | PROPOSED | v1 |
| AggTrade | PROPOSED | v1 |
| BookTicker | PROPOSED | v1 |
| ExchangeDepthSnapshot | PROPOSED | v1 |
| LocalOrderBookSnapshot | PROPOSED | v1 |
| MarketStateSnapshot | PROPOSED | v1 |
| DataHealthSnapshot | PROPOSED | v1 |
| HistoricalDatasetDescriptor | DRAFT | v1 |
| ReplayQuery | DRAFT | v1 |
| Telemetry | DRAFT | v1 |
| ControlCommand / CommandResult | DRAFT | v1 |

## Schema export

```bash
python -m binance_market_data_contracts.schema_export --output schemas/json
```

Outputs JSON Schema (Draft 2020-12) to `schemas/json/contracts/` with a catalog
at `schemas/json/contract-catalog.json`.

## Fixtures

Golden fixtures live in `fixtures/valid/` and `fixtures/invalid/`.
See `fixtures/manifest.json` for the machine-readable index with validation scope
and expected error metadata.

## Tests

```bash
pytest -q
```

## Version policy

Contracts follow `<contract-name>.v<major>` versioning.
Compatible additions (optional fields, new quality flags) do not bump major.
Field removal, renaming, unit changes, or semantic changes are BREAKING.

Every registered contract explicitly requires `schema_version` in serialized form.
Event metadata explicitly requires `stream`.

## Breaking change policy

Breaking changes require:
1. ADR documenting the change
2. DEPRECATED marking on the old version
3. New version with migration guide
4. Updated fixtures, schema, and tests

## What this package does NOT do

- Network connections to Binance
- Database or file persistence
- Trading, account, or order management
- Real-time data streaming
- Historical data storage or retrieval
- UI or visualization

## Related

- `BinanceMarketData_Living_Architecture.md` — full architecture document
- `docs/adr/` — architecture decision records
- `docs/contracts/` — contract semantics and compatibility