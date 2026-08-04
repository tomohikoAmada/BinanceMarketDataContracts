# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0a1] — Unreleased

### Added

- Initial Workstream 0 contracts baseline (PROPOSED status)
- Core market contracts: DepthUpdate, AggTrade, BookTicker, ExchangeDepthSnapshot
- State contracts: LocalOrderBookSnapshot, MarketStateSnapshot, DataHealthSnapshot
- Draft contracts: HistoricalDatasetDescriptor, ReplayQuery, Telemetry, ControlCommand
- Contract registry with status tracking (DRAFT / PROPOSED / ACCEPTED / DEPRECATED / REMOVED)
- Deterministic JSON Schema export (Draft 2020-12) with `--output` CLI argument
- Golden fixtures with machine-readable manifest and strict validation
- Architecture decision records (ADR-0001 through ADR-0006)
- CI workflow (ruff, mypy, pytest, schema drift, build, twine, wheel isolation)
- Compatibility policy and contract governance documentation
- Recursive time-field validation across nested models
- Wheel isolation test validating py.typed, fixture parsing, and schema equality

### Fixed

- Required explicit stream and schema_version in serialized contracts
- Aligned positive decimal semantics between Pydantic and JSON Schema
- Rejected whitespace-only identifiers and negative zero in signed decimals
- Replaced skipped semantic-schema tests with explicit assertions
- Added full installed-wheel fixture and typing-marker validation
- ReplayQuery and TelemetryEnvelope now require schema_version
- SignedDecimal JSON Schema regex rejects negative zero
- Fixture Manifest uses strict Pydantic model validation
- Control command type must match parameters.type
- Telemetry envelope type must match metrics.type
- Telemetry source_module uses NonEmptyText (rejects whitespace)
- Archive date uses Python date type with format validation

### Changed

- EventMetadata replaced by specific metadata types (DepthUpdateMetadata etc.)
- BaseEventMetadata is internal (_BaseEventMetadata, not in public API)
- top_n_depth replaced by top_bids/top_asks in MarketStateSnapshot
- Custom ValidationError removed (pydantic.ValidationError is the runtime error)
- Schema export uses --output CLI argument (no repo root guessing)
- Schemas organized in schemas/json/contracts/ with contract-catalog.json

### Status

All contracts are in **PROPOSED** or **DRAFT** status. No contract has been formally ACCEPTED yet.