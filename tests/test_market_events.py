"""Test core market event contracts (DepthUpdate, AggTrade, BookTicker)."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate, EventMetadata


def make_metadata(stream="DIFF_DEPTH"):
    return {
        "venue": "BINANCE",
        "market": "SPOT",
        "symbol": "BTCUSDT",
        "stream": stream,
        "producer": "test",
        "producer_version": "0.1.0",
        "schema_version": "depth-update.v1",
        "connection_id": "test-conn",
        "exchange_event_time_ms": 1000,
        "exchange_trade_time_ms": None,
        "exchange_transaction_time_ms": None,
        "receive_time_utc_ns": 2000,
        "receive_monotonic_ns": 2001,
        "quality_flags": [],
    }


class TestEventMetadata:
    def test_metadata_construction(self):
        m = EventMetadata(**make_metadata())
        assert m.venue == "BINANCE"
        assert m.market == "SPOT"
        assert m.symbol == "BTCUSDT"
        assert m.exchange_event_time_ms == 1000
        assert m.exchange_trade_time_ms is None

    def test_missing_time_is_none_not_zero(self):
        m = EventMetadata(**make_metadata())
        assert m.exchange_trade_time_ms is None

    def test_quality_flags_default_empty(self):
        data = make_metadata()
        del data["quality_flags"]
        m = EventMetadata(**data)
        assert m.quality_flags == []

    def test_missing_venue(self):
        data = make_metadata()
        del data["venue"]
        with pytest.raises(ValidationError):
            EventMetadata(**data)

    def test_unknown_field_rejected(self):
        data = make_metadata()
        data["timestamp"] = 123
        with pytest.raises(ValidationError, match="timestamp"):
            EventMetadata(**data)


class TestDepthUpdate:
    def test_valid_depth_update(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "first_update_id": 1001,
            "final_update_id": 1005,
            "previous_final_update_id": None,
            "bids": [{"price": "29500.00", "quantity": "1.5"}],
            "asks": [{"price": "29501.00", "quantity": "0.5"}],
        }
        du = DepthUpdate.model_validate(data)
        assert du.first_update_id == 1001
        assert du.final_update_id == 1005
        assert du.previous_final_update_id is None
        assert len(du.bids) == 1
        assert du.bids[0].price == "29500.00"

    def test_final_before_first_rejected(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "first_update_id": 10,
            "final_update_id": 5,
            "bids": [],
            "asks": [],
        }
        with pytest.raises(ValidationError):
            DepthUpdate.model_validate(data)

    def test_first_equals_final_allowed(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "first_update_id": 1,
            "final_update_id": 1,
            "bids": [],
            "asks": [],
        }
        du = DepthUpdate.model_validate(data)
        assert du.first_update_id == du.final_update_id == 1

    def test_empty_bids_asks_allowed(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "first_update_id": 1,
            "final_update_id": 1,
            "bids": [],
            "asks": [],
        }
        du = DepthUpdate.model_validate(data)
        assert du.bids == []
        assert du.asks == []

    def test_wrong_stream_rejected(self):
        data = {
            "metadata": make_metadata("AGG_TRADE"),
            "first_update_id": 1,
            "final_update_id": 1,
            "bids": [],
            "asks": [],
        }
        with pytest.raises(ValidationError):
            DepthUpdate.model_validate(data)

    def test_negative_update_id_rejected(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "first_update_id": -1,
            "final_update_id": 5,
            "bids": [],
            "asks": [],
        }
        with pytest.raises(ValidationError):
            DepthUpdate.model_validate(data)


class TestAggTrade:
    def test_valid_agg_trade(self):
        data = {
            "metadata": make_metadata("AGG_TRADE"),
            "aggregate_trade_id": 5001,
            "price": "29501.50",
            "quantity": "0.50000000",
            "first_trade_id": 10001,
            "last_trade_id": 10003,
            "trade_time_ms": 1690000003900,
            "buyer_is_maker": False,
        }
        at = AggTrade.model_validate(data)
        assert at.aggregate_trade_id == 5001
        assert at.buyer_is_maker is False

    def test_last_before_first_rejected(self):
        data = {
            "metadata": make_metadata("AGG_TRADE"),
            "aggregate_trade_id": 1,
            "price": "100.00",
            "quantity": "1.0",
            "first_trade_id": 10,
            "last_trade_id": 5,
            "trade_time_ms": 1000,
            "buyer_is_maker": False,
        }
        with pytest.raises(ValidationError):
            AggTrade.model_validate(data)

    def test_zero_price_rejected(self):
        data = {
            "metadata": make_metadata("AGG_TRADE"),
            "aggregate_trade_id": 1,
            "price": "0",
            "quantity": "1.0",
            "first_trade_id": 1,
            "last_trade_id": 1,
            "trade_time_ms": 1000,
            "buyer_is_maker": False,
        }
        with pytest.raises(ValidationError):
            AggTrade.model_validate(data)

    def test_wrong_stream_rejected(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "aggregate_trade_id": 1,
            "price": "100.00",
            "quantity": "1.0",
            "first_trade_id": 1,
            "last_trade_id": 1,
            "trade_time_ms": 1000,
            "buyer_is_maker": False,
        }
        with pytest.raises(ValidationError):
            AggTrade.model_validate(data)


class TestBookTicker:
    def test_valid_book_ticker(self):
        data = {
            "metadata": make_metadata("BOOK_TICKER"),
            "update_id": 7001,
            "best_bid_price": "29500.00",
            "best_bid_quantity": "1.5",
            "best_ask_price": "29501.00",
            "best_ask_quantity": "2.0",
        }
        bt = BookTicker.model_validate(data)
        assert bt.best_bid_price == "29500.00"

    def test_null_update_id_allowed(self):
        data = {
            "metadata": make_metadata("BOOK_TICKER"),
            "update_id": None,
            "best_bid_price": "29500.00",
            "best_bid_quantity": "1.0",
            "best_ask_price": "29501.00",
            "best_ask_quantity": "1.0",
        }
        bt = BookTicker.model_validate(data)
        assert bt.update_id is None

    def test_crossed_book_accepted(self):
        """Crossed book (bid >= ask) must be representable in the contract."""
        data = {
            "metadata": make_metadata("BOOK_TICKER"),
            "update_id": 1,
            "best_bid_price": "29510.00",
            "best_bid_quantity": "1.0",
            "best_ask_price": "29500.00",
            "best_ask_quantity": "0.5",
        }
        bt = BookTicker.model_validate(data)
        assert bt.best_bid_price == "29510.00"
        assert bt.best_ask_price == "29500.00"

    def test_wrong_stream_rejected(self):
        data = {
            "metadata": make_metadata("DIFF_DEPTH"),
            "update_id": 1,
            "best_bid_price": "29500.00",
            "best_bid_quantity": "1.0",
            "best_ask_price": "29501.00",
            "best_ask_quantity": "1.0",
        }
        with pytest.raises(ValidationError):
            BookTicker.model_validate(data)
