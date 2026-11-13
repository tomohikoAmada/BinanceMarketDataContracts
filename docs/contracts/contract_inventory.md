# Contract Inventory

The authoritative inventory is the runtime registry in
`binance_market_data_contracts.versions`; status is also listed in
[ARCHITECTURE.md](../../ARCHITECTURE.md). This page only explains scope.

## Current used subset

C1 fixed the internal runtime subset to the five market/book models
(`DepthUpdate`, `AggTrade`, `BookTicker`, `ExchangeDepthSnapshot`,
`LocalOrderBookSnapshot`), eight RPC-related models, existing
`StreamStatus`/helpers and three implemented RPCs. See
[the consumer capability page](current-capabilities.md).

## Everything else

Other registered Domain/Wire models (MarketState, DataHealth, history,
telemetry, control, remaining Gateway request/response surfaces) remain
PROPOSED or DRAFT. Their presence in a schema or registry is not a runtime
commitment, a producer assignment or permission to expand Projection Core.

Producer/consumer relationships are design inputs, not evidence that a module
currently imports Contracts. Recorder currently keeps independent
Raw/Normalize/Replay types; Gateway and the optional Projection ProtoAdapter are
the current wire consumers.

"Deterministic" alone does not assign a future OHLCV, trade-tape, premium,
funding/OI or microprice product to Projection Core. Such a product needs an
explicit design and an owning contract.
