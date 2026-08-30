# Contract Inventory

All contracts with status, producer, and consumer information from the current registry/documented
contract set.

## Interpretation note

This inventory records **contract surfaces and candidate producer/consumer relationships**. It does
not by itself assign runtime or computation ownership.

In particular:

- the presence of `market-state-snapshot.v1` does not mean current
  `BinanceMarketDataProjection` Core must compute every possible deterministic derived field;
- references to `health` or `control` identify logical contract consumers/producers and do not
  require standalone `BinanceMarketDataHealth` or `BinanceMarketDataControl` services;
- consumer-facing order-book sequence/gap semantics are owned by Projection, while Gateway owns
  realtime orchestration/serving;
- future OHLCV, trade-tape, premium, funding/OI composition, microprice or similar products remain
  **unassigned unless separately frozen by architecture/contract review**. "Deterministic" alone is
  not sufficient to place a product in Projection Core.

## Core Market Contracts (PROPOSED)

### depth-update.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: projection, health/status logic, history-replay, live-strategy

### agg-trade.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: health/status logic, history-replay, live-strategy; future derived-data consumers as explicitly designed

### book-ticker.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: health/status logic, history-replay, live-strategy; future market-state consumers as explicitly designed

### exchange-depth-snapshot.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: Projection/order-book bootstrap boundary, history/replay

### local-order-book-snapshot.v1
- **Producers**: Projection-backed Gateway publication, Projection-backed historical replay
- **Consumers**: view, live/historical consumers, health/status logic

### market-state-snapshot.v1
- **Producers**: future/unassigned composition surface; any producer must be frozen by a separate design
- **Consumers**: view, live-strategy or other consumers as explicitly accepted
- **Ownership note**: schema existence is not a current Projection Core implementation obligation

### data-health-snapshot.v1
- **Producers**: module-local health/status logic or a future optional aggregator
- **Consumers**: view, risk/policy consumers, operations tooling
- **Ownership note**: does not require a standalone Health service; trading permission remains outside MarketData

## Draft Contracts

| Contract | Version | Status | Notes |
|----------|---------|--------|-------|
| historical-dataset-descriptor | v1 | DRAFT | Pending alignment with Recorder/History |
| replay-query | v1 | DRAFT | Ordering rules need validation |
| telemetry | v1 | DRAFT | Metrics payload is required and must match telemetry type |
| gateway-status-request | v1 | DRAFT | Unary GetGatewayStatus RPC request |
| control-command | v1 | DRAFT | Logical/admin contract candidate; does not require a central Control service |
| command-result | v1 | DRAFT | Error codes need standardization |

## Status definitions

| Status | Meaning |
|--------|---------|
| DRAFT | Under development, not for production use |
| PROPOSED | Submitted for review, awaiting acceptance |
| ACCEPTED | Stable, versioned, with fixtures and tests |
| DEPRECATED | Still usable but will be removed |
| REMOVED | No longer available |
