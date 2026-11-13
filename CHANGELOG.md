# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0a1] — Unreleased

### Added

- Protobuf wire contracts and gRPC service definitions for Gateway streaming.
- Pydantic Gateway contracts and explicit Domain ↔ Wire adapters.
- Wire contract registry, Buf configuration and generated-code drift checks.
- Transcript and round-trip tests for adapter correctness and presence.
- Contracts-owned C++ message package plus a separate C++ gRPC service/stub
  package, with CMake/Conan consumers and provenance metadata.
- `GatewayStatusRequest` across registries, adapters, schemas, fixtures and docs.
- USD-M C2 wire surface: `Stream.MARK_PRICE/LIQUIDATION/REFERENCE_DATA`,
  `MarkPrice`, `Liquidation`, typed `ReferenceObservation` payloads,
  `StreamStatus.reference_source_kind`, `AggTrade.normal_quantity`,
  `ExchangeDepthSnapshot.exchange_event_time_ms`, fixtures and adapters.
- ADR-0007 through ADR-0012.

### Changed

- Removed redundant Decimal/enum validators, the unused legacy `EnvelopeMetadata`
  class and adapter-local enum maps/no-op conversion helpers.
- `TelemetryEnvelope.metrics` is required; missing wire metrics fail closed.
- `MarketRuntimeStatus.connection_generation` uses explicit optional presence
  when no unique upstream generation applies.
- Version `0.1.0a1` → `0.2.0a1`.
- `Symbol` uses opaque UTF-8 identity (ADR-0011), preserving code points and
  rejecting controls/whitespace, DEL and surrogates.
- Split the C++ gRPC artifact from the message-only package (ADR-0010).
- Compressed historical C0/C1/C-M4-001 plans and evidence into
  [docs/HISTORY.md](docs/HISTORY.md); current docs no longer pin moving
  cross-repository runtime status.
- C2 changes the canonical descriptor fingerprint to
  `a2a93ca5cf4e17c9a64ca0939ad208f1202c1746628eed5260bd0edb81666c86`; C++
  message/gRPC candidates must be re-exported from this schema.

### Architecture

- Dual contract strata: Pydantic Domain and Protobuf Wire.
- Protobuf as wire authority; Pydantic as Python domain authority.
- gRPC Server Streaming as the Gateway-to-consumer protocol.
- Explicit adapters, no reflection or `model_dump()` mapping.

### Compatibility

- Existing values accepted by the former `Symbol` constraint remain accepted.
- JSON Schema `Symbol` loses the incorrect `maxLength: 20` and ASCII-only
  restrictions.
- Wire contracts are additive; consumers not using Protobuf are unaffected.

### Pending

- Formal package revision assignment and publication.
- Gateway runtime work and cross-repository release decisions.
- Contracts remain PROPOSED or DRAFT; none is ACCEPTED.
