"""Test Protobuf compilation and descriptor properties."""

from pathlib import Path

import pytest


def _all_proto_files():
    proto_root = Path(__file__).resolve().parent.parent / "src" / "binance_market_data_contracts" / "proto"
    return sorted(proto_root.rglob("*.proto"))


def test_all_proto_files_exist():
    files = _all_proto_files()
    assert len(files) >= 8, f"Expected at least 8 .proto files, got {len(files)}"


def test_generated_code_exists():
    from pathlib import Path

    gen_dir = Path(__file__).resolve().parent.parent / "src" / "binance_market_data"
    assert gen_dir.is_dir()


def test_all_importable():
    from binance_market_data.market.v1 import market_events_pb2 as me

    assert me.DepthUpdate is not None
    assert me.AggTrade is not None
    assert me.BookTicker is not None
    assert me.ExchangeDepthSnapshot is not None

    from binance_market_data.common.v1 import enums_pb2 as ce

    assert ce.Venue.VENUE_BINANCE == 1
    assert ce.Stream.STREAM_DIFF_DEPTH == 1

    from binance_market_data.projection.v1 import snapshots_pb2

    assert snapshots_pb2.LocalOrderBookSnapshot is not None
    assert snapshots_pb2.MarketStateSnapshot is not None
    assert snapshots_pb2.DataHealthSnapshot is not None

    from binance_market_data.gateway.v1 import gateway_messages_pb2 as gw

    assert gw.GatewayEventEnvelope is not None
    assert gw.OrderBookStreamItem is not None
    assert gw.MarketStateStreamItem is not None

    from binance_market_data.gateway.v1 import gateway_service_pb2_grpc

    assert gateway_service_pb2_grpc.BinanceMarketDataGatewayServiceStub is not None


def test_service_methods():
    from binance_market_data.gateway.v1 import gateway_service_pb2_grpc

    stub = gateway_service_pb2_grpc.BinanceMarketDataGatewayServiceStub
    assert stub is not None
    # Stub methods are set at __init__ and require a channel.
    # Verify the service module exists.
    assert hasattr(gateway_service_pb2_grpc, "BinanceMarketDataGatewayServiceStub")


@pytest.mark.parametrize("proto_file", _all_proto_files())
def test_proto_file_is_valid(proto_file):
    content = proto_file.read_text()
    assert "syntax = " in content, f"Missing syntax in {proto_file.name}"
    assert "package " in content, f"Missing package in {proto_file.name}"
