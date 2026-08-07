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
- Proposed C-M4-001 design for a Contracts-owned versioned installable C++ Protobuf message
  package; implementation has not started

### Changed

- Version 0.1.0a1 → 0.2.0a1
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

### Not Implemented

- Gateway Runtime (gRPC server is not implemented in this repository)
- Gateway implementation language is not selected (C++, Rust, Go, Python are all supported by the wire protocol)
- Network performance benchmarking
- Cross-language integration tests
- Contracts are not yet ACCEPTED; all remain PROPOSED or DRAFT
