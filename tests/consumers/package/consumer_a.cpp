#include "binance_market_data/market/v1/market_events.pb.h"

std::string serialize_depth() {
  binance_market_data::market::v1::DepthUpdate value;
  value.set_first_update_id(1001);
  value.set_final_update_id(1002);
  value.set_previous_final_update_id(1000);
  return value.SerializeAsString();
}
