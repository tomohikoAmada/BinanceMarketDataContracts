# ADR-0006: Projection logical independence, deployment co-location

## Status

ACCEPTED

## Date

2026-08-04 (ACCEPTED 2026-08-05)

## Context

The BinanceMarketDataProjection module produces strategy-independent market facts:
best bid/ask, mid price, spread, microprice, top-N depth, OHLCV, trade tape,
mark/index, funding, OI. These were candidate examples considered when the logical
Projection boundary was first defined.

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

1. **Independent projection process**: Deferred. Adds deployment complexity without clear benefit in Phase 1. Will be re-evaluated if a concrete deployment/scaling requirement appears.
2. **No Projection module**: Rejected. Without it, every consumer must reimplement shared deterministic market-state semantics.
3. **Projection in Strategy**: Rejected. Violates separation of market facts from strategy features.

## Consequences

### Positive
- Simpler Phase 1 deployment
- Same semantic engine can be used for live and replay projections
- Gateway and History can both embed the same projection library

### Negative
- Projection is not independently scalable as a service
- Host CPU load includes Projection work
- A future independent-service migration would require a separate architecture review

## Compatibility impact

Public Projection outputs remain versioned Contracts surfaces. Changing public field semantics is a compatibility concern and must follow the owning contract/repository rules.

## Acceptance criteria

- [ ] Projection library produces identical results for equal ordered inputs/configuration in Gateway and History contexts
- [ ] Projection output contracts have explicit semantics
- [ ] Projection does not include alpha, prediction, or strategy features

## Current interpretation — 2026-08-30

The accepted decision in this ADR is the **logical-independence + embedded-deployment** decision. It must not be read as an authorization to place every deterministic derived market value into the current `BinanceMarketDataProjection` Core.

The implemented Projection repository has since established a narrower production authority:

- fixed-point numeric semantics;
- deterministic order book;
- Spot and USD-M sequence policies;
- stale / duplicate / bridge / gap classification;
- projection lifecycle, reset and resync semantics;
- optional Contracts ProtoAdapter;
- `LocalOrderBookSnapshot` construction.

The original Context examples such as microprice, OHLCV, trade tape, premium, funding and OI were early candidate examples, not a requirement that the current Projection Core implement or own them.

Any future derived-data capability must separately prove that it belongs in shared MarketData semantics rather than FeatureEngineering, and must not expand Projection merely because the computation is deterministic.

For current top-level ownership and dependency rules, see `BinanceMarketData_Living_Architecture.md` v0.3+.

## Superseded by

None.
