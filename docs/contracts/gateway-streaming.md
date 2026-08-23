# Gateway Streaming Protocol

Documents the Gateway gRPC streaming protocol semantics for Snapshot + Stream
handoff, gap detection, recovery, slow consumer behavior, and delivery modes.

## 1. Delivery Modes

### 1.1 CONTIGUOUS_EVENTS

Used by `SubscribeEvents` for DepthUpdate, AggTrade, BookTicker.

- Every event must be delivered. Silent message dropping is forbidden.
- `session_sequence` is scoped to one accepted subscription. The first emitted
  item is 1 and every subsequently emitted item increments the previous value
  by exactly 1. This applies to every emitted item, including control and
  status items.
- A consumer gap must be explicitly signaled via `ConsumerGapNotice`.
- A slow consumer whose queue overflows receives a `ConsumerGapNotice` and the
  stream is closed. It must not block other consumers.

### 1.2 LATEST_STATE

Used by `SubscribeMarketState` for MarketStateSnapshot.

- Intermediate states may be overwritten; only the latest is delivered.
- Overwritten states are NOT consumer gaps.
- Each snapshot is self-describing (contains `source_book_update_id`,
  `source_trade_id`, `book_synchronized`).
- `session_sequence` only reflects actual emitted delivery order, not Binance
  `U/u/pu`, `connection_generation`, or Projection `last_update_id`.
- Intermediate states may be coalesced before emission; an un-emitted state
  does not consume a session sequence value. Emitted latest-state items still
  use `1, 2, 3, ...` without visible gaps.
- Source book version must be read from snapshot fields, not inferred from
  `session_sequence`.

## 2. Order Book Snapshot + Stream Handoff

### 2.1 Normal Flow

The consumer-facing handoff is a serialized Projection/publication cut, not the
Binance REST bootstrap procedure:

1. Projection has deterministically accepted through update `C`.
2. Gateway captures `LocalOrderBookSnapshot(last_update_id=C)`.
3. Gateway establishes the subscription publication cut inside the same
   serialized Projection/publication ordering domain.
4. Gateway emits the snapshot.
5. Only subsequently applicable accepted `DepthUpdate`s appear after it.

The Gateway may emit `SubscriptionAccepted` and lifecycle status items as part
of the subscription stream. Every actually emitted item receives the next exact
`session_sequence` value; a coalesced or otherwise un-emitted item consumes no
visible sequence value.

**Consumer view**:

```
SubscriptionAccepted(seq=1)
Snapshot(last_update_id=C, seq=2)
subsequently applicable DepthUpdate(seq=3)
DepthUpdate(seq=4)
...
LIVE status
```

No invisible window exists after the publication cut: subsequent applicable
accepted DepthUpdates are ordered after the emitted Snapshot.

### 2.2 Gap / Failure Flow

If snapshot fails, bootstrap buffer overflows, the publication cut cannot be established,
upstream sequence gap is detected, Gateway restarts, or resume data is evicted:

1. Gateway sends `ConsumerGapNotice` or `StreamStatus(DEGRADED)` with
   `recovery_action = REQUEST_NEW_SNAPSHOT | RESUBSCRIBE`.
2. Subscription is closed or marked for resync.
3. No further DepthUpdates are sent until a new snapshot is established.
4. Gateway MUST NOT continue delivering DepthUpdates and claim the book is
   reliable after a known gap.

## 3. Gap and Recovery Protocol

### 3.1 Gap Detection

A continuity gap is detected when the Gateway has evidence of required source or
consumer-delivery loss, or when it explicitly sends `ConsumerGapNotice`.
`connection_generation` is a provenance/runtime lifecycle fact: a transition
may accompany a gap, but a generation change alone is not a data gap.
Gateway restart (new `gateway_instance_id`) is a separate lifecycle boundary.

### 3.2 Gap Types and Recovery

| Reason | Recovery Action |
|--------|----------------|
| SLOW_CONSUMER | RESUBSCRIBE |
| RESUME_NOT_AVAILABLE | REQUEST_NEW_SNAPSHOT |
| UPSTREAM_SEQUENCE_GAP | REQUEST_NEW_SNAPSHOT |
| GATEWAY_RESTART | RESUBSCRIBE |
| CONNECTION_GENERATION_CHANGED | RESUBSCRIBE when the transition is associated with an actual required continuity loss or recovery condition |
| SUBSCRIPTION_RECONFIGURED | RESUBSCRIBE |

### 3.3 Invalid Sequences

The following sequences MUST NOT occur in a valid transcript:

- DepthUpdate before initial Snapshot in an order book stream.
- Snapshot after DepthUpdate without a gap notice in between.
- `connection_generation` regression between present values.
- Gap without explicit `ConsumerGapNotice` or `StreamStatus`.
- `session_sequence` zero, regression, or any non-contiguous emitted value.

A generation transition alone is permitted and does not require a gap notice.

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
| `connection_generation` | Upstream connection cycle when uniquely applicable | 1 when present | Incremented on reconnect |
| `session_sequence` | Per accepted-subscription emitted-item order | 1 | Every emitted item increments exactly +1; not Binance `U/u/pu` |
| `publish_time_utc_ns` | Gateway wall-clock at publish | N/A | Monotonic within session |

- For a uniquely applicable upstream source, `connection_generation` does not
  reset on source reconnect; it increments. It is absent when no unique source
  generation applies.
- `MarketRuntimeStatus` is a per-market aggregate. Its `connection_generation`
  is therefore optional and must be omitted when multiple upstream sources are
  represented without one uniquely applicable generation.
- `session_sequence` is per accepted subscription and covers every emitted item,
  regardless of delivery mode. It is not reset or skipped for an emitted control,
  status, snapshot, or state item.
- A new `gateway_instance_id` implies previous sequences are invalid.

## 6. Metadata Authority

Each Gateway stream item retains field 1, `envelope_metadata`, as a legacy DRAFT
common-schema representation. Canonical Gateway writers leave field 1 absent and
populate field 2, `delivery_metadata`, with `GatewayEnvelopeMetadata`. Readers
reject legacy-only, dual, or missing metadata; they do not merge or prioritize
the two fields.

## 7. Browser Consumers

Browsers do not connect directly to gRPC. A future `ViewBackend` / BFF bridges
gRPC streams to WebSocket / JSON for browser UIs. This is not part of V1.

## 8. Transcript Validation Rules

Test-only rules (not Gateway runtime):

1. `accepted` before first payload.
2. Snapshot before first live DepthUpdate.
3. The first emitted item has `session_sequence=1`; each subsequent emitted item
   has the previous value plus exactly 1.
4. `connection_generation` may be absent; present values are >= 1 and must not
   decrease when compared with another present value.
5. Gap always accompanied by explicit notice.
6. After gap with REQUEST_NEW_SNAPSHOT, no DepthUpdates until new snapshot.
7. Latest State may skip intermediate source revisions but must not claim false
   continuity.
