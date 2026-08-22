"""Test Pydantic ↔ Protobuf adapter round-trip and negative cases."""

import pytest

from binance_market_data_contracts.common import PositiveQuantityString, PriceString, QuantityString
from binance_market_data_contracts.enums import (
    DeliveryMode,
    Market,
    SnapshotSource,
    Stream,
    StreamLifecycleState,
    Venue,
)
from binance_market_data_contracts.gateway import (
    EnvelopeMetadata,
    EventSubscriptionRequest,
    GatewayEventEnvelope,
    StreamSelector,
    StreamStatus,
    SubscriptionAccepted,
)
from binance_market_data_contracts.identifiers import (
    ConnectionId,
    GatewayInstanceId,
    InstanceId,
    RequestId,
    SubscriptionId,
    Symbol,
)
from binance_market_data_contracts.market_events import (
    AggTrade,
    AggTradeMetadata,
    BookTicker,
    BookTickerMetadata,
    DepthUpdate,
    DepthUpdateMetadata,
    PriceLevel,
)
from binance_market_data_contracts.snapshots import (
    ExchangeDepthSnapshot,
    GapDescriptor,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)
from binance_market_data_contracts.wire.adapters import (
    UnspecifiedEnumError,
    agg_trade_from_pb,
    agg_trade_to_pb,
    book_ticker_from_pb,
    book_ticker_to_pb,
    depth_update_from_pb,
    depth_update_to_pb,
    event_subscription_request_from_pb,
    event_subscription_request_to_pb,
    exchange_depth_snapshot_from_pb,
    exchange_depth_snapshot_to_pb,
    gateway_event_envelope_from_pb,
    gateway_event_envelope_to_pb,
    local_order_book_snapshot_from_pb,
    local_order_book_snapshot_to_pb,
    market_state_snapshot_from_pb,
    market_state_snapshot_to_pb,
    stream_status_from_pb,
    stream_status_to_pb,
    subscription_accepted_from_pb,
    subscription_accepted_to_pb,
)


def _make_depth_update_metadata(**overrides):
    kwargs = {
        "venue": Venue.BINANCE,
        "market": Market.SPOT,
        "symbol": Symbol("BTCUSDT"),
        "producer": "test",
        "producer_version": "1.0.0",
        "connection_id": ConnectionId("test-conn-1"),
        "stream": Stream.DIFF_DEPTH,
        "schema_version": "depth-update.v1",
        "exchange_event_time_ms": 1690000000000,
        "receive_time_utc_ns": 1690000000000000000,
        "receive_monotonic_ns": 1000000000,
    }
    kwargs.update(overrides)
    return DepthUpdateMetadata(**kwargs)


class TestDepthUpdateRoundtrip:
    def test_roundtrip_basic(self):
        du = DepthUpdate(
            metadata=_make_depth_update_metadata(),
            first_update_id=1001,
            final_update_id=1002,
            previous_final_update_id=1000,
            bids=(PriceLevel(price="65000.10", quantity="1.2500"),),
            asks=(PriceLevel(price="65100.00", quantity="0.5000"),),
        )

        pb = depth_update_to_pb(du)
        serialized = pb.SerializeToString()
        assert len(serialized) > 0

        pb_parsed = pb.__class__()
        pb_parsed.ParseFromString(serialized)

        du2 = depth_update_from_pb(pb_parsed)
        assert du.metadata.venue == du2.metadata.venue
        assert du.metadata.market == du2.metadata.market
        assert du.metadata.symbol == du2.metadata.symbol
        assert du.first_update_id == du2.first_update_id
        assert du.final_update_id == du2.final_update_id
        assert du.previous_final_update_id == du2.previous_final_update_id
        assert len(du.bids) == len(du2.bids)
        assert du.bids[0].price == du2.bids[0].price == "65000.10"
        assert du.bids[0].quantity == du2.bids[0].quantity == "1.2500"

    def test_roundtrip_trailing_zeros(self):
        du = DepthUpdate(
            metadata=_make_depth_update_metadata(),
            first_update_id=1,
            final_update_id=1,
            bids=(PriceLevel(price="100.00", quantity="1.2300"),),
        )
        pb = depth_update_to_pb(du)
        du2 = depth_update_from_pb(pb)
        assert du2.bids[0].price == "100.00"
        assert du2.bids[0].quantity == "1.2300"


class TestAggTradeRoundtrip:
    def test_roundtrip(self):
        at = AggTrade(
            metadata=AggTradeMetadata(
                venue=Venue.BINANCE,
                market=Market.USD_M_PERPETUAL,
                symbol=Symbol("BTCUSDT"),
                producer="test",
                producer_version="1.0",
                connection_id=ConnectionId("conn-1"),
                stream=Stream.AGG_TRADE,
                schema_version="agg-trade.v1",
            ),
            aggregate_trade_id=12345,
            price=PriceString("65000.50"),
            quantity=PositiveQuantityString("2.5000"),
            first_trade_id=100,
            last_trade_id=105,
            trade_time_ms=1690000000000,
            buyer_is_maker=False,
        )

        pb = agg_trade_to_pb(at)
        at2 = agg_trade_from_pb(pb)
        assert at.aggregate_trade_id == at2.aggregate_trade_id
        assert at.price == at2.price == "65000.50"
        assert at.quantity == at2.quantity == "2.5000"
        assert at.buyer_is_maker == at2.buyer_is_maker


class TestBookTickerRoundtrip:
    def test_roundtrip(self):
        bt = BookTicker(
            metadata=BookTickerMetadata(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol=Symbol("ETHUSDT"),
                producer="test",
                producer_version="1.0",
                connection_id=ConnectionId("conn-1"),
                stream=Stream.BOOK_TICKER,
                schema_version="book-ticker.v1",
            ),
            update_id=500,
            best_bid_price=PriceString("3500.00"),
            best_bid_quantity=QuantityString("10.5"),
            best_ask_price=PriceString("3501.00"),
            best_ask_quantity=QuantityString("5.0"),
        )

        pb = book_ticker_to_pb(bt)
        bt2 = book_ticker_from_pb(pb)
        assert bt.update_id == bt2.update_id == 500
        assert bt.best_bid_price == bt2.best_bid_price

    def test_null_update_id(self):
        bt = BookTicker(
            metadata=BookTickerMetadata(
                venue=Venue.BINANCE,
                market=Market.SPOT,
                symbol=Symbol("ETHUSDT"),
                producer="test",
                producer_version="1.0",
                connection_id=ConnectionId("conn-1"),
                stream=Stream.BOOK_TICKER,
                schema_version="book-ticker.v1",
            ),
            best_bid_price=PriceString("100.0"),
            best_bid_quantity=QuantityString("1.0"),
            best_ask_price=PriceString("101.0"),
            best_ask_quantity=QuantityString("2.0"),
        )
        pb = book_ticker_to_pb(bt)
        bt2 = book_ticker_from_pb(pb)
        assert bt2.update_id is None


class TestExchangeDepthSnapshotRoundtrip:
    def test_roundtrip(self):
        es = ExchangeDepthSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="exchange-depth-snapshot.v1",
            producer="test",
            producer_version="1.0",
            request_id=RequestId("req-1"),
            last_update_id=5000,
            bids=(PriceLevel(price="65000.00", quantity="1.0"),),
            asks=(PriceLevel(price="65100.00", quantity="2.0"),),
        )
        pb = exchange_depth_snapshot_to_pb(es)
        es2 = exchange_depth_snapshot_from_pb(pb)
        assert es.last_update_id == es2.last_update_id
        assert es.bids[0].price == es2.bids[0].price


class TestLocalOrderBookSnapshotRoundtrip:
    def test_roundtrip(self):
        ls = LocalOrderBookSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="local-order-book-snapshot.v1",
            producer="test",
            producer_version="1.0",
            source=SnapshotSource.GATEWAY_LIVE,
            last_update_id=5000,
            bids=(PriceLevel(price="65000.00", quantity="1.0"),),
            asks=(PriceLevel(price="65100.00", quantity="2.0"),),
            generated_time_utc_ns=1_690_000_000_000_000_000,
            synchronized=True,
        )
        pb = local_order_book_snapshot_to_pb(ls)
        ls2 = local_order_book_snapshot_from_pb(pb)
        assert ls.last_update_id == ls2.last_update_id
        assert ls.synchronized == ls2.synchronized

    def test_roundtrip_with_gap(self):
        gap = GapDescriptor(
            stream=Stream.DIFF_DEPTH,
            detected_at_utc_ns=1_690_000_000,
            previous_sequence=100,
            next_sequence=200,
        )
        ls = LocalOrderBookSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="local-order-book-snapshot.v1",
            producer="test",
            producer_version="1.0",
            source=SnapshotSource.GATEWAY_LIVE,
            last_update_id=5000,
            generated_time_utc_ns=1_690_000_000_000_000_000,
            synchronized=False,
            last_gap=gap,
        )
        pb = local_order_book_snapshot_to_pb(ls)
        ls2 = local_order_book_snapshot_from_pb(pb)
        assert ls2.last_gap is not None
        assert ls2.last_gap.previous_sequence == 100
        assert ls2.last_gap.next_sequence == 200


class TestMarketStateSnapshotRoundtrip:
    def test_roundtrip(self):
        ms = MarketStateSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="market-state-snapshot.v1",
            producer="test",
            producer_version="1.0",
            best_bid_price=PriceString("65000.00"),
            best_ask_price=PriceString("65100.00"),
            generated_time_utc_ns=1_690_000_000_000_000_000,
            source_book_update_id=5000,
        )
        pb = market_state_snapshot_to_pb(ms)
        ms2 = market_state_snapshot_from_pb(pb)
        assert ms2.best_bid_price == "65000.00"
        assert ms2.source_book_update_id == 5000

    def test_optional_none(self):
        ms = MarketStateSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="market-state-snapshot.v1",
            producer="test",
            producer_version="1.0",
            generated_time_utc_ns=1_690_000_000_000_000_000,
        )
        pb = market_state_snapshot_to_pb(ms)
        ms2 = market_state_snapshot_from_pb(pb)
        assert ms2.best_bid_price is None
        assert ms2.source_book_update_id is None


class TestGatewayRoundtrip:
    def test_event_subscription_request(self):
        req = EventSubscriptionRequest(
            request_id=RequestId("evt-req-1"),
            schema_version="event-subscription-request.v1",
            selectors=(
                StreamSelector(
                    venue=Venue.BINANCE,
                    market=Market.SPOT,
                    symbol=Symbol("BTCUSDT"),
                    stream=Stream.DIFF_DEPTH,
                ),
            ),
            delivery_mode=DeliveryMode.CONTIGUOUS_EVENTS,
            supported_payload_schema_versions=("depth-update.v1", "agg-trade.v1"),
        )
        pb = event_subscription_request_to_pb(req)
        req2 = event_subscription_request_from_pb(pb)
        assert req2.request_id == "evt-req-1"
        assert len(req2.selectors) == 1

    def test_subscription_accepted(self):
        sa = SubscriptionAccepted(
            request_id=RequestId("r-1"),
            subscription_id=SubscriptionId("sub-1"),
            schema_version="subscription-accepted.v1",
            gateway_instance_id=InstanceId("gw-1"),
            accepted_time_utc_ns=1_690_000_000,
            negotiated_payload_schema_versions=("depth-update.v1",),
        )
        pb = subscription_accepted_to_pb(sa)
        sa2 = subscription_accepted_from_pb(pb)
        assert sa2.subscription_id == "sub-1"
        assert sa2.gateway_instance_id == "gw-1"

    def test_envelope_with_depth_update(self):
        du = DepthUpdate(
            metadata=_make_depth_update_metadata(),
            first_update_id=1,
            final_update_id=1,
        )
        em = EnvelopeMetadata(
            gateway_instance_id=GatewayInstanceId("gw-1"),
            subscription_id=SubscriptionId("sub-1"),
            connection_generation=1,
            session_sequence=1,
            publish_time_utc_ns=1_690_000_000,
            protocol_version="gateway-stream.v1",
        )
        env = GatewayEventEnvelope(envelope_metadata=em, depth_update=du)

        pb = gateway_event_envelope_to_pb(env)
        env2 = gateway_event_envelope_from_pb(pb)
        assert env2.depth_update is not None
        assert env2.depth_update.first_update_id == 1
        assert env2.envelope_metadata.session_sequence == 1

    def test_envelope_connection_generation_absence_roundtrip(self):
        em = EnvelopeMetadata(
            gateway_instance_id=GatewayInstanceId("gw-1"),
            subscription_id=SubscriptionId("sub-1"),
            connection_generation=None,
            session_sequence=1,
            publish_time_utc_ns=1_690_000_000,
            protocol_version="gateway-stream.v1",
        )
        status = StreamStatus(
            schema_version="stream-status.v1",
            subscription_id=SubscriptionId("sub-1"),
            state=StreamLifecycleState.LIVE,
            observed_time_utc_ns=1_690_000_000,
        )
        env = GatewayEventEnvelope(envelope_metadata=em, stream_status=status)

        pb = gateway_event_envelope_to_pb(env)
        assert not pb.envelope_metadata.HasField("connection_generation")
        env2 = gateway_event_envelope_from_pb(pb)
        assert env2.envelope_metadata.connection_generation is None

    def test_stream_status(self):
        ss = StreamStatus(
            schema_version="stream-status.v1",
            subscription_id=SubscriptionId("sub-1"),
            state=StreamLifecycleState.LIVE,
            observed_time_utc_ns=1_690_000_000,
        )
        pb = stream_status_to_pb(ss)
        ss2 = stream_status_from_pb(pb)
        assert ss2.state == StreamLifecycleState.LIVE
        assert ss2.subscription_id == "sub-1"


class TestNegativeAdapters:
    def test_unspecified_venue_rejected(self):
        from binance_market_data.common.v1 import enums_pb2 as pb_enums
        from binance_market_data_contracts.wire.adapters import _venue_from_pb

        with pytest.raises(UnspecifiedEnumError, match="Venue"):
            _venue_from_pb(pb_enums.Venue.VENUE_UNSPECIFIED)

    def test_unspecified_market_rejected(self):
        from binance_market_data.common.v1 import enums_pb2 as pb_enums
        from binance_market_data_contracts.wire.adapters import _market_from_pb

        with pytest.raises(UnspecifiedEnumError, match="Market"):
            _market_from_pb(pb_enums.Market.MARKET_UNSPECIFIED)

    def test_unspecified_stream_rejected(self):
        from binance_market_data.common.v1 import enums_pb2 as pb_enums
        from binance_market_data_contracts.wire.adapters import _stream_from_pb

        with pytest.raises(UnspecifiedEnumError, match="Stream"):
            _stream_from_pb(pb_enums.Stream.STREAM_UNSPECIFIED)

    @pytest.mark.parametrize(
        ("enum_name", "mapper"),
        [
            (
                "Venue",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_venue_from_pb"]
                )._venue_from_pb(999, "TestContract.venue"),
            ),
            (
                "Market",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_market_from_pb"]
                )._market_from_pb(999, "TestContract.market"),
            ),
            (
                "Stream",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_stream_from_pb"]
                )._stream_from_pb(999, "TestContract.stream"),
            ),
            (
                "QualityFlag",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_quality_from_pb"]
                )._quality_from_pb([999], "TestContract.quality_flags"),
            ),
            (
                "ReasonCode",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_reason_code_from_pb"]
                )._reason_code_from_pb(999, "TestContract.reason_code"),
            ),
            (
                "ConnectionState",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_connection_state_from_pb"]
                )._connection_state_from_pb(999, "TestContract.connection_state"),
            ),
            (
                "ResyncState",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_resync_state_from_pb"]
                )._resync_state_from_pb(999, "TestContract.resync_state"),
            ),
            (
                "SnapshotSource",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_snapshot_source_from_pb"]
                )._snapshot_source_from_pb(999, "TestContract.source"),
            ),
            (
                "DeliveryMode",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_delivery_mode_from_pb"]
                )._delivery_mode_from_pb(999, "TestContract.delivery_mode"),
            ),
            (
                "InitialSnapshotMode",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_initial_snapshot_mode_from_pb"]
                )._initial_snapshot_mode_from_pb(999, "TestContract.initial_snapshot_mode"),
            ),
            (
                "ConsumerGapReason",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_consumer_gap_reason_from_pb"]
                )._consumer_gap_reason_from_pb(999, "TestContract.reason"),
            ),
            (
                "RecoveryAction",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_recovery_action_from_pb"]
                )._recovery_action_from_pb(999, "TestContract.recovery_action"),
            ),
            (
                "StreamLifecycleState",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_stream_lifecycle_state_from_pb"]
                )._stream_lifecycle_state_from_pb(999, "TestContract.state"),
            ),
            (
                "HealthState",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_health_state_from_pb"]
                )._health_state_from_pb(999, "TestContract.health"),
            ),
            (
                "TelemetryType",
                lambda: __import__(
                    "binance_market_data_contracts.wire.adapters", fromlist=["_telemetry_type_from_pb"]
                )._telemetry_type_from_pb(999, "TestContract.telemetry_type"),
            ),
        ],
    )
    def test_unknown_enum_values_are_normalized(self, enum_name, mapper):
        from binance_market_data_contracts.wire.adapters import UnknownEnumValueError

        with pytest.raises(UnknownEnumValueError) as exc_info:
            mapper()
        message = str(exc_info.value)
        assert enum_name in message
        assert "999" in message
        assert "TestContract." in message

    def test_wrong_schema_version_rejected(self):
        from binance_market_data.common.v1 import enums_pb2
        from binance_market_data.projection.v1 import snapshots_pb2
        from binance_market_data_contracts.wire.adapters import (
            UnexpectedWireValueError,
            market_state_snapshot_from_pb,
        )

        ms = snapshots_pb2.MarketStateSnapshot()
        ms.venue = enums_pb2.Venue.VENUE_BINANCE
        ms.market = enums_pb2.Market.MARKET_SPOT
        ms.symbol = "BTCUSDT"
        ms.schema_version = "wrong-version"
        ms.producer = "test"
        ms.producer_version = "1.0"
        ms.generated_time_utc_ns = 1000
        ms.source_book_update_id = 1

        with pytest.raises(UnexpectedWireValueError):
            market_state_snapshot_from_pb(ms)
