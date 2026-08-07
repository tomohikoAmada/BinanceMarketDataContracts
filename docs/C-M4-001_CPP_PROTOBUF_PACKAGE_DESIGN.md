# C-M4-001: Contracts-Owned C++ Protobuf Package Design

## Status

- C-M4-001 Design: **PROPOSED**
- C-M4-001 Implementation: **NOT STARTED**
- External Review: **REQUIRED**
- Schema Baseline: `01d76a41929f36d89573159f5f458f9f1e378ada`
- Schema Fingerprint: **NOT YET APPROVED**
- Package Revision: **NOT YET ASSIGNED**
- Package Version: **NOT ASSIGNED**
- Projection M4 Implementation: **NOT STARTED / BLOCKED**
- Date: 2026-08-07

This document designs the Contracts-owned, versioned, installable C++ Protobuf message package
required by Projection M4. It does not implement CMake, Conan, C++ generated files, a package, or a
release. It changes no `.proto` file, field number, enum number, package name, or wire semantic.

## Problem statement

Projection M4 has an approved optional adapter boundary. The future
`BinanceMarketDataProjection::ProtoAdapter` must consume one Contracts-owned C++ generated-message
target without copying `.proto` files, generating from an arbitrary checkout, linking Protobuf into
Projection Core, or pulling Gateway/gRPC runtime into the adapter.

The current Contracts repository provides the authoritative `.proto` files, Python generated
stubs, Pydantic models, explicit Python adapters, fixtures, and tests. It does not yet provide a
C++ generated-message package, CMake package, Conan recipe, installed C++ include layout, or
reproducible schema/package metadata. C-M4-001 supplies the design for that missing distribution
boundary. The later implementation must remain a separate reviewed change.

## Source-of-truth order

The design uses evidence in this order:

1. The current `.proto` files define field numbers, enum numbers, package names, imports,
   `oneof` structure, and Protobuf optional presence.
2. Pydantic models and explicit adapters define Python business meaning and validation.
3. `AGENTS.md` defines repository constraints, generated-file ownership, and dependency boundaries.
4. `ARCHITECTURE.md` defines Contracts as a leaf module whose contracts remain PROPOSED or DRAFT.
5. `BinanceMarketData_Living_Architecture.md` defines module and language boundaries.
6. Accepted Contracts ADRs define the dual Domain/Wire strata and Gateway gRPC protocol.
7. Projection commit `7d8a655a5349ae5764bb6bd404993153c890ea02` defines the consumer requirements for
   the future C++ package and the Core/Adapter boundary.
8. Current Python packaging, codegen, tests, fixtures, and CI establish implementation facts.
9. Build convenience is lowest priority and cannot weaken the preceding sources.

Contracts remains the authority for the `.proto` source. Projection consumes the installed package;
it does not become a second schema authority.

## Evidence reviewed

### Contracts

- `AGENTS.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`, and the living architecture.
- Accepted ADR-0001, ADR-0006, ADR-0007, and ADR-0008; proposed ADR-0003 through ADR-0005.
- All current `.proto` files under `src/binance_market_data_contracts/proto/`.
- Pydantic models, the explicit `wire/adapters.py` mapping layer, and the contract registries.
- `proto_codegen.py`, `buf.yaml`, `scripts/check_buf_breaking.sh`, and `.github/workflows/ci.yml`.
- Descriptor, codegen, compatibility, fixture, adapter, documentation, and dependency-boundary tests.
- Valid/invalid fixtures, JSON Schema exports, and the package metadata in `pyproject.toml`.

### Projection

The following were read from merged commit `7d8a655a5349ae5764bb6bd404993153c890ea02`:

- `ARCHITECTURE.md`;
- `docs/M4_SNAPSHOTS_AND_PROTOBUF_BOUNDARY_DESIGN.md`;
- `docs/MILESTONES.md`; and
- `docs/adr/ADR-0006-protobuf-adapter-boundary.md`.

Those documents require a Contracts-owned C++ message target, stable installed includes, separate
schema/package identity, a canonical M4 descriptor fingerprint, generator/runtime metadata,
static/shared/PIC behavior, offline consumption, duplicate-symbol protection, and isolated
downstream consumers. They also require no mandatory gRPC dependency for M4 and no Protobuf
dependency in Projection Core.

## Current artifact audit

The audit is against Contracts main and schema baseline
`01d76a41929f36d89573159f5f458f9f1e378ada`. A count of zero below means the corresponding artifact
was not present in the tracked baseline or the repository tree searched by the stated probe.

| Artifact | Current status | Evidence |
|---|---|---|
| `.proto` sources | Present | 8 files under `src/binance_market_data_contracts/proto/binance_market_data/` |
| Generated Python stubs | Present | `src/binance_market_data/` contains 8 `*_pb2.py` files and 8 `.pyi` files |
| Generated Python gRPC stub | Present | `src/binance_market_data/gateway/v1/gateway_service_pb2_grpc.py` |
| Generated C++ `.pb.h` / `.pb.cc` | Absent | `find` probe returned 0 for both patterns |
| Generated C++ gRPC files | Absent | `find` probe returned 0 for `*_grpc.pb.h` and `*_grpc.pb.cc` |
| CMake project | Absent | No `CMakeLists.txt` or tracked CMake files |
| Installed CMake config package | Absent | No CMake project or package config exists |
| Exported CMake message target | Absent | No CMake target or export set exists |
| Conan 2 recipe | Absent | No `conanfile.py` exists |
| Installable C++ package | Absent | `pyproject.toml` defines only the Python distribution |
| Stable C++ include layout | Absent | Only Python package paths exist; no installed C++ include root |
| Standalone descriptor set | Absent | No `.desc` or `.protoset` artifact exists |
| Canonical schema fingerprint | Absent | No fingerprint, SHA-256, or canonicalization metadata exists |
| Package revision metadata | Absent | No C++ package or exported revision metadata exists |
| Generator/runtime metadata | Absent for C++ | Python pins are present; no C++ `protoc`/ABI/runtime export exists |
| Static/shared consumer tests | Absent | No C++ consumer or CMake test package exists |
| Duplicate-symbol tests | Absent | No C++ generated library or link test exists |

The current Python package is version `0.2.0a1`. Its runtime dependency is
`protobuf>=6.33.5,<7`; its optional Python wire dependency is `grpcio>=1.81.1,<2`; and the dev
environment pins `protobuf==6.33.5`, `grpcio==1.81.1`, and `grpcio-tools==1.81.1`. These Python
dependencies are evidence about the current Python workflow, not a C++ ABI contract.

## Goals

C-M4-001 will define an implementation that:

- owns C++ code generation and the one generated C++ symbol set in Contracts;
- publishes a versioned, installable C++ message package usable without the Contracts source tree;
- exports `BinanceMarketDataContracts::Protobuf` through a component-aware CMake package;
- installs generated headers under a stable path matching the proto-relative import layout;
- propagates Protobuf headers, runtime linkage, compile features, definitions, and platform link
  requirements through the target;
- keeps message types separate from future gRPC service code and runtime;
- exports separately validated schema, package, generator, and runtime metadata;
- supports reproducible build and offline package consumption;
- supports explicitly tested static/shared and PIC combinations; and
- gives Projection a clean handoff for its optional `ProtoAdapter` consumer.

## Non-goals

C-M4-001 does not:

- modify any `.proto` source or Pydantic semantic rule;
- change field numbers, enum numbers, package names, optional presence, or wire behavior;
- implement a Gateway, gRPC server/client, Recorder, History, or network runtime;
- add Protobuf or generated types to Projection Core;
- copy `.proto` files or generated C++ files into Projection;
- let an arbitrary consumer run code generation against an undocumented source checkout;
- publish a package, create a release, or close C-M4-001 in this design PR; or
- accept any contract or ADR.

## Consumer requirements from Projection M4

The future Projection adapter must be able to consume:

```cmake
find_package(BinanceMarketDataContracts CONFIG REQUIRED COMPONENTS Protobuf)
target_link_libraries(app PRIVATE BinanceMarketDataContracts::Protobuf)
```

The package must provide:

- generated C++ messages for the fixed message protos required by the Contracts baseline;
- stable installed includes following `binance_market_data/...` proto imports;
- a Contracts-owned CMake config and exported target;
- no mandatory gRPC runtime or generated gRPC service code for the message component;
- separate Schema Baseline, Schema Fingerprint, Algorithm Version, Package Revision, Package
  Version, `protoc` identity, C++ generator options, and Protobuf runtime compatibility metadata;
- explicit static/shared/PIC behavior and transitive dependency propagation;
- an offline-consumable package; and
- downstream and duplicate-symbol tests proving that consumers do not regenerate the messages.

## Package boundary

### Package and component names

The proposed CMake package name is:

```text
BinanceMarketDataContracts
```

The first component is:

```text
Protobuf
```

The future optional service component is reserved as:

```text
Grpc
```

`Grpc` is not implemented by C-M4-001 and is not a dependency of `Protobuf`.

### Exported message target

The proposed message target is:

```text
BinanceMarketDataContracts::Protobuf
```

It is a real selectable `STATIC` or `SHARED` library, controlled by the package build option and
Conan `shared` option. It is not an `INTERFACE` target that asks consumers to compile generated
sources. Generated `.pb.cc` files are compiled exactly once by the Contracts package build.

The target publicly propagates:

- generated and public include directories;
- the supported C++ standard requirement;
- Protobuf headers;
- the compatible Protobuf runtime target and link requirements;
- required platform link libraries; and
- generated export/visibility definitions where needed.

Static consumers must not infer link order or add a second Protobuf runtime manually.

### Message versus gRPC boundary

The message component contains generated C++ message types for the non-service message protos. The
current `gateway_service.proto` is a service definition and is excluded from the message target's
C++ generation set. A future `Grpc` component may generate service bindings and link gRPC, but it
must depend on `Protobuf` rather than the reverse.

The message target does not link `grpc::grpc++`, does not install gRPC generated service classes,
and does not own Gateway queues, subscriptions, backpressure, connection state, or a server.

### Include layout

The installed generated include root is proposed as:

```text
<prefix>/include/binance_market_data/common/v1/enums.pb.h
<prefix>/include/binance_market_data/common/v1/metadata.pb.h
<prefix>/include/binance_market_data/market/v1/market_events.pb.h
<prefix>/include/binance_market_data/projection/v1/snapshots.pb.h
<prefix>/include/binance_market_data/gateway/v1/gateway_messages.pb.h
<prefix>/include/binance_market_data/telemetry/v1/telemetry.pb.h
```

The path is derived from the current proto import root and package-relative filenames. It does not
rewrite `binance_market_data` to a new namespace or add a consumer-specific prefix. Generated
headers retain the namespace emitted from the existing package declarations.

The message package generates all current non-service message protos so that the C++ artifact is a
complete message package. The M4 fingerprint closure is narrower and is defined separately below.

## Code-generation ownership

### Selected model: Contracts-owned package-build generation

C-M4-001 selects **A: configure/package-build-time `protoc` generation owned by Contracts**, with
the Conan package recipe supplying the pinned compiler and runtime. Generated C++ sources are not
committed to this repository in the design PR and are never generated by Projection or an arbitrary
consumer. The generated headers and compiled library are present in the resulting C++ package.

The package build receives the exact proto source revision from Contracts and invokes the declared
`protobuf::protoc` tool. The build records the compiler identity, generator options, source revision,
and fingerprint in package metadata. A prebuilt Conan package can be consumed offline without
running `protoc`; building from source offline requires the pinned Conan build dependencies to
already exist in the local cache.

### Alternatives

| Model | Reproducibility | Offline/install experience | ABI/source risk | Decision |
|---|---|---|---|---|
| A. Contracts package-build generation | Pinned source, compiler, options, and runtime; reproducibility tested | Prebuilt packages need no compiler; cached source builds work offline | One owner and one symbol set; package build must lock tools | **Selected** |
| B. Release-time generation into a source archive | Strong if release archive provenance is verified | Excellent for consumers of the archive; more release plumbing | Generated archive can drift from Git source if not checked | Rejected for first implementation; may complement A later |
| C. Commit generated C++ to Contracts | Easy source build | Good offline behavior | Large generated diff, source drift, duplicate ownership | Rejected |
| D. Consumer-side arbitrary generation | Depends on consumer toolchain | Poor and inconsistent | ABI, include, and symbol drift; not a package boundary | Forbidden |
| E. Projection/Host generation from Contracts checkout | Path-dependent | Not independently installable | Violates Contracts ownership and Core boundary | Forbidden |
| F. FetchContent/submodule coupling | Revision can be pinned but source acquisition is coupled | Configure-time network/offline failure risk | Hidden codegen and duplicate targets | Rejected |

The later implementation may add generated sources to a signed source distribution, but that is a
release artifact derived from the same package-build process, not a second authority.

## Schema identity model

The following identities remain distinct:

| Identity | Meaning | Initial status |
|---|---|---|
| Schema Baseline | Historical Contracts Git commit fixing the reviewed `.proto` source semantics | `01d76a41929f36d89573159f5f458f9f1e378ada` |
| Schema Fingerprint | SHA-256 of the Version 1 canonical M4 descriptor closure | Not generated; not approved |
| Canonicalization Algorithm Version | Version of the descriptor normalization/serialization procedure | Proposed `1`; not accepted |
| Package Revision | Actual Contracts commit/release revision containing the C++ package | Future implementation revision — not assigned |
| Package Version | Distribution SemVer for the C++ package | Independent; not assigned |
| Generator Identity | `protoc`, C++ generator options, and related build metadata | Proposed; implementation must record exact values |
| Runtime Compatibility | Supported C++ Protobuf runtime and linkage/build combinations | Proposed; exact matrix open |

The Schema Baseline is provenance, not a package revision. A later Contracts commit containing the
implementation will necessarily have a different source revision. A matching Schema Fingerprint
does not select a package: the Projection dependency lock must name the intended package revision
and version explicitly.

## Canonical descriptor fingerprint — Version 1

### Purpose and limits

The fingerprint identifies the reviewed M4 wire descriptor closure. It does not claim to encode all
Pydantic business semantics, fixture rules, or the Python adapter implementation. Those remain
covered by the Contracts semantic tests and are checked separately by the implementation package
and Projection integration.

No digest is generated in this design PR.

### Root files

Version 1 roots are the current proto files that contain the three M4 messages:

```text
binance_market_data/market/v1/market_events.proto
binance_market_data/projection/v1/snapshots.proto
```

`DepthUpdate` and `ExchangeDepthSnapshot` are in `market_events.proto`; `LocalOrderBookSnapshot` is
in `snapshots.proto`. Root descriptors are selected at file granularity. Therefore all declarations
in those root files are included, including other messages in the same files. A later split or
reorganization is a reviewed schema change.

### Transitive closure

The closure includes each root and every recursively imported proto, deduplicated by normalized
proto-relative filename. In the current baseline this includes:

```text
binance_market_data/common/v1/enums.proto
binance_market_data/common/v1/metadata.proto
binance_market_data/market/v1/market_events.proto
binance_market_data/projection/v1/snapshots.proto
```

`identifiers.proto`, `gateway_messages.proto`, `gateway_service.proto`, and `telemetry.proto` are
not in the current M4 closure because the roots do not import them. The future message package may
still install their generated message types where applicable; package contents and M4 schema
identity are separate concerns.

### Service policy

Gateway/gRPC service descriptors are not roots and are not imported by the current roots. A service
declaration appearing in a selected root in a future schema would remain in that selected file's
descriptor and would be included; Version 1 never edits descriptors to hide a selected-file
service. `gateway_service.proto` is reserved for the future `Grpc` component.

### Canonicalization procedure

The implementation must perform these steps:

1. Start from the exact Schema Baseline source tree and the declared `protoc` version.
2. Invoke `protoc` with the Version 1 roots, `--proto_path` set to the repository-relative proto
   root, `--include_imports`, and without `--include_source_info`.
3. Reject absolute or `..` proto paths in the descriptor set. Normalize every filename to UTF-8,
   forward-slash, proto-root-relative form without `./` or duplicate separators.
4. Retain only the root/recursive-import closure. Reject duplicate normalized names or a descriptor
   whose declared name does not equal its normalized source identity.
5. Clear `source_code_info` wherever present. Comments, source locations, and formatter-only source
   changes therefore do not affect the digest.
6. Clear unknown protobuf fields in every descriptor and nested descriptor used by the canonical
   set. Unknown options are not silently trusted; an unclassified custom option requires an
   implementation review before Version 1 can process it.
7. Normalize `FileDescriptorProto.dependency` names lexicographically and remap
   `public_dependency` and `weak_dependency` indexes to the normalized order. Declaration order
   inside a file is retained exactly because it is part of the source descriptor representation.
8. Sort `FileDescriptorProto` entries lexicographically by normalized filename. Do not sort messages,
   fields, oneofs, enums, enum values, reserved ranges, extension ranges, or service methods.
9. Retain syntax/edition, package, normalized dependencies, messages, fields, labels, types,
   `json_name`, oneofs, maps, enums, enum numbers, reserved declarations, extension declarations,
   services present in selected files, and every option affecting wire or contract semantics.
10. Remove only explicitly classified language/package-generation options from the canonical
    descriptor. For the current source this includes `go_package`; the Version 1 implementation
    must also classify equivalent Java, C#, PHP, Objective-C, Ruby, and generator-only options.
11. Remove C++ generator/ABI options such as arena or visibility choices from the schema digest and
    export them in Generator Identity instead. A change in those options must not be mistaken for a
    wire-schema change, but it still requires package compatibility review.
12. Retain semantic deprecation, presence, packedness, map-entry, reserved-name, and field-option
    information. A field option is removed only if the algorithm's explicit classification proves it
    cannot affect wire or contract semantics.
13. Deterministically serialize the normalized `FileDescriptorSet` using the pinned Protobuf
    runtime's deterministic serialization mode. The canonical byte stream is the exact serialized
    bytes, with no text formatting, path prefix, timestamp, host name, source archive name, or
    package revision appended.
14. Compute SHA-256 over those bytes. The lowercase hexadecimal digest is the Schema Fingerprint.

The canonicalizer must be an executable, hermetic tool in the future implementation package, with
golden input/output tests. It must fail closed when it encounters an option or descriptor feature
not covered by Version 1 rather than silently dropping it.

### Reproducibility and upgrades

The implementation must reproduce the same digest from independent clean checkouts located at
different absolute paths, with different file traversal order and without source-info data. A
comment-only change must not change the digest because source info is excluded, although the Git
source revision and package provenance still change.

A change in an M4 root or transitive import changes the fingerprint when it changes retained
descriptor semantics. A change outside the closure does not change the M4 fingerprint. A change to
an imported file's path or package identity changes the closure and therefore requires review.

`protoc` and Protobuf runtime upgrades are never silently accepted. The implementation must rerun
independent reproducibility and cross-version descriptor tests. If the normalized digest remains
identical, the package still records the new Generator Identity and requires a dependency-lock
review. If canonical bytes or digest change for an otherwise intended semantic-equivalent upgrade,
the implementation must stop and obtain a schema/fingerprint review; a new algorithm version is
required if the canonical procedure itself changes.

The fingerprint is never computed for each message at runtime. It is package/configuration metadata,
optionally checked once by a defensive startup probe. No message-reported value can invent a source
revision or package identity.

### Export and validation

The package must export the approved values through CMake config metadata and a C++ constexpr
metadata header after implementation. The design names are:

```text
BinanceMarketDataContracts_SCHEMA_BASELINE
BinanceMarketDataContracts_SCHEMA_FINGERPRINT
BinanceMarketDataContracts_SCHEMA_FINGERPRINT_ALGORITHM_VERSION
BinanceMarketDataContracts_PACKAGE_REVISION
BinanceMarketDataContracts_PACKAGE_VERSION
BinanceMarketDataContracts_PROTOC_VERSION
BinanceMarketDataContracts_CPP_GENERATOR_OPTIONS
BinanceMarketDataContracts_PROTOBUF_RUNTIME_RANGE
```

The fingerprint and package revision are not populated in this design PR. CMake configuration must
fail when required metadata is missing, the approved Schema Baseline/Fingerprint does not match, the
dependency lock selects a different package revision without an explicit update, or the generator/
runtime metadata is incompatible.

## Generated C++ package design

### Proposed CMake sketch

The following is an architecture sketch, not a checked-in implementation:

```cmake
cmake_minimum_required(VERSION 3.24)
project(BinanceMarketDataContracts VERSION 0.1.0 LANGUAGES CXX)

find_package(Protobuf CONFIG REQUIRED)

set(BMD_CONTRACTS_MESSAGE_PROTOS
    common/v1/enums.proto
    common/v1/identifiers.proto
    common/v1/metadata.proto
    market/v1/market_events.proto
    projection/v1/snapshots.proto
    gateway/v1/gateway_messages.proto
    telemetry/v1/telemetry.proto)

# Future implementation: invoke protobuf::protoc once for the fixed source set,
# emit include/binance_market_data/.../*.pb.h and private generated .pb.cc files,
# and compile the generated sources exactly once.
add_library(bmd_contracts_protobuf ${BMD_CONTRACTS_LIBRARY_TYPE} ${GENERATED_CPP_SOURCES})
add_library(BinanceMarketDataContracts::Protobuf ALIAS bmd_contracts_protobuf)
target_compile_features(bmd_contracts_protobuf PUBLIC cxx_std_20)
target_include_directories(bmd_contracts_protobuf
  PUBLIC $<BUILD_INTERFACE:${GENERATED_INCLUDE_DIR}>
         $<INSTALL_INTERFACE:include>)
target_link_libraries(bmd_contracts_protobuf PUBLIC protobuf::libprotobuf)

# Future implementation: install generated headers, export target/config files,
# expose the metadata variables, and keep Grpc in a separate component.
```

The exact generated source command must use the pinned `protobuf::protoc` target and an explicit
proto root. It must not download dependencies at configure time, use `FetchContent`, or invoke the
Python `grpc_tools.protoc` environment as an implicit C++ compiler.

The installed config will use `CMakePackageConfigHelpers`, `configure_package_config_file`, and
`write_basic_package_version_file`. It will define `BinanceMarketDataContracts_FOUND`, expose the
metadata variables, load only the requested `Protobuf` component, and call
`check_required_components(BinanceMarketDataContracts)`. Requesting only `Protobuf` will not call
`find_dependency(gRPC)`.

### Build-tree and install-tree consumption

The future implementation must test both:

```cmake
find_package(BinanceMarketDataContracts CONFIG REQUIRED COMPONENTS Protobuf)
target_link_libraries(consumer PRIVATE BinanceMarketDataContracts::Protobuf)
```

against a build-tree package and an installed prefix. The installed package must work without the
Contracts source tree and without consumer-side generated sources. A requested `Grpc` component must
fail clearly when it was not built, while a consumer requesting only `Protobuf` must remain unaware
of gRPC.

### Metadata API

The implementation should install a standard-library-only header at:

```text
include/binance_market_data/contracts_metadata.hpp
```

with a namespace such as `binance_market_data::contracts` and `inline constexpr std::string_view`
values for the same identities exported by CMake. The header is generated as package metadata; it is
not a second schema source and does not contain the descriptor itself. It must not be added to the
current design branch as an implementation artifact.

## Conan 2 design

### Package coordinates and ownership

The proposed Conan package name is:

```text
binance-market-data-contracts-cpp
```

It is a separate C++ artifact from the Python distribution
`binance-market-data-contracts==0.2.0a1`. The artifacts may be built from the same Contracts Git
source revision, but they do not share a version automatically. A future C++ release initially
starts at proposed SemVer `0.1.0`; the exact released version remains unassigned until the
implementation and review gates pass.

The message package is a separate recipe/artifact from any future gRPC package. The first recipe
has no `with_grpc` option that could accidentally add gRPC transitively. A future
`binance-market-data-contracts-grpc` package or separate `Grpc` component may depend on the message
package.

### Settings, options, and dependencies

The future recipe must declare and test:

- Settings: `os`, `arch`, `compiler`, `compiler.version`, `compiler.cppstd`, and `build_type`.
- Options: `shared` and `fPIC` where supported; no network, gRPC, or arbitrary-codegen option.
- C++ requirement: C++20 for the package's public target and metadata header.
- Runtime dependency: the C++ Protobuf package, initially tested at exact `6.33.5`; the supported
  range is not widened until the C++ ABI/configuration matrix proves it.
- Build requirement: the matching pinned Protobuf compiler/tool package supplying `protoc`.
- CMake integration: `CMakeToolchain` for settings/options and `CMakeDeps` for imported targets and
  `find_package(Protobuf CONFIG REQUIRED)`.

The exact Conan Center coordinate and whether one Protobuf recipe exports both runtime and compiler
tools are an Open Decision. The implementation must lock the actual packages rather than infer a
tool from the host or Python virtual environment.

### Package ID and metadata

Use the default full Conan package ID behavior initially. The package ID must vary with compiler,
architecture, C++ standard, build type, Protobuf ABI, `shared`, and `fPIC` where applicable. Do not
claim binary compatibility across arbitrary toolchains. The source Git commit, Conan recipe
revision, binary package ID, and exported `PACKAGE_REVISION` are distinct and must be reported in
package metadata.

The package recipe must expose CMake metadata without using the Schema Fingerprint as a package
selection shortcut. A matching fingerprint with a changed package revision still requires an
intentional Projection lock update.

### Offline behavior

Prebuilt Conan package consumption must work with no network and no `protoc` invocation. Source
package creation must work offline when the locked source and build/runtime dependencies are already
in the local Conan cache. The recipe must not use `FetchContent`, configure-time downloads, or an
undocumented source checkout.

## Static/shared/PIC model

The initial supported matrix is explicit rather than universal:

| Combination | Initial design position |
|---|---|
| Linux GCC, static Contracts + pinned static/shared Protobuf | Required implementation test |
| Linux Clang, static Contracts + pinned static/shared Protobuf | Required implementation test |
| macOS AppleClang, static Contracts + pinned static/shared Protobuf | Required implementation test |
| Linux/macOS shared Contracts | Required only after export-symbol tests pass |
| Windows/MSVC | Not an initial acceptance target; no support claim |

For static builds, `fPIC` is required on ELF/Mach-O when the static library may be linked into a
shared consumer. For shared builds, generated message classes must have an explicit export strategy:
the implementation should use a generated API macro/visibility configuration and verify Linux,
macOS, and any later Windows policy rather than relying on accidental default visibility. Debug and
Release package IDs are distinct; mixing them is unsupported unless the package manager and tests
prove it safe.

The target must propagate the Protobuf runtime linkage for static and shared consumers. Consumers
must not compile a second generated source set or guess platform libraries.

## Versioning and compatibility

### Six independent concepts

The following must never be substituted for one another:

1. **Schema Version String** such as `depth-update.v1`, a field-level contract value.
2. **Schema Baseline Commit**, the reviewed source provenance commit.
3. **Schema Fingerprint**, the canonical M4 descriptor digest.
4. **Package Version**, C++ distribution SemVer.
5. **Package Revision**, the exact implementation/source/distribution revision selected by the lock.
6. **Generated C++/Protobuf ABI**, the compiler, generator, runtime, visibility, and binary linkage
   contract.

### Change classification

| Change | Classification |
|---|---|
| Same descriptor closure and same generator/runtime, package-only fix | C++ package patch; dependency lock review still required |
| Same Schema Fingerprint, different source/package revision | Schema-compatible package revision; explicit lock update required |
| New optional C++ packaging metadata with no wire change | Package minor/patch depending on consumer API impact |
| Changed generator/runtime/visibility ABI | Generator/runtime compatibility change; package rebuild and matrix review |
| Wire field/enum/presence/package/ordering semantic change | Fingerprint change and reviewed wire compatibility decision; likely new contract major |
| Breaking C++ public API or ABI | C++ package major, independent of wire version |
| Comment-only proto change | Fingerprint unchanged under Version 1; source/package provenance still changes |
| Unrelated proto outside the M4 closure | No M4 fingerprint change; may affect other package consumers/components |

A different Package Revision with the same fingerprint still needs a dependency-lock update because
the revision can change generated ABI, build flags, transitive dependencies, metadata, or symbol
ownership. Schema compatibility is necessary but not sufficient for binary/package selection.

## Generator and runtime identity

The package must export at least:

- exact `protoc` version and executable provenance;
- C++ generator invocation/options, including generated export/visibility options;
- full versus lite runtime choice;
- C++ standard and ABI-affecting compile definitions;
- Protobuf C++ runtime exact version/range and linkage mode;
- static/shared/PIC policy; and
- the canonicalization algorithm version.

The initial implementation proposal is full `libprotobuf`, not lite, because Projection M4 needs the
normal generated message API and descriptor-compatible package checks. This is a proposed design
choice, not an implementation claim. Switching to lite would be a reviewed generator/runtime
compatibility change.

## Consumer and test-package design

### CMake consumers

The future implementation must provide isolated consumers for:

1. Build-tree message-only use;
2. Install-tree message-only use;
3. Static Contracts with each supported Protobuf linkage mode;
4. Shared Contracts after symbol-export verification; and
5. Projection-like inclusion of `market_events.pb.h`, `snapshots.pb.h`, common headers, and the
   metadata header without gRPC discovery.

Each consumer must construct `DepthUpdate`, `ExchangeDepthSnapshot`, and
`LocalOrderBookSnapshot`, exercise optional presence, serialize, parse, and compare known fields.

### Conan test package

The future `test_package` must:

- use `CMakeDeps`/`CMakeToolchain` and `find_package` the installed package;
- include generated message headers and `contracts_metadata.hpp`;
- construct and serialize/parse M4 messages;
- verify Schema Baseline, Fingerprint, Algorithm Version, Package Revision, Package Version, and
  Generator/Runtime metadata;
- link one executable through `BinanceMarketDataContracts::Protobuf`; and
- prove that no gRPC target or second generated source is needed.

### Duplicate-symbol tests

The implementation must test two independent consumer targets linking the same package and a
consumer that includes multiple generated headers. Link/map-file or object inspection must prove:

- exactly one generated definition for each message symbol;
- no generated `.cc` is compiled by the consumer;
- no copied schema or second generated target exists; and
- static/shared link interfaces resolve one compatible Protobuf runtime.

## Fingerprint and compatibility tests

The future implementation must test:

- independent clean checkouts at different absolute paths;
- different proto traversal order;
- absence of source info and comment-only changes;
- deterministic declaration/file ordering;
- selected M4 descriptor changes;
- unrelated schema changes outside the M4 closure;
- wrong Schema Baseline, wrong Fingerprint, wrong Algorithm Version, and missing metadata;
- same fingerprint with a different Package Revision requiring a lock update;
- `protoc` version changes and generator-option changes;
- compatible/incompatible Protobuf runtime metadata;
- optional presence, enum zero/unknown values, field numbers, serialization, and parsing; and
- descriptor identity compared with the fixed baseline.

The tests must never calculate a descriptor hash for every message. The fingerprint is built or
verified at package/configuration boundaries only.

## CI design

The current CI validates Python quality, JSON Schema export/drift, Python codegen drift, Buf format/
lint/build/breaking behavior, fixtures, adapters, descriptors, and Python wheel isolation. It does
not validate a C++ artifact because none exists at the baseline.

The future implementation PR should add separate jobs for:

- C++ configure/build/test on Ubuntu GCC;
- C++ configure/build/test on Ubuntu Clang;
- C++ configure/build/test on macOS AppleClang;
- install-tree CMake consumers;
- Conan `create` and `test_package` with a locked cache;
- canonical fingerprint reproducibility from clean paths;
- static/shared/PIC combinations supported by the declared matrix;
- Protobuf compiler/runtime compatibility checks;
- artifact inspection for headers, libraries, metadata, and no gRPC dependency;
- duplicate-symbol/link-interface checks; and
- fixed-fixture message semantic and optional-presence checks.

PR validation must run only the combinations declared supported and fail on missing metadata or
undeclared dependency acquisition. Main validation repeats the matrix after merge. Release
validation additionally signs/archives the source and binary package, verifies the package contents,
and records the source/package/reproducibility metadata. Publication is a separate release action;
this Design PR publishes nothing.

## Release and publication design

The future release pipeline must:

1. select an immutable Contracts source commit;
2. build from a locked Protobuf compiler/runtime dependency set;
3. generate the package and canonical fingerprint in a clean environment;
4. compare the digest and Schema Baseline with reviewed release metadata;
5. run CMake consumers and Conan `test_package`;
6. inspect headers, libraries, symbols, dependencies, and metadata;
7. produce a source/binary artifact manifest containing Package Version, Package Revision, Conan
   recipe revision, package ID, Schema Baseline, Fingerprint, Algorithm Version, `protoc`, and
   runtime identity; and
8. publish only after an independent implementation review.

No release or package publication occurs from this Design PR.

## Security and supply-chain design

- Pin the C++ Protobuf runtime and compiler in a Conan lockfile.
- Record the exact `protoc` version and generator options used for every package.
- Keep generated-source provenance tied to the immutable Contracts source revision and descriptor
  fingerprint.
- Verify source archives and package contents before publication.
- Distinguish Conan recipe revision, binary package ID, Contracts source revision, Package Version,
  and Schema Fingerprint.
- Support offline consumption from a verified local package/cache.
- Do not use configure-time arbitrary network downloads.
- Do not use `FetchContent`, submodules, or undocumented Host injection.
- Fail closed on missing or unclassified descriptor options and compatibility metadata.
- Do not trust a message field to report package identity.
- Do not run descriptor hashing on every message.
- Keep gRPC and Gateway runtime out of the message package's dependency graph.

## Alternatives considered and rejected

### Package ownership

- **Projection-owned generation**: rejected because it makes Projection a second schema/codegen
  authority and violates Core/Adapter ownership.
- **Host-injected arbitrary target**: rejected because include layout, ABI, revision, and symbols
  vary by integration tree.
- **Contracts source-tree consumption**: rejected because installed consumers cannot be independent.
- **Copied `.proto` files**: forbidden because they create silent schema drift.

### Code generation

- **Consumer-side generation**: rejected because tool/runtime/ABI choices become uncontrolled.
- **Committed C++ generated files in this repository**: rejected for the first package design because
  generated-source drift and duplicate ownership are harder to control; generated package outputs
  remain Contracts-owned build artifacts.
- **FetchContent/submodule**: rejected because it couples source acquisition and code generation to
  configure-time state.

### Runtime boundary

- **Link gRPC into the message target**: rejected because M4 only needs message types and gRPC is M6
  Gateway runtime scope.
- **Use Protobuf lite without evidence**: rejected initially because the required C++ API and
  descriptor/consumer matrix are not yet validated against lite.
- **Put Protobuf in Projection Core**: rejected by accepted Projection ADR-0006 and the merged M4
  design.

### Identity

- **Use Schema Baseline as Package Revision**: rejected because implementation/distribution revisions
  necessarily occur after the historical schema baseline.
- **Use Schema Fingerprint as Package Version**: rejected because wire compatibility and C++ ABI/API
  compatibility evolve independently.
- **Hash each message descriptor at runtime**: rejected for cost, determinism, and incorrect
  responsibility; package/configuration integrity is sufficient.

## Open decisions

The architecture is proposed, not accepted. These decisions must be closed with evidence in the
implementation planning/review cycle:

| ID | Question | Recommended answer | Alternatives | Impact | Blocks implementation? | Evidence required | Owner |
|---|---|---|---|---|---:|---|---|
| OD-CM4-001 | Which Conan package provides the C++ runtime/compiler? | Pin the exact Protobuf `6.33.5` package/tool set first | A verified compatible patch range | Dependency lock, ABI, offline build | Yes | Conan availability and clean-cache build | Contracts implementation owner |
| OD-CM4-002 | Are generated C++ sources built at package time or shipped in source archives? | Package-build generation; optional signed source archive later | Release-generated source archive | Provenance and offline source build | No beyond implementation gate | Reproducible package build | Contracts implementation owner |
| OD-CM4-003 | What exact C++ Package Version is released first? | Independent C++ version, proposed initial `0.1.0` | Reuse Python `0.2.0a1` | Release cadence and lock clarity | Yes for publication | Release/versioning review | Contracts maintainer |
| OD-CM4-004 | What exact Conan recipe/package coordinates are published? | `binance-market-data-contracts-cpp` | Unified Python/C++ recipe | Consumer discovery and migration | Yes for publication | Recipe and test package | Contracts maintainer |
| OD-CM4-005 | Which shared-library export strategy is used? | Generated API macro plus platform-specific visibility tests | Default visibility only; static-only first release | ABI and platform support | Yes for shared support | Linux/macOS symbol and consumer tests | Contracts implementation owner |
| OD-CM4-006 | Which static/shared combinations are supported initially? | Linux GCC/Clang and macOS AppleClang with explicit tested matrix | Static-only first release; Windows later | CI and package IDs | Yes for claimed combinations | Matrix results | Contracts implementation owner |
| OD-CM4-007 | Is a semantic manifest needed beside the descriptor fingerprint? | Keep Pydantic/adapter semantics separately tested; add a manifest only if package checks need it | Hash Python semantics into the descriptor digest | Prevents identity conflation | No for initial descriptor package | Projection/Contracts integration review | Contracts and Projection maintainers |

An Open Decision is not a license to weaken the fixed `.proto` or Projection consumer requirements.

## Implementation sequence

The following steps belong to a future independent C-M4-001 Implementation PR and are not executed
here:

1. Add the CMake project and metadata skeleton without changing proto sources.
2. Add the Version 1 canonical descriptor generation and closure tests.
3. Add pinned C++ message code generation owned by the Contracts package build.
4. Add the selectable message library and `BinanceMarketDataContracts::Protobuf` alias.
5. Add generated header install, CMake config/version files, component discovery, and metadata.
6. Add static/shared/PIC behavior and the generated visibility/export strategy.
7. Add the C++ constexpr metadata API.
8. Add build-tree and install-tree CMake consumers.
9. Add the Conan 2 recipe, lock integration, and `test_package`.
10. Add descriptor/fingerprint reproducibility and wrong-metadata rejection tests.
11. Add duplicate-symbol and no-consumer-regeneration tests.
12. Add Ubuntu GCC/Clang and macOS AppleClang CI matrix jobs.
13. Add release/package inspection and provenance documentation.
14. Obtain independent external implementation review before closing C-M4-001.

## Acceptance gates

C-M4-001 remains **OPEN / BLOCKING** until a future implementation review proves all of the
following:

- a versioned installable C++ message package exists;
- `BinanceMarketDataContracts::Protobuf` is exported and stable;
- the installed include layout follows proto-relative imports;
- the message target has no mandatory gRPC dependency;
- Version 1 fingerprint generation is reproducible and its approved digest is exported;
- Schema Baseline, Fingerprint, Algorithm Version, Package Revision, Package Version, and
  Generator/Runtime metadata are exported separately;
- declared static/shared/PIC combinations are verified;
- Conan package creation, cache/offline consumption, and `test_package` pass;
- generated symbols are defined once and consumers do not regenerate them;
- Projection's isolated adapter consumer configures, includes, links, and serializes successfully;
- fixed fixtures and optional presence semantics remain compatible;
- no `.proto` or Pydantic semantic change was smuggled into the implementation; and
- independent external implementation review approves the package.

Until then:

```text
C-M4-001 Design: PROPOSED
C-M4-001 Implementation: NOT STARTED
Projection M4 Implementation: NOT STARTED / BLOCKED
```

## Projection integration handoff

After C-M4-001 implementation is independently approved and the package is available, Projection
must consume it through its optional `ProtoAdapter` target. Projection must:

- lock the intended Package Version and Package Revision;
- verify the approved Schema Baseline, Fingerprint, Algorithm Version, and Generator/Runtime
  metadata at configure/package boundaries;
- include only installed Contracts generated headers;
- keep `BinanceMarketDataProjection::Core` independent of Protobuf and Contracts;
- link `BinanceMarketDataProjection::ProtoAdapter` publicly to
  `BinanceMarketDataContracts::Protobuf`; and
- run the Core-only and adapter install-consumer tests described in the merged M4 design.

The Contracts package does not authorize Projection M4 implementation. C-M4-001 must first pass its
own implementation and external review gates.

## Review boundary

This document is a Design-only proposal. The next step is:

```text
Independent C-M4-001 Architecture Review — Round 1
```
