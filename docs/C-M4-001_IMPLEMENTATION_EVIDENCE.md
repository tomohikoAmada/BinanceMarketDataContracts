# C-M4-001 Implementation Candidate Evidence

## Status

- Implementation: **IMPLEMENTED CANDIDATE / PENDING INDEPENDENT REVIEW**
- C-M4-001: **OPEN / PENDING INDEPENDENT IMPLEMENTATION REVIEW**
- Projection M4: **NOT STARTED / BLOCKED**
- Published: **NO**

This document records author-implementation evidence. It does not perform or substitute for the
required independent implementation review.

## Immutable inputs and candidate identities

| Identity | Value |
|---|---|
| Implementation branch base | `57b8cd9295ffc73f0bb9c9f96bfa331b1c386eef` |
| Schema baseline | `01d76a41929f36d89573159f5f458f9f1e378ada` |
| Fingerprint algorithm | Version 1 |
| Schema fingerprint candidate | `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` |
| Formal fingerprint approval | PENDING INDEPENDENT IMPLEMENTATION REVIEW |
| Package version candidate | `0.1.0` |
| Package revision | `NOT_FORMALLY_ASSIGNED` |
| Conan coordinate candidate | `binance-market-data-contracts-cpp/0.1.0` |
| Host/runtime dependency | `protobuf/6.33.5` |
| Build/tool dependency | `protobuf/6.33.5` |
| Protobuf recipe revision | `ca5ff466767b31a1b496ec60247e105c` |
| Generator | `libprotoc 33.5` |
| Generator options | `cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API` |
| Runtime linkage | full `protobuf::libprotobuf` |

The installed provenance manifest keeps the schema, source, generator, runtime, Conan, and package
identities distinct. Build-specific Conan package IDs and PREVs are evidence, not portable public
identity.

## Package boundary

The CMake package is `BinanceMarketDataContracts` and its installed message target is
`BinanceMarketDataContracts::Protobuf`. It generates exactly the seven current non-service proto
files into the build tree. `gateway_service.proto` is excluded, and gRPC is not a mandatory
dependency. Generated `.pb.cc` and `.pb.h` files are not committed as primary source files.

Fingerprint Algorithm Version 1 uses only these roots:

- `binance_market_data/market/v1/market_events.proto`
- `binance_market_data/projection/v1/snapshots.proto`

The validated closure is `enums.proto`, `metadata.proto`, `market_events.proto`, and
`snapshots.proto`. Package generation and fingerprint closure remain separate concepts.

## Candidate validation

Local native validation on macOS arm64 with AppleClang 21 established:

- static and shared configure, generation, build, and CTest;
- fixed-fixture C++ serialization semantics for `DepthUpdate`, `ExchangeDepthSnapshot`, and
  `LocalOrderBookSnapshot`;
- build-tree, install-tree, and relocated-prefix CMake consumers;
- a failing `protoc` sentinel, compiler input inspection, and absence of consumer `.pb.cc` inputs;
- singular generated-symbol ownership across multiple downstream consumers;
- Projection Core-like independence and Projection adapter-like package use;
- Conan create and its installed-package `test_package` using the committed lock;
- deterministic fingerprint tests, exact runtime/tool checks, and metadata cross-checks.

The PR CI adds the finite static support matrix for Ubuntu GCC, Ubuntu Clang, and macOS AppleClang,
plus shared Release validation on Ubuntu GCC and macOS AppleClang. It also performs a fresh-cache
Conan build, lock drift detection, and an offline replay. Those rows are implementation acceptance
evidence only when the Draft PR checks pass.

## Deferred lifecycle gates

- Independent implementation review has not been performed.
- The fingerprint candidate is not formally approved.
- The formal Contracts package revision is not assigned; release mode fails closed without it.
- No Conan package, Git tag, GitHub release, or other public artifact has been published.
- Projection M4 remains blocked and has not been modified or started by this implementation.
