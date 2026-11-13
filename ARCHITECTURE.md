# ARCHITECTURE.md — BinanceMarketDataContracts

Entry point for Contracts architectural context. The cross-repository top-level
boundary authority is [BinanceMarketData_Living_Architecture.md](BinanceMarketData_Living_Architecture.md).

## Module

`BinanceMarketDataContracts` is the public contracts layer for the
BinanceMarketData domain. It provides versioned data types, generated JSON
Schemas, golden fixtures, wire/service contracts, explicit adapters and
architecture decision records. It owns no network access, persistence, trading
policy or market runtime.

Contracts is the cross-module language authority, not a framework every internal
Core must import. For example, Projection Core remains independent of
Protobuf/gRPC; its optional ProtoAdapter consumes the Contracts message artifact.

## Contract status

All public Domain/Wire contracts remain **PROPOSED** or **DRAFT** unless
explicitly promoted by the formal acceptance process. An accepted ADR does not
itself promote a contract.

| Contract | Status | Version |
|----------|--------|---------|
| depth-update | PROPOSED | v1 |
| agg-trade | PROPOSED | v1 |
| book-ticker | PROPOSED | v1 |
| exchange-depth-snapshot | PROPOSED | v1 |
| local-order-book-snapshot | PROPOSED | v1 |
| market-state-snapshot | PROPOSED | v1 |
| data-health-snapshot | PROPOSED | v1 |
| historical-dataset-descriptor | DRAFT | v1 |
| replay-query | DRAFT | v1 |
| telemetry | DRAFT | v1 |
| control-command | DRAFT | v1 |
| command-result | DRAFT | v1 |
| event-subscription-request | DRAFT | v1 |
| order-book-subscription-request | DRAFT | v1 |
| market-state-subscription-request | DRAFT | v1 |
| gateway-status-request | DRAFT | v1 |
| subscription-accepted | DRAFT | v1 |
| consumer-gap-notice | DRAFT | v1 |
| stream-status | DRAFT | v1 |
| gateway-event-envelope | DRAFT | v1 |
| order-book-stream-item | DRAFT | v1 |
| market-state-stream-item | DRAFT | v1 |
| gateway-status-snapshot | DRAFT | v1 |

## Acceptance criteria

A contract is promoted from PROPOSED to ACCEPTED when:

1. Producer and Consumer are identified.
2. Schema is frozen.
3. Valid, invalid and boundary fixtures are complete.
4. Contract tests pass.
5. At least one producer adapter and one consumer usage are validated where applicable.
6. Architecture review is complete.

## Architecture decision records

- [ADR-0001](docs/adr/ADR-0001-recorder-gateway-independent-connections.md) — independent Recorder/Gateway connections (ACCEPTED)
- [ADR-0002](docs/adr/ADR-0002-python-pydantic-json-schema-first.md) — Pydantic + JSON Schema first (SUPERSEDED by ADR-0007)
- [ADR-0003](docs/adr/ADR-0003-time-semantics.md) — time semantics (PROPOSED)
- [ADR-0004](docs/adr/ADR-0004-decimal-string-price-quantity.md) — decimal strings for price/quantity (PROPOSED)
- [ADR-0005](docs/adr/ADR-0005-quality-and-health-semantics.md) — quality/health separation (PROPOSED)
- [ADR-0006](docs/adr/ADR-0006-projection-logical-boundary.md) — Projection logical boundary (ACCEPTED)
- [ADR-0007](docs/adr/ADR-0007-pydantic-domain-protobuf-wire-contracts.md) — Domain/Wire strata (ACCEPTED)
- [ADR-0008](docs/adr/ADR-0008-gateway-grpc-streaming-protocol.md) — Gateway gRPC streaming (ACCEPTED)
- [ADR-0009](docs/adr/ADR-0009-cpp-protobuf-package.md) — C++ Protobuf message package (ACCEPTED)
- [ADR-0010](docs/adr/ADR-0010-separate-cpp-grpc-artifact.md) — separate C++ gRPC artifact (ACCEPTED)
- [ADR-0011](docs/adr/ADR-0011-opaque-utf8-symbol-identity.md) — opaque UTF-8 symbol identity (ACCEPTED)
- [ADR-0012](docs/adr/ADR-0012-current-consumer-wire-correctness.md) — C0 representability/presence (PROPOSED; implementation delivered)

## Implemented package boundaries

- Python Domain contracts, generated JSON Schemas, fixtures and explicit adapters.
- Python Protobuf/gRPC artifacts generated from the tracked `.proto` sources.
- `binance-market-data-contracts-cpp/0.1.0`: message-only package exporting
  `BinanceMarketDataContracts::Protobuf`.
- `binance-market-data-contracts-grpc-cpp/0.1.0`: separate service/stub package
  exporting `BinanceMarketDataContracts::Grpc`.
- No package is published; the formal package revision is unassigned.
- Delivery identities, support matrix and review evidence are in
  [docs/HISTORY.md](docs/HISTORY.md).

## Current cross-repository orientation

The Gateway repository owns runtime configuration limits, product admission,
recovery and milestone status. Contracts owns the schemas and service contract.
At the time of writing the Gateway implements `SubscribeOrderBook`,
`SubscribeEvents` and `GetGatewayStatus`; `SubscribeMarketState` remains
UNIMPLEMENTED. Domain representability is broader than any current runtime
support. See [docs/contracts/current-capabilities.md](docs/contracts/current-capabilities.md)
and the Gateway repository's own `CURRENT_STATE.md` for live limits and status.

Recorder keeps independent Raw/Normalize/Replay types and does not currently
import Contracts at runtime. Projection Core stays independent; its optional
ProtoAdapter consumes Contracts messages.

## Open questions

| ID | Question | Status |
|----|----------|--------|
| O-001 | Recorder/Gateway independent connections | DECIDED (ADR-0001) |
| O-002 | Projection logical independence / deployment | DECIDED (ADR-0006): embedded library |
| O-004 | Gateway IPC protocol | DECIDED: gRPC Server Streaming + Protobuf (ADR-0008) |
| O-005 | Public schema | DECIDED: Pydantic Domain + Protobuf Wire (ADR-0007) |
| O-006 | History: library or service | TBD; library/CLI first |
| O-008 | Health SLO thresholds | TBD; Health is a capability, not a required service |
| O-009 | Spot initial depth bridging | Frozen in Projection's accepted bootstrap rules |

## Derived-product ownership

Legacy inventories and early ADR examples may mention microprice, OHLCV, trade
tape, premium, funding/OI composition or other deterministic products. Those
examples do not assign them to the current Projection Core.

> Deterministically computable is necessary for a deterministic market-data
> product, but is not by itself sufficient reason to add it to
> `BinanceMarketDataProjection` Core.

New shared derived-data authorities require explicit design and must preserve
the MarketData vs FeatureEngineering boundary.

## Module boundaries and contract semantics

- [docs/architecture/module_boundaries.md](docs/architecture/module_boundaries.md)
- [docs/architecture/dependency_rules.md](docs/architecture/dependency_rules.md)
- [docs/architecture/integration_model.md](docs/architecture/integration_model.md)
- [docs/contracts/](docs/contracts/) — time, quality, decimals, identity and compatibility

Health/status contracts report MarketData facts and assessments; they do not own
trading permission. `RiskManagement` owns normative trading authorization/policy.

## AI and independent-reviewer reading order

Start with [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md), then this file, the
top-level living architecture, relevant accepted ADRs, and actual code/tests.
Verify current GitHub main and PR/CI state independently; orientation documents
do not override narrower accepted semantic authorities.
