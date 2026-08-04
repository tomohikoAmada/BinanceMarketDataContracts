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
- Deterministic JSON Schema export (Draft 2020-12)
- Golden fixtures with machine-readable manifest
- Architecture decision records (ADR-0001 through ADR-0006)
- CI workflow (ruff, mypy, pytest, schema drift, build, twine)
- Compatibility policy and contract governance documentation

### Status

All contracts are in **PROPOSED** or **DRAFT** status. No contract has been formally ACCEPTED yet.
