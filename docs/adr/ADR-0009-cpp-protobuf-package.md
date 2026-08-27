# ADR-0009: Contracts-owned C++ Protobuf message package

## Status

ACCEPTED

## Date

2026-08-07

## Context

Projection M4 requires a Contracts-owned, versioned, installable C++ package containing the
generated Protobuf message types. The current Contracts baseline owns the `.proto` sources and
Python wire artifacts, but does not yet provide C++ generated messages, an installed include
layout, an exported CMake target, a Conan package, or C++ schema/package metadata.

The approved Projection M4 design requires the message package to remain outside Projection Core,
to be consumable by an optional adapter, and to avoid a mandatory Gateway/gRPC runtime dependency.
The historical schema baseline and future package revisions also have different identities and
must not be conflated.

## Decision

The proposed architecture is:

1. **Contracts owns the package.** BinanceMarketDataContracts owns the authoritative `.proto`
   sources, C++ code-generation workflow, package metadata, install layout, and published C++
   artifact.
2. **Consumers use the exported package target.** Consumers discover the installed CMake package
   `BinanceMarketDataContracts` and link `BinanceMarketDataContracts::Protobuf`; they do not copy
   Protobuf sources or generate a second symbol set from an arbitrary checkout.
3. **Schema and package identities remain separate.** Schema Baseline, canonical descriptor
   fingerprint, fingerprint algorithm version, Package Version, Package Revision, and
   generator/runtime metadata are distinct exported values.
4. **Message and gRPC targets remain separate.** The proposed `Protobuf` component contains only
   generated message types and the Protobuf runtime dependency. Any future gRPC generated code or
   Gateway runtime integration must use a separate optional component such as
   `BinanceMarketDataContracts::Grpc` and is outside C-M4-001.
5. **Consumer-side arbitrary generation is forbidden.** Projection and Hosts consume the
   Contracts-owned generated package and must not regenerate or copy the Contracts schema.

The detailed package, fingerprint, CMake, Conan, compatibility, test, CI, and release design is
in [`docs/C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md`](../C-M4-001_CPP_PROTOBUF_PACKAGE_DESIGN.md).

## Consequences

- The first implementation must establish one reproducible generated C++ message ownership path.
- The package must expose enough metadata for consumers to verify schema and generator identity
  without deriving Package Revision from a schema digest.
- C++ package versioning may proceed independently from the current Python distribution version.
- Static/shared, Protobuf runtime, compiler, and platform support claims require implementation
  and consumer-test evidence before they are declared supported.
- C-M4-001 remains **OPEN / BLOCKING** until the implementation acceptance gates pass.
- C-M4-001 Design is **APPROVED** and C-M4-001 Implementation remains **NOT STARTED**.

## Rejected alternatives

- Projection-owned C++ generation or copied `.proto` files: rejected because this creates a second
  schema authority and permits silent schema drift.
- Consumer-owned arbitrary generation: rejected because generator, runtime, and ABI choices become
  uncontrolled at each consumer.
- A message target that links gRPC: rejected because M4 needs message types only and Gateway/gRPC
  runtime belongs to the later M6 boundary.

## Acceptance record

Accepted: `2026-08-07`

Acceptance basis: Independent C-M4-001 Architecture Review — Round 1

Reviewed head: `c9c6f59dbb7f18cc2d630383f67619d9f0429d1b`

Architecture blocking findings: **0**

ADR acceptance records the architecture only. It does not imply that any Domain or Wire Contract
is accepted, does not close C-M4-001, and does not authorize C-M4-001 or Projection M4
implementation while the implementation-blocking Open Decisions remain open.

## M6 follow-on implementation note

The separately authorized M6 Contracts prerequisite exports the optional frozen target
`BinanceMarketDataContracts::Grpc`. ADR-0010 corrects its package-manager boundary: `Grpc` is
provided by the independent `binance-market-data-contracts-grpc-cpp/0.1.0` Conan artifact and
`BinanceMarketDataContractsGrpc` CMake package. It generates only the Gateway service and gRPC
stubs, links the one base `Protobuf` target, and keeps gRPC out of the message artifact's host and
build graphs. This note records follow-on implementation status; it does not rewrite the
historical C-M4-001 design or claim that the Gateway runtime exists.
