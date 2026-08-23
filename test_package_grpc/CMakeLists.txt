cmake_minimum_required(VERSION 3.24)
project(contracts_grpc_test_package LANGUAGES CXX)

find_package(BinanceMarketDataContracts 0.1.0 EXACT CONFIG REQUIRED COMPONENTS Protobuf)
find_package(BinanceMarketDataContractsGrpc 0.1.0 EXACT CONFIG REQUIRED)

add_library(projection_proto_adapter_like STATIC src/projection_proto_adapter_like.cpp)
target_compile_features(projection_proto_adapter_like PUBLIC cxx_std_20)
target_link_libraries(projection_proto_adapter_like PUBLIC
    BinanceMarketDataContracts::Protobuf)

add_executable(contracts_grpc_test_package src/test_package.cpp)
target_compile_features(contracts_grpc_test_package PRIVATE cxx_std_20)
target_link_libraries(contracts_grpc_test_package PRIVATE
    projection_proto_adapter_like
    BinanceMarketDataContracts::Grpc)
