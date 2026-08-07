#include <cstdlib>
#include <iostream>
#include <string>
#include <string_view>

#include "binance_market_data/contracts_metadata.hpp"
#include "binance_market_data/market/v1/market_events.pb.h"
#include "binance_market_data/projection/v1/snapshots.pb.h"

std::string serialize_depth();
std::string serialize_snapshot();

namespace {

bool check(bool condition, std::string_view description) {
  if (!condition) {
    std::cerr << "consumer check failed: " << description << '\n';
    return false;
  }
  return true;
}

}  // namespace

int main() {
  const std::string depth_fixture =
      "\x10\xe9\x07\x18\xea\x07\x20\xe8\x07";
  const std::string snapshot_fixture =
      "\x22\x1c"
      "local-order-book-snapshot.v1"
      "\x58\x14\x60\x80\x84\xdc\x8c\xbe\xc1\x85\xba\x17";
  binance_market_data::market::v1::DepthUpdate depth;
  const std::string serialized_depth = serialize_depth();
  if (!check(serialized_depth == depth_fixture, "consumer_a fixed fixture") ||
      !check(depth.ParseFromString(depth_fixture), "DepthUpdate parse") ||
      !check(depth.has_previous_final_update_id(), "DepthUpdate optional presence")) {
    return EXIT_FAILURE;
  }
  binance_market_data::projection::v1::LocalOrderBookSnapshot snapshot;
  const std::string serialized_snapshot = serialize_snapshot();
  if (!check(serialized_snapshot == snapshot_fixture, "consumer_b fixed fixture") ||
      !check(snapshot.ParseFromString(snapshot_fixture), "LocalOrderBookSnapshot parse") ||
      !check(snapshot.has_depth_limit(), "LocalOrderBookSnapshot optional presence") ||
      !check(binance_market_data::contracts::schema_fingerprint.size() == 64,
             "installed metadata fingerprint")) {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
