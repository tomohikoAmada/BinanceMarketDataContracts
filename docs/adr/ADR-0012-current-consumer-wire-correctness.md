# ADR-0012: Current consumer wire representability and presence (Contracts C0)

## Status

PROPOSED — implementation authorized by the BinanceMarketData v0.3 C0 plan on
2026-10-12. This records the bounded correction; it does not promote Domain/Wire
contracts to ACCEPTED or authorize publication.

## Context

At baseline `8701c330911c0f1c0b38207281dea426c2dee434`, Domain accepted `2**64`
for DepthUpdate IDs, but the explicit protobuf adapter raised `ValueError`.
Positive `depth_limit` similarly had no `int32` upper bound. Other integer
fields on the currently used surface had the same representability mismatch.
`ConsumerGapNotice(symbol="")` on protobuf had presence, but its adapter silently
returned Domain `None`, contrary to ADR-0011's non-empty identity and ADR-0007's
presence rule. Producer code also put USD-M depth `T` in trade-time metadata.

## Decision

- Apply the existing wire upper bounds to the five used market/book models and
  the numeric Gateway lifecycle/status helpers used by the three implemented
  RPCs. Keep existing lower bounds, strict integer validation and optionality.
  The exact list is in [C0 field changes](../C0_IMPLEMENTATION.md).
- Interpret optional Symbol using `HasField("symbol")` only. An absent Symbol
  remains `None`; a present empty value reaches Domain validation and fails.
- USD-M Diff Depth `T` maps to the **existing** transaction-time field. This is
  a producer correction, not a change to the meaning or shape of the contract.
  Do not globally forbid trade metadata based on this one source protocol.
- Document and test binary unknown-field/enum preservation separately from
  strict Domain JSON and adapter support. Unknown QualityFlag values remain
  rejected by adapters; do not silently drop unknown flags.
- Supply synthetic source-time oracles and binary presence examples that the
  independent producers can reuse without importing each other's internals.

## Compatibility and scope

Wire sources, descriptors, field/enum numbers, RPCs and schema versions remain
unchanged. Representable valid messages retain their encoding. Domain-accepted
overflow inputs now fail early; present-empty Symbol stops being silently
normalized. These are explicit admission corrections to PROPOSED/DRAFT contracts,
not a claim of compatibility with every historically accepted Python input.

Untouched model definitions include MarketStateSnapshot, DataHealthSnapshot,
MarketStateSubscriptionRequest, telemetry, history/control and legacy
EnvelopeMetadata. Their exported schemas can reflect corrected shared lifecycle
definitions where already referenced. No unused model is expanded or accepted.

Recorder/Gateway must make their own producer corrections and validate against
the fixtures. Contracts does not modify their repositories or immutable Raw.
C++ message/gRPC artifacts and locks are unchanged; no publication or repeated
dependency qualification is required by this Domain-only correction.

## Sources and validation

Official sources checked on 2026-10-12:

- [USD-M Diff. Book Depth Streams](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public#diff-book-depth-streams): `E` is event time; `T` is transaction time.
- [USD-M Order Book](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#order-book): REST `T` is transaction time.

Descriptor-driven boundaries, Domain/binary round-trips, present-empty Symbol,
unknown-field/enum boundaries and source-time oracles are covered by
`tests/test_c0_*.py`; the ordinary fixture manifest validates representative
boundaries using both Pydantic and JSON Schema. See the C0 evidence record for
commands, outcomes and the remaining producer integration requirements.
