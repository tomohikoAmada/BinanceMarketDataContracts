# Gateway Streaming Protocol

Documents the Gateway gRPC streaming protocol semantics for Snapshot + Stream
handoff, gap detection, recovery, slow consumer behavior, and delivery modes.

## 1. Delivery Modes

### 1.1 CONTIGUOUS_EVENTS

Used by `SubscribeEvents` for DepthUpdate, AggTrade, BookTicker.

- Every event must be delivered. Silent message dropping is forbidden.
- `session_sequence` is per-subscription, monotonic, starts at 1.
- A consumer gap must be explicitly signaled via `ConsumerGapNotice`.
- A slow consumer whose queue overflows receives a `ConsumerGapNotice` and the
  stream is closed. It must not block other consumers.

### 1.2 LATEST_STATE

Used by `SubscribeMarketState` for MarketStateSnapshot.

- Intermediate states may be overwritten; only the latest is delivered.
- Overwritten states are NOT consumer gaps.
- Each snapshot is self-describing (contains `source_book_update_id`,
  `source_trade_id`, `book_synchronized`).
- `session_sequence` only reflects actual delivery order, not Binance update IDs.
- Source book version must be read from snapshot fields, not inferred from
  `session_sequence`.

## 2. Order Book Snapshot + Stream Handoff

### 2.1 Normal Flow

Let the snapshot's `last_update_id = L`.

1. Gateway accepts subscription.
2. Gateway establishes a logical barrier behind which incoming DepthUpdates
   are cached.
3. Gateway obtains or generates a synchronized `LocalOrderBookSnapshot(L)`.
4. Gateway sends `SubscriptionAccepted` (seq=1).
5. Gateway may send `StreamStatus(SNAPSHOT_PENDING)` (seq=2, optional).
6. Gateway sends `OrderBookStreamItem` with `snapshot(L)` (seq=3).
7. Gateway sends cached DepthUpdates that can bridge to L.
8. Gateway enters `StreamStatus(LIVE)` (seq=N).
9. Subsequent live DepthUpdates are delivered contiguously.

**Consumer view**:

```
SubscriptionAccepted(seq=1)
Snapshot(L, seq=2)
DepthUpdate(bridgeable to L, seq=3)
DepthUpdate(seq=4)
...
LIVE status
```

No invisible window between Snapshot and first bridgeable DepthUpdate.

### 2.2 Gap / Failure Flow

If snapshot fails, bootstrap buffer overflows, bridge point cannot be found,
upstream sequence gap is detected, Gateway restarts, or resume data is evicted:

1. Gateway sends `ConsumerGapNotice` or `StreamStatus(DEGRADED)` with
   `recovery_action = REQUEST_NEW_SNAPSHOT | RESUBSCRIBE`.
2. Subscription is closed or marked for resync.
3. No further DepthUpdates are sent until a new snapshot is established.
4. Gateway MUST NOT continue delivering DepthUpdates and claim the book is
   reliable after a known gap.

## 3. Gap and Recovery Protocol

### 3.1 Gap Detection

A gap is detected when:
- `session_sequence` is non-contiguous on the consumer side.
- Gateway explicitly sends `ConsumerGapNotice`.
- `connection_generation` changes without an accompanying status notice.
- Gateway restarts (new `gateway_instance_id`).

### 3.2 Gap Types and Recovery

| Reason | Recovery Action |
|--------|----------------|
| SLOW_CONSUMER | RESUBSCRIBE |
| RESUME_NOT_AVAILABLE | REQUEST_NEW_SNAPSHOT |
| UPSTREAM_SEQUENCE_GAP | REQUEST_NEW_SNAPSHOT |
| GATEWAY_RESTART | RESUBSCRIBE |
| CONNECTION_GENERATION_CHANGED | RESUBSCRIBE |
| SUBSCRIPTION_RECONFIGURED | RESUBSCRIBE |

### 3.3 Invalid Sequences

The following sequences MUST NOT occur in a valid transcript:

- DepthUpdate before initial Snapshot in an order book stream.
- Snapshot after DepthUpdate without a gap notice in between.
- Connection generation change without explicit status transition.
- Gap without explicit `ConsumerGapNotice` or `StreamStatus`.
- `session_sequence` regression or zero.

## 4. Slow Consumer Protocol

### 4.1 CONTIGUOUS_EVENTS Consumers

- Each consumer has its own bounded queue (implemented by Gateway, not in
  Contracts).
- If queue depth exceeds threshold continuously, the Gateway:
  1. Sends `ConsumerGapNotice(reason=SLOW_CONSUMER, action=RESUBSCRIBE)`.
  2. Closes the stream.
  3. The consumer must re-subscribe.

### 4.2 LATEST_STATE Consumers

- Old states can be overwritten before delivery.
- Only the latest state is guaranteed.
- Overwritten intermediate states are NOT gaps.
- If the source data itself has gaps, the snapshot must carry
  `book_synchronized=false` or appropriate quality flags.

## 5. Session Metadata

| Field | Meaning | Starts At | Note |
|-------|---------|-----------|------|
| `gateway_instance_id` | Opaque Gateway identifier | New on restart | Changes after restart |
| `connection_generation` | Upstream connection cycle | 1 | Incremented on reconnect |
| `session_sequence` | Per-subscription delivery order | 1 | NOT Binance update ID |
| `publish_time_utc_ns` | Gateway wall-clock at publish | N/A | Monotonic within session |

- `connection_generation` does NOT reset on session reconnect; it increments.
- `session_sequence` is per-subscription, per-lifecycle.
- A new `gateway_instance_id` implies previous sequences are invalid.

## 6. Browser Consumers

Browsers do not connect directly to gRPC. A future `ViewBackend` / BFF bridges
gRPC streams to WebSocket / JSON for browser UIs. This is not part of V1.

## 7. Transcript Validation Rules

Test-only rules (not Gateway runtime):

1. `accepted` before first payload.
2. Snapshot before first live DepthUpdate.
3. No `session_sequence` regression.
4. No `connection_generation` regression without status notice.
5. Gap always accompanied by explicit notice.
6. After gap with REQUEST_NEW_SNAPSHOT, no DepthUpdates until new snapshot.
7. Latest State may skip intermediate source revisions but must not claim false
   continuity.
