#include <string>

#include "binance_market_data/market/v1/market_events.pb.h"

std::string projection_adapter_like_serialize_depth() {
  binance_market_data::market::v1::DepthUpdate depth;
  depth.set_first_update_id(10);
  depth.set_final_update_id(11);
  depth.set_previous_final_update_id(9);
  return depth.SerializeAsString();
}
