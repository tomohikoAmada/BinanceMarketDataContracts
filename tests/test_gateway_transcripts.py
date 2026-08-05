"""File-backed gateway transcript protocol validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

TRANSCRIPTS = Path(__file__).resolve().parents[1] / "fixtures" / "gateway" / "transcripts"


class TranscriptError(ValueError):
    """A transcript violates the gateway streaming protocol."""


def _load(name: str) -> dict[str, Any]:
    return json.loads((TRANSCRIPTS / name).read_text(encoding="utf-8"))


def validate_transcript(transcript: dict[str, Any]) -> None:
    items: list[dict[str, Any]] = transcript["items"]
    if not items or items[0]["payload"] != "SUBSCRIPTION_ACCEPTED":
        raise TranscriptError("first payload must be SubscriptionAccepted")

    previous_sequence = 0
    previous_generation = 0
    snapshot_seen = False
    gap_index: int | None = None
    for index, item in enumerate(items):
        sequence = item["session_sequence"]
        generation = item["connection_generation"]
        payload = item["payload"]
        if sequence <= previous_sequence:
            raise TranscriptError("session_sequence must be strictly increasing")
        if (
            transcript["delivery_mode"] == "CONTIGUOUS_EVENTS"
            and previous_sequence
            and sequence != previous_sequence + 1
        ):
            raise TranscriptError("event stream has a silent session_sequence gap")
        if generation < previous_generation:
            raise TranscriptError("connection_generation must not decrease")
        if (
            previous_generation
            and generation != previous_generation
            and payload not in {"STREAM_STATUS", "CONSUMER_GAP"}
        ):
            raise TranscriptError("generation change requires explicit status or gap")

        if transcript["stream_type"] == "ORDER_BOOK":
            if payload == "DEPTH_UPDATE" and not snapshot_seen:
                raise TranscriptError("DepthUpdate cannot precede Snapshot")
            if payload == "SNAPSHOT":
                snapshot_seen = True
            if payload == "CONSUMER_GAP":
                gap_index = index
                snapshot_seen = False
        previous_sequence = sequence
        previous_generation = generation

    if transcript["stream_type"] == "ORDER_BOOK":
        data_payloads = [item["payload"] for item in items if item["payload"] in {"SNAPSHOT", "DEPTH_UPDATE"}]
        if not data_payloads or data_payloads[0] != "SNAPSHOT":
            raise TranscriptError("first order book data payload must be Snapshot")

    if gap_index is not None:
        gap = items[gap_index]
        recovery = [item for item in items[gap_index + 1 :]]
        if gap.get("recovery_action") == "REQUEST_NEW_SNAPSHOT":
            payload_state = [(item["payload"], item.get("state")) for item in recovery]
            required = [
                ("STREAM_STATUS", "RESYNC_IN_PROGRESS"),
                ("SNAPSHOT", None),
                ("STREAM_STATUS", "LIVE"),
            ]
            positions = [payload_state.index(value) for value in required if value in payload_state]
            if len(positions) != len(required) or positions != sorted(positions):
                raise TranscriptError("gap recovery requires RESYNC_IN_PROGRESS, new Snapshot, then LIVE")


@pytest.mark.parametrize(
    "name",
    [
        "valid-order-book-handoff.json",
        "valid-order-book-resync.json",
        "valid-latest-state-skips-intermediate.json",
        "valid-event-stream-contiguous.json",
    ],
)
def test_valid_transcript_files(name: str) -> None:
    validate_transcript(_load(name))


@pytest.mark.parametrize(
    "name",
    [
        "invalid-depth-before-snapshot.json",
        "invalid-sequence-gap-without-notice.json",
        "invalid-generation-change-without-status.json",
    ],
)
def test_invalid_transcript_files(name: str) -> None:
    with pytest.raises(TranscriptError):
        validate_transcript(_load(name))


def test_expected_transcript_inventory_is_complete() -> None:
    assert len(list(TRANSCRIPTS.glob("*.json"))) == 7
