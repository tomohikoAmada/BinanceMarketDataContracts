# AGENTS.md — BinanceMarketDataContracts

Guidance for AI coding agents (OpenCode, Codex, etc.) working on this repository.

## Architecture documents

- `docs/CURRENT_STATE.md` — current orientation index; verify GitHub/code independently
- `ARCHITECTURE.md` — entry point for architectural context
- `BinanceMarketData_Living_Architecture.md` — full living architecture document
- `docs/adr/` — architecture decision records
- `docs/contracts/` — contract inventory, semantics, compatibility policy

Recommended AI/reviewer reading order: `docs/CURRENT_STATE.md`, `AGENTS.md`, `README.md`,
`ARCHITECTURE.md`, the relevant milestone/design document, accepted ADRs, actual code/tests, and
the active PR body plus exact-head CI. `docs/CURRENT_STATE.md` is a current-state summary only;
accepted ADRs and semantic designs remain authoritative.

## Responsibilities

This package provides **public data types only**:

- Versioned Pydantic domain contracts
- Versioned Protobuf wire contracts
- gRPC service definitions (proto files only)
- Generated JSON Schemas (Draft 2020-12)
- Generated Python protobuf stubs
- Explicit Pydantic ↔ Protobuf adapters
- Golden fixtures (valid, invalid, boundary)
- Contract registry and versioning (domain + wire)
- Architecture decision records

## Forbidden

- Network I/O (no Binance client, no WebSocket, no HTTP)
- Database or persistence (no SQLite, no filesystem access except schema export CLI)
- Trading, account, position, or API-key functionality
- Binary floating-point for public price/quantity fields
- Dependency on Recorder, Gateway, Health, History, or View internals
- Modifying ACCEPTED contract semantics without ADR
- Unrestricted `dict[str, Any]` as permanent contract payloads
- Using `timestamp` as a field name
- Server or daemon implementation (no gRPC runtime, no Gateway server)

## Protobuf rules

- `.proto` field numbers must **never** be reused
- Enum numbers must **never** be changed
- Deleted fields must be reserved by number and name:
  ```protobuf
  reserved 4, 5;
  reserved "old_field_name";
  ```
- Wire breaking change → new major package (e.g., `v2/`)
- Generated files under `src/binance_market_data/` are **never** hand-edited
- No binary floating-point for price/quantity fields in protobuf; use string representation
- No `google.protobuf.Any` or `google.protobuf.Struct`
- No `timestamp` as a field name; use `exchange_event_time_ms`, `receive_time_utc_ns`, etc.

## Cross-strata consistency

- Pydantic domain contract changes must check the corresponding proto mapping
- Proto changes must check the corresponding Pydantic adapter
- All changes must update fixtures, descriptor, registry, and ADR/docs
- No silent drift between Pydantic and Proto representations
- Adapter round-trip tests must pass for all mapped contract pairs

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src/binance_market_data_contracts
pytest -q
python -m binance_market_data_contracts.schema_export --output schemas/json
git diff --exit-code -- schemas/json
python -m build
python -m twine check dist/*
```

## Contract change process

1. Discuss semantic change in an ADR or issue
2. Mark contract as DEPRECATED; add new version if needed
3. Update fixtures, schema, manifest, tests, registry, and documentation
4. Ensure full validation passes before commit
5. Never silently change an ACCEPTED contract's meaning

## Decimal string rules

- **PriceString**: uses `POSITIVE_DECIMAL_PATTERN` — rejects zero, requires > 0
- **QuantityString**: allows zero (>= 0), used for order book levels
- **PositiveQuantityString**: rejects zero (used for AggTrade quantity)
- **SignedDecimalString**: rejects negative zero (-0, -0.0, -0.0000)
- No scientific notation, no leading zeros, no trailing dot, no leading dot
- No NaN, Infinity, float, int, empty string, whitespace
- Trailing zeros preserved: "1.2300" stays "1.2300"

## Serialization rules

- `stream` and `schema_version` are **required** in serialized form (no defaults)
- `_BaseEventMetadata` is internal; consumers use specific Metadata types
- All public collections use `tuple` for deep immutability
- JSON input: use `model_validate_json()` (string enums accepted)
- Python input: use Enum instances (strict mode, no string coercion)
- Schema export: `python -m binance_market_data_contracts.schema_export --output schemas/json`
