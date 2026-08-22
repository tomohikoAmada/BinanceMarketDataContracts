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
    previous_generation: int | None = None
    snapshot_seen = False
    gap_index: int | None = None
    for index, item in enumerate(items):
        sequence = item["session_sequence"]
        generation = item.get("connection_generation")
        payload = item["payload"]
        if sequence != previous_sequence + 1:
            raise TranscriptError("session_sequence must start at 1 and increment exactly by 1")
        if generation is not None and generation < 1:
            raise TranscriptError("connection_generation must be absent or >= 1")
        if previous_generation is not None and generation is not None and generation < previous_generation:
            raise TranscriptError("connection_generation must not decrease")

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
        "valid-generation-transition-without-gap.json",
    ],
)
def test_valid_transcript_files(name: str) -> None:
    validate_transcript(_load(name))


@pytest.mark.parametrize(
    "name",
    [
        "invalid-depth-before-snapshot.json",
        "invalid-sequence-gap-without-notice.json",
    ],
)
def test_invalid_transcript_files(name: str) -> None:
    with pytest.raises(TranscriptError):
        validate_transcript(_load(name))


@pytest.mark.parametrize(
    ("delivery_mode", "sequences", "valid"),
    [
        ("CONTIGUOUS_EVENTS", [1, 2, 3], True),
        ("LATEST_STATE", [1, 2, 3], True),
        ("CONTIGUOUS_EVENTS", [1, 2, 4], False),
        ("LATEST_STATE", [1, 2, 4], False),
        ("LATEST_STATE", [2, 3, 4], False),
        ("LATEST_STATE", [1, 1, 2], False),
        ("LATEST_STATE", [1, 3, 2], False),
    ],
)
def test_session_sequence_is_exactly_contiguous_for_every_delivery_mode(
    delivery_mode: str, sequences: list[int], valid: bool
) -> None:
    payload = "DEPTH_UPDATE" if delivery_mode == "CONTIGUOUS_EVENTS" else "MARKET_STATE"
    transcript = {
        "stream_type": "EVENT" if delivery_mode == "CONTIGUOUS_EVENTS" else "MARKET_STATE",
        "delivery_mode": delivery_mode,
        "items": [
            {
                "session_sequence": sequence,
                "connection_generation": 1,
                "payload": "SUBSCRIPTION_ACCEPTED" if index == 0 else payload,
            }
            for index, sequence in enumerate(sequences)
        ],
    }
    if valid:
        validate_transcript(transcript)
    else:
        with pytest.raises(TranscriptError):
            validate_transcript(transcript)


def test_expected_transcript_inventory_is_complete() -> None:
    assert len(list(TRANSCRIPTS.glob("*.json"))) == 7
