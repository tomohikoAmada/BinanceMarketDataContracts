#include <cassert>
#include <string>

#include "binance_market_data/contracts_metadata.hpp"
#include "binance_market_data/market/v1/market_events.pb.h"
#include "binance_market_data/projection/v1/snapshots.pb.h"

int main() {
  binance_market_data::market::v1::DepthUpdate depth;
  depth.set_first_update_id(10);
  depth.set_final_update_id(11);
  depth.set_previous_final_update_id(9);
  std::string bytes = depth.SerializeAsString();
  binance_market_data::market::v1::DepthUpdate parsed;
  assert(parsed.ParseFromString(bytes));
  assert(parsed.has_previous_final_update_id());

  binance_market_data::market::v1::ExchangeDepthSnapshot exchange;
  exchange.set_last_update_id(11);
  assert(exchange.ParseFromString(exchange.SerializeAsString()));

  binance_market_data::projection::v1::LocalOrderBookSnapshot local;
  local.set_depth_limit(20);
  assert(local.ParseFromString(local.SerializeAsString()));
  assert(local.has_depth_limit());

  using namespace binance_market_data::contracts;
  assert(schema_baseline == "01d76a41929f36d89573159f5f458f9f1e378ada");
  assert(schema_fingerprint == "33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0");
  assert(schema_fingerprint_algorithm_version == 1);
  assert(package_version == "0.1.0");
  assert(package_revision == "NOT_FORMALLY_ASSIGNED");
  assert(protoc_version == "libprotoc 33.5");
  assert(cpp_generator_options == "cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API");
  assert(protobuf_runtime_version == "6.33.5");
  assert(protobuf_runtime_rrev == "ca5ff466767b31a1b496ec60247e105c");
  assert(protobuf_runtime_compatibility == "exactly 6.33.5 for this implementation candidate");
  assert(protobuf_runtime_linkage == "full libprotobuf");
  assert(!contracts_source_revision.empty());
  return 0;
}
