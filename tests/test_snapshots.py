"""Test snapshot contracts."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.snapshots import (
    DataHealthSnapshot,
    ExchangeDepthSnapshot,
    GapDescriptor,
    LatencySummary,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)


class TestExchangeDepthSnapshot:
    def test_valid_snapshot(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "exchange-depth-snapshot.v1",
            "producer": "recorder",
            "producer_version": "0.1.0",
            "request_id": "req-001",
            "last_update_id": 50001,
            "bids": [{"price": "29500.00", "quantity": "1.5"}],
            "asks": [{"price": "29501.00", "quantity": "1.0"}],
            "exchange_transaction_time_ms": 1000,
            "receive_time_utc_ns": 2000,
            "receive_monotonic_ns": 2001,
            "quality_flags": [],
        }
        snap = ExchangeDepthSnapshot.model_validate(data)
        assert snap.last_update_id == 50001

    def test_empty_bids_asks(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "exchange-depth-snapshot.v1",
            "producer": "recorder",
            "producer_version": "0.1.0",
            "request_id": "req-001",
            "last_update_id": 1,
            "bids": [],
            "asks": [],
            "quality_flags": [],
        }
        snap = ExchangeDepthSnapshot.model_validate(data)
        assert snap.bids == []


class TestGapDescriptor:
    def test_gap_descriptor(self):
        gd = GapDescriptor(
            stream="DIFF_DEPTH",
            detected_at_utc_ns=1000,
            previous_sequence=100,
            next_sequence=200,
            reason_code="SEQUENCE_GAP_DETECTED",
            recovery_state="RESYNC_IN_PROGRESS",
        )
        assert gd.stream == "DIFF_DEPTH"
        assert gd.previous_sequence == 100
        assert gd.next_sequence == 200


class TestLocalOrderBookSnapshot:
    def test_synchronized_snapshot(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "local-order-book-snapshot.v1",
            "producer": "gateway",
            "producer_version": "0.1.0",
            "source": "gateway-live",
            "last_update_id": 100,
            "bids": [{"price": "29500.00", "quantity": "1.0"}],
            "asks": [],
            "depth_limit": 100,
            "generated_time_utc_ns": 1000,
            "generated_monotonic_ns": 1001,
            "synchronized": True,
            "last_gap": None,
            "quality_flags": [],
        }
        snap = LocalOrderBookSnapshot.model_validate(data)
        assert snap.synchronized is True
        assert snap.last_gap is None

    def test_with_gap(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "local-order-book-snapshot.v1",
            "producer": "gateway",
            "producer_version": "0.1.0",
            "source": "gateway-live",
            "last_update_id": 200,
            "bids": [],
            "asks": [],
            "synchronized": False,
            "last_gap": {
                "stream": "DIFF_DEPTH",
                "detected_at_utc_ns": 500,
                "previous_sequence": 10,
                "next_sequence": 20,
                "reason_code": "SEQUENCE_GAP_DETECTED",
                "recovery_state": "RESYNC_IN_PROGRESS",
            },
            "quality_flags": ["SEQUENCE_GAP"],
        }
        snap = LocalOrderBookSnapshot.model_validate(data)
        assert snap.synchronized is False
        assert snap.last_gap is not None
        assert snap.last_gap.previous_sequence == 10


class TestMarketStateSnapshot:
    def test_minimal_snapshot(self):
        data = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "market-state-snapshot.v1",
            "producer": "projection",
            "producer_version": "0.1.0",
        }
        snap = MarketStateSnapshot.model_validate(data)
        assert snap.best_bid_price is None
        assert snap.mid_price is None


class TestLatencySummary:
    def test_valid_summary(self):
        ls = LatencySummary(
            count=100,
            min_ms=10.0,
            max_ms=250.0,
            p50_ms=45.0,
            p95_ms=120.0,
            p99_ms=200.0,
            window_start_utc_ns=1000,
            window_end_utc_ns=2000,
        )
        assert ls.count == 100
        assert ls.p50_ms == 45.0

    def test_zero_count_nulls(self):
        ls = LatencySummary(
            count=0,
            min_ms=None,
            max_ms=None,
            p50_ms=None,
            p95_ms=None,
            p99_ms=None,
            window_start_utc_ns=1000,
            window_end_utc_ns=2000,
        )
        assert ls.count == 0
        assert ls.min_ms is None

    def test_zero_count_with_non_null_fields_fails(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=0,
                min_ms=10.0,
                max_ms=None,
                p50_ms=None,
                p95_ms=None,
                p99_ms=None,
                window_start_utc_ns=1000,
                window_end_utc_ns=2000,
            )

    def test_positive_count_with_null_fields_fails(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=1,
                min_ms=10.0,
                max_ms=None,
                p50_ms=20.0,
                p95_ms=30.0,
                p99_ms=40.0,
                window_start_utc_ns=1000,
                window_end_utc_ns=2000,
            )

    def test_ordering_violation(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=10,
                min_ms=100.0,
                max_ms=50.0,
                p50_ms=75.0,
                p95_ms=80.0,
                p99_ms=90.0,
                window_start_utc_ns=1000,
                window_end_utc_ns=2000,
            )

    def test_percentile_ordering(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=10,
                min_ms=10.0,
                max_ms=100.0,
                p50_ms=80.0,
                p95_ms=60.0,
                p99_ms=90.0,
                window_start_utc_ns=1000,
                window_end_utc_ns=2000,
            )

    def test_window_end_before_start(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=10,
                min_ms=10.0,
                max_ms=100.0,
                p50_ms=40.0,
                p95_ms=80.0,
                p99_ms=90.0,
                window_start_utc_ns=2000,
                window_end_utc_ns=1000,
            )

    def test_negative_count(self):
        with pytest.raises(ValidationError):
            LatencySummary(
                count=-1,
                min_ms=None,
                max_ms=None,
                p50_ms=None,
                p95_ms=None,
                p99_ms=None,
                window_start_utc_ns=1000,
                window_end_utc_ns=2000,
            )


class TestDataHealthSnapshot:
    def test_healthy_snapshot(self):
        data = {
            "overall_state": "HEALTHY",
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "data-health-snapshot.v1",
            "sequence_gap_count": 0,
            "book_synchronized": True,
            "recorder_alive": True,
            "gateway_alive": True,
            "reason_codes": [],
        }
        snap = DataHealthSnapshot.model_validate(data)
        assert snap.overall_state == "HEALTHY"

    def test_degraded_with_reasons(self):
        data = {
            "overall_state": "DEGRADED",
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "data-health-snapshot.v1",
            "sequence_gap_count": 3,
            "book_synchronized": False,
            "reason_codes": ["SEQUENCE_GAP_DETECTED", "BOOK_NOT_SYNCHRONIZED"],
        }
        snap = DataHealthSnapshot.model_validate(data)
        assert snap.overall_state == "DEGRADED"
        assert len(snap.reason_codes) == 2
