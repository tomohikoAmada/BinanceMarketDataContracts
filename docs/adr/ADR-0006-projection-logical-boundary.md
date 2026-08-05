# ADR-0006: Projection logical independence, deployment co-location

## Status

ACCEPTED

## Date

2026-08-04 (ACCEPTED 2026-08-05)

## Context

The BinanceMarketDataProjection module produces strategy-independent market facts:
best bid/ask, mid price, spread, microprice, top-N depth, OHLCV, trade tape,
mark/index, funding, OI. These are deterministic computations over market events.

The question is whether Projection should be:
1. An independent process with its own deployment
2. A library embedded in Gateway and/or History
3. An optional add-on to either

## Decision

Projection logic is **logically independent** (pure, deterministic, strategy-free)
but **deployment is not required to be independent** in Phase 1.

Projection can be embedded in Gateway (for real-time) or History (for replay).
The same projection logic must produce identical results whether run live or in replay.

## Alternatives considered

1. **Independent projection process**: Deferred. Adds deployment complexity without clear benefit in Phase 1. Will be re-evaluated if Gateway IPC latency becomes an issue.
2. **No Projection module**: Rejected. Without it, every consumer must reimplement basic market computations.
3. **Projection in Strategy**: Rejected. Violates separation of market facts from strategy features.

## Consequences

### Positive
- Simpler Phase 1 deployment
- Same code path for live and replay projections
- Gateway and History can both embed the same projection library

### Negative
- Projection is not independently scalable
- Gateway CPU load may increase if many consumers trigger projections
- Migration to independent process later may require API changes

## Compatibility impact

Projection outputs (`MarketStateSnapshot`) are versioned contracts. Changing projection algorithms is generally compatible if the output contract remains stable. Changing what fields are computed or their semantics is BREAKING.

## Acceptance criteria

- [ ] Projection library produces identical results in Gateway and History contexts
- [ ] MarketStateSnapshot contract has defined semantics for each field
- [ ] Projection does not include alpha, prediction, or strategy features

## Superseded by

None.
