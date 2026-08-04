# AGENTS.md — BinanceMarketDataContracts

Guidance for AI coding agents (OpenCode, Codex, etc.) working on this repository.

## Architecture documents

- `ARCHITECTURE.md` — entry point for architectural context
- `BinanceMarketData_Living_Architecture.md` — full living architecture document
- `docs/adr/` — architecture decision records
- `docs/contracts/` — contract inventory, semantics, compatibility policy

## Responsibilities

This package provides **public data types only**:

- Versioned Pydantic contracts
- Generated JSON Schemas (Draft 2020-12)
- Golden fixtures (valid, invalid, boundary)
- Contract registry and versioning
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

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src
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