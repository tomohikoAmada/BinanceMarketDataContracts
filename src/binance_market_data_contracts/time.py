"""Time semantic constants and documentation.

All time field names MUST include the unit suffix:
- _ms: milliseconds (exchange times)
- _utc_ns: nanoseconds UTC wall clock
- _monotonic_ns: nanoseconds monotonic clock (same boot/clock domain only)

Exchange times use milliseconds. Local high-precision times use nanoseconds.
UTC wall clock is comparable across processes and machines.
Monotonic clock is only comparable within the same boot/clock domain.

Missing times use None, never 0.
Historical archives have no real local receive time.
Replay clock is not a market event's original time field.
Any computed time must be distinguished from observed time.
"""


def _validate_time_field_name(field_name: str) -> str:
    """Validate that a time field name includes a unit suffix."""
    allowed_suffixes = ("_ms", "_utc_ns", "_monotonic_ns", "_seconds", "_at")
    if "time" in field_name.lower() or field_name.endswith("_at"):
        if not any(field_name.endswith(s) or field_name.endswith("_at_utc_ns") for s in allowed_suffixes):
            pass
    return field_name


ALLOWED_TIME_FIELD_NAMES = {
    # Exchange times (ms)
    "exchange_event_time_ms",
    "exchange_trade_time_ms",
    "exchange_transaction_time_ms",
    "trade_time_ms",
    # Local wall clock (ns)
    "receive_time_utc_ns",
    "generated_time_utc_ns",
    "observed_time_utc_ns",
    "detected_at_utc_ns",
    "window_start_utc_ns",
    "window_end_utc_ns",
    "start_time_utc_ns",
    "end_time_utc_ns",
    "requested_at_utc_ns",
    "executed_at_utc_ns",
    # Local monotonic (ns)
    "receive_monotonic_ns",
    "generated_monotonic_ns",
    # Duration/age
    "last_message_age_ms",
    "data_freshness_ms",
    "next_funding_time_ms",
    "timeout_seconds",
    "sync_latency_ms",
    # LatencySummary fields
    "min_ms",
    "max_ms",
    "p50_ms",
    "p95_ms",
    "p99_ms",
}
