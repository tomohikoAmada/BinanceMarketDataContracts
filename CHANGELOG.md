# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0a1] — Unreleased

### Added

- Protobuf wire contracts for cross-language data exchange
- gRPC service definitions for Gateway streaming
- Pydantic gateway contracts for type-safe IPC
- Explicit adapters between Pydantic domain contracts and Protobuf wire contracts
- Wire Contract Registry for tracking Protobuf message versions
- Proto codegen with Buf configuration
- Gateway-streaming protocol documentation
- ADR-0007: Dual-contract strata (Pydantic Domain + Protobuf Wire)
- ADR-0008: Gateway IPC via gRPC Server Streaming + Protobuf
- Transcript tests for adapter correctness
- Adapter round-trip tests ensuring lossless Pydantic ↔ Proto conversion
- Descriptor tests validating generated Protobuf descriptors
- C-M4-001 implementation candidate for a Contracts-owned versioned installable C++ Protobuf
  message package, including CMake and Conan consumers, fingerprinting, and provenance metadata

### Changed

- Version 0.1.0a1 → 0.2.0a1
- Approved the C-M4-001 architecture for the Contracts-owned C++ Protobuf message package.
- Accepted ADR-0009 after an independent architecture review with zero blocking findings.
- Implemented and merged the C-M4-001 Contracts-owned C++ Protobuf package; the package is not
  published and its formal package revision remains unassigned.
- Recorded the independent C-M4-001 implementation acceptance: initial review CHANGES REQUESTED,
  re-review APPROVED at `4e5d3d846afba982ab5e48d2737bc40560e34a6c` (CI `31167981350`, 15/15 PASS),
  IIR-1 through IIR-5 CLOSED, P0/P1/P2 = 0.
- Formally approved the C-M4-001 M4 Schema Fingerprint (Algorithm Version 1):
  `33286fb1d624f4dd0c827010e93113f523c7f37dc4f6ae526361d2b0c61626c0`.
- Confirmed proven static support (Ubuntu x86_64 GCC/Clang Release/Debug; macOS arm64 AppleClang
  Release/Debug) and proven shared support (Ubuntu x86_64 GCC Release; macOS arm64 AppleClang
  Release); C-M4-001 is merged to `main`.
- ADR-0002 superseded by ADR-0007 (Pydantic remains domain authority)
- MarketStateSnapshot: added source_book_update_id and source_trade_id fields
- TelemetryEnvelope: extended with stream and connection fields
- QueueMetrics: extended with capacity and utilization fields

### Architecture

- Dual-contract strata: Domain Contracts (Pydantic) and Wire Contracts (Protobuf)
- Protobuf as the wire authority for cross-device and cross-language communication
- Pydantic as the domain authority for Python-internal data modeling
- gRPC Server Streaming as the Gateway-to-consumer protocol
- Explicit adapters bridging Pydantic and Protobuf representations

### Compatibility

- All existing Pydantic contracts remain unchanged
- Existing JSON Schema export continues unchanged
- All existing tests pass without modification
- Wire contracts are additive; consumers not using Protobuf are unaffected

### Pending

- C-M4-001 implementation is merged into `main`; publication remains pending and the formal package
  revision is unassigned; Projection M4 is complete in the separate Projection repository
- Assignment of the Contracts package revision (gated on release)
- Publication of `binance-market-data-contracts-cpp/0.1.0`
- Gateway Runtime (gRPC server is not implemented in this repository)
- Gateway implementation language is not selected (C++, Rust, Go, Python are all supported by the wire protocol)
- Network performance benchmarking
- Cross-language integration tests
- Contracts are not yet ACCEPTED; all remain PROPOSED or DRAFT
