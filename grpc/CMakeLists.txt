cmake_minimum_required(VERSION 3.24)

project(BinanceMarketDataContractsGrpc VERSION 0.1.0 LANGUAGES CXX)

include(CMakePackageConfigHelpers)
include(CTest)
include(GNUInstallDirs)

include("${CMAKE_CURRENT_SOURCE_DIR}/../cmake/ContractsMetadata.cmake")

set(BMD_CONTRACTS_GRPC_LIBRARY_TYPE "AUTO" CACHE STRING
    "Contracts gRPC library type: AUTO, STATIC, or SHARED")
set_property(CACHE BMD_CONTRACTS_GRPC_LIBRARY_TYPE PROPERTY STRINGS AUTO STATIC SHARED)
option(BMD_CONTRACTS_GRPC_POSITION_INDEPENDENT_CODE
    "Build position-independent generated service objects" ON)
option(BMD_CONTRACTS_GRPC_RELEASE_MODE "Require formally assigned release identities" OFF)
set(BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE "" CACHE FILEPATH
    "Locked build-context protoc executable")
set(BMD_CONTRACTS_GRPC_PROTOC_PROVENANCE "" CACHE STRING
    "protoc provenance assertion")
set(BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE "" CACHE FILEPATH
    "Locked build-context grpc_cpp_plugin executable")
set(BMD_CONTRACTS_GRPC_CPP_PLUGIN_PACKAGE_FOLDER "" CACHE PATH
    "Locked Conan build-context gRPC package folder")
set(BMD_CONTRACTS_GRPC_CPP_PLUGIN_PROVENANCE "" CACHE STRING
    "grpc_cpp_plugin provenance assertion")
set(BMD_CONTRACTS_GRPC_PROTOBUF_RREV
    "${BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV}" CACHE STRING
    "Locked Protobuf recipe revision")
set(BMD_CONTRACTS_GRPC_RREV "" CACHE STRING "Locked gRPC recipe revision")
set(BMD_CONTRACTS_GRPC_BASE_RREV "" CACHE STRING
    "Resolved binance-market-data-contracts-cpp recipe revision")
set(BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE "" CACHE STRING
    "gRPC runtime linkage used by this build: STATIC or SHARED")
set_property(CACHE BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE PROPERTY STRINGS STATIC SHARED)
set(BinanceMarketDataContractsGrpc_PACKAGE_REVISION "NOT_FORMALLY_ASSIGNED" CACHE STRING
    "Candidate or formal gRPC package revision")
set(BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION "" CACHE STRING
    "Immutable Contracts source revision")

if(BMD_CONTRACTS_GRPC_LIBRARY_TYPE STREQUAL "AUTO")
    if(BUILD_SHARED_LIBS)
        set(_grpc_library_type SHARED)
    else()
        set(_grpc_library_type STATIC)
    endif()
elseif(BMD_CONTRACTS_GRPC_LIBRARY_TYPE STREQUAL "STATIC" OR
       BMD_CONTRACTS_GRPC_LIBRARY_TYPE STREQUAL "SHARED")
    set(_grpc_library_type "${BMD_CONTRACTS_GRPC_LIBRARY_TYPE}")
    if(DEFINED CACHE{BUILD_SHARED_LIBS})
        if(BMD_CONTRACTS_GRPC_LIBRARY_TYPE STREQUAL "STATIC" AND BUILD_SHARED_LIBS)
            message(FATAL_ERROR
                "BMD_CONTRACTS_GRPC_LIBRARY_TYPE=STATIC conflicts with BUILD_SHARED_LIBS=ON")
        elseif(BMD_CONTRACTS_GRPC_LIBRARY_TYPE STREQUAL "SHARED" AND NOT BUILD_SHARED_LIBS)
            message(FATAL_ERROR
                "BMD_CONTRACTS_GRPC_LIBRARY_TYPE=SHARED conflicts with BUILD_SHARED_LIBS=OFF")
        endif()
    endif()
else()
    message(FATAL_ERROR
        "BMD_CONTRACTS_GRPC_LIBRARY_TYPE must be AUTO, STATIC, or SHARED")
endif()

if(NOT BMD_CONTRACTS_GRPC_PROTOBUF_RREV STREQUAL
   BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV)
    message(FATAL_ERROR "Protobuf RREV does not match the approved lock identity")
endif()
if(NOT BMD_CONTRACTS_GRPC_BASE_RREV MATCHES "^[0-9a-f]+$")
    message(FATAL_ERROR "The exact base Contracts Conan RREV is required")
endif()
if(NOT BMD_CONTRACTS_GRPC_RREV MATCHES "^[0-9a-f]+$")
    message(FATAL_ERROR "The exact gRPC Conan RREV is required")
endif()
if(NOT BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE STREQUAL "STATIC" AND
   NOT BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE STREQUAL "SHARED")
    message(FATAL_ERROR
        "BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE must explicitly identify STATIC or SHARED")
endif()
string(TOLOWER "${BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE}"
    BinanceMarketDataContractsGrpc_GRPC_RUNTIME_LINKAGE)

if(NOT BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION)
    execute_process(
        COMMAND git rev-parse HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/.."
        RESULT_VARIABLE _git_result
        OUTPUT_VARIABLE _git_revision
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET)
    if(_git_result EQUAL 0 AND _git_revision MATCHES "^[0-9a-f]{40}$")
        set(BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION "${_git_revision}")
    else()
        set(BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION
            "CANDIDATE_SOURCE_REVISION_UNAVAILABLE")
    endif()
endif()

if(BMD_CONTRACTS_GRPC_RELEASE_MODE)
    if(BinanceMarketDataContractsGrpc_PACKAGE_REVISION STREQUAL
       "NOT_FORMALLY_ASSIGNED" OR
       BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION STREQUAL
       "CANDIDATE_SOURCE_REVISION_UNAVAILABLE")
        message(FATAL_ERROR "Release mode requires formal package and source revisions")
    endif()
endif()

find_package(BinanceMarketDataContracts 0.1.0 EXACT CONFIG REQUIRED COMPONENTS Protobuf)
find_package(Protobuf 6.33.5 EXACT CONFIG REQUIRED)
find_package(gRPC 1.83.0 EXACT CONFIG REQUIRED)
find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)

set(_required_protoc_provenance
    "conan:protobuf/6.33.5#${BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV}")
if(NOT BMD_CONTRACTS_GRPC_PROTOC_PROVENANCE STREQUAL
   "${_required_protoc_provenance}")
    message(FATAL_ERROR
        "Locked build-context protoc provenance is required: ${_required_protoc_provenance}")
endif()
if(NOT BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE)
    message(FATAL_ERROR "A locked build-context protoc executable is required")
endif()
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/../tools/verify_protoc.py"
            "--protoc=${BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE}"
            "--expected-version=${BinanceMarketDataContracts_PROTOC_VERSION}"
            "--actual-provenance=${BMD_CONTRACTS_GRPC_PROTOC_PROVENANCE}"
            "--expected-provenance=${_required_protoc_provenance}"
    RESULT_VARIABLE _protoc_result
    OUTPUT_VARIABLE _protoc_version
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_VARIABLE _protoc_error)
if(NOT _protoc_result EQUAL 0)
    message(FATAL_ERROR
        "protoc identity mismatch: expected '${BinanceMarketDataContracts_PROTOC_VERSION}', "
        "got '${_protoc_version}' (${_protoc_error})")
endif()

set(_required_grpc_plugin_provenance
    "conan:grpc/1.83.0#${BMD_CONTRACTS_GRPC_RREV}")
if(NOT BMD_CONTRACTS_GRPC_CPP_PLUGIN_PROVENANCE STREQUAL
   "${_required_grpc_plugin_provenance}")
    message(FATAL_ERROR
        "Locked build-context grpc_cpp_plugin provenance is required: "
        "${_required_grpc_plugin_provenance}")
endif()
if(NOT BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE)
    message(FATAL_ERROR "A locked build-context grpc_cpp_plugin executable is required")
endif()
execute_process(
    COMMAND "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/../tools/verify_grpc_cpp_plugin.py"
            "--executable=${BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE}"
            "--package-folder=${BMD_CONTRACTS_GRPC_CPP_PLUGIN_PACKAGE_FOLDER}"
            "--actual-provenance=${BMD_CONTRACTS_GRPC_CPP_PLUGIN_PROVENANCE}"
            "--expected-provenance=${_required_grpc_plugin_provenance}"
    RESULT_VARIABLE _grpc_plugin_result
    ERROR_VARIABLE _grpc_plugin_error)
if(NOT _grpc_plugin_result EQUAL 0)
    message(FATAL_ERROR "grpc_cpp_plugin identity mismatch: ${_grpc_plugin_error}")
endif()

set(_proto_root "${CMAKE_CURRENT_SOURCE_DIR}/../src/binance_market_data_contracts/proto")
set(_gateway_service_proto_relative
    "binance_market_data/gateway/v1/gateway_service.proto")
set(_gateway_service_proto "${_proto_root}/${_gateway_service_proto_relative}")
set(_gateway_messages_proto
    "${_proto_root}/binance_market_data/gateway/v1/gateway_messages.proto")
set(_generated_root "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(_gateway_service_pb_source
    "${_generated_root}/binance_market_data/gateway/v1/gateway_service.pb.cc")
set(_gateway_service_pb_header
    "${_generated_root}/binance_market_data/gateway/v1/gateway_service.pb.h")
set(_gateway_service_grpc_source
    "${_generated_root}/binance_market_data/gateway/v1/gateway_service.grpc.pb.cc")
set(_gateway_service_grpc_header
    "${_generated_root}/binance_market_data/gateway/v1/gateway_service.grpc.pb.h")

add_custom_command(
    OUTPUT
        "${_gateway_service_pb_source}"
        "${_gateway_service_pb_header}"
        "${_gateway_service_grpc_source}"
        "${_gateway_service_grpc_header}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${_generated_root}"
    COMMAND "${BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE}"
            "--proto_path=${_proto_root}"
            "--cpp_out=dllexport_decl=BMD_CONTRACTS_GRPC_API:${_generated_root}"
            "--grpc_out=${_generated_root}"
            "--plugin=protoc-gen-grpc=${BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE}"
            "${_gateway_service_proto_relative}"
    WORKING_DIRECTORY "${_proto_root}"
    DEPENDS "${_gateway_service_proto}" "${_gateway_messages_proto}"
    COMMENT "Generating the Contracts-owned Gateway service and gRPC stub files"
    VERBATIM)

add_library(binance_market_data_contracts_grpc ${_grpc_library_type}
    "${_gateway_service_pb_source}"
    "${_gateway_service_pb_header}"
    "${_gateway_service_grpc_source}"
    "${_gateway_service_grpc_header}")
add_library(BinanceMarketDataContracts::Grpc ALIAS
    binance_market_data_contracts_grpc)
set_target_properties(binance_market_data_contracts_grpc PROPERTIES
    EXPORT_NAME Grpc
    POSITION_INDEPENDENT_CODE "${BMD_CONTRACTS_GRPC_POSITION_INDEPENDENT_CODE}")
target_compile_features(binance_market_data_contracts_grpc PUBLIC cxx_std_20)
target_include_directories(binance_market_data_contracts_grpc PUBLIC
    "$<BUILD_INTERFACE:${_generated_root}>"
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")
target_link_libraries(binance_market_data_contracts_grpc PUBLIC
    BinanceMarketDataContracts::Protobuf
    gRPC::grpc++)

if(_grpc_library_type STREQUAL "SHARED")
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
        set_target_properties(binance_market_data_contracts_grpc PROPERTIES
            CXX_VISIBILITY_PRESET default
            VISIBILITY_INLINES_HIDDEN YES)
        target_compile_definitions(binance_market_data_contracts_grpc PUBLIC
            "BMD_CONTRACTS_GRPC_API=__attribute__((visibility(\"default\")))")
    else()
        message(FATAL_ERROR
            "Shared Contracts gRPC visibility is only implemented for GCC/Clang/AppleClang")
    endif()
else()
    target_compile_definitions(binance_market_data_contracts_grpc PUBLIC
        BMD_CONTRACTS_GRPC_API=)
endif()

set(BinanceMarketDataContractsGrpc_PACKAGE_VERSION "${PROJECT_VERSION}")
set(BinanceMarketDataContractsGrpc_BASE_PACKAGE_VERSION "0.1.0")
set(BinanceMarketDataContractsGrpc_GRPC_VERSION "1.83.0")
set(BinanceMarketDataContractsGrpc_GRPC_RREV "${BMD_CONTRACTS_GRPC_RREV}")
set(BinanceMarketDataContractsGrpc_BASE_RREV "${BMD_CONTRACTS_GRPC_BASE_RREV}")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/provenance.json.in"
    "${CMAKE_CURRENT_BINARY_DIR}/metadata/provenance.json" @ONLY)

set(_cmake_package_dir "${CMAKE_INSTALL_LIBDIR}/cmake/BinanceMarketDataContractsGrpc")
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsGrpcConfigVersion.cmake"
    VERSION "${PROJECT_VERSION}"
    COMPATIBILITY SameMajorVersion)
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/BinanceMarketDataContractsGrpcConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsGrpcConfig.cmake"
    INSTALL_DESTINATION "."
    NO_SET_AND_CHECK_MACRO)
export(TARGETS binance_market_data_contracts_grpc
    FILE "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsGrpcTargets.cmake"
    NAMESPACE BinanceMarketDataContracts::)

set(_install_config_dir "${CMAKE_CURRENT_BINARY_DIR}/install-config")
file(MAKE_DIRECTORY "${_install_config_dir}")
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/BinanceMarketDataContractsGrpcConfig.cmake.in"
    "${_install_config_dir}/BinanceMarketDataContractsGrpcConfig.cmake"
    INSTALL_DESTINATION "${_cmake_package_dir}"
    NO_SET_AND_CHECK_MACRO)

install(TARGETS binance_market_data_contracts_grpc
    EXPORT BinanceMarketDataContractsGrpcTargets
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
install(FILES "${_gateway_service_pb_header}" "${_gateway_service_grpc_header}"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/binance_market_data/gateway/v1")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/metadata/provenance.json"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/BinanceMarketDataContractsGrpc")
install(EXPORT BinanceMarketDataContractsGrpcTargets
    FILE BinanceMarketDataContractsGrpcTargets.cmake
    NAMESPACE BinanceMarketDataContracts::
    DESTINATION "${_cmake_package_dir}")
install(FILES
    "${_install_config_dir}/BinanceMarketDataContractsGrpcConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsGrpcConfigVersion.cmake"
    DESTINATION "${_cmake_package_dir}")

if(BUILD_TESTING)
    add_executable(contracts_cpp_grpc_tests "${CMAKE_CURRENT_SOURCE_DIR}/../tests/cpp/grpc_tests.cpp")
    target_link_libraries(contracts_cpp_grpc_tests PRIVATE
        BinanceMarketDataContracts::Grpc)
    add_test(NAME cpp_grpc_service_surface COMMAND contracts_cpp_grpc_tests)
endif()

message(STATUS "Contracts gRPC library type: ${_grpc_library_type}")
message(STATUS "Locked protoc: ${BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE} (${_protoc_version})")
message(STATUS "Locked grpc_cpp_plugin: ${BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE}")
message(STATUS "Base Contracts Conan RREV: ${BMD_CONTRACTS_GRPC_BASE_RREV}")
