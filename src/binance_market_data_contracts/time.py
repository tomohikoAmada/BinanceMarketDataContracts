"""Time semantic constants and documentation.

All time field names MUST include the unit suffix:
- _ms: milliseconds (exchange times)
- _utc_ns: nanoseconds UTC wall clock
- _monotonic_ns: nanoseconds monotonic clock (same boot/clock domain only)

Missing times use None, never 0.
"""

from __future__ import annotations

from typing import Annotated, get_args, get_origin

from pydantic import BaseModel

ALLOWED_TIME_FIELD_NAMES: set[str] = {
    "exchange_event_time_ms",
    "exchange_trade_time_ms",
    "exchange_transaction_time_ms",
    "trade_time_ms",
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
    "receive_monotonic_ns",
    "generated_monotonic_ns",
    "last_message_age_ms",
    "data_freshness_ms",
    "next_funding_time_ms",
    "timeout_seconds",
    "sync_latency_ms",
    "min_ms",
    "max_ms",
    "p50_ms",
    "p95_ms",
    "p99_ms",
    "archive_date_utc",
    "receive_latency",
    "publish_latency",
    "consumer_delivery_latency",
    "missing_exchange_time_policy",
    "accepted_time_utc_ns",
    "publish_time_utc_ns",
    "publish_monotonic_ns",
    "detected_time_utc_ns",
    "uptime_seconds",
    "last_event_utc_ns",
    "consumer_delivery_lag_ms",
    "oldest_message_age_ms",
    "minimum_publish_interval_ms",
    "connection_generation",
}


def is_time_like_field(name: str) -> bool:
    return (
        "time" in name.lower()
        or name.endswith("_at")
        or name.endswith("_date")
        or name.endswith("_duration")
        or name.endswith("_age")
        or name.endswith("_latency")
    )


def walk_models(model_type: type[BaseModel]) -> set[type[BaseModel]]:
    """Recursively discover all nested Pydantic model types."""
    seen: set[type[BaseModel]] = {model_type}
    queue: list[type[BaseModel]] = [model_type]

    while queue:
        current = queue.pop(0)
        for field_info in current.model_fields.values():
            ann = _unwrap_annotation(field_info.annotation)
            nested = _extract_model_types(ann)
            for nt in nested:
                if nt not in seen:
                    seen.add(nt)
                    queue.append(nt)
    return seen


def find_invalid_time_fields(model_type: type[BaseModel]) -> tuple[str, ...]:
    """Find time-like field names that are not in the allowed set."""
    invalid: list[str] = []
    for mt in walk_models(model_type):
        for field_name in mt.model_fields:
            if field_name == "timestamp":
                invalid.append(f"{mt.__name__}.timestamp")
                continue
            if is_time_like_field(field_name) and field_name not in ALLOWED_TIME_FIELD_NAMES:
                invalid.append(f"{mt.__name__}.{field_name}")
    return tuple(invalid)


def _unwrap_annotation(ann: object) -> object:
    """Peel Annotated wrapper if present."""
    if get_origin(ann) is Annotated:
        args = get_args(ann)
        if args:
            return args[0]
    return ann


def _extract_model_types(ann: object) -> set[type[BaseModel]]:
    """Extract all Pydantic BaseModel subclasses from a type annotation."""
    models: set[type[BaseModel]] = set()
    origin = get_origin(ann)
    args = get_args(ann)

    if isinstance(ann, type) and issubclass(ann, BaseModel):
        models.add(ann)

    if origin is not None:
        for arg in args:
            inner = _unwrap_annotation(arg)
            models.update(_extract_model_types(inner))

    return models
