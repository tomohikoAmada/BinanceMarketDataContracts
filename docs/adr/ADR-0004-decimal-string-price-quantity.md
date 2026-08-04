# ADR-0004: Decimal string representation for price and quantity

## Status

PROPOSED

## Date

2026-08-04

## Context

Binance market data includes prices and quantities that must be represented exactly. Using binary floating-point (IEEE 754) introduces rounding errors, especially when accumulating large numbers of small values or comparing values for equality.

## Decision

All public price and quantity fields use **validated decimal strings**. The exact string representation is preserved, including trailing zeros. Binary floating-point (`float`) is forbidden for public price and quantity fields.

### Validation rules

**Prices** (e.g., `PriceString`):
- Must match: `^(0|[1-9][0-9]*)(\.[0-9]+)?$`
- Decimal value must be > 0
- No scientific notation, leading zeros, trailing dot, leading dot, whitespace

**Quantities** (e.g., `QuantityString`):
- Must match: `^(0|[1-9][0-9]*)(\.[0-9]+)?$`
- Decimal value must be >= 0
- No scientific notation, leading zeros, trailing dot, leading dot, whitespace

### Explicitly rejected
- `float` and `int` types
- `NaN`, `Infinity`, `-Infinity`
- Scientific notation (`1e3`, `1.5E-2`)
- Leading plus sign (`+1.0`)
- Leading zeros (`0001.20`)
- Leading dot (`.5`)
- Trailing dot (`1.`)
- Negative zero (`-0`)
- Empty string, whitespace

### Trailing zeros
Trailing zeros in the fractional part are preserved (e.g., `"1.2300"` stays `"1.2300"`). This preserves the exchange's reported precision.

## Alternatives considered

1. **Binary float (float)**: Rejected. IEEE 754 cannot exactly represent all decimal values. `0.1 + 0.2 != 0.3` in float.
2. **Decimal type**: Pydantic's `Decimal` type was considered but it serializes to float in JSON by default. String is safer and portable.
3. **Integer with implicit scale (e.g., micro-units)**: Rejected. Requires knowing the scale per symbol, adds conversion complexity, error-prone.

## Consequences

### Positive
- Exact representation of all decimal values
- No floating-point precision surprises
- JSON representation is human-readable
- Compatible with Parquet/Arrow decimal types

### Negative
- Slightly larger JSON payloads (string vs number)
- Requires explicit Decimal parsing for arithmetic
- Consumers must handle string-to-decimal conversion

## Compatibility impact

Changing from string to float or from float to string is BREAKING. The string format rules are part of the contract and cannot change without a major version bump.

## Acceptance criteria

- [ ] All price/quantity fields use validated string types
- [ ] No float type in public price/quantity fields
- [ ] All rejection cases have tests
- [ ] Trailing zeros are preserved in round-trip
- [ ] Documented in ADR and AGENTS.md

## Superseded by

None.
