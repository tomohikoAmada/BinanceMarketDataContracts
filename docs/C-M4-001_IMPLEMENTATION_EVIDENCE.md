# C-M4-001 Implementation Candidate Evidence

## Status

- Implementation: **CORRECTED CANDIDATE / PENDING INDEPENDENT RE-REVIEW**
- Implementation acceptance: **NOT YET APPROVED**
- C-M4-001: **OPEN / PENDING INDEPENDENT IMPLEMENTATION RE-REVIEW**
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
| Formal fingerprint approval | PENDING INDEPENDENT IMPLEMENTATION RE-REVIEW |
| Package version candidate | `0.1.0` |
| Package revision | `NOT_FORMALLY_ASSIGNED` |
| Conan coordinate candidate | `binance-market-data-contracts-cpp/0.1.0` |
| Host/runtime dependency | `protobuf/6.33.5` |
| Build/tool dependency | `protobuf/6.33.5` |
| Protobuf recipe revision | `ca5ff466767b31a1b496ec60247e105c` |
| Generator | `libprotoc 33.5` |
| Generator options | `cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API` |
| Runtime flavor | full |
| Runtime linkage | static or shared, according to the built binary |

The installed CMake, C++, and source/package provenance surfaces contain only identities knowable
before Conan computes PREV. They keep runtime flavor and linkage distinct and identify binary-only
provenance as the external `c-m4-001-artifact-provenance.json`. That post-package artifact is
generated from the actual Conan graph/cache and records the concrete Contracts RREV, package ID,
PREV, Protobuf host package identity, build/profile identity, archive hash, object hashes, and
installed package manifest. These platform/options-specific values are evidence, not portable
public identity and are never manually copied into hash-covered package contents.

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

- static Release/Debug and shared Release configure, generation, build, CTest, and Conan
  `test_package` execution;
- fixed-fixture C++ serialization semantics for `DepthUpdate`, `ExchangeDepthSnapshot`, and
  `LocalOrderBookSnapshot`;
- build-tree, install-tree, and relocated-prefix CMake consumers;
- a failing `protoc` sentinel, compiler input inspection, and absence of consumer `.pb.cc` inputs;
- unconditional Release calls through both downstream consumer archives, link participation for
  both archive members, and singular generated-symbol ownership in the final executable;
- Projection Core-like independence and Projection adapter-like package use;
- Conan create and its installed-package `test_package` using the committed lock;
- two independent static Release package builds with equal Contracts RREV, package ID, PREV,
  archive SHA-256, seven generated-object hashes, and installed package manifest;
- independent copied-source-tree descriptor generation using the locked `libprotoc 33.5`, with
  equal canonical bytes and the unchanged candidate digest;
- a production-path negative test that rejects mismatched generator identity; and
- generated binary artifact provenance cross-checked against installed CMake, C++, package
  provenance, and the actual Conan graph/cache identity.

The PR CI adds the finite static support matrix for Ubuntu GCC, Ubuntu Clang, and macOS AppleClang,
plus shared Release validation on Ubuntu GCC and macOS AppleClang. It also performs active Release
consumer and `test_package` validation, a fresh-cache Conan build, lock drift detection, an offline
replay, and an AppleClang arm64 deterministic double-build job. The double-build job uploads the
generated `c-m4-001-artifact-provenance.json`; that external artifact is the authoritative exact
RREV/package-ID/PREV record for its corrected head and build tuple. Those rows are implementation
acceptance evidence only when the Draft PR checks pass.

## Deferred lifecycle gates

- Independent implementation re-review has not been performed.
- The fingerprint candidate is not formally approved.
- The formal Contracts package revision is not assigned; release mode fails closed without it.
- No Conan package, Git tag, GitHub release, or other public artifact has been published.
- Projection M4 remains blocked and has not been modified or started by this implementation.
