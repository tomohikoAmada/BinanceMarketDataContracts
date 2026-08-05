"""Test wire round-trip: Pydantic → Proto → serialize → parse → Pydantic."""

from binance_market_data_contracts.common import PriceString, QuantityString
from binance_market_data_contracts.enums import (
    ConsumerGapReason,
    DeliveryMode,
    Market,
    RecoveryAction,
    SnapshotSource,
    Stream,
    Venue,
)
from binance_market_data_contracts.gateway import (
    ConsumerGapNotice,
    EnvelopeMetadata,
    EventSubscriptionRequest,
    GatewayEventEnvelope,
    GatewayStatusSnapshot,
    MarketStateStreamItem,
    OrderBookStreamItem,
    StreamSelector,
)
from binance_market_data_contracts.identifiers import ConnectionId, GatewayInstanceId, RequestId, SubscriptionId, Symbol
from binance_market_data_contracts.market_events import (
    AggTrade,
    AggTradeMetadata,
    BookTicker,
    BookTickerMetadata,
    DepthUpdate,
    DepthUpdateMetadata,
)
from binance_market_data_contracts.snapshots import (
    ExchangeDepthSnapshot,
    LocalOrderBookSnapshot,
    MarketStateSnapshot,
)
from binance_market_data_contracts.wire.adapters import (
    agg_trade_from_pb,
    agg_trade_to_pb,
    book_ticker_from_pb,
    book_ticker_to_pb,
    consumer_gap_notice_from_pb,
    consumer_gap_notice_to_pb,
    depth_update_from_pb,
    depth_update_to_pb,
    event_subscription_request_from_pb,
    event_subscription_request_to_pb,
    exchange_depth_snapshot_from_pb,
    exchange_depth_snapshot_to_pb,
    gateway_event_envelope_from_pb,
    gateway_event_envelope_to_pb,
    gateway_status_snapshot_from_pb,
    gateway_status_snapshot_to_pb,
    local_order_book_snapshot_from_pb,
    local_order_book_snapshot_to_pb,
    market_state_snapshot_from_pb,
    market_state_snapshot_to_pb,
    market_state_stream_item_from_pb,
    market_state_stream_item_to_pb,
    order_book_stream_item_from_pb,
    order_book_stream_item_to_pb,
)


def _meta(**kw):
    defaults = {
        "venue": Venue.BINANCE,
        "market": Market.SPOT,
        "symbol": Symbol("BTCUSDT"),
        "producer": "test",
        "producer_version": "1.0",
        "connection_id": ConnectionId("c-1"),
        "stream": Stream.DIFF_DEPTH,
        "schema_version": "depth-update.v1",
    }
    defaults.update(kw)
    return DepthUpdateMetadata(**defaults)


def _agg_meta(**kw):
    defaults = {
        "venue": Venue.BINANCE,
        "market": Market.SPOT,
        "symbol": Symbol("BTCUSDT"),
        "producer": "test",
        "producer_version": "1.0",
        "connection_id": ConnectionId("c-1"),
        "schema_version": "agg-trade.v1",
    }
    defaults.update(kw)
    return AggTradeMetadata(**defaults, stream=Stream.AGG_TRADE)


def _bt_meta(**kw):
    defaults = {
        "venue": Venue.BINANCE,
        "market": Market.SPOT,
        "symbol": Symbol("BTCUSDT"),
        "producer": "test",
        "producer_version": "1.0",
        "connection_id": ConnectionId("c-1"),
        "schema_version": "book-ticker.v1",
    }
    defaults.update(kw)
    return BookTickerMetadata(**defaults, stream=Stream.BOOK_TICKER)


def _pb_roundtrip(py_to_pb_fn, pb_to_py_fn, py_obj, compare_attrs=None):
    pb = py_to_pb_fn(py_obj)
    serialized = pb.SerializeToString()
    assert len(serialized) > 0, f"Serialized empty for {type(py_obj).__name__}"

    pb2 = pb.__class__()
    pb2.ParseFromString(serialized)

    py2 = pb_to_py_fn(pb2)

    # Basic structural equality
    for attr in compare_attrs or []:
        v1 = getattr(py_obj, attr)
        v2 = getattr(py2, attr)
        assert v1 == v2, f"Roundtrip mismatch on {attr}: {v1!r} != {v2!r}"

    return py2


class TestWireRoundtrips:
    def test_depth_update(self):
        du = DepthUpdate(metadata=_meta(), first_update_id=1001, final_update_id=1002)
        _pb_roundtrip(
            depth_update_to_pb,
            depth_update_from_pb,
            du,
            ["first_update_id", "final_update_id"],
        )

    def test_agg_trade(self):
        at = AggTrade(
            metadata=_agg_meta(),
            aggregate_trade_id=12345,
            price=PriceString("65000.00"),
            quantity=QuantityString("2.5"),
            first_trade_id=100,
            last_trade_id=105,
            trade_time_ms=1690000000,
            buyer_is_maker=False,
        )
        _pb_roundtrip(agg_trade_to_pb, agg_trade_from_pb, at, ["aggregate_trade_id"])

    def test_book_ticker(self):
        bt = BookTicker(
            metadata=_bt_meta(),
            update_id=500,
            best_bid_price=PriceString("65000.00"),
            best_bid_quantity=QuantityString("1.0"),
            best_ask_price=PriceString("65100.00"),
            best_ask_quantity=QuantityString("2.0"),
        )
        _pb_roundtrip(book_ticker_to_pb, book_ticker_from_pb, bt, ["update_id"])

    def test_exchange_depth_snapshot(self):
        es = ExchangeDepthSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="exchange-depth-snapshot.v1",
            producer="test",
            producer_version="1.0",
            request_id=RequestId("r-1"),
            last_update_id=5000,
        )
        _pb_roundtrip(exchange_depth_snapshot_to_pb, exchange_depth_snapshot_from_pb, es, ["last_update_id"])

    def test_local_order_book_snapshot(self):
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
            synchronized=True,
        )
        _pb_roundtrip(local_order_book_snapshot_to_pb, local_order_book_snapshot_from_pb, ls, ["last_update_id"])

    def test_market_state_snapshot(self):
        ms = MarketStateSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="market-state-snapshot.v1",
            producer="test",
            producer_version="1.0",
            best_bid_price=PriceString("65000.00"),
            generated_time_utc_ns=1_690_000_000_000_000_000,
            source_book_update_id=5000,
        )
        ms2 = _pb_roundtrip(market_state_snapshot_to_pb, market_state_snapshot_from_pb, ms, [])
        assert ms2.best_bid_price == "65000.00"
        assert ms2.source_book_update_id == 5000

    def test_envelope_to_wire_and_back(self):
        du = DepthUpdate(metadata=_meta(), first_update_id=100, final_update_id=100)
        em = EnvelopeMetadata(
            gateway_instance_id=GatewayInstanceId("gw-x"),
            subscription_id=SubscriptionId("s-1"),
            connection_generation=1,
            session_sequence=5,
            publish_time_utc_ns=1_690_000_000,
            protocol_version="gateway-stream.v1",
        )
        env = GatewayEventEnvelope(envelope_metadata=em, depth_update=du)
        env2 = _pb_roundtrip(gateway_event_envelope_to_pb, gateway_event_envelope_from_pb, env, [])
        assert env2.depth_update is not None
        assert env2.depth_update.first_update_id == 100
        assert env2.envelope_metadata.session_sequence == 5

    def test_order_book_stream_item(self):
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
            synchronized=True,
        )
        em = EnvelopeMetadata(
            gateway_instance_id=GatewayInstanceId("gw-x"),
            subscription_id=SubscriptionId("s-1"),
            connection_generation=1,
            session_sequence=2,
            publish_time_utc_ns=1_690_000_000,
            protocol_version="gateway-stream.v1",
        )
        item = OrderBookStreamItem(envelope_metadata=em, snapshot=ls)
        item2 = _pb_roundtrip(order_book_stream_item_to_pb, order_book_stream_item_from_pb, item, [])
        assert item2.snapshot is not None
        assert item2.snapshot.last_update_id == 5000
        assert item2.envelope_metadata.session_sequence == 2

    def test_market_state_stream_item(self):
        ms = MarketStateSnapshot(
            venue=Venue.BINANCE,
            market=Market.SPOT,
            symbol=Symbol("BTCUSDT"),
            schema_version="market-state-snapshot.v1",
            producer="test",
            producer_version="1.0",
            generated_time_utc_ns=1_690_000_000_000_000_000,
        )
        em = EnvelopeMetadata(
            gateway_instance_id=GatewayInstanceId("gw-x"),
            subscription_id=SubscriptionId("s-1"),
            connection_generation=1,
            session_sequence=3,
            publish_time_utc_ns=1_690_000_000,
            protocol_version="gateway-stream.v1",
        )
        item = MarketStateStreamItem(envelope_metadata=em, market_state=ms)
        item2 = _pb_roundtrip(market_state_stream_item_to_pb, market_state_stream_item_from_pb, item, [])
        assert item2.market_state is not None
        assert item2.envelope_metadata.session_sequence == 3

    def test_consumer_gap_notice(self):
        cgn = ConsumerGapNotice(
            schema_version="consumer-gap-notice.v1",
            subscription_id=SubscriptionId("s-1"),
            detected_time_utc_ns=1_690_000_000,
            reason=ConsumerGapReason.SLOW_CONSUMER,
            recovery_action=RecoveryAction.RESUBSCRIBE,
        )
        cgn2 = _pb_roundtrip(consumer_gap_notice_to_pb, consumer_gap_notice_from_pb, cgn, [])
        assert cgn2.reason == ConsumerGapReason.SLOW_CONSUMER
        assert cgn2.recovery_action == RecoveryAction.RESUBSCRIBE

    def test_event_subscription_request(self):
        req = EventSubscriptionRequest(
            request_id=RequestId("r-1"),
            schema_version="event-subscription-request.v1",
            selectors=(
                StreamSelector(
                    venue=Venue.BINANCE, market=Market.SPOT, symbol=Symbol("BTCUSDT"), stream=Stream.DIFF_DEPTH
                ),
            ),
            delivery_mode=DeliveryMode.CONTIGUOUS_EVENTS,
            supported_payload_schema_versions=("depth-update.v1",),
        )
        req2 = _pb_roundtrip(event_subscription_request_to_pb, event_subscription_request_from_pb, req, [])
        assert len(req2.selectors) == 1
        assert req2.selectors[0].symbol == "BTCUSDT"

    def test_gateway_status_snapshot(self):
        gs = GatewayStatusSnapshot(
            schema_version="gateway-status-snapshot.v1",
            gateway_instance_id=GatewayInstanceId("gw-1"),
            observed_time_utc_ns=1_690_000_000,
            uptime_seconds=3600,
            total_active_subscriptions=5,
        )
        gs2 = _pb_roundtrip(gateway_status_snapshot_to_pb, gateway_status_snapshot_from_pb, gs, [])
        assert gs2.uptime_seconds == 3600
        assert gs2.total_active_subscriptions == 5
