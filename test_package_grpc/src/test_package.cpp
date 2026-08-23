#include <concepts>
#include <cstdlib>
#include <memory>
#include <string>
#include <utility>

#include "binance_market_data/gateway/v1/gateway_service.grpc.pb.h"
#include "binance_market_data/market/v1/market_events.pb.h"

std::string projection_adapter_like_serialize_depth();

int main() {
  using Service =
      binance_market_data::gateway::v1::BinanceMarketDataGatewayService;
  static_assert(std::derived_from<Service::Service, grpc::Service>);
  static_assert(std::same_as<
                decltype(Service::NewStub(
                    std::declval<const std::shared_ptr<grpc::ChannelInterface>&>())),
                std::unique_ptr<Service::Stub>>);
  [[maybe_unused]] Service::Service service;

  binance_market_data::market::v1::DepthUpdate depth;
  if (!depth.ParseFromString(projection_adapter_like_serialize_depth()) ||
      depth.first_update_id() != 10 || depth.final_update_id() != 11 ||
      !depth.has_previous_final_update_id()) {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
