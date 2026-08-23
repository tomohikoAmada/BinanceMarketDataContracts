# ARCHITECTURE.md — BinanceMarketDataContracts

Entry point for architectural context. See the full living architecture document at
`BinanceMarketData_Living_Architecture.md`.

## Module

`BinanceMarketDataContracts` is the public contracts layer for the BinanceMarketData domain.
It provides versioned data types, generated JSON Schemas, golden fixtures, and architecture
decision records. It has no network, storage, or trading dependencies.

## Contract status

All contracts are **PROPOSED** or **DRAFT**. No contract has been formally ACCEPTED.

**ADR acceptance does NOT imply contract acceptance.** ADRs document architectural decisions
(wire protocol choice, contract strata, module boundaries). Domain and Wire contracts remain
PROPOSED/DRAFT until they meet the formal acceptance criteria below.

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
1. Producer and Consumer are identified
2. Schema is frozen
3. Valid, invalid, and boundary fixtures are complete
4. Contract tests pass
5. At least one producer adapter and one consumer usage are validated
6. Architecture review is complete

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
- `docs/adr/ADR-0011-opaque-utf8-symbol-identity.md` (ACCEPTED; ADR-0010 is reserved by an
  in-flight package-boundary change)

## C-M4-001 C++ package design

The approved C-M4-001 architecture defines a Contracts-owned, versioned, installable C++ Protobuf
message package for the Projection M4 adapter. It does not change any `.proto` schema,
contract status, field semantics, or generated Python artifact.

- Design: **APPROVED**
- ADR-0009: **ACCEPTED**
- External architecture review: **APPROVED**
- Architecture blocking findings: **0**
- Implementation: **COMPLETE / MERGED** into Contracts main by commit `67ee1bf69fad980d114cfa278c3a6ffe310a4d7a`
- Independent implementation re-review: **APPROVED** (IIR-1 through IIR-5 CLOSED; P0/P1/P2 = 0)
- Reviewed corrected head: `4e5d3d846afba982ab5e48d2737bc40560e34a6c`
- Reviewed CI: `31167981350` — 15/15 PASS
- Schema baseline: `01d76a41929f36d89573159f5f458f9f1e378ada`
- Schema fingerprint: `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`
- Formal fingerprint approval: **APPROVED** (Algorithm Version 1)
- Package version candidate: `0.1.0`; package revision: **NOT FORMALLY ASSIGNED — RELEASE GATE**
- C-M4-001: **IMPLEMENTED / ACCEPTED / MERGED**
- Published: **NO**
- Projection M4 Implementation: **COMPLETE** in the separate Projection repository
- Design: [`docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md`](docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md)
- Candidate evidence: [`docs/C-M4-001_IMPLEMENTATION_EVIDENCE.md`](docs/C-M4-001_IMPLEMENTATION_EVIDENCE.md)

## Open questions

| ID | Question | Status |
|----|----------|--------|
| O-001 | Recorder/Gateway independent connections | DECIDED (ADR-0001) |
| O-002 | Projection as independent module | DECIDED (ADR-0006) |
| O-004 | Gateway IPC protocol | DECIDED: gRPC Server Streaming + Protobuf (ADR-0008) |
| O-005 | Public Schema | DECIDED: Pydantic Domain + Protobuf Wire (ADR-0007) |
| O-006 | History: library or service | TBD |
| O-008 | Health SLO thresholds | TBD |
| O-009 | Spot initial depth bridging | TBD |

## Module boundaries

See `docs/architecture/module_boundaries.md` and `docs/architecture/dependency_rules.md`.

## Contract semantics

See `docs/contracts/` for detailed documentation on time semantics, quality semantics,
decimal string rules, and compatibility policy.

## AI and independent-reviewer reading order

Start with [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), then read this file, the full living
architecture, the relevant accepted ADRs, and the actual code/tests. Verify current GitHub main and
PR/CI state independently; the orientation file is not semantic authority.
