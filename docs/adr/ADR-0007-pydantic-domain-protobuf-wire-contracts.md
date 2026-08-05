# ADR-0007: Pydantic domain contracts and Protobuf wire contracts

## Status

ACCEPTED

## Date

2026-08-05

## Context

The BinanceMarketData system has completed Workstream 0 with Pydantic v2 as the single
contract source of truth (ADR-0002). With the Gateway now targeting cross-device,
multi-language consumers (the wire protocol supports C++, Rust, Go, and Python implementations),
the system needs a language-agnostic binary wire protocol.

The Pydantic+JSON Schema approach served well for Python-only development, but:

- JSON is verbose and non-binary, unsuitable for high-throughput streaming
- JSON has no built-in field numbering, making schema evolution fragile
- JSON Schema has no gRPC or service definition capability
- Cross-language consumers would need to manually implement JSON Schema validation

Protobuf + gRPC provides well-supported code generation for C++, Rust, Go, and Python — the target language candidates. The Gateway implementation language will be selected through a separate ADR with benchmark evidence.

## Decision

Establish two explicit contract strata with distinct authorities:

### Domain Contracts (Pydantic)

- Authoritative for: Python domain model, field business semantics, Decimal String rules,
  complex runtime validation, JSON fixtures, strict Python types, documentation semantics.
- Remains the truth for what a field "means" in the Python ecosystem.
- JSON Schema continues to be generated for documentation and lightweight validation.

### Wire Contracts (Protobuf)

- Authoritative for: network message structure, field numbers, enum numbers, `oneof`
  structures, optional presence, package naming, gRPC service definitions, RPC method
  signatures, wire compatibility rules.
- `.proto` files are the canonical source for what goes on the wire.

### Explicit adapter layer

- Pydantic ↔ Protobuf conversion is done through explicit, hand-written adapter functions.
- No reflection-based auto-mapping, no `model_dump()` into Protobuf.
- Each adapter function maps fields explicitly.
- Round-trip tests enforce semantic consistency.

### Why not JSON as Gateway wire format

- No binary encoding standard; verbose representation.
- No gRPC integration; service definitions would need hand-coding.
- Field evolution fragile (no field numbers).
- Cross-language generation more manual.

### Why not auto-generate Protobuf from Pydantic

- Pydantic and Protobuf have different type systems (e.g., `oneof`, `optional`,
  field numbers, enum numbering).
- Auto-generation would either lose Protobuf expressiveness or create maintenance burden.
- Explicit mapping ensures both layers can evolve semi-independently.

### Why explicit adapters

- Enum mappings must not rely on coincidental name/number alignment.
- `UNSPECIFIED` (proto enum 0) must be rejected by Pydantic.
- Decimal strings must be preserved exactly (trailing zeros).
- Optional presence must be distinguished from default/zero values.
- Schema versions require explicit negotiation logic.

## Consequences

### Positive

- Clear separation: Domain semantics live in Python, wire format is language-agnostic.
- Rust/Go/Python consumers all share the same `.proto` source.
- gRPC provides well-tested streaming, backpressure, and code generation.
- Adapter layer prevents silent semantic drift between domain and wire.
- Each layer can evolve at its own pace within compatibility rules.

### Negative

- Dual maintenance: a field change requires updates to Pydantic model, protobuf message,
  and adapter function.
- No automatic reflection-based mapping (intentional trade-off).
- Generated code must be committed and drift-checked in CI.

### Risks

- Adapters may fall out of sync if not tested thoroughly. Mitigation: round-trip tests
  for every public message type.
- Enum numbering in `.proto` must be managed carefully; renumbering is a BREAKING wire change.

## Acceptance criteria

- [ ] All core market event Pydantic models have corresponding Protobuf messages
- [ ] All Protobuf messages have explicit Pydantic ↔ Proto adapters
- [ ] Round-trip tests pass for all core event types
- [ ] Proto enum 0 values are `*_UNSPECIFIED` and rejected by adapters
- [ ] Decimal strings round-trip with trailing zeros preserved
- [ ] Optional presence round-trips correctly (None stays None)
- [ ] CI enforces proto compile, format, lint, and generated code drift
- [ ] `.proto` files are packaged in wheel/sdist

## Compatibility impact

- Existing Pydantic contracts are unchanged.
- JSON Schema remains generated and drift-checked.
- All existing tests must continue to pass.
- Consumer code that only imports Pydantic contracts is unaffected.

## Supersedes

ADR-0002 (Pydantic remains Domain Contracts; Protobuf added as Wire Contracts)

## Superseded by

None.
