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

# Time suffixes used in field names
TIME_SUFFIX_MS = "_ms"
TIME_SUFFIX_UTC_NS = "_utc_ns"
TIME_SUFFIX_MONOTONIC_NS = "_monotonic_ns"

# Time unit documentation
TIME_FIELD_DOCS: dict[str, str] = {
    "exchange_event_time_ms": (
        "Exchange-assigned event time in milliseconds. "
        "Typically represents when the event occurred according to the exchange. "
        "May be None if the exchange does not provide this time."
    ),
    "exchange_trade_time_ms": (
        "Exchange-assigned trade time in milliseconds. "
        "Typically represents when a trade was executed according to the exchange. "
        "May be None for non-trade events or if not provided."
    ),
    "exchange_transaction_time_ms": (
        "Exchange-assigned transaction time in milliseconds. "
        "Typically represents when the transaction was processed. "
        "May be None if not provided."
    ),
    "receive_time_utc_ns": (
        "UTC wall clock time in nanoseconds when the event was received locally. "
        "Captured as close to network receive as possible. "
        "May be None for historical replay data."
    ),
    "receive_monotonic_ns": (
        "Monotonic clock time in nanoseconds when the event was received locally. "
        "Only comparable within the same boot/clock domain. Cannot be converted to UTC. "
        "May be None for historical replay data."
    ),
    "generated_time_utc_ns": ("UTC wall clock time in nanoseconds when this derived snapshot was generated."),
    "generated_monotonic_ns": ("Monotonic clock time in nanoseconds when this derived snapshot was generated."),
    "observed_time_utc_ns": ("UTC wall clock time in nanoseconds when an observation was recorded."),
    "detected_at_utc_ns": ("UTC wall clock time in nanoseconds when a condition was detected."),
    "window_start_utc_ns": ("UTC wall clock time in nanoseconds marking the start of a measurement window."),
    "window_end_utc_ns": ("UTC wall clock time in nanoseconds marking the end of a measurement window."),
    "trade_time_ms": ("Trade execution time in milliseconds as reported by the exchange."),
    "last_message_age_ms": ("Age in milliseconds since the last received message from this connection."),
    "requested_at": ("ISO-8601 UTC timestamp when a command was requested."),
    "executed_at": ("ISO-8601 UTC timestamp when a command was executed."),
}
