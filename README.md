# BinanceMarketDataContracts

Versioned public contracts, schemas, fixtures and architecture decisions for BinanceMarketData.

This package provides two contract strata:

- **Domain Contracts** — Pydantic models for Python-internal data modeling
- **Wire Contracts** — Protobuf/gRPC definitions for cross-language and cross-device communication

## Status

All contracts are **PROPOSED** or **DRAFT**. DRAFT contracts are **not frozen** — fields, semantics, and
structure may change. No contract has been formally ACCEPTED yet.

## Target Languages

The wire protocol is language-neutral. Generated types are available for:

| Role | Language |
|------|----------|
| Gateway Runtime | Undecided (C++, Rust, Go, and Python are all supported by the wire protocol) |
| Python Consumer | Python |
| Go Consumer | Go |
| Rust Consumer | Rust |
| C++ Consumer | C++ |

The Gateway implementation language is **not selected by this repository**. The wire protocol supports all languages listed above. A final decision requires a separate ADR with benchmark evidence.

The Gateway Runtime is **not implemented** in this repository. This package provides only the contract types.

## Installation

```bash
# Domain contracts only (Pydantic + JSON Schema)
python -m pip install -e ".[dev]"

# Domain + Wire contracts (includes protobuf codegen dependencies)
python -m pip install -e ".[dev,wire]"
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

### Domain Contracts (Pydantic)

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

### Wire Contracts (Protobuf) — DRAFT

| Contract | Status | Version |
|----------|--------|---------|
| GatewayStreamMarketSnapshot | DRAFT | v1 |
| GatewayStreamDepthUpdate | DRAFT | v1 |
| GatewayStreamAggTrade | DRAFT | v1 |
| GatewayControlCommand | DRAFT | v1 |

DRAFT wire contracts are **not frozen** and may change. Entry-level gRPC contract metadata
(market, symbol, schema version, stream name, timestamps, quality flags) is defined and
applies across all messages.

### Gateway RPCs

| RPC | Style | Description |
|-----|-------|-------------|
| `SubscribeMarketSnapshots` | Server Streaming | Stream of market state snapshots |
| `SubscribeDepthUpdates` | Server Streaming | Stream of depth update events |
| `SubscribeAggTrades` | Server Streaming | Stream of aggregated trade events |
| `IssueControlCommand` | Unary | Send a control command to the Gateway |

## Proto files

Wire contract definitions live in `proto/binance_market_data/`.

```
proto/
└── binance_market_data/
    ├── common.proto          — shared types, enums, metadata
    ├── market_snapshot.proto — MarketStateSnapshot wire contract
    ├── depth_update.proto    — DepthUpdate wire contract
    ├── agg_trade.proto       — AggTrade wire contract
    ├── control.proto         — ControlCommand wire contract
    ├── gateway.proto         — gRPC service definitions
    └── buf.yaml              — Buf build configuration
```

## Code generation

```bash
buf generate proto
```

Generated Python code is placed in `src/binance_market_data_contracts/wire/generated/`.
Generated files are **never hand-edited**.

## Adapter usage

Explicit adapters bridge Pydantic domain contracts and Protobuf wire contracts:

```python
from binance_market_data_contracts.wire.adapters import (
    depth_update_to_proto,
    depth_update_from_proto,
    agg_trade_to_proto,
    agg_trade_from_proto,
)
from binance_market_data_contracts import DepthUpdate

# Domain → Wire
event = DepthUpdate.model_validate_json(payload)
proto_msg = depth_update_to_proto(event)

# Wire → Domain
event_roundtrip = depth_update_from_proto(proto_msg)
assert event == event_roundtrip
```

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
- gRPC server implementation (Gateway runtime)
- Any server or daemon process

## Related

- `BinanceMarketData_Living_Architecture.md` — full architecture document
- `docs/adr/` — architecture decision records
- `docs/contracts/` — contract semantics and compatibility