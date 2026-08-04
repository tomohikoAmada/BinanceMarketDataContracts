"""Test compatibility rules and registry consistency."""

from binance_market_data_contracts.enums import ContractStatus
from binance_market_data_contracts.versions import CONTRACT_REGISTRY, ContractEntry, get_contract_status


class TestRegistry:
    def test_get_contract_status_known(self):
        assert get_contract_status("depth-update.v1") == ContractStatus.PROPOSED
        assert get_contract_status("agg-trade.v1") == ContractStatus.PROPOSED
        assert get_contract_status("historical-dataset-descriptor.v1") == ContractStatus.DRAFT

    def test_get_contract_status_unknown(self):
        assert get_contract_status("nonexistent.v99") is None

    def test_registry_entries_have_required_fields(self):
        for name, entry in CONTRACT_REGISTRY.items():
            assert isinstance(entry, ContractEntry)
            assert entry.name == name
            assert entry.status is not None
            assert entry.python_type is not None

    def test_proposed_contracts_have_producers(self):
        for entry in CONTRACT_REGISTRY.values():
            if entry.status == ContractStatus.PROPOSED:
                assert entry.producer is not None, f"PROPOSED {entry.name} has no producer"
                assert entry.consumer is not None, f"PROPOSED {entry.name} has no consumer"

    def test_no_accepted_contracts_yet(self):
        from binance_market_data_contracts.versions import get_accepted_contracts

        accepted = get_accepted_contracts()
        assert len(accepted) == 0, "No contracts should be ACCEPTED yet"


class TestCompatibilityRules:
    def test_depth_update_v1_accepts_previous_final(self):
        from binance_market_data_contracts.market_events import DepthUpdate, EventMetadata

        meta = EventMetadata(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            stream="DIFF_DEPTH",
            producer="test",
            producer_version="0.1.0",
            schema_version="depth-update.v1",
            connection_id="c1",
        )
        du = DepthUpdate(metadata=meta, first_update_id=1, final_update_id=2, previous_final_update_id=0)
        assert du.previous_final_update_id == 0

    def test_agg_trade_v1_accepts_quantity_zero(self):
        from binance_market_data_contracts.market_events import AggTrade, EventMetadata

        meta = EventMetadata(
            venue="BINANCE",
            market="SPOT",
            symbol="BTCUSDT",
            stream="AGG_TRADE",
            producer="test",
            producer_version="0.1.0",
            schema_version="agg-trade.v1",
            connection_id="c1",
        )
        at = AggTrade(
            metadata=meta,
            aggregate_trade_id=1,
            price="100.00",
            quantity="0",
            first_trade_id=1,
            last_trade_id=1,
            trade_time_ms=1000,
            buyer_is_maker=False,
        )
        assert at.quantity == "0"
