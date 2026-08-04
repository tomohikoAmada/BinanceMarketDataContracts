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
python -m binance_market_data_contracts.schema_export
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

- Prices: `^(0|[1-9][0-9]*)(\\.[0-9]+)?$` with Decimal > 0
- Quantities: `^(0|[1-9][0-9]*)(\\.[0-9]+)?$` with Decimal >= 0
- No scientific notation, no leading zeros, no trailing dot, no leading dot
- No NaN, Infinity, float, int, empty string, whitespace
