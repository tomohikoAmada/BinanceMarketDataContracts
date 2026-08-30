# Quality Semantics

## Three-layer model

### QualityFlag — observable data facts

Quality Flags describe **what is observed** about the data. They are facts, not trading-policy
judgments.

Examples:
- `DUPLICATE` — duplicate event detected
- `OUT_OF_ORDER` — event received out of sequence
- `SEQUENCE_GAP` — gap in update ID sequence
- `CROSSED_BOOK` — best bid >= best ask
- `IDENTITY_CONFLICT` — same identity, different content

### HealthState — aggregated MarketData condition

Health States describe the current operational/data-quality condition of a MarketData stream,
component or optional future aggregate:

| State | MarketData meaning |
|-------|--------------------|
| `HEALTHY` | Data/service is operating within its defined usable conditions |
| `DEGRADED` | A non-fatal issue is present; consumers should inspect reasons/quality facts |
| `UNRELIABLE` | MarketData cannot assert that the affected data/state is reliable |
| `UNAVAILABLE` | The affected MarketData surface is not available |

These states do **not** prescribe a trading action. A strategy or `RiskManagement` may use them as
inputs to its own policy, but BinanceMarketData does not own permission to open/close positions,
halt trading or resize exposure.

### ReasonCode — assessment rationale

Reason Codes explain **why** a particular HealthState was emitted:

- `SEQUENCE_GAP_DETECTED` — a gap was found
- `BOOK_CROSSED` — order book crossed state detected
- `RECORDER_STALLED` — Recorder not producing expected data
- `GATEWAY_STALLED` — Gateway not producing expected data
- `DIVERGENCE_DETECTED` — independently observed channels disagree under the applicable comparison rule

ReasonCodes explain MarketData condition; they are not trading commands.

## Separation principle

- **QualityFlag**: event/state-level observable fact.
- **HealthState**: aggregated MarketData operational/data-quality condition.
- **ReasonCode**: explanation for that condition.
- **Risk/strategy policy**: outside BinanceMarketData.

A standalone `BinanceMarketDataHealth` process is not required. At the current scale, Recorder,
Gateway and future History/View surfaces may expose their own status/telemetry. A later health
aggregator is an optional deployment/component decision if concrete multi-instance or operational
needs justify it.

Health/status computation must not block the Gateway hot path.

## BookTicker crossed state

`BookTicker` with `best_bid_price >= best_ask_price` must be representable in the contract.
The crossed state is reported via `QualityFlag.CROSSED_BOOK` and may contribute to a
`HealthState.DEGRADED` or stronger state with `ReasonCode.BOOK_CROSSED` according to the applicable
health policy. The event itself must not be rejected at contract construction solely because it is
crossed.

## Consumer responsibility

Consumers must treat MarketData health fields as factual/operational inputs. If a consumer needs a
normative action such as "stop automated trading", that rule belongs to the consumer's strategy/risk
policy and must not be encoded as the meaning of a MarketData HealthState.