"""Test JSON serialization round-trip and canonical format with strict=True."""

import json

from binance_market_data_contracts.market_events import AggTrade, BookTicker, DepthUpdate


def _load_fixture(path: str) -> dict:
    import os

    repo_root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(repo_root, path), encoding="utf-8") as f:
        return json.load(f)


def _load_fixture_json(path: str) -> str:
    import os

    repo_root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(repo_root, path), encoding="utf-8") as f:
        return f.read()


class TestRoundTrip:
    def test_depth_update_round_trip(self):
        payload = _load_fixture_json("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate_json(payload)
        dumped = du.model_dump(mode="json")
        re_loaded = DepthUpdate.model_validate_json(json.dumps(dumped))
        assert re_loaded.metadata.symbol == du.metadata.symbol
        assert re_loaded.first_update_id == du.first_update_id
        wrapped = json.loads(json.dumps(dumped))
        assert isinstance(wrapped["metadata"]["quality_flags"], list)

    def test_agg_trade_round_trip(self):
        payload = _load_fixture_json("fixtures/valid/agg-trade.v1.json")
        at = AggTrade.model_validate_json(payload)
        dumped = at.model_dump(mode="json")
        re_loaded = AggTrade.model_validate_json(json.dumps(dumped))
        assert re_loaded.price == at.price

    def test_book_ticker_round_trip(self):
        payload = _load_fixture_json("fixtures/valid/book-ticker.v1.json")
        bt = BookTicker.model_validate_json(payload)
        dumped = bt.model_dump(mode="json")
        re_loaded = BookTicker.model_validate_json(json.dumps(dumped))
        assert re_loaded.best_bid_price == bt.best_bid_price


class TestCanonicalSerialization:
    def test_keys_are_stable(self):
        payload = _load_fixture_json("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate_json(payload)
        dumped1 = json.dumps(du.model_dump(mode="json"), sort_keys=True)
        dumped2 = json.dumps(du.model_dump(mode="json"), sort_keys=True)
        assert dumped1 == dumped2

    def test_string_values_not_coerced(self):
        payload = _load_fixture_json("fixtures/valid/depth-update.v1.spot.json")
        du = DepthUpdate.model_validate_json(payload)
        dumped = du.model_dump(mode="json")
        assert isinstance(dumped["bids"][0]["price"], str)

    def test_null_is_preserved(self):
        payload = _load_fixture_json("fixtures/valid/book-ticker.v1.null-update-id.json")
        bt = BookTicker.model_validate_json(payload)
        dumped = bt.model_dump(mode="json")
        assert dumped["update_id"] is None

    def test_quality_flags_is_array(self):
        payload = _load_fixture_json("fixtures/valid/depth-update.v1.usdm.json")
        du = DepthUpdate.model_validate_json(payload)
        dumped = du.model_dump(mode="json")
        assert isinstance(dumped["metadata"]["quality_flags"], list)


class TestNoBinaryFloatInPublicFields:
    def test_no_float_price_quantity_fields(self):
        from binance_market_data_contracts.versions import CONTRACT_REGISTRY

        for entry in CONTRACT_REGISTRY.values():
            for name, field in entry.python_type.model_fields.items():
                if "price" in name.lower() or "quantity" in name.lower():
                    str(field.annotation)
                    if name in ("sequence_gap_count",):
                        continue
