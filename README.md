# BinanceMarketDataContracts

Versioned public contracts, schemas, fixtures and architecture decisions for BinanceMarketData.

This package provides two contract strata:

- **Domain Contracts** — Pydantic models for Python-internal data modeling
- **Wire Contracts** — Protobuf/gRPC definitions for cross-language and cross-device communication

## Status

All contracts are **PROPOSED** or **DRAFT**. DRAFT contracts are **not frozen** — fields, semantics, and
structure may change. No contract has been formally ACCEPTED yet.

The C-M4-001 architecture is **APPROVED** and ADR-0009 is **ACCEPTED** after an independent
architecture review with zero blocking findings. The implementation is **COMPLETE / MERGED**;
C-M4-001 was merged into Contracts main by commit
`67ee1bf69fad980d114cfa278c3a6ffe310a4d7a`. Its independent implementation re-review was approved
(IIR-1 through IIR-5 CLOSED; reviewed CI `31167981350` — 15/15 PASS).
The Contracts-owned CMake and Conan C++ message package exists at
`binance-market-data-contracts-cpp/0.1.0` and is not published. The formal package revision
remains **NOT FORMALLY ASSIGNED** (release gate). Projection M4 is **COMPLETE** in the separate
`BinanceMarketDataProjection` repository. Gateway runtime is implemented in the separate
`BinanceMarketDataGateway` repository; Contracts does not own that runtime.

## Wire Protocol Target Languages

The wire protocol is language-neutral and can be consumed by implementations in the following
target languages. Listing a language here does not mean that this repository currently publishes
generated artifacts for that language.

| Role | Language | Current artifact availability |
|------|----------|-------------------------------|
| Gateway Runtime | C++ | Implemented in the separate Gateway repository; this package supplies its contracts |
| Python Consumer | Python | Generated Protobuf/gRPC artifacts available |
| Go Consumer | Go | Protocol-compatible target; artifacts not published here |
| Rust Consumer | Rust | Protocol-compatible target; artifacts not published here |
| C++ Consumer | C++ | C-M4-001 package implemented and merged; publication pending |

The currently tracked generated wire artifacts are Python artifacts.

The C++ message artifact generates seven non-service message sources as build outputs and installs
their headers with the exported target `BinanceMarketDataContracts::Protobuf`. Its Conan host and
build graphs contain no gRPC dependency. The separate
`binance-market-data-contracts-grpc-cpp/0.1.0` artifact generates only the Gateway service and gRPC
stubs and exports `BinanceMarketDataContracts::Grpc`. Generated `.pb.cc` and `.pb.h` files are not
committed as primary sources, and the gRPC artifact links the one base message target rather than
generating a second message symbol set.

Contracts remains wire-language-neutral and does not own the Gateway implementation-language
decision. The accepted cross-repository M6 authority currently selects C++ for
`BinanceMarketDataGateway`; the wire protocol continues to support all languages listed above.

The Gateway Runtime is outside this repository. This package provides the contract types and the
separate C++ gRPC service/stub artifact consumed by Gateway.

## Current cross-repository Gateway orientation

The separate Gateway repository has completed G0-G11, post-G11 runtime
productization, recovery observability, performance instrumentation, and the
accepted post-G11 performance baseline. Its ordinary daemon is the fixed
two-product `bmd-gatewayd` for Spot BTCUSDT and USD-M perpetual BTCUSDT, with
`SubscribeOrderBook`, `SubscribeEvents`, and `GetGatewayStatus` implemented.
Contracts remains the owner of the public schemas and C++ artifacts; it has not
implemented those Gateway features. Contracts also declares `SubscribeMarketState`,
which the current Gateway service does not implement. That is nonblocking future
contract/implementation surface reconciliation debt, not a DOC-ALIGN-01 schema
change. Domain and Wire contracts remain PROPOSED or DRAFT, and formal package
revision/publication remains separately gated.

## Installation

```bash
# Domain contracts only (Pydantic + JSON Schema)
python -m pip install -e .

# Wire runtime (generated Protobuf and gRPC imports)
python -m pip install -e ".[wire]"

# Development environment (including code generation and wire runtime)
python -m pip install -e ".[dev,wire]"
```

### C++ candidate package

The candidate Conan coordinate is `binance-market-data-contracts-cpp/0.1.0`. Its locked host and
build dependency is `protobuf/6.33.5` at recipe revision
`ca5ff466767b31a1b496ec60247e105c`; the generator reports `libprotoc 33.5`. Runtime flavor (`full`)
and runtime linkage (`static` or `shared`) are exposed as separate installed metadata fields. Exact
Conan RREV, package ID, PREV, profile identity, and artifact hashes are emitted after package
creation in `c-m4-001-artifact-provenance.json`; they are deliberately not embedded in the
hash-covered package payload. A CMake consumer uses:

```cmake
find_package(BinanceMarketDataContracts CONFIG REQUIRED COMPONENTS Protobuf)
target_link_libraries(my_target PRIVATE BinanceMarketDataContracts::Protobuf)
```

A Gateway/service consumer additionally installs
`binance-market-data-contracts-grpc-cpp/0.1.0` and uses its separate CMake package while retaining
the frozen target namespace:

```cmake
find_package(BinanceMarketDataContracts 0.1.0 EXACT CONFIG REQUIRED COMPONENTS Protobuf)
find_package(BinanceMarketDataContractsGrpc 0.1.0 EXACT CONFIG REQUIRED)
target_link_libraries(my_gateway PRIVATE BinanceMarketDataContracts::Grpc)
```

`conan.lock` pins the message-only graph. `grpc/conan.lock` independently pins the gRPC artifact's
host/build graph and exact base message RREV. Both recipes require a clean checkout and fail closed
when the exported recipe cannot receive an exact source revision. A local static build is:

```bash
test -z "$(git status --porcelain)" || { echo "Contracts checkout must be clean" >&2; exit 1; }
export BMD_CONTRACTS_SOURCE_REVISION="$(git rev-parse HEAD)"
conan create . --build=missing --lockfile=conan.lock \
  -pr:h=profiles/conan/cpp20 -pr:b=profiles/conan/cpp20 -o:h '&:shared=False'
conan create conanfile_grpc.py --test-folder=test_package_grpc \
  --build=missing --lockfile=grpc/conan.lock \
  -pr:h=profiles/conan/cpp20 -pr:b=profiles/conan/cpp20 -o:h '&:shared=False'
```

CI injects its already-checked-out `github.sha` through `BMD_CONTRACTS_SOURCE_REVISION`; local
builds must set it explicitly as above. The SHA is provenance, not exported recipe content, so a
lock-refresh commit cannot recursively change the base RREV that the lock records.

The Schema Fingerprint Algorithm Version 1 digest is
`33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` and is formally **APPROVED**
as the C-M4-001 M4 schema fingerprint. Package revision is **NOT FORMALLY ASSIGNED** (assignment
gate: release) and release-mode configuration fails closed until a formal revision is provided.

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
| GatewayStatusRequest | DRAFT | v1 |
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

`TelemetryEnvelope.metrics` is required in `telemetry.v1`; its concrete metric type must match
`telemetry_type`.

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
| `gateway_status_request_to_pb` | `gateway_status_request_from_pb` |
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

- `docs/CURRENT_STATE.md` — current repository orientation for humans and AI reviewers
- `BinanceMarketData_Living_Architecture.md` — full architecture document
- `docs/adr/` — architecture decision records
- `docs/contracts/` — contract semantics and compatibility
- `docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md` — approved Contracts-owned C++ package architecture
- `docs/C-M4-001_IMPLEMENTATION_EVIDENCE.md` — implementation candidate identity and validation evidence
- `docs/adr/ADR-0009-cpp-protobuf-package.md` — accepted C++ package ownership decision
