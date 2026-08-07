# ADR-0009: Contracts-owned C++ Protobuf message package

## Status

PROPOSED

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
- C-M4-001 Design remains **PROPOSED** and C-M4-001 Implementation remains **NOT STARTED**.

## Rejected alternatives

- Projection-owned C++ generation or copied `.proto` files: rejected because this creates a second
  schema authority and permits silent schema drift.
- Consumer-owned arbitrary generation: rejected because generator, runtime, and ABI choices become
  uncontrolled at each consumer.
- A message target that links gRPC: rejected because M4 needs message types only and Gateway/gRPC
  runtime belongs to the later M6 boundary.

## Review requirement

This ADR is **PROPOSED**, not ACCEPTED. It requires an independent C-M4-001 Architecture Review
before implementation begins. Acceptance of this ADR must not be inferred from the existing
accepted wire-contract or Gateway ADRs.
