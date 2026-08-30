# BinanceMarketData Dependency Rules

Top-level authority: [`../../BinanceMarketData_Living_Architecture.md`](../../BinanceMarketData_Living_Architecture.md).

## Logical dependency direction

```text
Binance Public APIs
   |                    |
   v                    v
Recorder              Gateway
                        |
                        v
                   Projection

Recorder-owned datasets
   |
   v
History --------------> Projection   (only when historical reconstruction needs it)

Gateway ---------------------------> live consumers / View
History ---------------------------> historical consumers / View

Contracts defines public cross-module data/wire boundaries.
```

## Hard runtime rules

1. `Gateway -> Recorder` runtime dependency is forbidden.
2. `Recorder -> Gateway` runtime dependency is forbidden.
3. `Projection -> Gateway` dependency is forbidden.
4. `Projection Core -> network/storage/gRPC` dependency is forbidden.
5. `History` must not require direct mutation access to Recorder internals.
6. `View` must not read Raw/Catalog internals directly.
7. `FeatureEngineering`, `Strategy`, `Risk`, `Execution`, and `Portfolio` must not become dependencies of MarketData Core.

## Contracts rule

Contracts owns cross-module public schema and wire compatibility, but it is not a universal internal framework.

Allowed pattern:

```text
Projection Core
    (standard C++ only / no Protobuf requirement)

Projection ProtoAdapter
    -> Contracts message package

Gateway
    -> Contracts message package
    -> Projection ProtoAdapter/Core
    -> Contracts gRPC package when gRPC surface is enabled
```

Forbidden pattern:

```text
Contracts -> Recorder/Gateway/Projection/History/View runtime internals
```

Contracts must not acquire network/database/business-process responsibilities.

## Realtime integration patterns

### Canonical event path

```text
Binance frame
 -> Gateway transport/parser
 -> Contracts-compatible canonical event
 -> Gateway SubscribeEvents
 -> consumer
```

Projection is not required merely to relay `DepthUpdate`, `AggTrade`, or `BookTicker` events.

### Order-book path

```text
Binance Depth + REST Snapshot
 -> Gateway bootstrap/orchestration
 -> Projection
 -> LocalOrderBookSnapshot / accepted ordered updates
 -> Gateway SubscribeOrderBook
 -> consumer
```

Consumers use Gateway APIs. Projection is not directly exposed as a network service.

## Historical integration pattern

```text
Recorder Raw
 -> Recorder Normalize/Replay/Dataset
 -> History
 -> historical consumer
```

When a point-in-time order book is required:

```text
Recorder-owned dataset
 -> History replay
 -> Projection
 -> historical LocalOrderBookSnapshot
```

History must not implement a second sequence/order-book authority.

## Health and Control

Current architecture does not require standalone `Health` or `Control` services.

- each component exposes its own status/metrics;
- module-local CLI/admin interfaces own control actions;
- a later aggregator/control plane may consume public APIs only when real scale requires it.

## Anti-overengineering rule

Do not introduce a generic event bus, plugin framework, DI framework, Kafka, Kubernetes, shared Recorder/Gateway runtime framework, or lock-free infrastructure without a concrete measured requirement and explicit architecture review.
