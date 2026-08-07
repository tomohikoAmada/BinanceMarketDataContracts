#include <array>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <string>
#include <string_view>

#include "binance_market_data/common/v1/enums.pb.h"
#include "binance_market_data/contracts_metadata.hpp"
#include "binance_market_data/market/v1/market_events.pb.h"
#include "binance_market_data/projection/v1/snapshots.pb.h"

namespace common = binance_market_data::common::v1;
namespace market = binance_market_data::market::v1;
namespace projection = binance_market_data::projection::v1;

void require(bool condition, std::string_view description, int line) {
  if (!condition) {
    std::cerr << "semantic check failed at line " << line << ": " << description << '\n';
    std::exit(EXIT_FAILURE);
  }
}

#define REQUIRE(condition) require(static_cast<bool>(condition), #condition, __LINE__)

std::string bytes_from_hex(std::string_view hex) {
  REQUIRE(hex.size() % 2 == 0);
  std::string bytes;
  bytes.reserve(hex.size() / 2);
  auto nibble = [](char value) -> unsigned char {
    if (value >= '0' && value <= '9') return static_cast<unsigned char>(value - '0');
    if (value >= 'a' && value <= 'f') return static_cast<unsigned char>(value - 'a' + 10);
    REQUIRE(false && "fixture contains non-hex input");
    return 0;
  };
  for (std::size_t index = 0; index < hex.size(); index += 2) {
    bytes.push_back(static_cast<char>((nibble(hex[index]) << 4) | nibble(hex[index + 1])));
  }
  return bytes;
}

template <typename Message>
Message round_trip(const Message& original) {
  std::string bytes;
  REQUIRE(original.SerializeToString(&bytes));
  Message parsed;
  REQUIRE(parsed.ParseFromString(bytes));
  REQUIRE(parsed.SerializeAsString() == bytes);
  return parsed;
}

int main() {
  REQUIRE(common::VENUE_BINANCE == 1);
  REQUIRE(common::MARKET_SPOT == 1);
  REQUIRE(common::STREAM_DIFF_DEPTH == 1);

  market::DepthUpdate depth;
  auto* metadata = depth.mutable_metadata();
  metadata->set_venue(common::VENUE_BINANCE);
  metadata->set_market(common::MARKET_SPOT);
  metadata->set_symbol("BTCUSDT");
  metadata->set_stream(common::STREAM_DIFF_DEPTH);
  metadata->set_schema_version("depth-update.v1");
  metadata->set_exchange_event_time_ms(1690000000123ULL);
  depth.set_first_update_id(1001);
  depth.set_final_update_id(1002);
  REQUIRE(!depth.has_previous_final_update_id());
  depth.set_previous_final_update_id(1000);
  auto* bid = depth.add_bids();
  bid->set_price("65000.10");
  bid->set_quantity("1.2500");
  auto parsed_depth = round_trip(depth);
  REQUIRE(parsed_depth.has_previous_final_update_id());
  REQUIRE(parsed_depth.previous_final_update_id() == 1000);
  REQUIRE(parsed_depth.bids(0).price() == "65000.10");
  const auto depth_fixture = bytes_from_hex(
      "0a27080110011a07425443555344543801420f64657074682d7570646174652e763148"
      "fb88e6de973110e90718ea0720e8072a120a0836353030302e31301206312e32353030");
  REQUIRE(depth.SerializeAsString() == depth_fixture);
  market::DepthUpdate fixture_depth;
  REQUIRE(fixture_depth.ParseFromString(depth_fixture));
  REQUIRE(fixture_depth.SerializeAsString() == depth.SerializeAsString());

  market::ExchangeDepthSnapshot exchange;
  exchange.set_venue(common::VENUE_BINANCE);
  exchange.set_market(common::MARKET_SPOT);
  exchange.set_symbol("BTCUSDT");
  exchange.set_schema_version("exchange-depth-snapshot.v1");
  exchange.set_last_update_id(4242);
  exchange.mutable_bids()->Add()->CopyFrom(*bid);
  REQUIRE(!exchange.has_exchange_transaction_time_ms());
  exchange.set_exchange_transaction_time_ms(1690000000456ULL);
  auto parsed_exchange = round_trip(exchange);
  REQUIRE(parsed_exchange.has_exchange_transaction_time_ms());
  REQUIRE(parsed_exchange.last_update_id() == 4242);
  const auto exchange_fixture = bytes_from_hex(
      "080110011a0742544355534454221a65786368616e67652d64657074682d736e617073"
      "686f742e76314092214a120a0836353030302e31301206312e3235303058c88be6de9731");
  REQUIRE(exchange.SerializeAsString() == exchange_fixture);
  market::ExchangeDepthSnapshot fixture_exchange;
  REQUIRE(fixture_exchange.ParseFromString(exchange_fixture));
  REQUIRE(fixture_exchange.SerializeAsString() == exchange.SerializeAsString());

  projection::LocalOrderBookSnapshot local;
  local.set_venue(common::VENUE_BINANCE);
  local.set_market(common::MARKET_SPOT);
  local.set_symbol("BTCUSDT");
  local.set_schema_version("local-order-book-snapshot.v1");
  local.set_source(common::SNAPSHOT_SOURCE_GATEWAY_LIVE);
  local.set_last_update_id(4242);
  local.set_generated_time_utc_ns(1690000000456000000ULL);
  local.set_synchronized(true);
  local.mutable_bids()->Add()->CopyFrom(*bid);
  REQUIRE(!local.has_depth_limit());
  local.set_depth_limit(20);
  auto parsed_local = round_trip(local);
  REQUIRE(parsed_local.has_depth_limit());
  REQUIRE(parsed_local.depth_limit() == 20);
  REQUIRE(parsed_local.synchronized());
  const auto local_fixture = bytes_from_hex(
      "080110011a0742544355534454221c6c6f63616c2d6f726465722d626f6f6b2d736e"
      "617073686f742e763138014092214a120a0836353030302e31301206312e3235303058"
      "14608084dc8cbec185ba177001");
  REQUIRE(local.SerializeAsString() == local_fixture);
  projection::LocalOrderBookSnapshot fixture_local;
  REQUIRE(fixture_local.ParseFromString(local_fixture));
  REQUIRE(fixture_local.SerializeAsString() == local.SerializeAsString());

  using namespace binance_market_data::contracts;
  static_assert(schema_fingerprint_algorithm_version == 1);
  REQUIRE(schema_baseline == "01d76a41929f36d89573159f5f458f9f1e378ada");
  REQUIRE(schema_fingerprint.size() == 64);
  REQUIRE(package_version == "0.1.0");
  REQUIRE(package_revision == "NOT_FORMALLY_ASSIGNED");
  REQUIRE(protoc_version == "libprotoc 33.5");
  REQUIRE(cpp_generator_options == "cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API");
  REQUIRE(protobuf_runtime_version == "6.33.5");
  REQUIRE(protobuf_runtime_rrev == "ca5ff466767b31a1b496ec60247e105c");
  REQUIRE(protobuf_runtime_compatibility == "exactly 6.33.5 for this implementation candidate");
  REQUIRE(protobuf_runtime_flavor == "full");
  REQUIRE(protobuf_runtime_linkage == "static" || protobuf_runtime_linkage == "shared");
  REQUIRE(!contracts_source_revision.empty());
  return 0;
}
