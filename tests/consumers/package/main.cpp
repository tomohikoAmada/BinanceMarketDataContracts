#include <cassert>
#include <string>

#include "binance_market_data/contracts_metadata.hpp"
#include "binance_market_data/market/v1/market_events.pb.h"
#include "binance_market_data/projection/v1/snapshots.pb.h"

std::string serialize_depth();
std::string serialize_snapshot();

int main() {
  const std::string depth_fixture =
      "\x10\xe9\x07\x18\xea\x07\x20\xe8\x07";
  const std::string snapshot_fixture =
      "\x22\x1c"
      "local-order-book-snapshot.v1"
      "\x58\x14\x60\x80\x84\xdc\x8c\xbe\xc1\x85\xba\x17";
  binance_market_data::market::v1::DepthUpdate depth;
  assert(serialize_depth() == depth_fixture);
  assert(depth.ParseFromString(depth_fixture));
  assert(depth.has_previous_final_update_id());
  binance_market_data::projection::v1::LocalOrderBookSnapshot snapshot;
  assert(serialize_snapshot() == snapshot_fixture);
  assert(snapshot.ParseFromString(snapshot_fixture));
  assert(snapshot.has_depth_limit());
  assert(binance_market_data::contracts::schema_fingerprint.size() == 64);
  return 0;
}
