"""Test snapshot contracts with strict=True and tuple collections."""

import json

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
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "recorder",
            "producer_version": "0.1.0",
            "schema_version": "exchange-depth-snapshot.v1",
            "request_id": "req-001",
            "last_update_id": 50001,
            "bids": [{"price": "29500.00", "quantity": "1.5"}],
            "asks": [{"price": "29501.00", "quantity": "1.0"}],
        }
        snap = ExchangeDepthSnapshot.model_validate_json(json.dumps(payload))
        assert snap.last_update_id == 50001
        assert snap.schema_version == "exchange-depth-snapshot.v1"

    def test_empty_bids_asks(self):
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "recorder",
            "producer_version": "0.1.0",
            "schema_version": "exchange-depth-snapshot.v1",
            "request_id": "req-001",
            "last_update_id": 1,
        }
        snap = ExchangeDepthSnapshot.model_validate_json(json.dumps(payload))
        assert snap.bids == ()


class TestGapDescriptor:
    def test_gap_descriptor(self):
        gd = GapDescriptor.model_validate_json(
            json.dumps(
                {
                    "stream": "DIFF_DEPTH",
                    "detected_at_utc_ns": 1000,
                    "previous_sequence": 100,
                    "next_sequence": 200,
                    "reason_code": "SEQUENCE_GAP_DETECTED",
                    "recovery_state": "RESYNC_IN_PROGRESS",
                }
            )
        )
        assert gd.stream == "DIFF_DEPTH"


class TestLocalOrderBookSnapshot:
    def test_synchronized_snapshot(self):
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "gateway",
            "producer_version": "0.1.0",
            "schema_version": "local-order-book-snapshot.v1",
            "source": "GATEWAY_LIVE",
            "last_update_id": 100,
            "bids": [{"price": "29500.00", "quantity": "1.0"}],
            "generated_time_utc_ns": 1000,
            "synchronized": True,
        }
        snap = LocalOrderBookSnapshot.model_validate_json(json.dumps(payload))
        assert snap.synchronized is True

    def test_with_gap(self):
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "gateway",
            "producer_version": "0.1.0",
            "schema_version": "local-order-book-snapshot.v1",
            "source": "GATEWAY_LIVE",
            "last_update_id": 200,
            "generated_time_utc_ns": 11000000000,
            "synchronized": False,
            "last_gap": {
                "stream": "DIFF_DEPTH",
                "detected_at_utc_ns": 500,
                "previous_sequence": 10,
                "next_sequence": 20,
            },
            "quality_flags": ["SEQUENCE_GAP"],
        }
        snap = LocalOrderBookSnapshot.model_validate_json(json.dumps(payload))
        assert snap.last_gap is not None


class TestMarketStateSnapshot:
    def test_minimal_snapshot(self):
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "market-state-snapshot.v1",
            "producer": "projection",
            "producer_version": "0.1.0",
            "generated_time_utc_ns": 1000,
        }
        snap = MarketStateSnapshot.model_validate_json(json.dumps(payload))
        assert snap.best_bid_price is None
        assert snap.schema_version == "market-state-snapshot.v1"

    def test_top_bids_asks(self):
        payload = {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "schema_version": "market-state-snapshot.v1",
            "producer": "projection",
            "producer_version": "0.1.0",
            "generated_time_utc_ns": 1000,
            "top_bids": [{"price": "29500.00", "quantity": "1.0"}],
            "top_asks": [{"price": "29501.00", "quantity": "2.0"}],
        }
        snap = MarketStateSnapshot.model_validate_json(json.dumps(payload))
        assert len(snap.top_bids) == 1
        assert len(snap.top_asks) == 1


class TestLatencySummary:
    def test_valid_summary(self):
        ls = LatencySummary.model_validate_json(
            json.dumps(
                {
                    "count": 100,
                    "min_ms": 10.0,
                    "max_ms": 250.0,
                    "p50_ms": 45.0,
                    "p95_ms": 120.0,
                    "p99_ms": 200.0,
                    "window_start_utc_ns": 1000,
                    "window_end_utc_ns": 2000,
                }
            )
        )
        assert ls.count == 100

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

    def test_zero_count_with_non_null_fails(self):
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


class TestDataHealthSnapshot:
    def test_healthy_snapshot(self):
        payload = {
            "health_snapshot_id": "hs-001",
            "overall_state": "HEALTHY",
            "schema_version": "data-health-snapshot.v1",
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "health",
            "producer_version": "0.1.0",
            "source_instance_id": "health-001",
            "observed_time_utc_ns": 1000,
            "sequence_gap_count": 0,
            "book_synchronized": True,
            "recorder_alive": True,
            "gateway_alive": True,
        }
        snap = DataHealthSnapshot.model_validate_json(json.dumps(payload))
        assert snap.overall_state == "HEALTHY"

    def test_degraded_with_reasons(self):
        payload = {
            "health_snapshot_id": "hs-002",
            "overall_state": "DEGRADED",
            "schema_version": "data-health-snapshot.v1",
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "producer": "health",
            "producer_version": "0.1.0",
            "source_instance_id": "health-001",
            "observed_time_utc_ns": 2000,
            "sequence_gap_count": 3,
            "book_synchronized": False,
            "reason_codes": ["SEQUENCE_GAP_DETECTED", "BOOK_NOT_SYNCHRONIZED"],
        }
        snap = DataHealthSnapshot.model_validate_json(json.dumps(payload))
        assert snap.overall_state == "DEGRADED"
        assert len(snap.reason_codes) == 2
