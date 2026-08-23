# C-M4-001 Implementation Evidence and Acceptance

## Status

- Implementation: **COMPLETE / MERGED** to Contracts `main`
- Independent implementation review: **CHANGES REQUESTED** (historical), resolved
- Independent implementation re-review: **APPROVED**
- Implementation acceptance: **APPROVED / ACCEPTED / MERGED**
- C-M4-001: **IMPLEMENTED / ACCEPTED / MERGED**
- Projection M4: **COMPLETE** in the separate Projection repository
- Published: **NO**

> Current implementation status is recorded above. The review tables below preserve the historical
> candidate/re-review evidence and must not be read as a current pending-merge state. See
> `docs/CURRENT_STATE.md` for the current orientation index.

> ADR-0010 restores this accepted message-only boundary after the first M6 follow-on recipe
> accidentally made gRPC an unconditional Conan dependency. The gRPC service/stub target now lives
> in a separate artifact; the C-M4 fingerprint, seven message sources, and this acceptance record
> are unchanged.

This document records author-implementation evidence and the recorded independent
implementation acceptance. It is not itself a substitute for the independent review, which
concluded in the acceptance recorded below.

## Independent implementation acceptance record

Historical review sequence, recorded after the fact:

| Step | Result |
|---|---|
| Independent C-M4-001 Implementation Review | CHANGES REQUESTED |
| Independent C-M4-001 Implementation Re-Review | APPROVED |

Reviewed corrected head and CI:

| Item | Value |
|---|---|
| Reviewed corrected head | `4e5d3d846afba982ab5e48d2737bc40560e34a6c` |
| Reviewed CI run | `31167981350` |
| Reviewed CI result | 15/15 PASS |

Re-review findings:

| Finding | Status |
|---|---|
| IIR-1 | CLOSED |
| IIR-2 | CLOSED |
| IIR-3 | CLOSED |
| IIR-4 | CLOSED |
| IIR-5 | CLOSED |

| Severity | Count |
|---|---|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

## Immutable inputs and candidate identities

| Identity | Value |
|---|---|
| Implementation branch base | `57b8cd9295ffc73f0bb9c9f96bfa331b1c386eef` |
| Schema baseline | `01d76a41929f36d89573159f5f458f9f1e378ada` |
| Fingerprint algorithm | Version 1 |
| Schema fingerprint | `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` |
| Formal fingerprint approval | APPROVED |
| Package version candidate | `0.1.0` |
| Package revision | `NOT_FORMALLY_ASSIGNED` (assignment gate: RELEASE) |
| Conan coordinate candidate | `binance-market-data-contracts-cpp/0.1.0` |
| Host/runtime dependency | `protobuf/6.33.5` |
| Build/tool dependency | `protobuf/6.33.5` |
| Protobuf recipe revision | `ca5ff466767b31a1b496ec60247e105c` |
| Generator | `libprotoc 33.5` |
| Generator options | `cpp_out=dllexport_decl=BMD_CONTRACTS_PROTOBUF_API` |
| Runtime flavor | full |
| Runtime linkage | static or shared, according to the built binary |

### Formal schema fingerprint approval

| Item | Value |
|---|---|
| Formal Schema Fingerprint | APPROVED |
| Algorithm | M4 Schema Fingerprint Algorithm Version 1 |
| Implementation digest | `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` |
| Independent digest | `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` |
| Match | YES |

This is the formal approved C-M4-001 M4 schema fingerprint. Algorithm Version 1 is not
redesigned and no different digest is regenerated.

### Identity separation

Distinct identities are never conflated:

| Identity | Value |
|---|---|
| Schema Baseline | `01d76a41929f36d89573159f5f458f9f1e378ada` |
| Schema Fingerprint | `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0` |
| Fingerprint Algorithm | Version 1 |
| Package Version | `0.1.0` candidate |
| Contracts Package Revision | NOT FORMALLY ASSIGNED (release gate) |
| Contracts Git SHA | build/source-specific |
| Conan RREV | build/package identity |
| Conan PREV | binary artifact identity |

The Contracts Package Revision remains **NOT FORMALLY ASSIGNED** until release. It is never
replaced by the Conan RREV, Conan PREV, Git SHA, or Package Version.

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
RREV/package-ID/PREV record for its corrected head and build tuple.

## Proven support

### Static support (PROVEN)

| Platform | Compiler | Config |
|---|---|---|
| Ubuntu x86_64 | GCC | Release |
| Ubuntu x86_64 | GCC | Debug |
| Ubuntu x86_64 | Clang | Release |
| Ubuntu x86_64 | Clang | Debug |
| macOS arm64 | AppleClang | Release |
| macOS arm64 | AppleClang | Debug |

Static support is **PROVEN** for exactly these rows. Windows is not claimed.

### Shared support (PROVEN)

| Platform | Compiler | Config |
|---|---|---|
| Ubuntu x86_64 | GCC | Release |
| macOS arm64 | AppleClang | Release |

Shared support is **PROVEN** only for these two rows. Ubuntu Clang shared, Debug shared, and
Windows are not claimed.

## Reproducibility acceptance (IIR-1 CLOSED)

| Item | Result |
|---|---|
| macOS deterministic static archive | PASS |
| Independent same-input double build | PASS |
| Archive SHA match | YES |
| PREV match | YES |

Candidate native evidence remains recorded as platform/options-specific evidence:

| Identity | Value |
|---|---|
| Contracts RREV | `c90effa0eff5c7915809dcdbd5406d77` |
| Package ID | `a1a286da6ca09b590d78bcb14d8250c025131c29` |
| PREV | `eee4bdf3c274d457770b48c7850d8d6a` |

These values are evidence, not portable identity constants.

## Binary provenance acceptance

| Item | Result |
|---|---|
| Concrete Binary Provenance | PASS |
| Cross-Surface Provenance | PASS |
| Runtime Flavor | full |
| Runtime Linkage | static/shared according to built artifact |

The external post-package provenance mechanism is preserved. No self-referential PREV is embedded
into package content.

## Consumer acceptance

| Item | Result |
|---|---|
| Release Consumer Calls | ACTIVE |
| consumer_a Final-Link Participation | PASS |
| consumer_b Final-Link Participation | PASS |
| Duplicate Generated Symbol Ownership | PASS |
| Release test_package | PASS |
| Build-Tree Consumer | PASS |
| Install-Tree Consumer | PASS |
| Relocation Consumer | PASS |
| No Consumer Regeneration | PASS |

## Deferred lifecycle gates

- The acceptance-recorded head is merged into `main`; C-M4-001 is IMPLEMENTED / ACCEPTED / MERGED
  and Projection M4 is COMPLETE in the separate Projection repository.
- The formal Contracts package revision is not assigned; assignment is gated on RELEASE, and
  release mode fails closed without it.
- No published Conan package, Git tag, GitHub release, or other public artifact exists.
