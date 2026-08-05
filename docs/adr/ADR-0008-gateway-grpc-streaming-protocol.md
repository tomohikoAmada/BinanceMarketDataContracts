# ADR-0008: Gateway gRPC streaming protocol

## Status

ACCEPTED

## Date

2026-08-05

## Context

The BinanceMarketDataGateway is the low-latency real-time distribution module. Its
consumers include:

- Live trading strategies (Python)
- View backend (Python, later Go/Rust)
- Health monitoring (Python)
- External consumers (Go, Rust)

These consumers may run on different machines (macOS, Ubuntu). The Gateway must support:

1. Multiple concurrent subscribers with independent lifecycles
2. Three read modes: contiguous event stream, order book (snapshot + diff stream),
   and latest market state
3. Backpressure and slow-consumer isolation
4. Explicit gap/recovery semantics
5. Cross-language compatibility via Protobuf wire contracts

## Decision

### Primary protocol: gRPC over HTTP/2 with Protobuf payloads

- Server-streaming RPCs for all real-time subscriptions.
- Unary RPC for one-shot status queries.
- V1 does NOT include bidirectional streaming, client-streaming, or trading/account RPCs.

### Three streaming RPCs

1. `SubscribeEvents` → server-streaming `GatewayEventEnvelope`
   - Delivers `DepthUpdate`, `AggTrade`, `BookTicker` as contiguous events.
   - Delivery mode: `CONTIGUOUS_EVENTS`. Silent message dropping is forbidden.

2. `SubscribeOrderBook` → server-streaming `OrderBookStreamItem`
   - Initial snapshot required, then continuous depth updates.
   - Snapshot + Stream handoff must be gapless.

3. `SubscribeMarketState` → server-streaming `MarketStateStreamItem`
   - `LATEST_STATE` delivery mode: intermediate states may be skipped.
   - Each state snapshot is self-describing.

### Unary RPC

- `GetGatewayStatus` → `GatewayStatusSnapshot`

### Slow consumer semantics

- Each consumer has an independent bounded queue (implemented in Gateway, not Contracts).
- `CONTIGUOUS_EVENTS` consumers: if queue overflows, Gateway sends explicit
  `ConsumerGapNotice` with recovery action and closes the stream.
- `LATEST_STATE` consumers: old states are overwritten; latest state is always available.
  Overwritten intermediate states are NOT gaps.
- One slow consumer must not block other consumers.

### Snapshot + Stream handoff

- Gateway accepts subscription → caches incoming DepthUpdates behind a logical barrier
  → obtains/generates synchronized LocalOrderBookSnapshot(L) → sends
  SubscriptionAccepted → sends Snapshot(L) → sends cached DepthUpdates bridgeable to L
  → enters LIVE → continues with live DepthUpdates.
- Consumers: Snapshot(L) → first bridgeable DepthUpdate → contiguous stream.
- If handoff fails: Gateway sends `ConsumerGapNotice` with `REQUEST_NEW_SNAPSHOT` or
  `RESUBSCRIBE`, does NOT silently deliver unreliable order books.

### Gap and recovery

- Every gap is explicit (`ConsumerGapNotice` or `StreamStatus`).
- `session_sequence` is per-subscription delivery sequence, NOT Binance update ID.
- Gateway restart → new `gateway_instance_id`.
- Upstream connection rebuild → incremented `connection_generation`.
- Gap without notice → protocol violation.

### Browser consumers

- Browsers do not connect directly to gRPC.
- Future: View Backend / BFF bridges gRPC → WebSocket/JSON for browser UIs.

## Alternatives considered

1. **WebSocket + JSON**: rejected. No built-in streaming semantics, field evolution
   fragile, verbose.
2. **Unix Domain Socket (same-machine only)**: rejected. Does not support cross-device
   consumers without additional bridging.
3. **Kafka**: rejected for V1. Adds infrastructure complexity without clear benefit at
   current scale.
4. **Bidirectional streaming**: deferred. Not needed for V1 read-only consumption pattern.

## Consequences

### Positive

- Single `.proto` source for C++, Rust, Go, and Python consumers.
- gRPC provides streaming, backpressure, code generation, and health checking.
- Explicit gap semantics prevent silent data corruption.
- Protocol is self-describing and implementable in any language with gRPC support.

### Negative

- gRPC has higher operational complexity than simple WebSocket.
- Browser consumers need a proxy/BFF layer.
- Protobuf code generation adds build step.

### Risks

- gRPC streaming performance under high message rates not yet measured.
  Mitigation: Gateway is a separate process, can be tuned independently.
- Cross-language implementations may diverge if not tested.
  Mitigation: shared Protobuf source and adapter tests.

## Acceptance criteria

- [ ] `.proto` files define all three streaming RPCs and one unary RPC
- [ ] `gateway-streaming.md` documents snapshot handoff, gap, and slow consumer semantics
- [ ] Transcript fixtures cover normal handoff, gap, and invalid sequences
- [ ] Protocol constraints are tested in CI
- [ ] Protocol is reviewed and implementable in C++, Rust, Go, and Python

## Compatibility impact

- New contracts: Gateway service definition, gateway messages.
- Existing Pydantic market event contracts unchanged.
- This is a V1 protocol baseline; V1 consumers must implement these semantics.

## Superseded by

None.
