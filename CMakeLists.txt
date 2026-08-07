cmake_minimum_required(VERSION 3.24)

project(BinanceMarketDataContracts VERSION 0.1.0 LANGUAGES CXX)

include(CMakePackageConfigHelpers)
include(CTest)
include(GNUInstallDirs)

include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/ContractsMetadata.cmake")

set(BMD_CONTRACTS_LIBRARY_TYPE "AUTO" CACHE STRING "Contracts library type: AUTO, STATIC, or SHARED")
set_property(CACHE BMD_CONTRACTS_LIBRARY_TYPE PROPERTY STRINGS AUTO STATIC SHARED)
option(BMD_CONTRACTS_POSITION_INDEPENDENT_CODE "Build position-independent generated objects" ON)
option(BMD_CONTRACTS_RELEASE_MODE "Require formally assigned release identities" OFF)
set(BMD_CONTRACTS_PROTOC_EXECUTABLE "" CACHE FILEPATH "Locked build-context protoc executable")
set(BMD_CONTRACTS_PROTOC_PROVENANCE "" CACHE STRING "protoc provenance assertion")
set(BMD_CONTRACTS_PROTOBUF_RREV
    "${BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV}" CACHE STRING "Locked Protobuf recipe revision")
set(BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE "" CACHE STRING
    "Protobuf runtime linkage used by this build: STATIC or SHARED")
set_property(CACHE BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE PROPERTY STRINGS STATIC SHARED)
set(BinanceMarketDataContracts_PACKAGE_REVISION "NOT_FORMALLY_ASSIGNED" CACHE STRING
    "Candidate or formal package revision")
set(BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION "" CACHE STRING
    "Immutable Contracts source revision")

if(BMD_CONTRACTS_LIBRARY_TYPE STREQUAL "AUTO")
    if(BUILD_SHARED_LIBS)
        set(_contracts_library_type SHARED)
    else()
        set(_contracts_library_type STATIC)
    endif()
elseif(BMD_CONTRACTS_LIBRARY_TYPE STREQUAL "STATIC" OR
       BMD_CONTRACTS_LIBRARY_TYPE STREQUAL "SHARED")
    set(_contracts_library_type "${BMD_CONTRACTS_LIBRARY_TYPE}")
    if(DEFINED CACHE{BUILD_SHARED_LIBS})
        if(BMD_CONTRACTS_LIBRARY_TYPE STREQUAL "STATIC" AND BUILD_SHARED_LIBS)
            message(FATAL_ERROR "BMD_CONTRACTS_LIBRARY_TYPE=STATIC conflicts with BUILD_SHARED_LIBS=ON")
        elseif(BMD_CONTRACTS_LIBRARY_TYPE STREQUAL "SHARED" AND NOT BUILD_SHARED_LIBS)
            message(FATAL_ERROR "BMD_CONTRACTS_LIBRARY_TYPE=SHARED conflicts with BUILD_SHARED_LIBS=OFF")
        endif()
    endif()
else()
    message(FATAL_ERROR "BMD_CONTRACTS_LIBRARY_TYPE must be AUTO, STATIC, or SHARED")
endif()

if(NOT BMD_CONTRACTS_PROTOBUF_RREV STREQUAL
   BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV)
    message(FATAL_ERROR "Protobuf RREV does not match the approved lock identity")
endif()

if(NOT BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION)
    execute_process(
        COMMAND git rev-parse HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE _git_result
        OUTPUT_VARIABLE _git_revision
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET)
    if(_git_result EQUAL 0 AND _git_revision MATCHES "^[0-9a-f]{40}$")
        set(BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION "${_git_revision}")
    else()
        set(BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION
            "CANDIDATE_SOURCE_REVISION_UNAVAILABLE")
    endif()
endif()

if(BMD_CONTRACTS_RELEASE_MODE)
    if(BinanceMarketDataContracts_PACKAGE_REVISION STREQUAL "NOT_FORMALLY_ASSIGNED" OR
       BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION STREQUAL
       "CANDIDATE_SOURCE_REVISION_UNAVAILABLE")
        message(FATAL_ERROR "Release mode requires formal package and source revisions")
    endif()
endif()

find_package(Protobuf 6.33.5 EXACT CONFIG REQUIRED)
find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)

if(NOT BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE STREQUAL "STATIC" AND
   NOT BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE STREQUAL "SHARED")
    message(FATAL_ERROR
        "BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE must explicitly identify STATIC or SHARED")
endif()
string(TOLOWER "${BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE}"
    BinanceMarketDataContracts_PROTOBUF_RUNTIME_LINKAGE)

set(_required_protoc_provenance
    "conan:protobuf/6.33.5#ca5ff466767b31a1b496ec60247e105c")
if(NOT BMD_CONTRACTS_PROTOC_PROVENANCE STREQUAL "${_required_protoc_provenance}")
    message(FATAL_ERROR
        "Locked build-context protoc provenance is required: ${_required_protoc_provenance}")
endif()

if(TARGET protobuf::protoc)
    get_target_property(_protoc_location protobuf::protoc IMPORTED_LOCATION_RELEASE)
    if(NOT _protoc_location)
        get_target_property(_protoc_location protobuf::protoc IMPORTED_LOCATION)
    endif()
    if(_protoc_location)
        set(_protoc_executable "${_protoc_location}")
    else()
        set(_protoc_executable "$<TARGET_FILE:protobuf::protoc>")
    endif()
elseif(BMD_CONTRACTS_PROTOC_EXECUTABLE)
    set(_protoc_executable "${BMD_CONTRACTS_PROTOC_EXECUTABLE}")
else()
    message(FATAL_ERROR
        "protobuf::protoc is unavailable; provide the locked Conan build-context protoc and provenance")
endif()

if(_protoc_executable MATCHES "\\$<")
    message(FATAL_ERROR "Unable to resolve protobuf::protoc location for identity verification")
endif()
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/verify_protoc.py"
            "--protoc=${_protoc_executable}"
            "--expected-version=${BinanceMarketDataContracts_PROTOC_VERSION}"
            "--actual-provenance=${BMD_CONTRACTS_PROTOC_PROVENANCE}"
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

set(_proto_root "${CMAKE_CURRENT_SOURCE_DIR}/src/binance_market_data_contracts/proto")
set(_message_protos
    binance_market_data/common/v1/enums.proto
    binance_market_data/common/v1/identifiers.proto
    binance_market_data/common/v1/metadata.proto
    binance_market_data/gateway/v1/gateway_messages.proto
    binance_market_data/market/v1/market_events.proto
    binance_market_data/projection/v1/snapshots.proto
    binance_market_data/telemetry/v1/telemetry.proto)
set(_fingerprint_roots
    binance_market_data/market/v1/market_events.proto
    binance_market_data/projection/v1/snapshots.proto)
set(_generated_root "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(_descriptor_set "${CMAKE_CURRENT_BINARY_DIR}/metadata/m4-descriptor.pb")
set(_canonical_descriptor "${CMAKE_CURRENT_BINARY_DIR}/metadata/m4-canonical.pb")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/metadata")

execute_process(
    COMMAND "${_protoc_executable}"
            "--proto_path=${_proto_root}"
            "--descriptor_set_out=${_descriptor_set}"
            --include_imports
            ${_fingerprint_roots}
    WORKING_DIRECTORY "${_proto_root}"
    RESULT_VARIABLE _descriptor_result
    ERROR_VARIABLE _descriptor_error)
if(NOT _descriptor_result EQUAL 0)
    message(FATAL_ERROR "M4 descriptor generation failed: ${_descriptor_error}")
endif()
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/schema_fingerprint.py"
            "--descriptor-set=${_descriptor_set}"
            "--expected-runtime=${BinanceMarketDataContracts_PROTOBUF_RUNTIME_VERSION}"
            "--canonical-output=${_canonical_descriptor}"
    RESULT_VARIABLE _fingerprint_result
    OUTPUT_VARIABLE _computed_fingerprint
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_VARIABLE _fingerprint_error)
string(LENGTH "${_computed_fingerprint}" _fingerprint_length)
if(NOT _fingerprint_result EQUAL 0 OR NOT _fingerprint_length EQUAL 64 OR
   NOT _computed_fingerprint MATCHES "^[0-9a-f]+$")
    message(FATAL_ERROR "M4 fingerprint generation failed: ${_fingerprint_error}")
endif()
if(NOT _computed_fingerprint STREQUAL BinanceMarketDataContracts_SCHEMA_FINGERPRINT)
    message(FATAL_ERROR
        "M4 fingerprint candidate mismatch: metadata has "
        "${BinanceMarketDataContracts_SCHEMA_FINGERPRINT}, computed ${_computed_fingerprint}")
endif()

set(_generated_sources)
set(_generated_headers)
set(_absolute_protos)
foreach(_proto IN LISTS _message_protos)
    string(REGEX REPLACE "\\.proto$" ".pb.cc" _source "${_proto}")
    string(REGEX REPLACE "\\.proto$" ".pb.h" _header "${_proto}")
    list(APPEND _generated_sources "${_generated_root}/${_source}")
    list(APPEND _generated_headers "${_generated_root}/${_header}")
    list(APPEND _absolute_protos "${_proto_root}/${_proto}")
endforeach()

add_custom_command(
    OUTPUT ${_generated_sources} ${_generated_headers}
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${_generated_root}"
    COMMAND "${_protoc_executable}"
            "--proto_path=${_proto_root}"
            "--cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API:${_generated_root}"
            ${_message_protos}
    WORKING_DIRECTORY "${_proto_root}"
    DEPENDS ${_absolute_protos}
    COMMENT "Generating the seven Contracts-owned C++ Protobuf message files"
    VERBATIM)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/contracts_metadata.hpp.in"
    "${_generated_root}/binance_market_data/contracts_metadata.hpp" @ONLY)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/provenance.json.in"
    "${CMAKE_CURRENT_BINARY_DIR}/metadata/provenance.json" @ONLY)

if(APPLE AND _contracts_library_type STREQUAL "STATIC")
    # Apple ar records current timestamps by default. ZERO_AR_DATE and ranlib -D are the
    # native Apple-toolchain reproducible modes. CMake invokes ranlib again during install,
    # so use the deterministic wrapper for both archive finishing and package installation.
    set(_apple_native_ranlib "${CMAKE_RANLIB}")
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/apple-ranlib.sh.in"
        "${CMAKE_CURRENT_BINARY_DIR}/apple-ranlib" @ONLY)
    file(CHMOD "${CMAKE_CURRENT_BINARY_DIR}/apple-ranlib"
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
    set(CMAKE_RANLIB "${CMAKE_CURRENT_BINARY_DIR}/apple-ranlib")
    set(CMAKE_CXX_ARCHIVE_CREATE
        "\"${CMAKE_COMMAND}\" -E env ZERO_AR_DATE=1 \"<CMAKE_AR>\" qc \"<TARGET>\" <LINK_FLAGS> <OBJECTS>")
    set(CMAKE_CXX_ARCHIVE_FINISH "\"<CMAKE_RANLIB>\" \"<TARGET>\"")
endif()

add_library(binance_market_data_contracts_protobuf ${_contracts_library_type}
    ${_generated_sources} ${_generated_headers})
add_library(BinanceMarketDataContracts::Protobuf ALIAS
    binance_market_data_contracts_protobuf)
set_target_properties(binance_market_data_contracts_protobuf PROPERTIES
    EXPORT_NAME Protobuf
    POSITION_INDEPENDENT_CODE "${BMD_CONTRACTS_POSITION_INDEPENDENT_CODE}")
target_compile_features(binance_market_data_contracts_protobuf PUBLIC cxx_std_20)
target_include_directories(binance_market_data_contracts_protobuf PUBLIC
    "$<BUILD_INTERFACE:${_generated_root}>"
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")
target_link_libraries(binance_market_data_contracts_protobuf PUBLIC protobuf::libprotobuf)

if(_contracts_library_type STREQUAL "SHARED")
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
        set_target_properties(binance_market_data_contracts_protobuf PROPERTIES
            CXX_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN YES)
        target_compile_definitions(binance_market_data_contracts_protobuf PUBLIC
            "BMD_CONTRACTS_PROTOBUF_API=__attribute__((visibility(\"default\")))")
    else()
        message(FATAL_ERROR "Shared C-M4-001 visibility is only implemented for GCC/Clang/AppleClang")
    endif()
else()
    target_compile_definitions(binance_market_data_contracts_protobuf PUBLIC
        BMD_CONTRACTS_PROTOBUF_API=)
endif()

set(_cmake_package_dir "${CMAKE_INSTALL_LIBDIR}/cmake/BinanceMarketDataContracts")
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsConfigVersion.cmake"
    VERSION "${PROJECT_VERSION}"
    COMPATIBILITY SameMajorVersion)
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/BinanceMarketDataContractsConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsConfig.cmake"
    INSTALL_DESTINATION "."
    NO_SET_AND_CHECK_MACRO)
export(TARGETS binance_market_data_contracts_protobuf
    FILE "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsTargets.cmake"
    NAMESPACE BinanceMarketDataContracts::)

set(_install_config_dir "${CMAKE_CURRENT_BINARY_DIR}/install-config")
file(MAKE_DIRECTORY "${_install_config_dir}")
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/BinanceMarketDataContractsConfig.cmake.in"
    "${_install_config_dir}/BinanceMarketDataContractsConfig.cmake"
    INSTALL_DESTINATION "${_cmake_package_dir}"
    NO_SET_AND_CHECK_MACRO)

install(TARGETS binance_market_data_contracts_protobuf
    EXPORT BinanceMarketDataContractsTargets
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
install(DIRECTORY "${_generated_root}/binance_market_data"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    FILES_MATCHING PATTERN "*.pb.h" PATTERN "contracts_metadata.hpp")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/metadata/provenance.json"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/BinanceMarketDataContracts")
install(EXPORT BinanceMarketDataContractsTargets
    FILE BinanceMarketDataContractsTargets.cmake
    NAMESPACE BinanceMarketDataContracts::
    DESTINATION "${_cmake_package_dir}")
install(FILES
    "${_install_config_dir}/BinanceMarketDataContractsConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/BinanceMarketDataContractsConfigVersion.cmake"
    DESTINATION "${_cmake_package_dir}")

if(BUILD_TESTING)
    add_executable(contracts_cpp_semantic_tests tests/cpp/semantic_tests.cpp)
    target_link_libraries(contracts_cpp_semantic_tests PRIVATE
        BinanceMarketDataContracts::Protobuf)
    add_test(NAME cpp_semantic_and_metadata COMMAND contracts_cpp_semantic_tests)
    add_test(NAME fingerprint_algorithm
        COMMAND "${Python3_EXECUTABLE}" -m pytest -q
                "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cpp_fingerprint.py")
    set_tests_properties(fingerprint_algorithm PROPERTIES
        ENVIRONMENT
            "BMD_DESCRIPTOR_SET=${_descriptor_set};PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR};BMD_PROTO_ROOT=${_proto_root};BMD_PROTOC_EXECUTABLE=${_protoc_executable};BMD_PROTOC_VERSION=${BinanceMarketDataContracts_PROTOC_VERSION};BMD_PROTOC_PROVENANCE=${BMD_CONTRACTS_PROTOC_PROVENANCE}")
endif()

message(STATUS "Contracts library type: ${_contracts_library_type}")
message(STATUS "Locked protoc: ${_protoc_executable} (${_protoc_version})")
message(STATUS "M4 schema fingerprint candidate: ${BinanceMarketDataContracts_SCHEMA_FINGERPRINT}")
