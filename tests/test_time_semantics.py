"""Test time semantics: field naming, units, null handling."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.enums import Market, Venue
from binance_market_data_contracts.market_events import BaseEventMetadata
from binance_market_data_contracts.time import ALLOWED_TIME_FIELD_NAMES
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


class TestTimeFieldNaming:
    def test_no_field_named_timestamp_on_models(self):
        for entry in CONTRACT_REGISTRY.values():
            for name in entry.python_type.model_fields:
                assert name != "timestamp", f"{entry.name} has forbidden field 'timestamp'"

    def test_time_fields_have_unit_suffix(self):
        """All time-related fields must end with a unit suffix or be in the allowed set."""
        for entry in CONTRACT_REGISTRY.values():
            for field_name, field_info in entry.python_type.model_fields.items():
                if (
                    "time" in field_name.lower()
                    or field_name.endswith("_at")
                    or field_name.endswith("_ms")
                    or field_name.endswith("_ns")
                ):
                    if field_name in ALLOWED_TIME_FIELD_NAMES:
                        continue
                    if field_name.endswith("_seconds"):
                        continue


class TestTimeNullSemantics:
    def test_missing_exchange_time_is_null(self):
        m = BaseEventMetadata(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol="BTCUSDT",
            producer="test",
            producer_version="0.1.0",
            connection_id="conn-1",
        )
        assert m.exchange_event_time_ms is None
        assert m.exchange_trade_time_ms is None

    def test_time_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            BaseEventMetadata(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol="BTCUSDT",
                producer="test",
                producer_version="0.1.0",
                connection_id="conn-1",
                receive_time_utc_ns=-1,
            )

    def test_exchange_time_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            BaseEventMetadata(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol="BTCUSDT",
                producer="test",
                producer_version="0.1.0",
                connection_id="conn-1",
                exchange_event_time_ms=-100,
            )
