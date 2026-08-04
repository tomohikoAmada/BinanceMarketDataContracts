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
- Adding new QualityFlag values that old consumers can ignore
- Documentation clarifications without semantic changes
- Relaxing constraints that don't invalidate previously-valid values

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
- NOT for production use

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
