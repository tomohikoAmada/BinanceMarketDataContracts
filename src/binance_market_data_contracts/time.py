"""Time semantic constants and documentation.

All time field names MUST include the unit suffix:
- _ms: milliseconds (exchange times)
- _utc_ns: nanoseconds UTC wall clock
- _monotonic_ns: nanoseconds monotonic clock (same boot/clock domain only)

Missing times use None, never 0.
"""

from __future__ import annotations

from typing import get_args, get_origin

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
    "archive_date_yyyy_mm_dd",
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


def _unwrap_annotation(ann: object) -> object:
    """Peel Annotated wrapper if present."""
    origin = get_origin(ann)
    if origin is not None and hasattr(origin, "__name__") and origin.__name__ == "Annotated":
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
