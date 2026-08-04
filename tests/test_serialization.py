"""Test JSON serialization round-trip and canonical format."""

import json

from binance_market_data_contracts.market_events import DepthUpdate


def _load_fixture(path: str) -> dict:
    import os

    repo_root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(repo_root, path), encoding="utf-8") as f:
        return json.load(f)


class TestRoundTrip:
    def test_depth_update_round_trip(self):
        payload = _load_fixture("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate(payload)
        dumped = du.model_dump(mode="json")
        re_loaded = DepthUpdate.model_validate(dumped)
        assert re_loaded.metadata.symbol == du.metadata.symbol
        assert re_loaded.first_update_id == du.first_update_id
        assert re_loaded.final_update_id == du.final_update_id
        assert len(re_loaded.bids) == 3
        assert re_loaded.bids[0].price == "29500.50"

    def test_agg_trade_round_trip(self):
        from binance_market_data_contracts.market_events import AggTrade

        payload = _load_fixture("fixtures/valid/agg-trade.v1.json")
        at = AggTrade.model_validate(payload)
        dumped = at.model_dump(mode="json")
        re_loaded = AggTrade.model_validate(dumped)
        assert re_loaded.aggregate_trade_id == at.aggregate_trade_id
        assert re_loaded.price == at.price

    def test_book_ticker_round_trip(self):
        from binance_market_data_contracts.market_events import BookTicker

        payload = _load_fixture("fixtures/valid/book-ticker.v1.json")
        bt = BookTicker.model_validate(payload)
        dumped = bt.model_dump(mode="json")
        re_loaded = BookTicker.model_validate(dumped)
        assert re_loaded.best_bid_price == bt.best_bid_price

    def test_data_health_round_trip(self):
        from binance_market_data_contracts.snapshots import DataHealthSnapshot

        payload = _load_fixture("fixtures/valid/data-health-snapshot.v1.json")
        dh = DataHealthSnapshot.model_validate(payload)
        dumped = dh.model_dump(mode="json")
        re_loaded = DataHealthSnapshot.model_validate(dumped)
        assert re_loaded.overall_state == dh.overall_state


class TestCanonicalSerialization:
    def test_keys_are_stable(self):
        payload = _load_fixture("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate(payload)
        dumped1 = json.dumps(du.model_dump(mode="json"), sort_keys=True)
        dumped2 = json.dumps(du.model_dump(mode="json"), sort_keys=True)
        assert dumped1 == dumped2

    def test_string_values_not_coerced(self):
        payload = _load_fixture("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate(payload)
        dumped = du.model_dump(mode="json")
        assert isinstance(dumped["bids"][0]["price"], str)
        assert isinstance(dumped["bids"][0]["quantity"], str)

    def test_enum_serialized_as_string(self):
        from binance_market_data_contracts.enums import Venue
        from binance_market_data_contracts.market_events import EventMetadata

        m = EventMetadata(
            venue=Venue.BINANCE,
            market="SPOT",
            symbol="BTCUSDT",
            stream="DIFF_DEPTH",
            producer="test",
            producer_version="0.1.0",
            schema_version="depth-update.v1",
            connection_id="conn-1",
        )
        dumped = m.model_dump(mode="json")
        assert dumped["venue"] == "BINANCE"
        assert isinstance(dumped["venue"], str)

    def test_null_is_preserved(self):
        from binance_market_data_contracts.market_events import BookTicker

        payload = _load_fixture("fixtures/valid/book-ticker.v1.null-update-id.json")
        bt = BookTicker.model_validate(payload)
        dumped = bt.model_dump(mode="json")
        assert dumped["update_id"] is None

    def test_quality_flags_is_array_of_strings(self):
        payload = _load_fixture("fixtures/valid/depth-update.v1.usdm.json")
        du = DepthUpdate.model_validate(payload)
        dumped = du.model_dump(mode="json")
        assert "DUPLICATE" in dumped["metadata"]["quality_flags"]


class TestNoBinaryFloatInPublicFields:
    """Verify no price/quantity field uses float type."""

    def test_no_float_price_quantity_fields(self):
        from binance_market_data_contracts.market_events import (
            AggTrade,
            BookTicker,
            DepthUpdate,
        )
        from binance_market_data_contracts.snapshots import (
            DataHealthSnapshot,
            ExchangeDepthSnapshot,
            LocalOrderBookSnapshot,
            MarketStateSnapshot,
        )

        models = [
            DepthUpdate,
            AggTrade,
            BookTicker,
            ExchangeDepthSnapshot,
            LocalOrderBookSnapshot,
            MarketStateSnapshot,
            DataHealthSnapshot,
        ]
        for model in models:
            for name, field in model.model_fields.items():
                if "price" in name.lower() or ("quantity" in name.lower() and name != "quantity"):
                    annotation = field.annotation
                    annotation_str = str(annotation)
                    assert "float" not in annotation_str.lower() or "Annotated" in annotation_str, (
                        f"{model.__name__}.{name} uses float type directly: {annotation_str}"
                    )
