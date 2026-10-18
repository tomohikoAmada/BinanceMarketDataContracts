CURRENT-STATE ORIENTATION ONLY. Verify actual source, Git/GitHub and CI when
freshness matters. Accepted ADRs and semantic designs remain authoritative.

# Current State

Updated 2026-10-18; all six sibling Milestone Plan documents were read.

## Current v0.3 milestones

| Stage | State | Evidence |
| --- | --- | --- |
| C0 correctness | Existing local implementation preserved as source `db8156f1e16ba7a4a5ee8d5b26316139b7e218f3`; independently reviewed; all 675 tests passed with C1 | [C0 fields/fixtures/migration](C0_IMPLEMENTATION.md), [ADR-0012](adr/ADR-0012-current-consumer-wire-correctness.md) |
| C1 used internal v1 contract | COMPLETE: used internal semantics/pins, fixed-dependency offline validation and independent review; delivery/CI/merge tracked by PR #23 | [Consumer page](contracts/current-capabilities.md), [C1 evidence](C1_EVIDENCE.md) |
| C2 conditional simplification | Not triggered; no evidenced maintenance/performance reason for changes in this task | Sibling Contracts milestone plan |

## Repository role and implemented boundaries

Contracts owns public Pydantic Domain models, Protobuf wire/service schemas,
generated Python/JSON artifacts, explicit adapters, fixtures and package
compatibility. It owns no network client/server, persistence or Projection
sequence algorithm. Recorder currently uses independent Raw/Normalize/Replay
types. Projection Core stays independent; its optional ProtoAdapter consumes
Contracts messages. Gateway owns runtime, transport and gRPC serving.

C0 bounds current-consumer integers by existing uint64/int32 types and rejects
present-empty optional Symbol while preserving absence/zero. USD-M depth T is
transaction-time per shared fixture; producer migrations remain producer-owned.
Gateway v0.3 G1 has implemented and tested that mapping plus Applied Depth time.
Recorder production qualification remains in Recorder and is not revalidated here.

C1 fixes five used market/book models, eight RPC-related models and existing
StreamStatus/helpers at the [documented internal combination](contracts/current-capabilities.md).
Gateway now configures 1..8 products; three RPCs are implemented, Spot supports
three event streams and USD-M only depth. SubscribeMarketState is UNIMPLEMENTED.
Gateway G0/G1 are complete; G2/G3/four-product delivery/VPS/API/performance are open.

## Package and compatibility facts

- Historical C-M4-001 implementation/re-review is complete and merged; see
  [implementation evidence](C-M4-001_IMPLEMENTATION_EVIDENCE.md).
- Message-only `binance-market-data-contracts-cpp/0.1.0` exports
  `BinanceMarketDataContracts::Protobuf`; no gRPC in its host/build graph.
- Separate `binance-market-data-contracts-grpc-cpp/0.1.0` exports
  `BinanceMarketDataContracts::Grpc`, links the exact message artifact and
  owns only generated service/stub symbols. Exact RREVs/source/PREVs: C1 evidence.
- Schema Fingerprint Algorithm Version 1 digest stays
  `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.
- Domain/Wire statuses and schema versions remain unchanged (23 contracts,
  19 wire mappings, PROPOSED/DRAFT). Internal C1 support is narrower than
  schema representability; unused models are not promised or expanded.
- Formal Package Revision stays NOT_FORMALLY_ASSIGNED; publication is separate
  and is not needed for internal C1. No new RPC/descriptor/enum/Conan-lock change.
- Binary protobuf compatibility differs from strict Domain/JSON/adapter support;
  see [compatibility policy](contracts/compatibility_policy.md).

## Review and history

Current branch/PR/CI delivery is recorded in [C1 evidence](C1_EVIDENCE.md), rather
than inferred from historical CI. Historical baseline `8701c330` and earlier
C-M4-001/Gateway dependency proofs retain their original meaning; C1 does not
repeat cold third-party builds or reopen completed proof stages.

Read this file, AGENTS.md, README, ARCHITECTURE, relevant current plan/accepted
ADRs, code/tests, and exact PR/CI. Historical C-M4-001 plans remain historical.
