CURRENT-STATE ORIENTATION ONLY.
This file summarizes repository state for humans and AI reviewers.
It does not override accepted ADRs or semantic design documents.
When this file and Git/GitHub/code disagree, verify Git/GitHub/code and update this file.

# Current State

## Purpose of This File

This is the current orientation index for a fresh human or AI reviewer. It separates current
repository facts from historical design, planning, and review evidence.

## Repository Role

Contracts owns public Pydantic domain contracts, Protobuf wire schemas, generated artifacts and
package workflows, schema/package compatibility, and explicit domain/wire adapters. It does not
own exchange sequence classification, Projection lifecycle semantics, Recorder reconnect behavior,
or Gateway runtime.

## Source-of-Truth Order

For implemented facts, use checked-out code, tests, build configuration, Git history, and current
GitHub state. Accepted ADRs and accepted semantic designs govern deliberate semantics. This file is
orientation only.

## Current Main

- `origin/main`: `67ee1bf69fad980d114cfa278c3a6ffe310a4d7a`
- Current main CI: run `31173390048`, completed `success`.

## Active Candidate / Pull Request

- No open Contracts pull requests.
- The former C-M4-001 implementation candidate is merged; there is no active candidate branch.

## Deployed State

N/A. The C++ package is not published or deployed. The repository contains the package source and
build/package workflow only.

## Implemented

- C-M4-001 is implemented, accepted, and merged to `main`.
- Package coordinate: `binance-market-data-contracts-cpp/0.1.0`.
- Installed target: `BinanceMarketDataContracts::Protobuf`.
- Seven non-service Protobuf message sources are generated at build time; generated C++ files are
  build outputs, not primary committed sources.
- Formal Schema Fingerprint Algorithm Version 1 digest:
  `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.

## Not Implemented

- Formal Contracts Package Revision assignment; it remains `NOT_FORMALLY_ASSIGNED` and is gated on
  release.
- Package publication/release.
- Gateway runtime or gRPC server.
- Formal acceptance of the Domain and Wire Contracts; they remain PROPOSED or DRAFT unless a
  separate contract authority says otherwise.

## Current Blockers

- Release/publication is not authorized until release identities, including Package Revision, are
  intentionally assigned.
- Contract semantic acceptance remains separate from C-M4-001 package implementation acceptance.

## Accepted Semantic Authorities

Accepted ADRs and accepted semantic designs remain authoritative, especially ADR-0007 for the
contract strata and ADR-0009 for Contracts-owned C++ Protobuf package ownership. This file does not
promote any PROPOSED/DRAFT contract or redefine another repository's semantics.

## Known Semantic Conflicts

- Contracts owns neither Spot bootstrap policy nor Recorder R-034. Projection owns its accepted
  Spot bootstrap rule; Recorder's local L+1 behavior remains an open Recorder-local conflict.

## Cross-Repository Relationships

- Recorder owns acquisition, immutable Raw, capture/provenance, Catalog, archive, normalization,
  replay/source evidence, and operational integrity.
- Contracts owns the schemas/package consumed by Projection's optional adapter.
- Projection owns deterministic projection semantics, fixed-point interpretation, order book,
  market-specific sequencing, lifecycle, and M5 validation.
- Contracts schemas may be consumed by Projection's optional adapter; Contracts does not redefine
  Projection M3 sequence semantics.
- Projection M4 is complete in `BinanceMarketDataProjection`; Gateway runtime is not implemented.

## Current Validation / CI Evidence

The current main CI run `31173390048` completed successfully for the current main SHA. The accepted
C-M4-001 implementation re-review recorded CI `31167981350` as 15/15 PASS; that is historical
review evidence, not a current PR state.

## Next Authorized Step

Maintain contract/schema compatibility and prepare a separately authorized release/publication
decision when the formal Package Revision and release identities are assigned. Do not start Gateway
runtime or redefine Projection sequence semantics in this repository.

## AI / Reviewer Reading Order

Read `docs/CURRENT_STATE.md`, `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, the relevant milestone or
design document, accepted ADRs, actual code/tests, and then verify GitHub PR and exact-head CI state.
Do not trust this file alone for an independent review.

## Historical Documents

`docs/C-M4-001_IMPLEMENTATION_PLAN.md` and
`docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md` are preserved historical planning/design snapshots.
`docs/C-M4-001_IMPLEMENTATION_EVIDENCE.md` preserves candidate and review evidence with a current
status header. ADR-0009 preserves its accepted architectural decision and historical acceptance
record; it is not rewritten by this synchronization.
