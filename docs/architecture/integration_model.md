# Integration Model

## Cross-module conversion rule

Cross-module data flows use public Contracts at the boundary, but an adapter is **not** required to
live on the producer side in every case.

The rule is:

> The module that owns the conversion semantics owns the adapter.

Contracts owns the public schema/wire meaning. It does not own runtime adapters.

Typical producer-side flow:

```text
Producer Module -> producer-owned adapter/parser -> Public Contract -> Consumer
```

Accepted consumer-side example:

```text
Contracts message -> Projection ProtoAdapter -> Projection Core input
```

`Projection::ProtoAdapter` belongs to Projection because Projection owns the conversion from the
public wire/message representation into Projection's internal semantic input. Moving that conversion
into Gateway or History would leak Projection-specific semantics into the host.

## Recorder -> Contracts

Recorder is responsible for translating its internal durable/capture representation into public
market-event contracts when it exposes such a boundary:

```text
Recorder EventEnvelope -> Recorder adapter -> DepthUpdate / AggTrade / BookTicker
```

The adapter belongs to Recorder because Recorder owns the internal capture representation being
translated.

## Gateway -> Contracts

Gateway parses Binance transport payloads and produces canonical public market-event messages:

```text
Raw Binance WS/REST payload -> Gateway parser/adapter -> Contracts market event
```

Gateway owns transport parsing, receive provenance, connection identity and orchestration. It does
not own Projection's order-book/sequence classification semantics.

For projected order-book flow:

```text
Contracts DepthUpdate / ExchangeDepthSnapshot
    -> Projection ProtoAdapter
    -> Projection Core
    -> Projection result / LocalOrderBookSnapshot
    -> Gateway publication
    -> consumer
```

Consumers connect to Gateway; they do not connect directly to Projection as a network service.

## History -> Contracts / Projection

History will read Recorder-owned datasets and expose public historical contracts:

```text
Recorder-owned normalized/replay data -> History adapter -> public historical/event contract
```

When History needs a historical order book, it may reuse the Projection-owned conversion and
semantic engine instead of implementing another classifier:

```text
Historical Contracts messages -> Projection ProtoAdapter/Core -> historical order book
```

## Contracts NEVER

Contracts never:

- parses raw Binance JSON;
- opens Recorder Raw/spool files;
- queries Recorder Catalog storage;
- creates HTTP/WebSocket connections;
- implements Projection sequence/order-book algorithms;
- schedules Gateway runtime work;
- chooses trading/risk actions.

## Design consequence

Do not apply a blanket rule such as "all adapters live in the producer". Adapter placement follows
semantic ownership while Contracts remains the stable cross-module language.