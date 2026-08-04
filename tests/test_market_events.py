"""Test core market event contracts with strict=True and model_validate_json."""

import json

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.market_events import (
    AggTrade,
    BookTicker,
    DepthUpdate,
    DepthUpdateMetadata,
    _BaseEventMetadata,
)


def md_json(stream="DIFF_DEPTH", schema_version="depth-update.v1", **overrides):
    """Make metadata dict for JSON input."""
    base = {
        "metadata": {
            "venue": "BINANCE",
            "market": "SPOT",
            "symbol": "BTCUSDT",
            "stream": stream,
            "schema_version": schema_version,
            "producer": "test",
            "producer_version": "0.1.0",
            "connection_id": "test-conn",
            "exchange_event_time_ms": None,
            "exchange_trade_time_ms": None,
            "exchange_transaction_time_ms": None,
            "receive_time_utc_ns": None,
            "receive_monotonic_ns": None,
            **overrides,
        }
    }
    return base


class TestBaseMetadata:
    def test_metadata_json_construction(self):
        m = _BaseEventMetadata.model_validate_json(
            json.dumps(
                {
                    "venue": "BINANCE",
                    "market": "SPOT",
                    "symbol": "BTCUSDT",
                    "producer": "test",
                    "producer_version": "0.1.0",
                    "connection_id": "conn-1",
                }
            )
        )
        assert m.venue == "BINANCE"
        assert m.exchange_event_time_ms is None

    def test_missing_time_is_none(self):
        m = _BaseEventMetadata.model_validate_json(
            json.dumps(
                {
                    "venue": "BINANCE",
                    "market": "SPOT",
                    "symbol": "BTCUSDT",
                    "producer": "test",
                    "producer_version": "0.1.0",
                    "connection_id": "conn-1",
                }
            )
        )
        assert m.exchange_event_time_ms is None


class TestDepthUpdateMetadata:
    def test_stream_and_version_fixed(self):
        m = DepthUpdateMetadata.model_validate_json(
            json.dumps(
                {
                    "venue": "BINANCE",
                    "market": "SPOT",
                    "symbol": "BTCUSDT",
                    "stream": "DIFF_DEPTH",
                    "schema_version": "depth-update.v1",
                    "producer": "test",
                    "producer_version": "0.1.0",
                    "connection_id": "conn-1",
                }
            )
        )
        assert m.stream == "DIFF_DEPTH"
        assert m.schema_version == "depth-update.v1"


class TestDepthUpdate:
    def test_valid_depth_update(self):
        payload = {
            **md_json(),
            "first_update_id": 1001,
            "final_update_id": 1005,
            "bids": [{"price": "29500.00", "quantity": "1.5"}],
            "asks": [{"price": "29501.00", "quantity": "0.5"}],
        }
        du = DepthUpdate.model_validate_json(json.dumps(payload))
        assert du.first_update_id == 1001
        assert du.bids[0].price == "29500.00"

    def test_final_before_first_rejected(self):
        payload = {**md_json(), "first_update_id": 10, "final_update_id": 5, "bids": [], "asks": []}
        with pytest.raises(ValidationError):
            DepthUpdate.model_validate_json(json.dumps(payload))

    def test_first_equals_final_allowed(self):
        payload = {**md_json(), "first_update_id": 1, "final_update_id": 1, "bids": [], "asks": []}
        du = DepthUpdate.model_validate_json(json.dumps(payload))
        assert du.first_update_id == du.final_update_id == 1

    def test_empty_bids_asks_allowed(self):
        payload = {**md_json(), "first_update_id": 1, "final_update_id": 1}
        du = DepthUpdate.model_validate_json(json.dumps(payload))
        assert du.bids == ()
        assert du.asks == ()

    def test_wrong_metadata_for_depth_update_rejected_json(self):
        """DepthUpdate needs DepthUpdateMetadata, not _BaseEventMetadata."""
        payload = {
            "metadata": {
                "venue": "BINANCE",
                "market": "SPOT",
                "symbol": "BTCUSDT",
                "stream": "AGG_TRADE",
                "producer": "test",
                "producer_version": "0.1.0",
                "connection_id": "conn-1",
                "schema_version": "depth-update.v1",
            },
            "first_update_id": 1,
            "final_update_id": 1,
        }
        with pytest.raises(ValidationError):
            DepthUpdate.model_validate_json(json.dumps(payload))

    def test_frozen_collection(self):
        payload = {
            **md_json(),
            "first_update_id": 1,
            "final_update_id": 1,
            "bids": [{"price": "100.00", "quantity": "1.0"}],
        }
        du = DepthUpdate.model_validate_json(json.dumps(payload))
        assert not hasattr(du.bids, "append")


class TestAggTrade:
    def test_valid_agg_trade(self):
        payload = {
            **md_json("AGG_TRADE", "agg-trade.v1"),
            "aggregate_trade_id": 5001,
            "price": "29501.50",
            "quantity": "0.50000000",
            "first_trade_id": 10001,
            "last_trade_id": 10003,
            "trade_time_ms": 1690000003900,
            "buyer_is_maker": False,
        }
        at = AggTrade.model_validate_json(json.dumps(payload))
        assert at.aggregate_trade_id == 5001

    def test_zero_quantity_rejected(self):
        payload = {
            **md_json(),
            "aggregate_trade_id": 1,
            "price": "100.00",
            "quantity": "0",
            "first_trade_id": 1,
            "last_trade_id": 1,
            "trade_time_ms": 1000,
            "buyer_is_maker": False,
        }
        with pytest.raises(ValidationError):
            AggTrade.model_validate_json(json.dumps(payload))

    def test_last_before_first_rejected(self):
        payload = {
            **md_json(),
            "aggregate_trade_id": 1,
            "price": "100.00",
            "quantity": "1.0",
            "first_trade_id": 10,
            "last_trade_id": 5,
            "trade_time_ms": 1000,
            "buyer_is_maker": False,
        }
        with pytest.raises(ValidationError):
            AggTrade.model_validate_json(json.dumps(payload))


class TestBookTicker:
    def test_valid_book_ticker(self):
        payload = {
            **md_json("BOOK_TICKER", "book-ticker.v1"),
            "update_id": 7001,
            "best_bid_price": "29500.00",
            "best_bid_quantity": "1.5",
            "best_ask_price": "29501.00",
            "best_ask_quantity": "2.0",
        }
        bt = BookTicker.model_validate_json(json.dumps(payload))
        assert bt.best_bid_price == "29500.00"

    def test_null_update_id_allowed(self):
        payload = {
            **md_json("BOOK_TICKER", "book-ticker.v1"),
            "update_id": None,
            "best_bid_price": "29500.00",
            "best_bid_quantity": "1.0",
            "best_ask_price": "29501.00",
            "best_ask_quantity": "1.0",
        }
        bt = BookTicker.model_validate_json(json.dumps(payload))
        assert bt.update_id is None

    def test_crossed_book_accepted(self):
        payload = {
            **md_json("BOOK_TICKER", "book-ticker.v1"),
            "best_bid_price": "29510.00",
            "best_bid_quantity": "1.0",
            "best_ask_price": "29500.00",
            "best_ask_quantity": "0.5",
        }
        bt = BookTicker.model_validate_json(json.dumps(payload))
        assert bt.best_bid_price == "29510.00"
