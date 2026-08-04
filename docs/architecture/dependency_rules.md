# Dependency Rules

## Dependency direction

```
Contracts (leaf)
    ↑
    │
Recorder  Gateway  Health  History  View  Control
```

Contracts is imported by all other modules. Contracts imports nothing from any other module.

## Forbidden imports

Contracts must NEVER import:

| Forbidden | Reason |
|-----------|--------|
| `binance_market_data_recorder.*` | Contracts must not depend on Recorder internals |
| `sqlite3` | No database access |
| `websocket` / `websockets` | No network I/O |
| `aiohttp` / `httpx` / `requests` | No HTTP client |
| `fastapi` / `flask` / `starlette` | No web framework |
| `binance.websocket.*` | No Binance SDK |
| `binance.spot` / `binance.um_futures` | No Binance API access |

## Allowed capabilities

- Pydantic model definitions
- String/enum validation (via `re`, `decimal`)
- JSON Schema generation (to filesystem via CLI only)
- Package metadata and versioning

## Integration patterns

### Recorder Adapter (in Recorder repo)
```
Recorder EventEnvelope → Adapter mapping → DepthUpdate / AggTrade / BookTicker
```

### Gateway Adapter (in Gateway repo)
```
Raw Binance WS Message → Gateway Parser → DepthUpdate → Consumer
```

### History Adapter (in History repo)
```
Normalized Parquet Row → Public Historical Event → Replay Consumer
```
