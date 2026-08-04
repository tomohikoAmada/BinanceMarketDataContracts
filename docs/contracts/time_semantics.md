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

## Capture points

| Field | Captured at | Description |
|-------|-------------|-------------|
| `exchange_event_time_ms` | Exchange | When the exchange says the event occurred |
| `receive_time_utc_ns` | Local NIC/parser | As close to network receive as possible |
| `receive_monotonic_ns` | Local NIC/parser | Monotonic time paired with receive |
| `generated_time_utc_ns` | Producer | When a derived snapshot was computed |
| `observed_time_utc_ns` | Health/Telemetry | When an observation was recorded |
| `detected_at_utc_ns` | Health | When a condition was detected |
