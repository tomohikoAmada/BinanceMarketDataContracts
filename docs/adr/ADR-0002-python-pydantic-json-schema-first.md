# ADR-0002: Python Pydantic + JSON Schema first

## Status

SUPERSEDED

## Date

2026-08-04 (SUPERSEDED 2026-08-05)

## Note (2026-08-05)

The Pydantic-first phase has been completed successfully. Pydantic remains the
authoritative Domain Contract layer for Python — it defines field business semantics,
Decimal String rules, complex runtime validation, JSON fixtures, and strict Python types.

However, the original claim that "Pydantic models are the single source of truth for all
contracts" no longer applies. For cross-device, multi-language Gateway streaming, Protobuf
is now the authoritative Wire Contract layer. Pydantic and Protobuf serve different strata
and are kept consistent through explicit adapters, fixtures, and CI.

See ADR-0007 for the full Domain/Wire dual-authority architecture.

## Context

The BinanceMarketData system needs a public contract layer that:
1. Serves as the single source of truth for data types across all modules
2. Generates machine-readable schemas for cross-module and cross-language validation
3. Is executable (can be used directly in Python code)
4. Supports strict validation (no silent coercion)

## Decision

Phase 1 uses **Python with Pydantic v2** as the executable contract definition.
JSON Schema (Draft 2020-12) is generated deterministically from Pydantic models.
These schemas serve for cross-module validation and future cross-language adoption.

## Alternatives considered

1. **Protobuf first**: Rejected for Phase 1. Protobuf requires a compilation step and has weaker runtime validation ergonomics in Python. Will be considered for Phase 2 cross-language adoption.
2. **Hand-written JSON Schema**: Rejected. Risk of drift between code and schema.
3. **dataclass + custom validation**: Rejected. Pydantic provides battle-tested validation and schema generation.
4. **Avro**: Rejected. JSON Schema has broader tooling support and is more readable.

## Consequences

### Positive
- Single source of truth: Pydantic models ARE the contract
- Deterministic schema generation eliminates hand-maintenance drift
- JSON Schema is language-agnostic for future Go/C++ consumers
- Strict validation prevents silent data corruption

### Negative
- Pydantic is Python-only; cross-language consumers use generated JSON Schema
- JSON Schema has limitations compared to Protobuf (no binary, no versioning built in)
- Schema regeneration must be part of CI to prevent drift

## Compatibility impact

None initially. When Protobuf is adopted, the Pydantic models will serve as the reference for Protobuf message definitions.

## Acceptance criteria

- [x] All PROPOSED contracts have generated JSON Schemas
- [x] Schema generation is deterministic (byte-identical across runs)
- [x] Schema drift CI check passes on every PR
- [x] JSON Schema validates all valid fixtures
- [x] JSON Schema rejects all invalid fixtures

## Superseded by

ADR-0007: Pydantic domain contracts and Protobuf wire contracts
