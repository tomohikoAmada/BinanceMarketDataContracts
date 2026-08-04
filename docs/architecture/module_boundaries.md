# Module Boundaries

## BinanceMarketDataContracts

### Responsible
- Public data types with strict validation
- Schema versioning
- Units and precision definitions
- Time semantics
- Unique identifiers
- Quality flags
- Compatibility rules
- Error and status codes
- Serialization conventions

### NOT responsible
- Network connections
- Business processes
- Persistence (no filesystem I/O except schema export)
- Data computation
- UI

## Interaction with other modules

Contracts is a **leaf dependency** — all other modules depend on it, but it depends on none of them.

```
Recorder ─────────┐
Gateway ──────────┤
Health ───────────┼──► Contracts
History ──────────┤
View ─────────────┤
Control ──────────┘
```

## Dependency rules

1. No module may bypass Contracts to define its own cross-module types
2. Adapter code translating between module-internal types and public contracts belongs in the producer module, not in Contracts
3. Contracts never imports from Recorder, Gateway, Health, History, View, or Control
4. Contracts never imports Binance SDK, HTTP clients, or database drivers
