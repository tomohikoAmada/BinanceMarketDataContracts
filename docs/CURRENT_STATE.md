CURRENT-STATE ORIENTATION ONLY. Verify actual source, Git/GitHub and CI when
freshness matters. Accepted ADRs and semantic designs remain authoritative.

# Current State

Updated 2026-11-13.

## Milestones

| Stage | State | Evidence |
| --- | --- | --- |
| C0 correctness | COMPLETE: bounded current-consumer integers and optional Symbol presence; no wire/descriptor change | [ADR-0012](adr/ADR-0012-current-consumer-wire-correctness.md), [HISTORY](HISTORY.md) |
| C1 used internal v1 contract | COMPLETE: fixed used subset, dependency pins and offline validation; merged in PR #23 | [Consumer page](contracts/current-capabilities.md), [HISTORY](HISTORY.md) |
| C1.1 hygiene | COMPLETE: explicit present-empty `StreamStatus.message` is rejected instead of coerced to absence; documentation scans prune `.venv`/cache/build dirs before traversal | `tests/test_wire_adapters.py`, `tests/test_documentation_consistency.py` |
| C1.2 simplification | COMPLETE: removed redundant Decimal/enum validators, unused `EnvelopeMetadata`, adapter-local enum maps and no-op conversion helpers. No schema/fingerprint change | `common.py`, `gateway.py`, `telemetry.py`, `wire/adapters.py` |
| C2 USD-M contract extension | COMPLETE (candidate): MarkPrice, Liquidation, ReferenceObservation, Stream/Reference enums, AggTrade.normal_quantity and REST event-time presence; fixtures/adapters/regenerated Python and C++ package lineage | `market_events.proto`, `reference_data.proto`, `gateway_messages.proto`, `wire/adapters.py` |
| C2 conditional simplification | Not triggered; no evidenced maintenance/performance reason | Sibling Contracts milestone plan |

## Repository role

Contracts owns public Pydantic Domain models, Protobuf wire/service schemas,
generated Python/JSON artifacts, explicit adapters, fixtures and package
compatibility. It owns no network client/server, persistence or Projection
sequence algorithm.

Recorder currently uses independent Raw/Normalize/Replay types. Projection Core
stays independent; its optional ProtoAdapter consumes Contracts messages.
Gateway owns runtime, transport, configuration limits and gRPC serving.

## Current contract use

C1 fixes the used internal v1 subset to five market/book models, eight
RPC-related models, existing `StreamStatus`/helpers, and three implemented RPCs.
C2 adds USD-M mark-price, liquidation and typed REST reference-observation
contracts as PROPOSED; Gateway/Recorder adoption remains downstream work.
`SubscribeMarketState` remains UNIMPLEMENTED. Domain representability is broader
than current runtime support; unused models are not promised or expanded. See
[the consumer page](contracts/current-capabilities.md).

Gateway runtime limits and milestone status belong to the Gateway repository.
This repository does not pin a current Gateway product count or development
stage.

## Package and compatibility facts

- Historical C-M4-001 delivery is complete and merged; see [HISTORY](HISTORY.md).
- `binance-market-data-contracts-cpp/0.1.0` exports
  `BinanceMarketDataContracts::Protobuf`; no gRPC in its host/build graph.
- `binance-market-data-contracts-grpc-cpp/0.1.0` exports
  `BinanceMarketDataContracts::Grpc`, links the exact message artifact and owns
  only generated service/stub symbols.
- Schema Fingerprint Algorithm Version 1 digest is
  `a2a93ca5cf4e17c9a64ca0939ad208f1202c1746628eed5260bd0edb81666c86` after the C2 message-field extension.
- Domain/Wire statuses and schema versions remain PROPOSED/DRAFT: 26 contracts,
  22 wire mappings.
- Formal Package Revision stays NOT_FORMALLY_ASSIGNED; publication is separate.
- Binary protobuf compatibility differs from strict Domain/JSON/adapter support;
  see [compatibility policy](contracts/compatibility_policy.md).

## Review and history

Detailed C0/C1/C1.1/C-M4-001 logs, pins and review transcripts were compressed
into [HISTORY](HISTORY.md). Git history and linked PRs remain the full record.
C1 does not repeat cold third-party builds or reopen completed proof stages.

Read this file, AGENTS.md, README, ARCHITECTURE, relevant accepted ADRs,
code/tests, and exact PR/CI. Historical records do not override current
authorities.
