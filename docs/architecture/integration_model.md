# Integration Model

## Producer → Contract → Consumer pattern

Every cross-module data flow follows:

```
Producer Module → Adapter (in producer) → Public Contract → Consumer
```

The Adapter lives in the producer module, not in Contracts.

## Recorder → Contracts

Recorder is responsible for parsing its internal EventEnvelope and producing public contract instances:

```python
# In Recorder repo (not Contracts)
from binance_market_data_contracts import DepthUpdate

def to_public_contract(envelope: EventEnvelope) -> DepthUpdate:
    return DepthUpdate(
        metadata=to_metadata(envelope),
        first_update_id=envelope.first_update_id,
        final_update_id=envelope.final_update_id,
        bids=[...],
        asks=[...],
    )
```

## Gateway → Contracts

Gateway parses raw Binance JSON and produces contract instances:

```python
# In Gateway repo (not Contracts)
from binance_market_data_contracts import DepthUpdate

def parse_depth_message(raw_json: bytes) -> DepthUpdate:
    payload = orjson.loads(raw_json)
    return DepthUpdate(
        metadata=EventMetadata(
            venue=Venue.BINANCE,
            ...
        ),
        ...
    )
```

## History → Contracts

History reads internal storage and produces public contract instances:

```python
# In History repo (not Contracts)
from binance_market_data_contracts import DepthUpdate, HistoricalDatasetDescriptor

def read_dataset(descriptor: HistoricalDatasetDescriptor) -> Iterator[DepthUpdate]:
    ...
```

## Contracts NEVER

- Parses raw Binance JSON
- Opens Raw files or Spools
- Queries SQLite Catalog
- Creates HTTP connections
- Opens WebSocket streams
