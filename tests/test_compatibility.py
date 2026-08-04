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

    def test_no_accepted_contracts_yet(self):
        from binance_market_data_contracts.versions import get_accepted_contracts

        accepted = get_accepted_contracts()
        assert len(accepted) == 0, "No contracts should be ACCEPTED yet"


class TestCompatibilityRules:
    def test_depth_update_v1_accepts_previous_final(self):
        from binance_market_data_contracts.enums import Market, Stream, Venue
        from binance_market_data_contracts.market_events import DepthUpdate, DepthUpdateMetadata

        meta = DepthUpdateMetadata(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol="BTCUSDT",
            stream=Stream.DIFF_DEPTH,
            schema_version="depth-update.v1",
            producer="test",
            producer_version="0.1.0",
            connection_id="c1",
        )
        du = DepthUpdate(metadata=meta, first_update_id=1, final_update_id=2, previous_final_update_id=0)
        assert du.previous_final_update_id == 0
