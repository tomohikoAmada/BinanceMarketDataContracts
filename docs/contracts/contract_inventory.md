# Contract Inventory

All contracts with status, producer, and consumer information.

## Core Market Contracts

| Contract | Version | Status | Producer | Consumer |
|----------|---------|--------|----------|----------|
| depth-update | v1 | PROPOSED | recorder or gateway | all modules |
| agg-trade | v1 | PROPOSED | recorder or gateway | all modules |
| book-ticker | v1 | PROPOSED | recorder or gateway | all modules |
| exchange-depth-snapshot | v1 | PROPOSED | recorder or gateway | order book, history |
| local-order-book-snapshot | v1 | PROPOSED | gateway or replay | view, health |
| market-state-snapshot | v1 | PROPOSED | projection or gateway | view, strategy |
| data-health-snapshot | v1 | PROPOSED | health | view, control, risk |

## Draft Contracts

| Contract | Version | Status | Notes |
|----------|---------|--------|-------|
| historical-dataset-descriptor | v1 | DRAFT | Pending alignment with Recorder/History implementation |
| replay-query | v1 | DRAFT | Ordering rules need validation with real data |
| telemetry | v1 | DRAFT | Metrics payload types need refinement |
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
