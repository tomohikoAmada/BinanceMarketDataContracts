# Naming and Units

## Field naming conventions

- **snake_case**: All field names use lower_snake_case
- **Unit suffix**: Time fields must include unit suffix (`_ms`, `_utc_ns`, `_monotonic_ns`)
- **No ambiguous names**: `timestamp` is forbidden as a field name
- **No abbreviations without definition**: Prefer `quantity` over `qty`

## Price fields

- Named `price`, `best_bid_price`, `best_ask_price`, `mid_price`, `mark_price`, `index_price`
- Type: `PriceString` (validated decimal string)
- Unit: Quote currency of the trading pair
- Constraint: value > 0

## Quantity fields

- Named `quantity`, `best_bid_quantity`, `best_ask_quantity`, `open_interest`
- Type: `QuantityString` (validated decimal string)
- Unit: Base currency of the trading pair
- Constraint: value >= 0

## Time fields

See `docs/contracts/time_semantics.md`.

## ID fields

- Named descriptively: `connection_id`, `request_id`, `aggregate_trade_id`, `command_id`, `dataset_id`
- Type: `str` or validated `str` (`ConnectionId`, `RequestId`)
- All IDs are non-empty strings

## Symbol fields

- `Symbol` is an opaque exchange identity, not a normalized ticker code.
- Preserve its Unicode code points and case exactly; do not normalize or case-fold it.
- It must be non-empty and contain no U+0000..U+0020, U+007F, or surrogate code points.
- It has no contract-level maximum length. U+0080, U+00A0, and U+3000 are not forbidden.
- See accepted ADR-0011 for the compatibility and wire rationale.

## Enum values

- All enum values are UPPER_SNAKE_CASE strings
- Enum field types use `StrEnum` for JSON compatibility
- New enum values are compatible additions; removing values is BREAKING
