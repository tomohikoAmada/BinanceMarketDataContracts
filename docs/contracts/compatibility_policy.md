# Compatibility Policy

## Versioning scheme

Contracts follow `<contract-name>.v<major>` versioning:

```
depth-update.v1
agg-trade.v1
book-ticker.v1
```

## Compatible changes

Generally compatible (do not bump major version):
- Adding optional fields with clear default semantics
- Adding enum values only at a binary transport boundary that preserves unknown
  values; strict Domain/JSON consumers need explicit support before using them
- Documentation clarifications without semantic changes
- Relaxing constraints that don't invalidate previously-valid values

## Compatibility depends on the boundary

| Boundary | Added unknown fields | Unknown QualityFlag values |
|----------|----------------------|----------------------------|
| Binary protobuf parse/serialize | Retained by the supported runtime unless explicitly discarded | Numeric value retained by proto3 |
| Protobuf → Pydantic adapter | Only mapped fields enter Domain; unknown fields are lost on Domain → protobuf conversion | Rejected with `UnknownEnumValueError`; enum zero is also rejected |
| Domain JSON / Pydantic | Rejected (`extra="forbid"`) | Rejected; no automatic ignore or coercion |

Domain JSON is not ProtoJSON. A lossless binary round-trip is not a guarantee of
a lossless Domain round-trip or semantic support for new flags. A new QualityFlag
requires coordinated consumer support/negotiation at strict boundaries.

C0 aligns the **currently consumed** PROPOSED/DRAFT integer fields with existing
`uint64` and positive `int32` wire ranges (see [C0 field table](../C0_IMPLEMENTATION.md)).
Previously valid, representable messages keep their wire format and meaning.
Previously Domain-accepted overflow values now fail validation; this is a Domain
admission restriction, not universal backward compatibility. Present-empty optional
Symbol is invalid, rather than silently converted to absence (ADR-0011/ADR-0012).
No field number, enum number, proto type, RPC, schema version or contract status changes.

## Breaking changes

BREAKING changes require a new major version:

- Removing a field
- Renaming a field
- Adding a required field
- Changing a field's unit
- Changing a field's semantics
- Changing the meaning of `null`
- Switching between float and decimal string
- Changing ID rules
- Changing ordering rules
- Changing gap policy
- Adding/changing enum values that old consumers cannot safely handle
- Changing field name semantics within the same contract name

## Contract status lifecycle

```
DRAFT → PROPOSED → ACCEPTED → DEPRECATED → REMOVED
```

### DRAFT
- Under active development
- May change without notice
- No general production support promise. The [C1 internal subset](current-capabilities.md)
  is consumed only at its fixed versions and documented runtime support; this
  does not promote or freeze every DRAFT contract.

### PROPOSED
- Submitted for review
- Has defined Producer and Consumer
- Review in progress

### ACCEPTED
- Stable and versioned
- Has complete fixtures and tests
- Changing semantics is BREAKING

### DEPRECATED
- Still functional but will be removed
- Must specify replacement version
- Consumers should migrate

### REMOVED
- No longer available
- Must have had a migration period

## Acceptance criteria for PROPOSED → ACCEPTED

1. Producer and Consumer identified
2. Schema frozen
3. Valid, invalid, and boundary fixtures complete
4. Contract tests pass
5. At least one producer adapter and one consumer usage validated
6. Architecture review complete

## Migration rules

- Deprecated contracts remain functional for at least one release
- Migration guides must document all breaking changes
- New version must coexist with deprecated version during migration
