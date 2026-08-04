# ADR-0003: Time semantics

## Status

PROPOSED

## Date

2026-08-04

## Context

Market data events carry multiple timestamps from different clocks:
- Exchange-assigned event times
- Local receive times (wall clock and monotonic)
- Generation times for derived snapshots
- Observation times for health assessments

Without explicit conventions, consumers risk misinterpreting timestamps, comparing incompatible clocks, or silently using missing time as zero.

## Decision

All time field names MUST include their unit suffix. Time values are always integers. Missing times use `null`, never `0`. The contracts package defines clear semantics for each clock type.

### Required suffixes
- `_ms` — milliseconds (exchange times)
- `_utc_ns` — nanoseconds UTC wall clock
- `_monotonic_ns` — nanoseconds monotonic clock

### Forbidden
- `timestamp` as a field name (ambiguously named)
- Using `0` to mean "missing"
- Negative time values
- Mixing monotonic and UTC times in comparisons

## Alternatives considered

1. **Single `timestamp` field**: Rejected. Cannot distinguish between different clocks and capture points.
2. **Timestamp as datetime object**: Rejected. Adds serialization complexity; int nanosecond is simpler and more precise.
3. **Float seconds**: Rejected. Floating-point cannot precisely represent nanosecond timestamps.

## Consequences

### Positive
- Field names are self-documenting
- No ambiguity about which clock a timestamp comes from
- Type system enforces correct usage (comparing `_utc_ns` with `_utc_ns`)
- Integer representation is precise and compact in JSON/Parquet

### Negative
- Longer field names (e.g., `receive_time_utc_ns` vs `ts`)
- Consumers must handle null for missing times
- Requires discipline in producer modules to capture timestamps correctly

## Compatibility impact

Changing a field's time unit (e.g., `_ms` to `_ns`) is BREAKING. Adding new optional time fields is compatible.

## Acceptance criteria

- [ ] All public contract time fields have unit suffixes
- [ ] No field named `timestamp` exists in any public contract
- [ ] Missing times use `null` (validated by tests)
- [ ] Negative times are rejected (validated by tests)
- [ ] Time semantics documented in `docs/contracts/time_semantics.md`

## Superseded by

None.
