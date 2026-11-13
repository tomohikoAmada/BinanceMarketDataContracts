# Current internal v1 contract

2026-10-18 · Contracts C1. This page fixes the **used internal subset** and its
package identities. It does not promote registry statuses, publish packages or
promise the unused schema surface. Historical validation details:
[HISTORY](../HISTORY.md).

## Consumer capability table

| RPC | Current Gateway support | Request / payload schema versions |
| --- | --- | --- |
| `SubscribeOrderBook` | Binance Spot and USD-M perpetual; one exact configured product; REQUIRED initial snapshot, then Projection-Applied depth updates | `order-book-subscription-request.v1`; `local-order-book-snapshot.v1`, `depth-update.v1` |
| `SubscribeEvents` | CONTIGUOUS_EVENTS, exactly one selector. Spot: DIFF_DEPTH, AGG_TRADE, BOOK_TICKER. USD-M perpetual: DIFF_DEPTH only | `event-subscription-request.v1`; selected `depth-update.v1`, `agg-trade.v1`, or `book-ticker.v1` |
| `GetGatewayStatus` | Unary observation of every configured product; no selector | `gateway-status-request.v1`; `gateway-status-snapshot.v1` |
| `SubscribeMarketState` | **UNIMPLEMENTED** (gRPC default); declarations remain for compatibility | No current supported runtime request/payload |

The Gateway runtime owns its current product-count limit, admission rules and
milestone status; consult the Gateway repository's `CURRENT_STATE.md` rather than
copying those moving values here. Contracts states only the stable boundary:
exact identity is `(venue, market, symbol)` with no case folding; Gateway accepts
a narrower operational identity subset than opaque Unicode `Symbol`, and the
Domain permits multiple selectors while the current Gateway accepts one.
Unsupported or malformed product/stream/request is rejected as
INVALID_ARGUMENT; missing supported v1 payload negotiation is
FAILED_PRECONDITION. Offer the schema versions listed above.

Recorder uses its own Raw/Normalize/Replay types, with no current Contracts
runtime import or new adapter obligation.

## Used models and semantics

| Surface | Current use / fixed v1 meaning |
| --- | --- |
| `DepthUpdate` | Gateway normalizes depth; Projection ProtoAdapter consumes it. U/u/optional pu are source sequence facts; Projection alone decides Spot/USD-M continuity. Event RPC depth is PRE_PROJECTION_NORMALIZED, so it does not prove Applied or book synchronization. |
| `AggTrade`, `BookTicker` | Spot Event RPC only; Projection Core does not compute a trade/ticker product. Decimal strings retain exact precision/trailing zeros; zero quantity deletes a depth level, while aggregate trade quantity is positive. |
| `ExchangeDepthSnapshot` | Gateway REST bootstrap input to Projection, not the client-facing order-book snapshot. |
| `LocalOrderBookSnapshot` | Projection-backed client snapshot at publication cut C, followed only by applicable Applied depth updates. Bids descend, asks ascend. `depth_limit` bounds the initial snapshot per side; subsequent depth payloads are not top-N filtered. |
| `EventSubscriptionRequest`, `OrderBookSubscriptionRequest`, `GatewayStatusRequest` | The three implemented RPC requests; runtime support is the table above, not every value representable in Domain/proto. |
| `SubscriptionAccepted`, `ConsumerGapNotice` | Accepted session identity/schema negotiation; explicit delivery/continuity loss with required recovery action. Slow clients are isolated and terminated; reconnect requires a new subscription/snapshot, with no resume replay promise. |
| `GatewayEventEnvelope`, `OrderBookStreamItem` | Exactly one payload. Canonical field 2 `delivery_metadata` only; legacy field 1 is absent. Accepted precedes data; book snapshot precedes updates. |
| `GatewayStatusSnapshot` | Product lifecycle, counts and optional generation. `markets[].last_event_utc_ns` is the current valid generation's last **Applied Depth receive UTC**, not any-stream activity. |
| `StreamStatus` (existing envelope payload) | Session lifecycle/diagnostic state; not a second recovery policy or a Health service. |
| Existing helpers | `PriceLevel`; DepthUpdate/AggTrade/BookTicker metadata; `GapDescriptor`; `StreamSelector`; `GatewayEnvelopeMetadata`; `MarketRuntimeStatus`; exact IDs, enums, decimal and time types. These support the rows above, not extra products/RPCs. |

The five market/snapshot models and eight RPC-related models above, plus
StreamStatus/helpers, are the C1 scope. Other registered models (including
MarketState, DataHealth, history, telemetry and control) remain non-committed
draft/proposed surface. Existing wire field/enum numbers are preserved.

- `session_sequence` starts at 1 and increments by exactly one for every emitted
  item in one subscription, including controls. It is not U/u/pu or book version.
  `connection_generation` is optional source provenance, positive when present;
  a generation change alone is not a universal gap definition. This Gateway
  ends sessions across full rebootstrap/source replacement; clients must not
  stitch them into one continuous book. Restart changes `gateway_instance_id`.
- USD-M depth E is event-time, T is transaction-time, and trade-time is absent.
  Optional absence and present zero differ; never substitute a clock or field.
  C0 [source oracle](../../fixtures/integration/usdm-depth-time.v1.json) fixes the
  mapping; producer raw-input acceptance remains producer-owned.
- Status depth time is absent for missing Applied/time/provenance, invalid book,
  Gap/recovery/stopped or mismatched generation. Trade/ticker activity does not
  refresh it. UTC can go backwards: compare against observation UTC safely,
  treating future/invalid ages as unknown. This is time evidence, not a freshness
  SLA or a reason to resynchronize a quiet market.
- Current integer fields fit existing uint64/int32 wire ranges; positive fields
  retain their lower bounds. Prices/quantities never pass through float.
  Optional Symbol absent stays absent; present-empty is invalid. See
  [ADR-0012](../adr/ADR-0012-current-consumer-wire-correctness.md) and
  [compatibility boundaries](compatibility_policy.md):
  binary unknown fields/enums may survive binary round-trip; strict Domain/JSON
  and adapters do not promise unknown-field retention or unknown-QualityFlag support.

## Fixed internal dependency combination

| Artifact / source | Exact selected identity |
| --- | --- |
| Contracts Python/JSON C0 semantic baseline (`0.2.0a1`) | Source `db8156f1e16ba7a4a5ee8d5b26316139b7e218f3`; C1 adds documentation, without changing those models/generated schemas |
| Contracts C++ messages (`0.1.0`) | `binance-market-data-contracts-cpp/0.1.0#53713fb82c27cf6ea0395f6b8a853006`; installed provenance source `518880bdfa60948c3b65b6b3525d024526995166` |
| Contracts C++ service/stubs (`0.1.0`) | `binance-market-data-contracts-grpc-cpp/0.1.0#c3661aa735e1eb6450c1a93f635dbc20`; same installed source; requires the exact message RREV above |
| Projection Core + ProtoAdapter (`0.1.0`) | `binance-market-data-projection/0.1.0#d95fa71d6dca8d931e72fbb5b74114a9`; source `555dd1f4d846e19cfd6fbe55676c86504559048e` reproduces that RREV; `proto_adapter=True` |
| C++ Protobuf generator/runtime | `protobuf/6.33.5#ca5ff466767b31a1b496ec60247e105c` (full runtime; libprotoc 33.5) |
| C++ gRPC runtime/plugin | `grpc/1.83.0#67e377a995d4a1279bffe2b941ac2f55` |

These are internal immutable identities, not formal Package Revision assignments
or public releases. C0 does not change C++ export inputs or the descriptor;
therefore the existing message/gRPC/Projection combination stays pinned. The
v1 descriptor fingerprint remains
`33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.
C++20, matching host ABI/build type/linkage and a **single** message artifact
lineage are required. Targets: `BinanceMarketDataContracts::Protobuf`, separate
`BinanceMarketDataContracts::Grpc`, `BinanceMarketDataProjection::Core` and
`BinanceMarketDataProjection::ProtoAdapter`; Core builds independently without
Protobuf/gRPC. Platform-specific package IDs/PREVs were validation evidence and
remain in Git history, not as portable identity constants.

Python base requires Pydantic `>=2.10,<3` and protobuf `>=6.33.5,<7`; optional
wire runtime uses grpcio `>=1.81.1,<2`. These package compatibility ranges are
not exact environment locks. Python gRPC and C++ gRPC versions need not be
identical.

For an upgrade: select an immutable source commit/RREV, retain exact base
message lineage across Projection and gRPC, and use existing Conan locks and
matching binary profiles (`--build=never` when available). Run Domain/binary
round-trips, Projection sequence/replay and Gateway production RPC regressions;
record the new identities/results here. A Domain/docs-only correction with
unchanged C++ export inputs needs no C++ repin. Do not update historical smoke
pins merely to follow newer main. Wire/semantic changes use the existing
compatibility/ADR process; unused DRAFT models require no release ceremony.
