# Contract Inventory

All contracts with status, producer, and consumer information from `CONTRACT_REGISTRY`.

## Core Market Contracts (PROPOSED)

### depth-update.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: projection, health, history-replay, live-strategy

### agg-trade.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: projection, health, history-replay, live-strategy

### book-ticker.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: projection, health, history-replay, live-strategy

### exchange-depth-snapshot.v1
- **Producers**: recorder-adapter, gateway-adapter
- **Consumers**: order-book, history

### local-order-book-snapshot.v1
- **Producers**: gateway-adapter, replay
- **Consumers**: view, health

### market-state-snapshot.v1
- **Producers**: projection, gateway-adapter
- **Consumers**: view, live-strategy

### data-health-snapshot.v1
- **Producers**: health
- **Consumers**: view, control, risk

## Draft Contracts

| Contract | Version | Status | Notes |
|----------|---------|--------|-------|
| historical-dataset-descriptor | v1 | DRAFT | Pending alignment with Recorder/History |
| replay-query | v1 | DRAFT | Ordering rules need validation |
| telemetry | v1 | DRAFT | Metrics payload is required and must match telemetry type |
| gateway-status-request | v1 | DRAFT | Unary GetGatewayStatus RPC request |
| control-command | v1 | DRAFT | Command parameters may expand |
| command-result | v1 | DRAFT | Error codes need standardization |

## Status definitions

| Status | Meaning |
|--------|---------|
| DRAFT | Under development, not for production use |
| PROPOSED | Submitted for review, awaiting acceptance |
| ACCEPTED | Stable, versioned, with fixtures and tests |
| DEPRECATED | Still usable but will be removed |
| REMOVED | No longer available |
