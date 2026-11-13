# Time Semantics

## Clock types

### Exchange wall clock (`exchange_event_time_ms`, `exchange_trade_time_ms`, `exchange_transaction_time_ms`)

- **Unit**: milliseconds
- **Source**: Assigned by Binance exchange
- **Comparable across**: all consumers of the same event
- **Missing value**: `null` (never `0`)
- **Applicable to**: individual events

### Local wall clock (`receive_time_utc_ns`, `generated_time_utc_ns`, `observed_time_utc_ns`, `detected_at_utc_ns`)

- **Unit**: nanoseconds
- **Source**: Local system UTC clock (e.g., `time.time_ns()` or equivalent)
- **Comparable across**: processes and machines (assuming NTP synchronization)
- **Missing value**: `null` for historical replay data
- **Applicable to**: receive/produce/generate/detect timestamps

### Local monotonic clock (`receive_monotonic_ns`, `generated_monotonic_ns`)

- **Unit**: nanoseconds
- **Source**: Local monotonic clock (e.g., `time.monotonic_ns()`)
- **Comparable within**: same boot/clock domain only
- **Cannot be converted**: to UTC wall clock
- **Purpose**: precise interval/duration measurement without clock drift

### Window timestamps (`window_start_utc_ns`, `window_end_utc_ns`)

- Used in `LatencySummary` to define measurement windows
- Must satisfy: `window_start <= window_end`

### Historical replay time

- Not a field in market event contracts
- Replay clock is a consumer concept, not an event property
- Defined in `ReplayQuery.clock` and `ReplayQuery.ordering_version`

## Rules

1. Field names MUST include unit suffix
2. Exchange times use milliseconds (`_ms`)
3. Local high-precision times use nanoseconds (`_ns`, `_utc_ns`, `_monotonic_ns`)
4. Missing times use `null`, never `0`
5. Negative times are rejected
6. Monotonic time cannot be converted to UTC
7. Historical replay data has no real local receive time
8. Computed times must be distinguished from observed times
9. Every time field documents where/when it was captured

## USD-M depth producer mapping (C0)

For USD-M Diff. Book Depth Streams, `E` is event time and `T` is transaction time.
Producers map `E` to `exchange_event_time_ms` and `T` to
`exchange_transaction_time_ms`; `exchange_trade_time_ms` remains absent.
For the REST Order Book response, `T` is also transaction time; the existing
`ExchangeDepthSnapshot.exchange_transaction_time_ms` field is correct. No new
schema field is needed. Trade streams retain their trade-time mapping.

## USD-M mark-price and liquidation mapping (C2)

MarkPrice payload `E` is `metadata.exchange_event_time_ms`; `T` is the **next
funding time** and maps only to `next_funding_time_ms`. It is not transaction
time. `funding_rate` is signed.

Liquidation/forceOrder payload `E` is `metadata.exchange_event_time_ms`; `T` is
the order trade time and maps to `order_trade_time_ms`. The stream is a
per-order sample, not a complete liquidation list.

REST reference observations carry the response receive time in
`receive_time_utc_ns`; a source-provided observation time maps to
`source_time_ms` when present. `ExchangeDepthSnapshot.exchange_event_time_ms`
is optional and distinct from `exchange_transaction_time_ms`.

An absent optional time remains `None`/absent on protobuf. Present zero remains
present zero, and must not be used as an absence sentinel. Do not substitute `E`,
receive time or trade time for a missing `T`. Raw protocol acceptance (including
whether a missing `T` is malformed) remains the producer's responsibility.
Current C0 time fields are integers in `[0, 18446744073709551615]` to match `uint64`.

Verified against official Binance documentation on 2026-10-12:

- [USD-M public WebSocket streams, Diff. Book Depth Streams](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public#diff-book-depth-streams)
- [USD-M REST market data, Order Book](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#order-book)

Shared producer test inputs and exact cross-repository changes are recorded in
[HISTORY](../HISTORY.md) and the C0 commit history. Contracts round-trips
cannot detect an upstream source-field misassignment without that source oracle.

## Capture points

| Field | Captured at | Description |
|-------|-------------|-------------|
| `exchange_event_time_ms` | Exchange | When the exchange says the event occurred |
| `receive_time_utc_ns` | Local NIC/parser | As close to network receive as possible |
| `receive_monotonic_ns` | Local NIC/parser | Monotonic time paired with receive |
| `generated_time_utc_ns` | Producer | When a derived snapshot was computed |
| `observed_time_utc_ns` | Health/Telemetry | When an observation was recorded |
| `detected_at_utc_ns` | Health | When a condition was detected |

## Current Gateway Status time (C1)

From Gateway v0.3 G1, `MarketRuntimeStatus.last_event_utc_ns` means the current
valid source generation's last Projection-Applied Depth receive UTC, replacing
historical any-stream activity. Trade/ticker do not refresh it; invalid book,
Gap/recovery, missing time/provenance or generation mismatch yield absence.
Present zero is distinct from absence. Clients must handle wall-clock rollback
and future values as unknown age; there is no freshness SLA or quiet-market
resynchronization policy. See [consumer capabilities](current-capabilities.md).
