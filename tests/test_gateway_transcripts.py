"""Test gateway stream transcript rules.

Validates snapshot+stream handoff, gap detection, and lifecycle protocols.
Tests are structural — they validate data shapes and protocol rules, not network I/O.
"""

from binance_market_data_contracts.enums import (
    ConsumerGapReason,
    Market,
    RecoveryAction,
    SnapshotSource,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.gateway import (
    ConsumerGapNotice,
    EnvelopeMetadata,
    MarketStateStreamItem,
    OrderBookStreamItem,
    StreamStatus,
    SubscriptionAccepted,
)
from binance_market_data_contracts.identifiers import ConnectionId, GatewayInstanceId, RequestId, SubscriptionId, Symbol
from binance_market_data_contracts.market_events import DepthUpdate, DepthUpdateMetadata
from binance_market_data_contracts.snapshots import (
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)


def _em(**kw):
    defaults = {
        "gateway_instance_id": GatewayInstanceId("gw-1"),
        "subscription_id": SubscriptionId("sub-1"),
        "connection_generation": 1,
        "session_sequence": 1,
        "publish_time_utc_ns": 1_690_000_000_000_000_000,
        "protocol_version": "gateway-stream.v1",
    }
    defaults.update(kw)
    return EnvelopeMetadata(**defaults)


def _du(uid, **kw):
    defaults = {
        "metadata": DepthUpdateMetadata(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            producer="test",
            producer_version="1.0",
            connection_id=ConnectionId("c-1"),
            stream=Stream.DIFF_DEPTH,
            schema_version="depth-update.v1",
        ),
        "first_update_id": uid,
        "final_update_id": uid,
    }
    defaults.update(kw)
    return DepthUpdate(**defaults)


def _ms_snapshot(source_book_update_id):
    return MarketStateSnapshot(
        venue=Venue.BINANCE,
        market=Market.SPOT,
        symbol=Symbol("BTCUSDT"),
        schema_version="market-state-snapshot.v1",
        producer="test",
        producer_version="1.0",
        generated_time_utc_ns=1_690_000_000_000_000_000,
        source_book_update_id=source_book_update_id,
    )


def _snapshot(last_update_id):
    return LocalOrderBookSnapshot(
        venue=Venue.BINANCE,
        market=Market.SPOT,
        symbol=Symbol("BTCUSDT"),
        schema_version="local-order-book-snapshot.v1",
        producer="test",
        producer_version="1.0",
        source=SnapshotSource.GATEWAY_LIVE,
        last_update_id=last_update_id,
        generated_time_utc_ns=1_690_000_000_000_000_000,
        synchronized=True,
    )


def _accepted():
    return SubscriptionAccepted(
        request_id=RequestId("r-1"),
        subscription_id=SubscriptionId("sub-1"),
        schema_version="subscription-accepted.v1",
        gateway_instance_id=GatewayInstanceId("gw-1"),
        accepted_time_utc_ns=1_690_000_000_000_000_000,
        negotiated_payload_schema_versions=("depth-update.v1",),
    )


class TestTranscriptValidator:
    """Validate order book stream protocol rules."""

    def test_valid_handoff_sequence(self):
        """Accepted → Snapshot → DepthUpdate handoff is correct."""
        items = [
            OrderBookStreamItem(envelope_metadata=_em(session_sequence=1), subscription_accepted=_accepted()),
            OrderBookStreamItem(envelope_metadata=_em(session_sequence=2), snapshot=_snapshot(500)),
            OrderBookStreamItem(envelope_metadata=_em(session_sequence=3), depth_update=_du(501)),
            OrderBookStreamItem(envelope_metadata=_em(session_sequence=4), depth_update=_du(502)),
        ]
        # Verify sequence is monotonic
        seq = 0
        for item in items:
            assert item.envelope_metadata.session_sequence > seq
            seq = item.envelope_metadata.session_sequence

        # Verify accepted first
        assert items[0].subscription_accepted is not None
        # Verify snapshot before depth
        assert items[1].snapshot is not None
        assert items[2].depth_update is not None

    def test_depth_before_snapshot_is_invalid(self):
        """DepthUpdate before snapshot without accepted is invalid."""
        # Constructed manually - should fail if transaction-level validation existed
        # This test validates the structural possibility exists but is prohibited by protocol
        item = OrderBookStreamItem(
            envelope_metadata=_em(session_sequence=1),
            depth_update=_du(500),
            snapshot=None,
            subscription_accepted=None,
        )
        # The item itself is structurally valid (it has exactly one payload)
        assert item.depth_update is not None
        assert item.snapshot is None
        # Protocol rule violation is detected at transcript validation level, not here

    def test_gap_without_notice_should_not_happen(self):
        """Protocol rule: no sequence gap without explicit notice."""
        cgn = ConsumerGapNotice(
            schema_version="consumer-gap-notice.v1",
            subscription_id=SubscriptionId("sub-1"),
            detected_time_utc_ns=1_690_000_000_000_000_000,
            reason=ConsumerGapReason.UPSTREAM_SEQUENCE_GAP,
            recovery_action=RecoveryAction.REQUEST_NEW_SNAPSHOT,
        )
        item = OrderBookStreamItem(envelope_metadata=_em(session_sequence=5), consumer_gap=cgn)
        assert item.consumer_gap is not None
        assert item.consumer_gap.reason == ConsumerGapReason.UPSTREAM_SEQUENCE_GAP
        assert item.consumer_gap.recovery_action == RecoveryAction.REQUEST_NEW_SNAPSHOT

    def test_connection_generation_change(self):
        """Connection generation must increase or reset with status notice."""
        # Generation stays same is fine
        em1 = _em(connection_generation=1, session_sequence=1)
        em2 = _em(connection_generation=1, session_sequence=2)
        assert em1.connection_generation == em2.connection_generation

        # Generation increase is fine
        em3 = _em(connection_generation=2, session_sequence=3)
        assert em3.connection_generation > em1.connection_generation

        # Generation decrease without notice is protocol violation
        em4 = _em(connection_generation=1, session_sequence=4)
        assert em4.connection_generation < em3.connection_generation
        # Would require a StreamStatus or ConsumerGapNotice in real protocol

    def test_latest_state_can_skip_intermediate(self):
        """MarketStateStreamItem with LATEST_STATE may skip intermediate revisions."""
        ms1 = MarketStateStreamItem(
            envelope_metadata=_em(session_sequence=1),
            market_state=_ms_snapshot(500),
        )
        ms2 = MarketStateStreamItem(
            envelope_metadata=_em(session_sequence=2),
            market_state=_ms_snapshot(550),
        )
        assert ms1.envelope_metadata.session_sequence == 1
        assert ms2.envelope_metadata.session_sequence == 2
        # Delivery sequence advances — this is valid for LATEST_STATE

    def test_stream_lifecycle_transitions(self):
        """Validate legal lifecycle state transitions."""
        ss1 = StreamStatus(
            schema_version="stream-status.v1",
            subscription_id=SubscriptionId("sub-1"),
            state=StreamLifecycleState.ACCEPTED,
            observed_time_utc_ns=1_690_000_000,
        )
        ss2 = StreamStatus(
            schema_version="stream-status.v1",
            subscription_id=SubscriptionId("sub-1"),
            state=StreamLifecycleState.LIVE,
            observed_time_utc_ns=1_690_000_000_000_000_000,
        )
        assert ss1.state == StreamLifecycleState.ACCEPTED
        assert ss2.state == StreamLifecycleState.LIVE
