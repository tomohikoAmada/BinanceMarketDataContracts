# Contracts History

Historical record only. This page preserves durable delivery facts; it is not a
current implementation checklist and does not override accepted ADRs, the
current consumer page, or the source/tests. Use Git history and the linked PRs
for full logs, field-by-field migration tables and review transcripts.

## C0 — current-consumer wire correctness (2026-10-12)

- Baseline: `8701c330911c0f1c0b38207281dea426c2dee434`.
- Preserved source: `db8156f1e16ba7a4a5ee8d5b26316139b7e218f3`.
- Decision: [ADR-0012](adr/ADR-0012-current-consumer-wire-correctness.md).
- Bounded the currently used integer fields to the existing `uint64` and
  positive `int32` wire ranges. Lower bounds, strict typing and optionality
  were retained; present-empty optional `Symbol` reaches Domain validation and
  fails instead of becoming absence.
- Corrected the USD-M depth `T` mapping to the existing transaction-time field.
  That is a producer correction, not a new contract field.
- No field/enum number, proto type, RPC, schema version, registry status,
  descriptor or schema fingerprint changed.
- Validation at C0: 673 passed / 2 skipped without injected descriptor inputs;
  the full C1 run supplied those inputs and passed 675 / 0 skipped.

## C1 — used internal v1 subset (2026-10-18)

- Fixed the used internal subset to five market/book models, eight RPC-related
  models, existing `StreamStatus`/helpers, and the three implemented RPCs
  (`SubscribeOrderBook`, `SubscribeEvents`, `GetGatewayStatus`).
  `SubscribeMarketState` remained unimplemented. See the
  [current consumer page](contracts/current-capabilities.md).
- Validated the fixed dependency combination: Contracts C++ messages and gRPC
  stubs, Projection Core + ProtoAdapter, Protobuf `6.33.5` and gRPC `1.83.0`.
- Validation: 675 Python tests with descriptor/locked generator identity;
  Gateway production RPC graph 22/22; Projection sequence/replay 58/58,
  adapter replay 50/50, wire admission 21/21; schema/codegen/Buf/fingerprint
  checks and local wheel/sdist/twine passed.
- Delivered through [PR #23](https://github.com/tomohikoAmada/BinanceMarketDataContracts/pull/23)
  and merged at `cdefd7d08cacac4b54996bf9872decfb13e74287`.
- No contract status promotion, package publication or Recorder runtime
  dependency was created.

## C1.1 — hygiene corrections (2026-11-10)

- Removed the adapter's silent coercion of a present-empty `StreamStatus.message`
  to `None`. An explicitly present empty wire string now reaches Domain
  validation and is rejected.
- The old-generated-path documentation scan now prunes `.git`, virtual
  environments, build/dist and cache directories before traversal.
- Validation: 668 passed / 9 skipped (the descriptor-dependent C++-provided
  checks are the expected skips in a plain local run).
- No schema, registry, fingerprint or contract-status change.

## C1.2 — validation/adapter simplification (2026-11-10)

- Removed the three redundant Decimal after-validators for price, quantity and
  positive quantity; their regular expressions already enforce the same ranges.
- Removed Gateway validators duplicated by `Literal` fields and the unreferenced
  legacy `EnvelopeMetadata` Pydantic class plus its unused adapters.
- Removed telemetry queue checks already enforced by `Field` constraints.
- Promoted all remaining adapter enum maps to module-level constants and removed
  the no-op `_optional_uint64` and `PriceString(...)`/`QuantityString(...)`
  wrappers.
- Validation: 675 passed / 2 skipped with the C++ descriptor set; JSON Schema
  export is byte-identical and the schema fingerprint remains unchanged.

## C-M4-001 — Contracts-owned C++ package (2026-08)

- Design approved; [ADR-0009](adr/ADR-0009-cpp-protobuf-package.md) and
  [ADR-0010](adr/ADR-0010-separate-cpp-grpc-artifact.md) accepted.
- Implementation complete and merged. Independent re-review approved the
  corrected head `4e5d3d846afba982ab5e48d2737bc40560e34a6c`; CI `31167981350`
  passed 15/15; IIR-1 through IIR-5 closed; P0/P1/P2 = 0.
- `binance-market-data-contracts-cpp/0.1.0` is message-only and exports
  `BinanceMarketDataContracts::Protobuf`.
- `binance-market-data-contracts-grpc-cpp/0.1.0` owns only the Gateway service
  and gRPC stubs, links the exact message artifact and exports
  `BinanceMarketDataContracts::Grpc`.
- Package version candidate `0.1.0`; formal Package Revision remains
  `NOT_FORMALLY_ASSIGNED` (release gate). Nothing is published.
- Schema fingerprint Algorithm Version 1 remains
  `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.
- Proven static support: Ubuntu x86_64 GCC/Clang Release+Debug and macOS arm64
  AppleClang Release+Debug. Proven shared support: Ubuntu x86_64 GCC Release
  and macOS arm64 AppleClang Release. Other matrices are not claimed.
- The original 1,100-line design, 535-line plan and acceptance transcript were
  removed as redundant history. The merged CMake/Conan implementation,
  acceptance commits and linked CI runs remain the evidence.
