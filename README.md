# BinanceMarketDataContracts

Versioned public contracts, schemas, fixtures and architecture decisions for BinanceMarketData.

This package provides two contract strata:

- **Domain Contracts** — Pydantic models for Python-internal data modeling
- **Wire Contracts** — Protobuf/gRPC definitions for cross-language and cross-device communication

## Status

All contracts are **PROPOSED** or **DRAFT**. DRAFT contracts are **not frozen** — fields, semantics, and
structure may change. No contract has been formally ACCEPTED yet.

The C-M4-001 architecture is **APPROVED** and ADR-0009 is **ACCEPTED** after an independent
architecture review with zero blocking findings. Implementation is **NOT STARTED** and C-M4-001
remains **OPEN / BLOCKING** for Projection M4. No C++ package, CMake target, Conan recipe, or
generated C++ artifact is provided by this baseline.

## Wire Protocol Target Languages

The wire protocol is language-neutral and can be consumed by implementations in the following
target languages. Listing a language here does not mean that this repository currently publishes
generated artifacts for that language.

| Role | Language | Current artifact availability |
|------|----------|-------------------------------|
| Gateway Runtime | Undecided: C++, Rust, Go, or Python | Runtime not implemented |
| Python Consumer | Python | Generated Protobuf/gRPC artifacts available |
| Go Consumer | Go | Protocol-compatible target; artifacts not published here |
| Rust Consumer | Rust | Protocol-compatible target; artifacts not published here |
| C++ Consumer | C++ | Planned through C-M4-001; package not yet implemented |

The currently tracked generated wire artifacts are Python artifacts.

The C++ generated message package, exported CMake target, Conan package, and installable C++
headers are not currently available. They require the future C-M4-001 implementation.

The Gateway implementation language is **not selected by this repository**. The wire protocol supports all languages listed above. A final decision requires a separate ADR with benchmark evidence.

The Gateway Runtime is **not implemented** in this repository. This package provides only the contract types.

## Installation

```bash
# Domain contracts only (Pydantic + JSON Schema)
python -m pip install -e .

# Wire runtime (generated Protobuf and gRPC imports)
python -m pip install -e ".[wire]"

# Development environment (including code generation and wire runtime)
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

### Wire Contracts (Protobuf)

Wire contracts are defined in proto files under `src/binance_market_data_contracts/proto/binance_market_data/`:

| Contract group | Status |
|----------------|--------|
| Core Market Wire Contracts | PROPOSED |
| Projection Wire Contracts | PROPOSED |
| Gateway Wire Contracts | DRAFT |
| Telemetry Wire Contract | DRAFT |

DRAFT wire contracts are **not frozen** and may change.

### Gateway RPCs

| RPC | Style | Description |
|-----|-------|-------------|
| `SubscribeEvents` | Server Streaming | Contiguous real-time event stream (DepthUpdate, AggTrade, BookTicker) |
| `SubscribeOrderBook` | Server Streaming | Order book snapshot + diff stream |
| `SubscribeMarketState` | Server Streaming | Latest market state updates |
| `GetGatewayStatus` | Unary | One-shot Gateway operational status |

## Proto files

Wire contract definitions live in `src/binance_market_data_contracts/proto/binance_market_data/`.

```
src/binance_market_data_contracts/proto/binance_market_data/
├── common/v1/
│   ├── enums.proto       — shared enumerations
│   ├── metadata.proto    — event and envelope metadata
│   └── identifiers.proto — identifiers (ConnectionId, Symbol, etc.)
├── market/v1/
│   └── market_events.proto  — DepthUpdate, AggTrade, BookTicker, ExchangeDepthSnapshot
├── projection/v1/
│   └── snapshots.proto      — MarketStateSnapshot, LocalOrderBookSnapshot, DataHealthSnapshot
├── gateway/v1/
│   ├── gateway_messages.proto — Gateway request/response messages
│   └── gateway_service.proto  — gRPC service definitions
└── telemetry/v1/
    └── telemetry.proto        — Telemetry metrics and envelope
```

`buf.yaml` is located at the repository root, outside the Proto source tree.

## Code generation

```bash
python -m binance_market_data_contracts.proto_codegen
python -m binance_market_data_contracts.proto_codegen --check
```

Generated Python code is placed in `src/binance_market_data/`.
Generated files are **never hand-edited**.

## Adapter usage

Explicit adapters bridge Pydantic domain contracts and Protobuf wire contracts.
Key adapter pairs follow the `<contract>_to_pb` / `<contract>_from_pb` naming convention:

| Domain → Wire | Wire → Domain |
|---|---|
| `depth_update_to_pb` | `depth_update_from_pb` |
| `agg_trade_to_pb` | `agg_trade_from_pb` |
| `book_ticker_to_pb` | `book_ticker_from_pb` |
| `exchange_depth_snapshot_to_pb` | `exchange_depth_snapshot_from_pb` |
| `market_state_snapshot_to_pb` | `market_state_snapshot_from_pb` |
| `local_order_book_snapshot_to_pb` | `local_order_book_snapshot_from_pb` |
| `data_health_snapshot_to_pb` | `data_health_snapshot_from_pb` |
| `gateway_event_envelope_to_pb` | `gateway_event_envelope_from_pb` |
| `gateway_status_snapshot_to_pb` | `gateway_status_snapshot_from_pb` |
| `order_book_stream_item_to_pb` | `order_book_stream_item_from_pb` |
| `market_state_stream_item_to_pb` | `market_state_stream_item_from_pb` |
| `event_subscription_request_to_pb` | `event_subscription_request_from_pb` |
| `telemetry_envelope_to_pb` | `telemetry_envelope_from_pb` |

Example usage:

```python
from binance_market_data_contracts.wire.adapters import (
    depth_update_to_pb,
    depth_update_from_pb,
)
from binance_market_data_contracts import DepthUpdate

# Domain → Wire
event = DepthUpdate.model_validate_json(payload)
proto_msg = depth_update_to_pb(event)

# Wire → Domain
event_roundtrip = depth_update_from_pb(proto_msg)
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
- `docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md` — approved Contracts-owned C++ package architecture
- `docs/adr/ADR-0009-cpp-protobuf-package.md` — accepted C++ package ownership decision
