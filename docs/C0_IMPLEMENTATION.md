# Contracts C0 — field changes, fixtures and producer migration

2026-10-12 · BinanceMarketData v0.3 BMD-1 / Contracts C0.
Contracts baseline: `8701c330911c0f1c0b38207281dea426c2dee434`.
Decision: [ADR-0012](adr/ADR-0012-current-consumer-wire-correctness.md).

All six documents in the sibling `Milestone Plan` directory were read. This
delivery implements C0 within Contracts; cross-repository producer integration
remains with Gateway/Recorder. No other repository was edited. No new RPC,
unused model, runtime adapter for Recorder, acceptance promotion or publication.

## Exact field changes

`U64 = 18446744073709551615` (`2**64-1`), `I32 = 2147483647` (`2**31-1`).
All listed fields gain an inclusive upper bound; existing lower bounds and
`None`/optional behavior remain. This is a representability limit, not a claim
that a producer operationally supports every value up to the limit.

| Domain type | Fields | Range when present |
|-------------|--------|--------------------|
| DepthUpdateMetadata, AggTradeMetadata, BookTickerMetadata (shared base) | `exchange_event_time_ms`, `exchange_trade_time_ms`, `exchange_transaction_time_ms`, `receive_time_utc_ns`, `receive_monotonic_ns` | `0..U64` |
| DepthUpdate | `first_update_id`, `final_update_id`, `previous_final_update_id` | `0..U64`; existing final ≥ first rule |
| AggTrade | `aggregate_trade_id`, `first_trade_id`, `last_trade_id`, `trade_time_ms` | `0..U64`; existing last ≥ first rule |
| BookTicker | `update_id` | `0..U64` |
| ExchangeDepthSnapshot | `last_update_id`, `exchange_transaction_time_ms`, `receive_time_utc_ns`, `receive_monotonic_ns` | `0..U64` |
| GapDescriptor | `detected_at_utc_ns`, `previous_sequence`, `next_sequence` | `0..U64` |
| LocalOrderBookSnapshot | `last_update_id`, `generated_time_utc_ns`, `generated_monotonic_ns` | `0..U64` |
| LocalOrderBookSnapshot, OrderBookSubscriptionRequest | `depth_limit` | `1..I32` |
| SubscriptionAccepted | `accepted_time_utc_ns` | `0..U64` |
| ConsumerGapNotice | `detected_time_utc_ns` | `0..U64` |
| ConsumerGapNotice | `last_delivered_session_sequence`, `next_available_session_sequence` | `1..U64`; existing next > last rule |
| StreamStatus | `observed_time_utc_ns` | `0..U64` |
| GatewayEnvelopeMetadata | `connection_generation`, `session_sequence` | `1..U64` |
| GatewayEnvelopeMetadata | `publish_time_utc_ns`, `publish_monotonic_ns` | `0..U64` |
| MarketRuntimeStatus | `last_event_utc_ns`, `active_subscription_count` | `0..U64` |
| MarketRuntimeStatus | `connection_generation` | `1..U64` |
| GatewayStatusSnapshot | `observed_time_utc_ns`, `uptime_seconds`, `total_active_subscriptions` | `0..U64` |

`GatewayEventEnvelope` and `OrderBookStreamItem` inherit these corrected bounds
through their existing payload/metadata types. EventSubscriptionRequest and
GatewayStatusRequest contain no numeric fields to change. Unused model
definitions are untouched. Schema export also updates already shared nested
types inside unused envelopes; this does not expand their capabilities.

`ConsumerGapNotice.symbol` adapter change:

| Wire input | Domain result |
|------------|---------------|
| `has_symbol() == false` | `None`; re-encoding leaves it absent |
| Present `"BTCUSDT"` or valid Unicode | Exact value preserved, including presence |
| Present `""` | `ValidationError` at `symbol` (`string_too_short`), including inside current stream envelopes |

Optional numeric zero remains present where its existing lower bound is zero.
Zero generation/session sequence/depth limit remains invalid. No sentinel,
clamping, truncation, float conversion, field number/type or enum changes.

The registry still contains 23 Domain contracts and 19 wire mappings with the
same schema versions and PROPOSED/DRAFT statuses. `.proto` and generated Python
files are unchanged. Formal M4 descriptor fingerprint remains
`33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.

## Minimal reusable producer fixtures

- [USD-M source-time oracle](../fixtures/integration/usdm-depth-time.v1.json):
  synthetic raw depth JSON including current `st=1` and `ps`, distinct `E/T`,
  `U/u/pu`, decimal trailing zeros and a deletion quantity. Apply each
  `source_patch`, then remove `remove_source_fields`. Compare the three named
  metadata fields with `expected_metadata`; `null` means absent on protobuf.
  Cases include present `T`, present `T=0`, and absent `T`; negative source
  patches cover negative/string/bool/null/overflow. The `invalid_metadata`
  examples are structurally valid but semantically wrong producer outputs.
- [Consumer gap binary presence](../fixtures/integration/consumer-gap-presence.v1.json):
  decode `protobuf_hex` as `ConsumerGapNotice` and inspect presence before
  adapting. Covers absence, ASCII, Unicode and present-empty. This avoids
  ProtoJSON erasing the distinction being tested.
- Representative U64/I32 valid and overflow fixtures plus empty Symbol and
  negative transaction time are indexed in [the manifest](../fixtures/manifest.json).
  All current numeric fields are additionally checked against real descriptors.

These files are test specifications, not new public contracts. Read integer JSON
tokens exactly (Python int / C++ uint64-capable parser); do not pass extrema
through binary floating-point. No dependency on Contracts is needed merely to
read the fixture JSON in Recorder tests.

The absent-`T` case specifies optional output semantics, not universal acceptance
of incomplete exchange frames. Gateway currently accepts absent `T`; Recorder's
parser currently marks it malformed and clears extracted metadata. Preserve
each explicit raw-input policy: neither may fabricate a transaction/trade time.
Explicit source `T:null` is an invalid source value; Domain `None` represents
absence. Contracts does not parse Binance JSON, so rejecting malformed raw
inputs must be tested in each producer repository.

## Producer changes and cross-repository acceptance

Read-only locations were checked in Gateway HEAD `fb4c8606a6023795d2f14dbe64426d5e863c2ca0`,
Recorder HEAD `150fb52cb8400de7ddd4629d064d1017dfce959c` and Projection HEAD
`555dd1f4d846e19cfd6fbe55676c86504559048e`; Gateway/Recorder have pre-existing
local changes. These are checkout identities, not deployed artifact identities.

| Owner / actual call site | Required change |
|--------------------------|-----------------|
| Gateway `src/g11/usdm_protocol.cpp`, `populate_depth_metadata()` | Replace `set_exchange_trade_time_ms(*transaction_time_ms)` with `set_exchange_transaction_time_ms(*transaction_time_ms)`. Keep `E` → event time; leave trade-time absent. Preserve optional `T` presence, including zero. |
| Recorder `src/binance_market_data_recorder/binance/usdm/schema.py`, `envelope_from_websocket_frame()` | Branch by stream: DIFF_DEPTH `T` → `EventEnvelope.exchange_transaction_time`, trade-time `None`. AGG_TRADE retains `T` → `exchange_trade_time`. Official USD-M BOOK_TICKER also defines `T` as transaction time and shares this call site: correct its transaction slot as part of that producer fix, without adding a new stream. |
| Gateway USD-M REST parser in the same file | Existing `snapshot.set_exchange_transaction_time_ms(*transaction_time)` is correct; retain it and add a regression, without a schema rewrite. |
| Recorder Normalize `normalize/pipeline.py`, `_candidate()` | Both its normalized row and logical-content hash copy stored Raw envelope time slots. Correcting only new capture does not repair old derived output. Use versioned re-derivation from original payload `T` where available; record source/build/normalization version and new derived hashes/manifests. Preserve old derived-version meaning and immutable Raw. |
| Recorder Replay `replay/clock.py` | Diff-depth/book-ticker exchange clock prefers transaction time, then event time. Verify the corrected derivation and clock selection together; do not silently reinterpret old normalized versions. |
| Projection ProtoAdapter | No source-field remapping or Core change required. It must consume the producer's corrected contract and retain typed validation; run existing USD-M replay/sequence tests when integrated by Gateway. |

The official [USD-M public stream definition](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public#diff-book-depth-streams)
defines depth `E` as event time and `T` as transaction time; its bookTicker
section also calls `T` transaction time. The
[REST Order Book definition](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#order-book)
confirms snapshot `T`. Checked on 2026-10-12. Trade stream `T` semantics must not
be changed by a blind global replacement.

Producer tests must run their **actual parser/envelope path** with the shared
source oracle, assert transaction-time presence/value and trade-time absence,
and reject both wrong-slot and `E`-substitution examples. Check malformed raw
patches under each producer's existing rejection/capture policy. Preserve
`U/u/pu`, precision, deletion quantities and route identity. Gateway then proves
JSON → Projection → gRPC metadata through its real production path; Contracts
tests alone do not close that integration gate. Recorder additionally proves
Raw → versioned Normalize → Replay time selection for old and new captures.

Existing C++ message/service definitions and Conan export inputs are unchanged;
the current C++ message/gRPC/Projection pins can be retained for this correction.
Any Python/JSON consumer adopts the validated C0 source revision and regenerated
schemas when committed. C1 owns the final internal dependency/capability table.
Do not claim a new package revision or require public publication. A Recorder
production code change needs a new wheel/build identity and a new formal test
window; previous Q7/Q8 durations cannot be transferred.

## Validation evidence

Local validation used Python 3.12.9, Pydantic 2.14.1, protobuf 6.33.5,
grpcio/grpcio-tools 1.81.1 and pytest 9.1.1. The isolated development environment
was `/tmp/bmd-contracts-c0-venv`; it is not a repository/deployment dependency.

| Check | Result |
|-------|--------|
| `ruff check .` / `ruff format --check .` | PASS; 92 Python files formatted |
| `mypy src/binance_market_data_contracts` | PASS; 17 source files |
| `BMD_DESCRIPTOR_SET=/tmp/bmd-c0-descriptor.pb pytest -q -ra` | **673 passed, 2 skipped** in 6.64s |
| C0-only `tests/test_c0_*.py` | 127 cases included in the full run; descriptor tests cover 50 integer field occurrences across 16 concrete types (40 distinct field definitions, because the metadata base is shared) |
| `python -m binance_market_data_contracts.schema_export --output schemas/json` | 24 files exported; 13 schemas gain the relevant shared/numeric maxima; catalog unchanged |
| Second export to a temporary directory, `diff -ru schemas/json <export>` | PASS; byte-identical |
| `python -m binance_market_data_contracts.proto_codegen --check` | PASS; all 8 generated proto modules match |
| `buf format --diff --exit-code`, `buf lint`, `buf build --as-file-descriptor-set -o /tmp/bmd-c0-descriptor.pb` | PASS |
| `buf breaking --against '.git#ref=main'` | PASS against baseline main |
| `python -m tools.schema_fingerprint --descriptor-set /tmp/bmd-c0-descriptor.pb` | PASS; same M4 fingerprint shown above |
| `git diff --exit-code -- src/binance_market_data src/binance_market_data_contracts/proto schemas/json/contract-catalog.json conan.lock grpc/conan.lock` | PASS; wire/generated/registry-catalog/locks unchanged |
| `python -m build --outdir /tmp/bmd-contracts-c0-dist`; `python -m twine check /tmp/bmd-contracts-c0-dist/*` | PASS for local wheel and sdist; no upload/release |

The two skipped checks are the C++ build-provided locked-protoc independent-tree
and production generator-identity tests. The current descriptor was built and
its fingerprint verified; no C++/Conan export input changed, so the historical
full C++ dependency/package qualification was not repeated. Producer migrations,
Gateway production-path regression and Recorder historical re-derivation are
not executed here and must not be claimed as passed.

Live baseline CI was successful at exact HEAD `8701c330...`:
[run 33970928350](https://github.com/tomohikoAmada/BinanceMarketDataContracts/actions/runs/33970928350).
That is baseline evidence, not CI for this local candidate.

The new tests cover representability at both extrema, strict types, optional
zero/absence, all current integer descriptors, valid-fixture binary round-trips,
source-time positive/negative oracles, nested empty Symbol rejection, binary
unknown-field retention and strict unknown-QualityFlag rejection. The latter
does not promise that Domain adaptation preserves unknown binary fields.
