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
