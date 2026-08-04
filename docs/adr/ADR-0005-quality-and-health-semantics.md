# ADR-0005: Separation of quality flags, health states, and reason codes

## Status

PROPOSED

## Date

2026-08-04

## Context

The BinanceMarketData system needs to communicate both what is observed about data (facts) and whether data should be used (judgments). Conflating these concepts leads to confusion — a consumer might not know whether a flag means "the data has an issue" or "the system has decided to stop using this data."

## Decision

Three separate concepts with clear boundaries:

### QualityFlag — observable data facts
Produced in the data path (Gateway, Recorder). Describes what was observed.
Examples: `DUPLICATE`, `SEQUENCE_GAP`, `CROSSED_BOOK`, `IDENTITY_CONFLICT`, `OUT_OF_ORDER`.

### HealthState — overall assessment
Produced by the Health module. Represents a judgment about whether data should be used.
Values: `HEALTHY`, `DEGRADED`, `UNRELIABLE`, `UNAVAILABLE`.

### ReasonCode — judgment rationale
Produced by the Health module. Explains why a particular HealthState was chosen.
Examples: `SEQUENCE_GAP_DETECTED`, `BOOK_CROSSED`, `RECORDER_STALLED`, `DIVERGENCE_DETECTED`.

## Key principles

1. QualityFlags travel with the data (in event metadata)
2. HealthState is an asynchronous assessment, not in the hot data path
3. ReasonCodes explain the HealthState, not the data
4. Health must not block the Gateway hot path
5. Unreliable data must be explicitly communicated; silence is not consent

## Alternatives considered

1. **Single status field**: Rejected. Cannot distinguish between "this event has a gap flag" (fact) and "we judge the entire stream unreliable" (judgment).
2. **Exceptions for bad data**: Rejected. Exceptions are not portable across module/process boundaries.
3. **Health inline in every event**: Rejected. Health assessment requires aggregation across events; per-event health would be stale or inaccurate.

## Consequences

### Positive
- Clear separation of concerns: data path vs health assessment
- Consumers can make their own decisions based on QualityFlag even if they disagree with HealthState
- Health module can be developed, tested, and deployed independently
- Evolution of health logic does not require contract changes

### Negative
- Three concepts instead of one — more for consumers to understand
- Risk that QUALITY_FLAG values and REASON_CODE values overlap confusingly

## Compatibility impact

Adding new QualityFlag or ReasonCode values is generally compatible. Removing or renaming existing values is BREAKING.

## Acceptance criteria

- [ ] QualityFlag enum exists and is included in event metadata
- [ ] HealthState enum exists and is used in DataHealthSnapshot
- [ ] ReasonCode enum exists and is used in DataHealthSnapshot
- [ ] No QualityFlag is also a ReasonCode and vice versa
- [ ] Separation documented in `docs/contracts/quality_semantics.md`

## Superseded by

None.
