# ADR-0001: Recorder and Gateway use independent connections

## Status

PROPOSED

## Date

2026-08-04

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
- Health module can compare two independent data channels for divergence detection

### Negative
- Double the WebSocket connections to Binance
- Slight data divergence between Recorder and Gateway is possible (detected by Health)
- Higher operational complexity (two connection lifecycles to manage)

## Compatibility impact

None. This is an operational deployment decision that does not affect public contracts.

## Acceptance criteria

- [ ] Gateway latency meets targets with independent connection
- [ ] Recorder completeness meets targets with independent connection
- [ ] Health module detects and reports Recorder/Gateway divergence
- [ ] Connection limits are within Binance rate limits

## Superseded by

None.
