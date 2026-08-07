cmake_minimum_required(VERSION 3.24)
project(contracts_isolated_consumer LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
find_package(BinanceMarketDataContracts CONFIG REQUIRED COMPONENTS Protobuf)

if(NOT BinanceMarketDataContracts_SCHEMA_FINGERPRINT STREQUAL
   "33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0" OR
   NOT BinanceMarketDataContracts_SCHEMA_FINGERPRINT_ALGORITHM_VERSION STREQUAL "1" OR
   NOT BinanceMarketDataContracts_PACKAGE_VERSION STREQUAL "0.1.0" OR
   NOT BinanceMarketDataContracts_PACKAGE_REVISION STREQUAL "NOT_FORMALLY_ASSIGNED" OR
   NOT BinanceMarketDataContracts_PROTOC_VERSION STREQUAL "libprotoc 33.5" OR
   NOT BinanceMarketDataContracts_PROTOBUF_RUNTIME_VERSION STREQUAL "6.33.5" OR
   NOT BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV STREQUAL
       "ca5ff466767b31a1b496ec60247e105c")
    message(FATAL_ERROR "installed CMake metadata does not match the reviewed candidate")
endif()

add_library(consumer_a STATIC consumer_a.cpp)
add_library(consumer_b STATIC consumer_b.cpp)
target_link_libraries(consumer_a PRIVATE BinanceMarketDataContracts::Protobuf)
target_link_libraries(consumer_b PRIVATE BinanceMarketDataContracts::Protobuf)

add_executable(contracts_isolated_consumer main.cpp)
target_compile_features(contracts_isolated_consumer PRIVATE cxx_std_20)
target_link_libraries(contracts_isolated_consumer PRIVATE
    consumer_a consumer_b BinanceMarketDataContracts::Protobuf)
