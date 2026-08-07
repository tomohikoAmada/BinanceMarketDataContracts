#include "binance_market_data/projection/v1/snapshots.pb.h"

std::string serialize_snapshot() {
  binance_market_data::projection::v1::LocalOrderBookSnapshot value;
  value.set_schema_version("local-order-book-snapshot.v1");
  value.set_generated_time_utc_ns(1690000000456000000ULL);
  value.set_depth_limit(20);
  return value.SerializeAsString();
}

