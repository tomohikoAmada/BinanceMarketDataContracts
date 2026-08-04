# Identity and Ordering

## Event identity

### Raw layer
- Duplicates are allowed and expected
- Identity is not enforced at the raw storage level

### Normalized layer
- Deterministic deduplication based on explicit identity rules
- "Looks the same" is NOT a valid deduplication criterion
- Same identity with different content → `IDENTITY_CONFLICT` quality flag
- Blue/green deployment overlaps must be identifiable

### Identity rules (TBD per stream)

| Stream | Identity fields | Status |
|--------|----------------|--------|
| Diff Depth | (symbol, final_update_id) candidate | TBD |
| AggTrade | (symbol, aggregate_trade_id) candidate | TBD |
| BookTicker | (symbol, update_id) if available, otherwise TBD | TBD |

## Ordering

### Replay ordering modes

| Mode | Description |
|------|------------|
| `receive_time` | Order by local receive time then monotonic time |
| `exchange_time` | Order by exchange event time (may be unavailable) |

### Tie-breaker
When two events have the same ordering key, use monotonic receive time as tie-breaker.

### Missing exchange time policy
| Policy | Behavior |
|--------|----------|
| `skip` | Skip events without exchange time |
| `error` | Fail replay |
| `use_receive_time` | Use local receive time as fallback |

### Gap policy
| Policy | Behavior |
|--------|----------|
| `report` | Emit gap events, continue |
| `skip_gap` | Skip the gap interval |
| `abort` | Stop replay |

## Gap definition

A structured gap records:
- Which market and stream
- Detection time
- Sequence before and after the gap
- Whether resync occurred
- Which data interval is unreliable
- Reason code
- Evidence reference

Gaps are never silently filled, forward-filled, or faked as continuous.
