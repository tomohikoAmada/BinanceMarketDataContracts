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

```python
from binance_market_data_contracts import DepthUpdate

json_payload = '{"metadata":{...},"first_update_id":1,"final_update_id":2,"bids":[],"asks":[]}'
event = DepthUpdate.model_validate_json(json_payload)
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
python -m binance_market_data_contracts.schema_export
```

Outputs JSON Schema (Draft 2020-12) to `schemas/json/`.

## Fixtures

Golden fixtures live in `fixtures/valid/` and `fixtures/invalid/`.
See `fixtures/manifest.json` for the machine-readable index.

## Tests

```bash
pytest -q
```

## Version policy

Contracts follow `<contract-name>.v<major>` versioning.
Compatible additions (optional fields, new quality flags) do not bump major.
Field removal, renaming, unit changes, or semantic changes are BREAKING.

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
