# Quality Semantics

## Three-layer model

### QualityFlag — observable data facts

Quality Flags describe **what is observed** about the data. They are facts, not judgments.

Examples:
- `DUPLICATE` — duplicate event detected
- `OUT_OF_ORDER` — event received out of sequence
- `SEQUENCE_GAP` — gap in update ID sequence
- `CROSSED_BOOK` — best bid >= best ask
- `IDENTITY_CONFLICT` — same identity, different content

### HealthState — overall assessment

Health States describe **whether the data should be used**:

| State | Meaning | Action |
|-------|---------|--------|
| `HEALTHY` | All systems operational, data current and consistent | Use normally |
| `DEGRADED` | Minor issues present, data still usable with caution | Monitor, may restrict automated trading |
| `UNRELIABLE` | Significant issues, data may be incorrect | Stop automated trading, alert ops |
| `UNAVAILABLE` | No data available | Halt all dependent operations |

### ReasonCode — judgment rationale

Reason Codes explain **why** a particular HealthState was chosen:

- `SEQUENCE_GAP_DETECTED` — a gap was found
- `BOOK_CROSSED` — order book crossed state detected
- `RECORDER_STALLED` — Recorder not producing data
- `GATEWAY_STALLED` — Gateway not producing data
- `DIVERGENCE_DETECTED` — Recorder and Gateway disagree

## Separation principle

- **QualityFlag**: Facts — produced in the data path (Gateway, Recorder)
- **HealthState**: Judgment — produced by Health module
- **ReasonCode**: Explanation — produced by Health module

Health must not block the Gateway hot path. It consumes telemetry asynchronously and produces assessments.

## BookTicker crossed state

`BookTicker` with `best_bid_price >= best_ask_price` must be representable in the contract.
The crossed state is reported via `QualityFlag.CROSSED_BOOK` and may trigger
`HealthState.DEGRADED` with `ReasonCode.BOOK_CROSSED`. But the event itself must not be
rejected at contract construction.
