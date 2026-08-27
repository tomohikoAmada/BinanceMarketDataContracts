# ADR-0010: Separate C++ gRPC artifact

## Status

ACCEPTED

## Date

2026-08-23

## Context

ADR-0009 requires the C++ message package to have no mandatory gRPC dependency. The first M6
follow-on implementation kept `Protobuf` and `Grpc` as separate CMake targets, but placed both in
one Conan recipe. Because that recipe unconditionally required gRPC in both host and build
contexts, a consumer requesting only `BinanceMarketDataContracts::Protobuf` still resolved and
cold-built the complete gRPC graph. CMake component separation did not establish an artifact
boundary at the package-manager layer.

## Decision

1. `binance-market-data-contracts-cpp/0.1.0` is the message-only artifact. It generates, compiles,
   and installs exactly the seven non-service message protos and exports only
   `BinanceMarketDataContracts::Protobuf`. Its host and build graphs contain no gRPC package.
2. `binance-market-data-contracts-grpc-cpp/0.1.0` is a separate artifact. It depends on the exact
   locked message artifact and `grpc/1.83.0`, generates only `gateway_service.pb.*` and
   `gateway_service.grpc.pb.*`, and exports the frozen target
   `BinanceMarketDataContracts::Grpc`.
3. The gRPC target publicly links the one base `BinanceMarketDataContracts::Protobuf` target and
   `gRPC::grpc++`. It does not compile or package any of the seven message `.pb.cc` files.
4. Consumers discover the packages independently:

   ```cmake
   find_package(BinanceMarketDataContracts 0.1.0 EXACT CONFIG REQUIRED COMPONENTS Protobuf)
   find_package(BinanceMarketDataContractsGrpc 0.1.0 EXACT CONFIG REQUIRED)
   ```

5. The host gRPC dependency is runtime-only: codegen and every language/telemetry plugin are off.
   The build-context gRPC tool requirement enables only codegen and `cpp_plugin`; C#, Node,
   Objective-C, PHP, Python, Ruby, OpenTelemetry, and C# extension outputs remain off.
6. Static/shared linkage follows the selected gRPC artifact option through its base and host gRPC
   dependencies. Separate locks preserve base, gRPC, Protobuf, generator, and plugin recipe
   identities.
7. A Git SHA is injected into package provenance only after it exists and is checked against the
   clean source checkout. It is not an exported recipe file and therefore cannot make the base
   RREV depend recursively on the sibling gRPC lock that pins that RREV.

## Consequences

- Projection and any message-only consumer no longer resolve or build gRPC.
- Gateway links the Projection ProtoAdapter path and `BinanceMarketDataContracts::Grpc` while
  retaining one generated message-symbol owner.
- A consumer that needs service/stub code must request both CMake packages; the public target name
  remains unchanged.
- The gRPC artifact has its own Conan RREV, package ID, PREV, provenance, and publication gate.
  Neither artifact is published by this decision.

## Rejected alternatives

- A `with_grpc` option on the message recipe: rejected because it makes one coordinate represent
  incompatible dependency graphs and can reintroduce gRPC transitively.
- Keeping one recipe with component-only CMake discovery: rejected because Conan resolves recipe
  requirements before CMake components are selected.
- Regenerating the seven message sources in the gRPC artifact: rejected because it creates a
  second symbol owner and violates ADR-0009.
- Exporting the current Git SHA as recipe content: rejected because every lock-refresh commit would
  change the base RREV again, creating an unstable self-reference.

## Acceptance record

Accepted as the architectural correction for GitHub Issue #14. Merge and exact-head CI remain the
implementation acceptance gates.
