# ADR-0002: Python Pydantic + JSON Schema first

## Status

PROPOSED

## Date

2026-08-04

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

- [ ] All PROPOSED contracts have generated JSON Schemas
- [ ] Schema generation is deterministic (byte-identical across runs)
- [ ] Schema drift CI check passes on every PR
- [ ] JSON Schema validates all valid fixtures
- [ ] JSON Schema rejects all invalid fixtures

## Superseded by

None.
