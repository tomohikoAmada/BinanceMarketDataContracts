#include <cstdlib>
#include <iostream>
#include <string>
#include <string_view>

#include "binance_market_data/contracts_metadata.hpp"
#include "binance_market_data/gateway/v1/gateway_service.grpc.pb.h"
#include "binance_market_data/market/v1/market_events.pb.h"
#include "binance_market_data/projection/v1/snapshots.pb.h"

namespace {

bool check(bool condition, std::string_view description) {
  if (!condition) {
    std::cerr << "test_package check failed: " << description << '\n';
    return false;
  }
  return true;
}

}  // namespace

int main() {
  binance_market_data::gateway::v1::BinanceMarketDataGatewayService::Service service;
  if (!check(static_cast<grpc::Service*>(&service) != nullptr, "Gateway gRPC service surface")) {
    return EXIT_FAILURE;
  }

  binance_market_data::market::v1::DepthUpdate depth;
  depth.set_first_update_id(10);
  depth.set_final_update_id(11);
  depth.set_previous_final_update_id(9);
  std::string bytes = depth.SerializeAsString();
  binance_market_data::market::v1::DepthUpdate parsed;
  if (!check(parsed.ParseFromString(bytes), "DepthUpdate parse") ||
      !check(parsed.has_previous_final_update_id(), "DepthUpdate optional presence") ||
      !check(parsed.SerializeAsString() == bytes, "DepthUpdate round trip")) {
    return EXIT_FAILURE;
  }

  binance_market_data::market::v1::ExchangeDepthSnapshot exchange;
  exchange.set_last_update_id(11);
  const std::string exchange_bytes = exchange.SerializeAsString();
  binance_market_data::market::v1::ExchangeDepthSnapshot parsed_exchange;
  if (!check(parsed_exchange.ParseFromString(exchange_bytes), "ExchangeDepthSnapshot parse") ||
      !check(parsed_exchange.SerializeAsString() == exchange_bytes, "ExchangeDepthSnapshot round trip")) {
    return EXIT_FAILURE;
  }

  binance_market_data::projection::v1::LocalOrderBookSnapshot local;
  local.set_depth_limit(20);
  const std::string local_bytes = local.SerializeAsString();
  binance_market_data::projection::v1::LocalOrderBookSnapshot parsed_local;
  if (!check(parsed_local.ParseFromString(local_bytes), "LocalOrderBookSnapshot parse") ||
      !check(parsed_local.has_depth_limit(), "LocalOrderBookSnapshot optional presence") ||
      !check(parsed_local.SerializeAsString() == local_bytes, "LocalOrderBookSnapshot round trip")) {
    return EXIT_FAILURE;
  }

  using namespace binance_market_data::contracts;
  if (!check(schema_baseline == "01d76a41929f36d89573159f5f458f9f1e378ada", "schema baseline") ||
      !check(schema_fingerprint == "33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0",
             "schema fingerprint") ||
      !check(schema_fingerprint_algorithm_version == 1, "fingerprint algorithm") ||
      !check(package_version == "0.1.0", "package version") ||
      !check(package_revision == "NOT_FORMALLY_ASSIGNED", "package revision status") ||
      !check(protoc_version == "libprotoc 33.5", "protoc version") ||
      !check(cpp_generator_options == "cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API",
             "generator options") ||
      !check(protobuf_runtime_version == "6.33.5", "runtime version") ||
      !check(protobuf_runtime_rrev == "ca5ff466767b31a1b496ec60247e105c", "runtime RREV") ||
      !check(protobuf_runtime_compatibility == "exactly 6.33.5 for this implementation candidate",
             "runtime compatibility") ||
      !check(protobuf_runtime_flavor == "full", "runtime flavor") ||
      !check(protobuf_runtime_linkage == "static" || protobuf_runtime_linkage == "shared",
             "runtime linkage") ||
      !check(!contracts_source_revision.empty(), "Contracts source revision")) {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
