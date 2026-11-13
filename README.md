# BinanceMarketDataContracts

Versioned public contracts, schemas, fixtures and architecture decisions for BinanceMarketData.

The package has two contract strata:

- **Domain Contracts** — Pydantic models for Python-internal data modeling
- **Wire Contracts** — Protobuf/gRPC definitions for cross-language communication

## Status

All Domain and Wire contracts remain **PROPOSED** or **DRAFT**; none is formally
ACCEPTED. C1 fixed the currently used internal v1 subset at explicit source and
package pins ([consumer capabilities](docs/contracts/current-capabilities.md)).
That bounded internal agreement does not freeze or promise every unused DRAFT
model.

The C++ message package and the separate gRPC service/stub package are
implemented and merged, but not published. The formal package revision remains
**NOT FORMALLY ASSIGNED** (release gate). Historical delivery identities and
review evidence are in [docs/HISTORY.md](docs/HISTORY.md).

## Wire protocol target languages

The wire protocol is language-neutral. Listing a language does not mean this
repository publishes generated artifacts for it.

| Role | Language | Current artifact availability |
|------|----------|-------------------------------|
| Gateway Runtime | C++ | Implemented in the separate Gateway repository |
| Python Consumer | Python | Generated Protobuf/gRPC artifacts available |
| Go Consumer | Go | Protocol-compatible target; artifacts not published here |
| Rust Consumer | Rust | Protocol-compatible target; artifacts not published here |
| C++ Consumer | C++ | Message and separate gRPC Conan/CMake packages implemented |

Only Python generated wire artifacts are tracked in this repository.

## Installation

```bash
# Domain contracts only (Pydantic + JSON Schema)
python -m pip install -e .

# Wire runtime (generated Protobuf and gRPC imports)
python -m pip install -e ".[wire]"

# Development environment (including code generation and wire runtime)
python -m pip install -e ".[dev,wire]"
```

## C++ packages

- `binance-market-data-contracts-cpp/0.1.0` generates the seven non-service
  message protos and exports `BinanceMarketDataContracts::Protobuf`. Its host
  and build graphs contain no gRPC dependency.
- `binance-market-data-contracts-grpc-cpp/0.1.0` generates only the Gateway
  service and gRPC stubs, links the exact message artifact, and exports
  `BinanceMarketDataContracts::Grpc`.

```cmake
find_package(BinanceMarketDataContracts 0.1.0 EXACT CONFIG REQUIRED COMPONENTS Protobuf)
find_package(BinanceMarketDataContractsGrpc 0.1.0 EXACT CONFIG REQUIRED)
target_link_libraries(my_gateway PRIVATE BinanceMarketDataContracts::Grpc)
```

The exact locked Protobuf generator/runtime is `protobuf/6.33.5`
(`libprotoc 33.5`). Package publication and formal revision assignment remain
release concerns; see [HISTORY](docs/HISTORY.md) for the merged implementation
record.

## Quick start

### JSON input (recommended)

Use `model_validate_json()` to parse JSON payloads. JSON string enum values are
converted to `StrEnum` instances:

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
  "bids": [{"price": "65000.10", "quantity": "1.2500"}],
  "asks": []
}
"""

event = DepthUpdate.model_validate_json(payload)
assert event.metadata.stream.value == "DIFF_DEPTH"
assert event.bids[0].price == "65000.10"
```

### Python object input

`strict=True` means Python construction requires enum instances, not strings:

```python
from binance_market_data_contracts import DepthUpdate, DepthUpdateMetadata, Market, Stream, Venue

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

## Contract inventory

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
| GatewayStatusRequest | DRAFT | v1 |
| ControlCommand / CommandResult | DRAFT | v1 |

### Wire Contracts (Protobuf)

Wire contracts are defined under `src/binance_market_data_contracts/proto/binance_market_data/`.

| Contract group | Status |
|----------------|--------|
| Core Market Wire Contracts | PROPOSED |
| Projection Wire Contracts | PROPOSED |
| Gateway Wire Contracts | DRAFT |
| Telemetry Wire Contract | DRAFT |

DRAFT wire contracts are **not frozen** and may change. `TelemetryEnvelope.metrics`
is required in `telemetry.v1`; its concrete metric type must match
`telemetry_type`.

### Gateway RPCs

| RPC | Style | Description |
|-----|-------|-------------|
| `SubscribeEvents` | Server Streaming | Contiguous real-time depth, aggTrade and bookTicker events |
| `SubscribeOrderBook` | Server Streaming | Order book snapshot followed by applicable depth updates |
| `SubscribeMarketState` | Server Streaming | Declared but currently UNIMPLEMENTED by the Gateway runtime |
| `GetGatewayStatus` | Unary | One-shot Gateway operational status |

The Gateway repository owns runtime configuration limits, admission rules and
milestone status. Contracts only owns the schemas and service contract.

## Proto files

```text
src/binance_market_data_contracts/proto/binance_market_data/
├── common/v1/
│   ├── enums.proto
│   ├── metadata.proto
│   └── identifiers.proto
├── market/v1/
│   └── market_events.proto
├── projection/v1/
│   └── snapshots.proto
├── gateway/v1/
│   ├── gateway_messages.proto
│   └── gateway_service.proto
└── telemetry/v1/
    └── telemetry.proto
```

`buf.yaml` is at the repository root, outside the Proto source tree.

## Code generation

```bash
python -m binance_market_data_contracts.proto_codegen
python -m binance_market_data_contracts.proto_codegen --check
```

Generated Python code is placed in `src/binance_market_data/` and is **never
hand-edited**.

## Adapter usage

Explicit adapters bridge Pydantic domain contracts and Protobuf wire contracts.
Adapter pairs follow the `<contract>_to_pb` / `<contract>_from_pb` convention:

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
| `gateway_status_request_to_pb` | `gateway_status_request_from_pb` |
| `telemetry_envelope_to_pb` | `telemetry_envelope_from_pb` |

```python
from binance_market_data_contracts import DepthUpdate
from binance_market_data_contracts.wire.adapters import depth_update_from_pb, depth_update_to_pb

event = DepthUpdate.model_validate_json(payload)
proto_msg = depth_update_to_pb(event)
assert depth_update_from_pb(proto_msg) == event
```

Adapters copy fields explicitly; there is no reflection, `model_dump()` mapping
or silent coercion. Optional presence is preserved, and an explicitly present
empty value that violates a domain constraint is rejected rather than treated
as absence.

## Schema export

```bash
python -m binance_market_data_contracts.schema_export --output schemas/json
```

Outputs JSON Schema (Draft 2020-12) to `schemas/json/contracts/` with a catalog
at `schemas/json/contract-catalog.json`.

## Fixtures

Golden fixtures live in `fixtures/valid/` and `fixtures/invalid/`; see
`fixtures/manifest.json` for the machine-readable index. Shared producer oracles
live in `fixtures/integration/` and are test specifications, not new contracts.

## Tests

```bash
pytest -q
```

## Version policy

Contracts follow `<contract-name>.v<major>` versioning. Compatible optional wire
additions do not bump the major. Binary unknown-enum preservation does not imply
strict Domain/JSON support for new values; see
[docs/contracts/compatibility_policy.md](docs/contracts/compatibility_policy.md).
Field removal, renaming, unit changes or semantic changes are BREAKING.

Every registered contract requires `schema_version` in serialized form; event
metadata requires `stream`.

## Breaking change policy

Breaking changes require an ADR, DEPRECATED marking, a new version with a
migration guide, and updated fixtures, schemas and tests.

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

- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — current orientation
- [docs/HISTORY.md](docs/HISTORY.md) — compressed historical delivery record
- [ARCHITECTURE.md](ARCHITECTURE.md) — repository architecture entry point
- [BinanceMarketData_Living_Architecture.md](BinanceMarketData_Living_Architecture.md) — top-level boundaries
- [docs/adr/](docs/adr/) — architecture decision records
- [docs/contracts/](docs/contracts/) — contract semantics and compatibility
