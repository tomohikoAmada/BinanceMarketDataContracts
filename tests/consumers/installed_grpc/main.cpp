#include <cstdlib>

#include "binance_market_data/gateway/v1/gateway_service.grpc.pb.h"

int main() {
  binance_market_data::gateway::v1::BinanceMarketDataGatewayService::Service service;
  return static_cast<grpc::Service*>(&service) != nullptr ? EXIT_SUCCESS : EXIT_FAILURE;
}
