"""Test time semantics: field naming, units, null handling."""

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.market_events import EventMetadata
from binance_market_data_contracts.snapshots import DataHealthSnapshot, ExchangeDepthSnapshot


class TestTimeFieldNaming:
    def test_no_field_named_timestamp_on_metadata(self):
        fields = EventMetadata.model_fields
        for name in fields:
            assert name != "timestamp", "EventMetadata has forbidden field 'timestamp'"

    def test_no_field_named_timestamp_on_snapshot(self):
        fields = ExchangeDepthSnapshot.model_fields
        for name in fields:
            assert name != "timestamp", "ExchangeDepthSnapshot has forbidden field 'timestamp'"

    def test_no_field_named_timestamp_on_health(self):
        fields = DataHealthSnapshot.model_fields
        for name in fields:
            assert name != "timestamp", "DataHealthSnapshot has forbidden field 'timestamp'"

    def test_time_fields_have_unit_suffix(self):
        fields = EventMetadata.model_fields
        time_fields = [n for n in fields if "time" in n.lower()]
        for tf in time_fields:
            assert tf.endswith("_ms") or tf.endswith("_ns"), f"Time field '{tf}' missing unit suffix"


class TestTimeNullSemantics:
    def test_missing_exchange_time_is_null(self):
        m = EventMetadata(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            stream="DIFF_DEPTH",
            producer="test",
            producer_version="0.1.0",
            schema_version="depth-update.v1",
            connection_id="conn-1",
        )
        assert m.exchange_event_time_ms is None
        assert m.exchange_trade_time_ms is None

    def test_time_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            EventMetadata(
                venue="BINANCE",
                market="SPOT",
                symbol="BTCUSDT",
                stream="DIFF_DEPTH",
                producer="test",
                producer_version="0.1.0",
                schema_version="depth-update.v1",
                connection_id="conn-1",
                receive_time_utc_ns=-1,
            )

    def test_exchange_time_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            EventMetadata(
                venue="BINANCE",
                market="SPOT",
                symbol="BTCUSDT",
                stream="DIFF_DEPTH",
                producer="test",
                producer_version="0.1.0",
                schema_version="depth-update.v1",
                connection_id="conn-1",
                exchange_event_time_ms=-100,
            )
