# ARCHITECTURE.md — BinanceMarketDataContracts

Entry point for Contracts architectural context. The cross-repository BinanceMarketData top-level
boundary authority is `BinanceMarketData_Living_Architecture.md`.

## Module

`BinanceMarketDataContracts` is the public contracts layer for the BinanceMarketData domain.
It provides versioned data types, generated JSON Schemas, golden fixtures, wire/service contracts,
and architecture decision records. It has no network, storage, trading-policy, or market-runtime
ownership.

Contracts is the cross-module language authority, not a framework that every internal Core must
import. For example, Projection Core remains independent of Protobuf/gRPC; its optional ProtoAdapter
may consume the Contracts message artifact.

## Contract status

All public Domain/Wire contracts remain **PROPOSED** or **DRAFT** unless explicitly promoted by the
formal acceptance process. An accepted ADR does not itself promote a contract.

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
3. Valid, invalid, and boundary fixtures are complete.
4. Contract tests pass.
5. At least one producer adapter and one consumer usage are validated where applicable.
6. Architecture review is complete.

## Architecture decision records

- `docs/adr/ADR-0001-recorder-gateway-independent-connections.md` (ACCEPTED)
- `docs/adr/ADR-0002-python-pydantic-json-schema-first.md` (SUPERSEDED by ADR-0007)
- `docs/adr/ADR-0003-time-semantics.md` (PROPOSED)
- `docs/adr/ADR-0004-decimal-string-price-quantity.md` (PROPOSED)
- `docs/adr/ADR-0005-quality-and-health-semantics.md` (PROPOSED)
- `docs/adr/ADR-0006-projection-logical-boundary.md` (ACCEPTED)
- `docs/adr/ADR-0007-pydantic-domain-protobuf-wire-contracts.md` (ACCEPTED)
- `docs/adr/ADR-0008-gateway-grpc-streaming-protocol.md` (ACCEPTED)
- `docs/adr/ADR-0009-cpp-protobuf-package.md` (ACCEPTED)
- `docs/adr/ADR-0010-separate-cpp-grpc-artifact.md` (ACCEPTED)
- `docs/adr/ADR-0011-opaque-utf8-symbol-identity.md` (ACCEPTED)

## C-M4-001 C++ package design

The approved C-M4-001 architecture defines a Contracts-owned, versioned, installable C++ Protobuf
message package for Projection's optional wire adapter. It does not change `.proto` field semantics
or make Projection Core depend on Protobuf/gRPC.

- Design: **APPROVED**
- ADR-0009: **ACCEPTED**
- C-M4-001 implementation: **COMPLETE / MERGED**
- Independent implementation re-review: **APPROVED**
- Package version candidate: `0.1.0`
- Package revision: **NOT FORMALLY ASSIGNED — RELEASE GATE**
- Published: **NO**
- Message target: `BinanceMarketDataContracts::Protobuf`
- Separate gRPC artifact: `binance-market-data-contracts-grpc-cpp/0.1.0`, exporting
  `BinanceMarketDataContracts::Grpc`
- Projection M4 package integration: **COMPLETE** in the Projection repository

Detailed package evidence remains in:

- `docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md`
- `docs/C-M4-001_IMPLEMENTATION_EVIDENCE.md`

## Current cross-repository orientation

The older G8/M6 planning state is historical. The separate Gateway repository
has completed G0-G11, post-G11 runtime productization, recovery observability,
performance instrumentation, and the accepted post-G11 performance baseline.
Its ordinary `bmd-gatewayd` is a fixed two-product daemon for Spot BTCUSDT and
USD-M perpetual BTCUSDT, and it currently implements `SubscribeOrderBook`,
`SubscribeEvents`, and `GetGatewayStatus`.

Contracts remains the schema/package owner and does not own or implement the
Gateway runtime. Contracts declares `SubscribeMarketState`, while the current
Gateway service does not implement it; this is nonblocking future
contract/implementation surface reconciliation debt. Domain and Wire contract
status remains PROPOSED/DRAFT, and formal package revision/publication remains
separately gated.

Exact SHAs and CI/evidence belong in repository-local `CURRENT_STATE`/milestone documents rather than
being frozen here.

## Open questions

| ID | Question | Status |
|----|----------|--------|
| O-001 | Recorder/Gateway independent connections | DECIDED (ADR-0001) |
| O-002 | Projection logical independence / deployment | DECIDED (ADR-0006): embedded library in current deployment |
| O-004 | Gateway IPC protocol | DECIDED: gRPC Server Streaming + Protobuf (ADR-0008) |
| O-005 | Public Schema | DECIDED: Pydantic Domain + Protobuf Wire (ADR-0007) |
| O-006 | History: library or service | TBD; top-level v0.3 direction is library/CLI first |
| O-008 | Health SLO thresholds | TBD; Health is currently a capability, not a required standalone service |
| O-009 | Spot initial depth bridging | SEMANTIC AUTHORITY FROZEN in Projection's accepted Spot successor-coverage/bootstrap rules; reopen only through Projection architecture review |

## Derived-product ownership note

Legacy contract inventories and early ADR examples may mention microprice, OHLCV, trade tape,
premium, funding/OI composition or other deterministic products. Those examples do not assign the
current Projection Core responsibility for all such products.

Current top-level rule:

> Deterministically computable is necessary for a deterministic market-data product, but is not by
> itself sufficient reason to add that product to `BinanceMarketDataProjection` Core.

New shared derived-data authorities must be designed explicitly and must preserve the MarketData vs
FeatureEngineering boundary.

## Module boundaries

See:

- `docs/architecture/module_boundaries.md`
- `docs/architecture/dependency_rules.md`
- `docs/architecture/integration_model.md`

## Contract semantics

See `docs/contracts/` for detailed time, quality, decimal/string and compatibility semantics.

Health/status contracts report MarketData facts and assessments; they do not own trading permission.
`RiskManagement` owns normative trading authorization/policy.

## AI and independent-reviewer reading order

Start with `docs/CURRENT_STATE.md`, then read this file, the top-level living architecture, relevant
accepted ADRs, and actual code/tests. Verify current GitHub main and PR/CI state independently;
orientation documents do not override narrower accepted semantic authorities.
