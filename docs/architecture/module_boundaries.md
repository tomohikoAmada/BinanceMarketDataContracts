# BinanceMarketData Module Boundaries

This file is a compact boundary reference. The top-level authority is
[`../../BinanceMarketData_Living_Architecture.md`](../../BinanceMarketData_Living_Architecture.md).

## Named top-level components

Current architecture names six logical components:

- `BinanceMarketDataContracts`
- `BinanceMarketDataRecorder`
- `BinanceMarketDataProjection`
- `BinanceMarketDataGateway`
- `BinanceMarketDataHistory`
- `BinanceMarketDataView`

`Health` and `Control` are currently capabilities owned by the relevant components, not mandatory standalone services or repositories.

---

## Contracts

### Responsible

- cross-module public data types and wire contracts;
- schema/version compatibility;
- time, identity, units and presence semantics;
- Gateway RPC definitions;
- language/package surfaces including message and separate gRPC artifacts.

### Not responsible

- Binance network access;
- runtime orchestration;
- order-book sequence classification;
- persistence;
- UI.

Contracts is a leaf dependency at **public integration boundaries**. It is not a requirement that every internal core depend on Contracts. For example, Projection Core remains independent of Protobuf/gRPC while the optional ProtoAdapter consumes Contracts messages.

---

## Recorder

### Responsible

- independent Binance acquisition for durable capture;
- immutable Raw/provenance;
- Catalog/manifests/gap evidence;
- crash recovery;
- archive lifecycle;
- normalize/replay/historical import;
- storage and operational integrity.

### Not responsible

- low-latency live serving;
- Gateway subscription lifecycle;
- consumer-facing shared Projection semantics;
- strategy/trading.

Recorder may keep internal order-book/quality logic needed for capture integrity, but that internal implementation is not the cross-module consumer-facing order-book authority.

---

## Projection

### Responsible

- deterministic fixed-point/order-book semantics;
- Spot/USD-M sequence policies;
- stale/duplicate/bridge/gap classification;
- projection lifecycle/reset/resync semantics;
- optional ProtoAdapter;
- `LocalOrderBookSnapshot` construction.

### Not responsible

- networking;
- threads/scheduling;
- runtime queues;
- persistence;
- gRPC;
- subscriber management;
- strategy features.

Projection is logically independent but deployed as an embedded library in Phase 1.

---

## Gateway

### Responsible

- independent Binance real-time REST/WebSocket acquisition;
- transport parsing, receive timestamps and metadata;
- bootstrap buffering and snapshot acquisition;
- reconnect/resync orchestration and planned rotation;
- bounded runtime queues;
- serialized Projection scheduling;
- subscriptions, slow-consumer isolation and gRPC serving;
- Gateway runtime identities and telemetry facts.

### Not responsible

- a second order book or sequence classifier;
- durable Raw/archive persistence;
- historical query authority;
- strategy features/trading.

Consumers connect to Gateway, not Projection. Gateway may publish canonical events directly and publishes order-book products after driving embedded Projection.

---

## History

### Responsible

- serving/querying Recorder-owned historical datasets;
- coverage/gap/lineage queries;
- historical event/replay APIs;
- point-in-time reconstruction;
- embedding Projection when historical order-book reconstruction is required.

### Not responsible

- a second Raw persistence system;
- a second Catalog authority;
- modifying Recorder history;
- a second sequence/order-book implementation;
- strategy backtesting or feature computation.

History starts as a logical query boundary. Service/repository deployment is deferred until real consumer requirements justify it.

---

## View

### Responsible

- human-facing visualization and BFF/protocol adaptation;
- live reads from Gateway;
- historical reads from History;
- presentation of public component status/read APIs.

### Not responsible

- direct Binance acquisition;
- direct Raw/Catalog access;
- order-book reconstruction;
- market sequence semantics;
- strategy/trading.

---

## Health and Control capabilities

Health/observability starts inside each owner component. MarketData reports facts such as stale/gap/resync/unavailable; `RiskManagement` owns trading-permission decisions.

Control starts as module-local CLI/admin interfaces. A future centralized control plane may orchestrate public commands but must never mutate another component's internal database/files directly.

---

## Boundary invariants

1. Recorder and Gateway use independent Binance connections.
2. Gateway does not depend on Recorder at runtime.
3. Projection is an embedded deterministic library, not a network service.
4. Consumer-facing order-book/sequence/gap semantics have one authority: Projection.
5. History serves Recorder-owned data and does not become Recorder 2.0.
6. View is a consumer only.
7. Strategy-specific features live outside BinanceMarketData Core.
