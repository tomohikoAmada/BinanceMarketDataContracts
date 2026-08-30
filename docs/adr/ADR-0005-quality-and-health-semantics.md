# ADR-0005: Separation of quality flags, health states, and reason codes

## Status

PROPOSED

## Date

2026-08-04

## Clarified

2026-08-30 — aligned with BinanceMarketData top-level architecture v0.3.

## Context

The BinanceMarketData system needs to communicate both what is observed about data and the
aggregated operational/data-quality state of a stream or component. These concepts must remain
separate from trading authorization.

A MarketData status may report that data is stale, degraded, unavailable, crossed or has a sequence
gap. It must not itself decide whether a strategy may open, close or resize a position. Trading
permission belongs to `RiskManagement` (or another explicitly designated trading-policy owner), not
to BinanceMarketData.

The earlier wording assumed a standalone `BinanceMarketDataHealth` module. Top-level architecture
v0.3 does not require such a service. Health is currently a cross-cutting capability: each runtime
component can publish factual status/telemetry, and an optional aggregator may be introduced later if
real scale or operational requirements justify it.

## Decision

Keep three distinct public concepts with clear boundaries.

### QualityFlag — observable data facts

Produced at the relevant data/semantic boundary (for example Gateway, Recorder or Projection-backed
serving logic). Describes what was observed about a specific event/state.

Examples: `DUPLICATE`, `SEQUENCE_GAP`, `CROSSED_BOOK`, `IDENTITY_CONFLICT`, `OUT_OF_ORDER`.

### HealthState — aggregated MarketData condition

Represents an operational/data-quality assessment such as whether a stream/component is healthy,
degraded, unreliable or unavailable.

Values: `HEALTHY`, `DEGRADED`, `UNRELIABLE`, `UNAVAILABLE`.

A `HealthState` is a MarketData fact/assessment for consumers. It is **not** a command to trade or
not trade.

The producer may be module-local health/status logic or, in a future larger deployment, an optional
health aggregator. A dedicated Health process is not required by this ADR.

### ReasonCode — assessment rationale

Explains why a particular `HealthState` was emitted.

Examples: `SEQUENCE_GAP_DETECTED`, `BOOK_CROSSED`, `RECORDER_STALLED`,
`DIVERGENCE_DETECTED`.

Like `HealthState`, a reason code reports MarketData condition; it does not own Risk policy.

## Key principles

1. QualityFlags travel with or describe the affected data/state.
2. Aggregated health assessment must not block the Gateway hot path.
3. ReasonCodes explain the MarketData health assessment.
4. Unreliable data must be explicitly communicated; silence is not consent.
5. MarketData reports condition; `RiskManagement` owns trading permission/action.
6. No standalone Health service is required until concrete aggregation/lifecycle needs justify it.

## Alternatives considered

1. **Single status field**: Rejected. Cannot distinguish a specific observed quality fact from an
   aggregated stream/component condition.
2. **Exceptions for bad data**: Rejected. Exceptions are not portable across module/process
   boundaries.
3. **Health inline in every event**: Rejected. Aggregated health may require state across events and
   should not be recomputed as a mandatory hot-path operation.
4. **Central Health service from day one**: Rejected for the current scale. It adds a deployment and
   failure boundary without a present requirement.
5. **Health decides trading permission**: Rejected. That would move Risk policy into MarketData.

## Consequences

### Positive

- Clear separation of specific data facts, aggregated MarketData condition and trading policy.
- Consumers may apply their own policy to MarketData facts.
- Module-local status can exist without a central service.
- A later aggregator can be introduced without changing the fundamental ownership boundary.

### Negative

- Consumers must understand the difference between QualityFlag, HealthState and ReasonCode.
- A future aggregator will need explicit composition rules if multiple module-local states disagree.

## Compatibility impact

This clarification does not change the current schema. Adding/removing/renaming enum values still
follows the normal contract compatibility policy.

## Acceptance criteria

- [ ] QualityFlag enum exists and is included where the relevant public event/state contract requires it.
- [ ] HealthState enum is usable in DataHealthSnapshot.
- [ ] ReasonCode enum is usable in DataHealthSnapshot.
- [ ] The semantics do not require a dedicated Health process.
- [ ] No MarketData health value normatively commands a trading action.
- [ ] Separation is documented in `docs/contracts/quality_semantics.md`.

## Superseded by

None.
