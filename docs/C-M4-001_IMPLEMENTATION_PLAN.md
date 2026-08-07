# C-M4-001 C++ Protobuf Package Implementation Plan

## Status and authorization

- Implementation Planning: **APPROVED**
- C-M4-001 Design: **APPROVED / MERGED**
- ADR-0009: **ACCEPTED**
- OD-CM4-001: **CLOSED**
- C-M4-001 Implementation: **NOT STARTED / NOT AUTHORIZED**
- Projection M4 Implementation: **NOT STARTED / BLOCKED**
- Planning Evidence Baseline: `2ba5098bbd89f14403c0fa5e0dd00459f962b68a`
- Actual Implementation Branch Base: **the then-current merged Contracts `main` containing the approved implementation plan; SHA captured at implementation start**
- Schema baseline: `01d76a41929f36d89573159f5f458f9f1e378ada`
- Schema Fingerprint: **NOT YET GENERATED / RECORDED / APPROVED**
- Contracts Package Version: **NOT ASSIGNED TO AN ARTIFACT**
- Contracts Package Revision: **NOT YET ASSIGNED**
- Independent C-M4-001 Implementation Plan Re-Review: **APPROVED**
- Reviewed Head: `1bbf9e89787230900423b444eacbda1d434b1acb`
- New P0 Findings: **0**
- New P1 Findings: **0**
- New P2 Findings: **0**

This is a planning document. It creates no CMake project, Conan recipe, lockfile, generated C++
source, package binary, release artifact, or Projection change. Implementation starts only after an
independent planning review approves this plan and the authorization gate at the end passes.

## Scope and fixed architecture

The future implementation will provide a Contracts-owned, versioned, installable C++ Protobuf
message package for the Projection M4 adapter. The following approved decisions are fixed:

- Contracts owns the authoritative `.proto` sources, package-build-time C++ generation, installed
  headers, package metadata, and one generated symbol set.
- Consumers use the installed `BinanceMarketDataContracts::Protobuf` target.
- Projection does not copy schemas or regenerate Contracts messages.
- Projection Core remains independent of Protobuf and Contracts.
- The message target has no mandatory gRPC dependency; a future `Grpc` component is separate.
- Generated sources are build outputs, not primary committed source ownership.
- FetchContent, submodules, configure-time downloads, and undocumented host injection are forbidden.
- Offline prebuilt-package consumption is required.
- Schema Identity and Package Identity remain separate.

This plan translates those decisions into reviewable work; it does not redesign them.

## Evidence and baselines

### Planning Evidence Baseline

The Contracts `main` content inspected when this implementation plan was authored and reviewed was:

```text
2ba5098bbd89f14403c0fa5e0dd00459f962b68a
```

This is planning evidence and provenance only. It is not the mandatory future implementation branch
point. Once this planning PR is merged, `main` will move. The future C-M4-001 implementation branch
MUST be created from the then-current merged Contracts `main` that contains the approved
implementation plan. The actual SHA must be captured at implementation start as the
**Implementation Branch Base**.

### Schema identity baseline

The approved historical Schema Baseline remains:

```text
01d76a41929f36d89573159f5f458f9f1e378ada
```

It fixes the reviewed `.proto` package names, field and enum numbers, imports, presence, and
wire-relevant declarations. A later implementation commit, Package Version, Package Revision,
Conan RREV, Conan PREV, and binary package ID are distinct identities.

### Closed dependency decision

OD-CM4-001 is closed by independently verified evidence:

```text
Host/runtime: protobuf/6.33.5
Build/compiler: protobuf/6.33.5
Host declaration: requires("protobuf/6.33.5")
Build declaration: tool_requires("protobuf/6.33.5")
RREV: ca5ff466767b31a1b496ec60247e105c
Pinning: Conan 2 lockfile
Generator: libprotoc 33.5
Runtime target: protobuf::libprotobuf
Compiler library target observed: protobuf::libprotoc
gRPC required: NO
```

The observed native package ID and PREV are platform/options-specific evidence and must not become
global package identity.

Before any Contracts C++ generation, the implementation must resolve the Conan build-context
Protobuf from `tool_requires("protobuf/6.33.5")`. It must verify whether the active generated
build-context CMake dependency metadata exposes the imported executable target
`protobuf::protoc`. If it does, generation should use the target executable, conceptually
`$<TARGET_FILE:protobuf::protoc>`. If that executable target is unavailable in the active
Conan/CMakeDeps configuration, generation must use the verified tool-requirement executable from
the Conan build environment / VirtualBuildEnv `PATH`. It must not silently fall back to an arbitrary
system `protoc`.

The selected executable must report `libprotoc 33.5` and correspond to Protobuf `6.33.5` with RREV
`ca5ff466767b31a1b496ec60247e105c`. Generation fails closed if the discovered executable does not
match that locked build-context identity. `protobuf::libprotoc` is the observed compiler library
target; it is not the `protoc` executable and must not be confused with it.

## Planning decision register

| Decision | Status | Decision and boundary | Blocks |
|---|---|---|---|
| OD-CM4-001 | CLOSED | Exact Protobuf `6.33.5` host/build references, lockfile, and RREV | Nothing in planning |
| OD-CM4-002 | CLOSED | Package-build generation; source archives, if any, are derived release artifacts | No; archive work is release-only |
| OD-CM4-003 | CLOSED FOR PLANNING | Initial planned C++ Package Version is independent `0.1.0`; artifact assignment and publication remain gated | No; release assignment remains gated |
| OD-CM4-004 | DEFERRED — PUBLICATION ONLY | Logical coordinate `binance-market-data-contracts-cpp/0.1.0`; remote/publication policy deferred | Publication only |
| OD-CM4-005 | DEFERRED — SHARED SUPPORT CLAIM | Explicit generated export/visibility macro and static/shared mapping; shared claim waits for tests | Shared support claim |
| OD-CM4-006 | DEFERRED — SUPPORT CLAIMS | Validate the declared Linux/macOS matrix in implementation CI; Windows unclaimed | Platform/support claims |
| OD-CM4-007 | CLOSED FOR INITIAL PACKAGE | No semantic manifest for the initial package; domain semantics remain separately tested | Nothing for initial package |

OD-CM4-002 is closed because the verified package-build path uses Conan-supplied `protoc`, while a
prebuilt package consumes generated artifacts without `protoc`. A cached source build may invoke the
locked tool offline. A future signed source archive is derived from this same path, not a second
authority.

OD-CM4-003 is **CLOSED FOR PLANNING**. It selects the initial planned C++ Package Version `0.1.0`,
independent from Python `0.2.0a1`. Artifact assignment is **NOT YET PERFORMED** and publication is
**NOT AUTHORIZED**. A release tag/manifest may assign the version only after implementation
acceptance. Package Version remains distinct from Package Revision, Git SHA, Conan RREV/PREV, Schema
Version, and Schema Fingerprint.

OD-CM4-004 uses the logical Conan reference:

```text
binance-market-data-contracts-cpp/0.1.0
```

The publication remote, channel, recipe export policy, and registry procedure remain release
decisions. This coordinate is unrelated to `protobuf/6.33.5`.

OD-CM4-005 plans a generated API/visibility macro, explicit hidden/default visibility policy, and
tests for `BUILD_SHARED_LIBS`, the Contracts library-type option, Conan `shared`, and `fPIC`. Static
support is implemented first; shared support is not claimed until symbol-export and install-consumer
tests pass on the declared platforms.

OD-CM4-006 initially claims only these combinations after implementation evidence passes:

| Platform/toolchain | Contracts library | Build types | PIC |
|---|---|---|---|
| Ubuntu x86_64 GCC | Static | Release, Debug | Enabled where supported |
| Ubuntu x86_64 Clang | Static | Release, Debug | Enabled where supported |
| macOS arm64 AppleClang | Static | Release, Debug | Enabled |

Shared Contracts Release builds on Ubuntu GCC and macOS AppleClang are a gated additional claim
after OD-CM4-005 tests. Protobuf linkage modes are claimed only when the exact Conan/CMake
combination is tested. Windows/MSVC is not an initial target.

OD-CM4-007 deliberately does not hash Pydantic or adapter semantics into the descriptor fingerprint.
Existing domain, adapter, fixture, and downstream tests remain the semantic authority. Reopen only
with evidence of a concrete metadata requirement.

## Schema graph and generated package scope

### M4 fingerprint roots and closure

Approved roots:

```text
binance_market_data/market/v1/market_events.proto
binance_market_data/projection/v1/snapshots.proto
```

Verified current M4 closure:

```text
binance_market_data/common/v1/enums.proto
binance_market_data/common/v1/metadata.proto
binance_market_data/market/v1/market_events.proto
binance_market_data/projection/v1/snapshots.proto
```

The roots do not import `identifiers.proto`, Gateway files, or telemetry. This closure is the M4
fingerprint input set, not the complete message-package generation set.

### Complete non-service message generation set

The future message package generates these seven current non-service files:

```text
binance_market_data/common/v1/enums.proto
binance_market_data/common/v1/identifiers.proto
binance_market_data/common/v1/metadata.proto
binance_market_data/gateway/v1/gateway_messages.proto
binance_market_data/market/v1/market_events.proto
binance_market_data/projection/v1/snapshots.proto
binance_market_data/telemetry/v1/telemetry.proto
```

`gateway_service.proto` is excluded from `Protobuf`; future gRPC generation belongs to a separate
component. `identifiers.proto` is outside the M4 closure but is required because
`gateway_messages.proto` imports it.

### Installed include mapping

All generated headers follow the proto-relative root:

| Proto | Installed header |
|---|---|
| `common/v1/enums.proto` | `include/binance_market_data/common/v1/enums.pb.h` |
| `common/v1/identifiers.proto` | `include/binance_market_data/common/v1/identifiers.pb.h` |
| `common/v1/metadata.proto` | `include/binance_market_data/common/v1/metadata.pb.h` |
| `gateway/v1/gateway_messages.proto` | `include/binance_market_data/gateway/v1/gateway_messages.pb.h` |
| `market/v1/market_events.proto` | `include/binance_market_data/market/v1/market_events.pb.h` |
| `projection/v1/snapshots.proto` | `include/binance_market_data/projection/v1/snapshots.pb.h` |
| `telemetry/v1/telemetry.proto` | `include/binance_market_data/telemetry/v1/telemetry.pb.h` |

Generated `.pb.cc` files are staged under the build/package directory only and are never copied to
Projection or compiled by a consumer.

## Future file-level implementation plan

No file in this table is created by this planning PR.

| Future file/category | Purpose | Inputs/dependencies | Outputs and acceptance |
|---|---|---|---|
| `CMakeLists.txt` | Project, options, generation, library, install orchestration | CMake, Conan toolchain, proto source revision | One exported message target; offline-safe configure |
| `cmake/*.cmake` and Config template | Relocatable package config, components, metadata, generation helpers | Exported targets, metadata, locked build-context `protobuf::protoc` executable discovery or verified VirtualBuildEnv path | Build/install package discovery outside source tree |
| `conanfile.py` | Contracts Conan 2 recipe | Host/build `protobuf/6.33.5`, options/settings | Correct host/build graph and package ID |
| `conan.lock` | Exact dependency graph | Protobuf RREV and recipe revisions | Clean-cache and offline replay select identical graph |
| `test_package/*` | Conan installed-package consumer | CMakeDeps, CMakeToolchain, installed headers/target | `conan create` and `test_package` pass without `.proto` |
| `tools/*` | Canonical descriptor and metadata tools | Descriptor set, pinned Protobuf runtime, source revision | Canonical bytes, digest candidate, metadata inputs |
| `tests/cpp/*` | C++ message, metadata, linkage, fingerprint tests | CMake targets and fixed fixtures | Tests cover acceptance gates |
| `tests/consumers/*` | Build-tree/install-tree/relocation consumers | Exported CMake package | No source-tree assumption or consumer codegen |
| CI workflow additions | Future C++/Conan/platform jobs | Declared matrix and locked cache | Added only in implementation PR |
| Release documentation/manifest | Provenance and publication procedure | Accepted artifacts and identities | Publication fails with missing identities |

Generated output is staged under `<build>/generated/binance_market_data/...`; no generated file is
written into `src/` or committed.

## Implementation phases and gates

1. **Build skeleton and metadata.** Add CMake options, C++ standard, package version input,
   metadata schema, and empty export scaffolding. Phase 1 uses explicitly labeled candidate/test
   identity values only to validate the metadata mechanism. It does **not** assign or approve the
   formal production Schema Fingerprint Digest or Contracts Package Revision. The negative test
   removes or omits a required candidate identity field and requires configuration/metadata
   generation to fail. Exit: offline configure works and the candidate identity mechanism fails
   closed when required fields are missing.
2. **Canonical descriptor/fingerprint.** Resolve the locked Conan build-context Protobuf before
   invoking `protoc`, using the discovery and fail-closed rules above. Invoke it with the two roots,
   `--include_imports`, and no source info. Normalize filenames/dependencies, clear source info and
   unknown fields, classify options, preserve declaration order, deterministically serialize, and
   SHA-256 the exact bytes. Phase 2 may generate candidate fingerprint values for reproducibility
   tests, but those candidate digests remain **NOT FORMALLY APPROVED**. Exit: golden and
   reproducibility vectors pass; no production digest is approved yet.
3. **Contracts-owned generation.** Generate the seven non-service files once into the build
   directory and record exact generator options. Exit: every generated include resolves and no
   consumer generation rule exists.
4. **Message library/package.** Build one selectable static/shared library and export
   `BinanceMarketDataContracts::Protobuf` with `protobuf::libprotobuf`, include paths, C++ standard,
   platform requirements, and visibility definitions. Exit: build-tree package and metadata header
   work; gRPC is absent from the dependency graph.
5. **Build/install consumers.** Configure consumers outside the source tree from build and install
   packages. Exit: `find_package(BinanceMarketDataContracts CONFIG REQUIRED COMPONENTS Protobuf)`
   and target linking work from a relocated prefix without source `.proto` or `protoc`.
6. **Conan recipe, lock, and test package.** Before formal recipe/lockfile creation, any phase that
   requires `protoc` may use the already independently verified OD-CM4-001 identity
   `protobuf/6.33.5`, RREV `ca5ff466767b31a1b496ec60247e105c`, through controlled temporary or
   developer dependency resolution; this is not the committed production lockfile. In Phase 6,
   generate the actual project `conan.lock` from the Contracts Conan recipe, declared host profile,
   declared build profile, `requires("protobuf/6.33.5")`, `tool_requires("protobuf/6.33.5")`, and
   all relevant recipe options. The lock must include the required host and build dependency graph.
   CI must deterministically regenerate/resolve the expected graph from those declared inputs and
   fail on any difference from committed lock state, then perform offline replay with the committed
   lock. Intentional dependency updates require an explicit recipe/reference change, lockfile
   regeneration, reviewed diff, clean-cache verification, and offline replay. Exit: clean-cache
   `conan create`, `test_package`, lock conformance, and offline replay pass with no automatic drift.
7. **Static/shared/PIC.** Validate the exact support matrix, export macro, visibility, `fPIC`, and
   option mapping. For Conan builds, recipe `shared` is the source of truth and flows through
   `CMakeToolchain` to the Contracts library-type setting and actual library type. For direct CMake
   builds, the Contracts-specific library-type option is authoritative when explicitly set; when
   unset, it may derive its default from `BUILD_SHARED_LIBS`. Conflicting explicit settings fail
   with a clear configuration error rather than silently choosing one. Static builds map `fPIC`
   according to platform/Conan semantics. Exit: static claims pass; shared claims remain deferred
   until symbol/export tests pass.
8. **Duplicate symbols/no regeneration.** Link multiple consumers and inspect map/object inputs;
   fail if `protoc`, `.proto`, or generated `.cc` enters a consumer. Use a consumer workspace with
   no Contracts source-tree reference, assert the installed inputs contain no required `.proto`
   files, run with `protoc` unavailable from `PATH` (or a trap/sentinel that fails on invocation),
   inspect build commands/logs for `protoc`, inspect compiler/linker inputs for generated `.pb.cc`
   ownership, and fail on any source-tree path. These mechanisms validate the build rather than only
   inspecting consumer CMake text. Exit: one definition per symbol and no consumer regeneration.
9. **Contracts-owned Projection-like consumers.** This phase is performed in the Contracts
   implementation PR using minimal projection-like test consumers; it does not modify
   `tomohikoAmada/BinanceMarketDataProjection` and does not start Projection M4. The Core-like
   probe represents the Projection Core dependency posture and proves no Protobuf dependency and no
   Contracts dependency. The adapter-like probe consumes the installed package, finds
   `BinanceMarketDataContracts`, links `BinanceMarketDataContracts::Protobuf`, serializes and
   deserializes, checks optional presence, checks fixed fixture compatibility where applicable, and
   checks metadata. Real integration with the Projection repository occurs only after C-M4-001
   passes its implementation acceptance/review and Projection M4 is separately authorized. Exit:
   Core remains independent and adapter linkage is exact.
10. **CI and platform matrix.** Add Ubuntu GCC/Clang and macOS AppleClang jobs plus install, Conan,
    reproducibility, symbol, offline, and consumer jobs. Exit: required matrix proves only declared
    support.
11. **Release/provenance.** Inspect artifacts and produce a manifest containing all identities,
    recipe revisions, package ID/PREV, and source provenance. Exit: release review approves exact
    artifacts; publication is separate.
12. **Independent implementation review.** Review ownership, identities, reproducibility, package
    consumers, platform claims, and Projection handoff. Exit: only then may C-M4-001 close.

Each phase requires the prior phase's exit evidence and a clean source tree. No phase authorizes
Projection work by itself.

## CMake and Conan graphs

```text
BinanceMarketDataContracts::Protobuf
    -> protobuf::libprotobuf
    -> generated message sources and installed headers
    -> C++ standard, platform, visibility, and PIC requirements

Future BinanceMarketDataContracts::Grpc
    -> BinanceMarketDataContracts::Protobuf
    -> gRPC runtime and service-generated sources
```

The exported package is `BinanceMarketDataContracts`; the stable target is
`BinanceMarketDataContracts::Protobuf`. It is a normal selectable static/shared library, not an
`INTERFACE` target that compiles sources in consumers. Metadata is exposed through relocatable CMake
variables/properties, an installed `include/binance_market_data/contracts_metadata.hpp`, and an
artifact manifest:

```text
SCHEMA_BASELINE
SCHEMA_FINGERPRINT
SCHEMA_FINGERPRINT_ALGORITHM_VERSION
PACKAGE_VERSION
PACKAGE_REVISION
PROTOC_VERSION
CPP_GENERATOR_OPTIONS
BinanceMarketDataContracts_PROTOBUF_RUNTIME_VERSION
BinanceMarketDataContracts_PROTOBUF_RUNTIME_RREV
BinanceMarketDataContracts_PROTOBUF_RUNTIME_COMPATIBILITY
BinanceMarketDataContracts_PROTOBUF_RUNTIME_LINKAGE
CONTRACTS_SOURCE_REVISION
```

The authoritative runtime build identity is exact: version `6.33.5` and RREV
`ca5ff466767b31a1b496ec60247e105c`. The tested linkage/configuration identity is recorded
separately. Any compatibility statement or supported range is non-authoritative metadata and must
use a distinct name such as `BinanceMarketDataContracts_PROTOBUF_RUNTIME_COMPATIBILITY`; it must
not replace the exact version/RREV identity. Installed and public metadata uses the canonical
`BinanceMarketDataContracts_...` prefix. Shorter internal implementation symbols, if used, must be
explicitly mapped to these public names rather than exposed as a competing convention.

The Conan recipe will use `binance-market-data-contracts-cpp/0.1.0`, `CMakeToolchain`, `CMakeDeps`,
`requires("protobuf/6.33.5")`, `tool_requires("protobuf/6.33.5")`, and an exact lockfile RREV.
Full default package ID behavior is retained initially; compiler, architecture, C++ standard, build
type, Protobuf ABI, `shared`, and `fPIC` are package identity inputs where applicable.

## Fingerprint and identity lifecycle

The Version 1 implementation must keep the approved algorithm unchanged:

1. Generate the descriptor set from the exact source baseline and roots with imports included and
   source info excluded.
2. Normalize and validate proto-relative names; retain the four-file closure only.
3. Sort files by normalized name, normalize dependency indexes, and retain declaration order.
4. Clear source info/unknown fields and only explicitly classified language/generator-only options;
   fail closed on unclassified options.
5. Retain syntax, package, wire fields, presence, enums, oneofs, reserved/extension declarations,
   and semantic options.
6. Deterministically serialize with the pinned runtime and SHA-256 the exact canonical bytes.

Tests cover independent paths, traversal order, comment-only changes, selected and unrelated
changes, unknown options, wrong metadata, generator/runtime upgrades, and no per-message hashing.
Candidate digests are test outputs only until implementation and schema review approve a release.

| Identity | Planning status | Assignment point |
|---|---|---|
| Schema Version String | Existing contract values | `.proto` authority |
| Schema Baseline | `01d76a...` | Historical provenance already fixed |
| Schema Fingerprint | Not generated/approved | Reproducible implementation plus schema review |
| Algorithm Version | `1` | Architecture-approved |
| Package Version | Planned `0.1.0` | Release manifest/tag after acceptance |
| Package Revision | Not assigned | Accepted implementation/release revision |
| Contracts source revision | Future implementation commit | Package provenance |
| Conan RREV | Third-party/recipe revision | Conan lockfile |
| Conan PREV/package ID | Platform/options-specific | Binary package build |
| Generator identity | `libprotoc 33.5` plus options | Package metadata |
| Runtime identity | Exact C++ Protobuf `6.33.5` / RREV `ca5ff466767b31a1b496ec60247e105c`, plus tested linkage | Conan/CMake metadata |

The dependency lock selects a concrete package/revision tuple. The Schema Fingerprint does not
select a package, and a same-fingerprint Package Revision still requires an intentional lock update.
This single lifecycle table is authoritative for the distinct Schema Baseline, Schema Fingerprint,
Package Version, Package Revision, Contracts source SHA, Protobuf dependency RREV, Contracts Conan
RREV, Conan PREV, and binary package ID. No payload field may be used as identity authority.

## Tests and CI

The implementation must provide:

- C++ message construction, serialization, parsing, known enum values, optional presence, and
  fixed-fixture semantics for `DepthUpdate`, `ExchangeDepthSnapshot`, and
  `LocalOrderBookSnapshot`.
- Build-tree, install-tree, relocated-prefix, static, shared-after-export, Debug, and Release
  consumers for the exact supported matrix.
- Conan `create`, `test_package`, clean-cache installation, lockfile replay, and offline replay.
- Fingerprint reproducibility, closure exactness, wrong metadata, generator/runtime compatibility,
  comment-only, unrelated-schema, and option-classification tests.
- Duplicate-symbol link/map tests, two-consumer tests, shared-library plugin tests where claimed,
  and a no-consumer-regeneration test that fails on `protoc` or `.proto` use.
- An isolated Projection-like consumer proving Core configures with Protobuf/Contracts unavailable,
  while the optional adapter links the installed `BinanceMarketDataContracts::Protobuf` target.

Required PR CI is finite: Ubuntu GCC and Clang static Release/Debug, macOS AppleClang static
Release/Debug, install/Conan/offline/fingerprint/symbol/consumer tests, and fixed semantic tests.
Shared Release jobs on Ubuntu GCC and macOS AppleClang are gated until export tests pass. Main
repeats required jobs; nightly/release jobs add only declared combinations and artifact inspection.
The current Python/Buf CI remains unchanged by this planning PR.

## Local prerequisites

| Tool | Requirement |
|---|---|
| CMake 3.24+ and Ninja/Make | Native configure/build/install and consumers |
| GCC, Clang, AppleClang | Corresponding platform matrix rows |
| Python 3.12+ | Existing repository tooling and helper tests |
| Conan 2.31.2-compatible | Locked host/build graph and package tests |
| Buf 1.60.0 | Existing schema validation |
| Docker or equivalent Linux environment | Optional local Linux reproduction; CI is authoritative |

No system-global installation is planned. Caches, virtual environments, and build directories stay
repository-local or CI-managed.

## Implementation PR strategy

Use one controlled C-M4-001 implementation PR with reviewable commits or phase sections, keeping
`main` buildable and never exposing a partial exported target. Contracts remains **OPEN / BLOCKING**
until package, metadata, install consumers, Conan, reproducibility, symbol, offline, and independent
implementation review gates pass. Projection remains separate and may not consume a local
implementation candidate.

## Risk register

| Risk | Mitigation and detection |
|---|---|
| Protobuf compiler/runtime mismatch | Lock host/build `6.33.5`; export identity; compile/link compatibility matrix |
| Conan RREV drift | Exact lockfile RREV; clean-cache and offline replay |
| Shared visibility failure | Generated export macro; symbol and relocated shared-consumer tests |
| Static/shared/PIC mismatch | Full package ID; explicit `fPIC`; exact matrix only |
| Descriptor non-determinism | Canonical names/order/serialization; different-path vectors |
| Wrong import closure | Root/closure golden test; unrelated-file test |
| Include-layout drift | Install manifest and every-header consumer test |
| Duplicate symbols | One Contracts target; link-map and negative regeneration tests |
| Offline assumptions | Network-disabled Conan replay with locked cache |
| CMake relocation failure | Relocated install-prefix consumer |
| Projection boundary leakage | Core-only consumer with Protobuf unavailable |
| Identity conflation | Maintain one identity lifecycle table, prefixed public metadata names, separate assignment points, and no payload-field identity authority; detect metadata mismatch/rejection, cross-surface consistency, and release-manifest consistency failures |
| Linux/macOS divergence | Required GCC/Clang/AppleClang matrix; no untested claims |

## Implementation acceptance checklist

- [ ] Versioned installable C++ message package exists.
- [ ] `BinanceMarketDataContracts::Protobuf` is stable and exported.
- [ ] All seven non-service generated headers have stable installed paths.
- [ ] No mandatory gRPC dependency exists.
- [ ] Version 1 fingerprint is reproducible and its approved digest is exported.
- [ ] Schema, package, source, generator, runtime, Conan, and binary identities are separate.
- [ ] Declared static/shared/PIC claims pass the exact matrix.
- [ ] Conan `create`, `test_package`, clean-cache, and offline replay pass.
- [ ] Generated symbols are defined once and consumers do not regenerate.
- [ ] Build-tree, install-tree, relocation, and Projection-isolated consumers pass.
- [ ] Fixtures and optional presence remain compatible.
- [ ] No `.proto` or Pydantic semantic change is present.
- [ ] Provenance manifest and artifact inspection pass.
- [ ] Independent implementation review approves the package.

## Implementation plan review record

The implementation-author corrections were independently re-reviewed; all historical findings are
closed and the plan is approved.

| Finding | Status |
|---|---|
| IPR-1 | CLOSED |
| IPR-2 | CLOSED |
| IPR-3 | CLOSED |
| IPR-4 | CLOSED |
| IPR-5 | CLOSED |
| IPR-6 | CLOSED |
| IPR-7 | CLOSED |
| IPR-8 | CLOSED |
| IPR-9 | CLOSED |
| IPR-10 | CLOSED |

Independent C-M4-001 Implementation Plan Re-Review: **APPROVED** at reviewed head
`1bbf9e89787230900423b444eacbda1d434b1acb`; new P0 / P1 / P2 findings: **0 / 0 / 0**.

Implementation Planning: **APPROVED**. C-M4-001 Implementation Authorization remains **NO** —
pending merge of this approved planning PR.

## Authorization gate

The independent planning review has approved the plan:

```text
Implementation Planning: APPROVED
OD-CM4-001: CLOSED
OD-CM4-002: CLOSED
OD-CM4-003: CLOSED for initial planned version
OD-CM4-004: explicitly scoped for implementation/publication
OD-CM4-005: explicitly scoped for static/shared claims
OD-CM4-006: explicitly scoped for platform claims
OD-CM4-007: CLOSED for initial package
file-level implementation plan: APPROVED
test matrix: APPROVED
identity lifecycle: APPROVED
CMake/Conan dependency graph: APPROVED
```

The approval is recorded in this planning PR. Implementation authorization becomes effective only
after the approved planning PR is merged into `main` and a final state guard confirms the merge:

```text
C-M4-001 Implementation Authorization: NO — PENDING MERGE OF APPROVED IMPLEMENTATION PLAN
C-M4-001 Implementation: NOT STARTED
Projection M4 Implementation: NOT STARTED / BLOCKED
```

Next task: `Final State Guard + Ready Transition + Squash Merge PR #5`.
