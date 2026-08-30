# ADR-0001: Recorder and Gateway use independent connections

## Status

ACCEPTED

## Date

2026-08-04 (ACCEPTED 2026-08-05)

## Context

The BinanceMarketData system has two primary producers of market data events:
- **Recorder**: responsible for reliable, verifiable, and replayable data persistence
- **Gateway**: responsible for low-latency real-time data distribution

These modules have fundamentally different quality requirements:
- Recorder prioritizes reliability and completeness
- Gateway prioritizes minimal latency

## Decision

The Recorder and Gateway will each maintain their own independent WebSocket connections to Binance. They will not share a connection, queue, or event stream.

## Alternatives considered

1. **Shared connection**: Gateway publishes to Recorder. Rejected because Gateway failure would cause data loss in Recorder.
2. **Recorder publishes to Gateway**: Rejected because Recorder's write path adds unacceptable latency for real-time consumers.
3. **Both from a single shared downstream**: Rejected because no shared component should become a single point of failure.

## Consequences

### Positive
- Fault isolation: Recorder failure does not affect Gateway and vice versa
- Each module can optimize for its own quality target
- Independent channels can be compared later by an observability/health capability if that comparison is operationally useful

### Negative
- Double the WebSocket connections to Binance
- Slight data divergence between Recorder and Gateway is possible
- Higher operational complexity (two connection lifecycles to manage)

## Compatibility impact

None. This is an operational deployment decision that does not affect public contracts.

## Acceptance criteria

- [ ] Gateway latency meets targets with independent connection
- [ ] Recorder completeness meets targets with independent connection
- [ ] Connection limits are within Binance rate limits
- [ ] If Recorder/Gateway divergence comparison is implemented, it remains out of both critical data paths and reports facts rather than trading decisions

## Current interpretation — 2026-08-30

The accepted authority of this ADR is the **independent Recorder/Gateway source connection and failure-domain decision**.

References in the original design to a dedicated `Health` module must not be interpreted as requiring a standalone `BinanceMarketDataHealth` service. Under the current top-level architecture, health/observability is first a capability of each component; a future aggregator may compare the independent Recorder and Gateway channels when scale or operations justify it.

See `BinanceMarketData_Living_Architecture.md` v0.3+ for the current top-level component model.

## Superseded by

None.
