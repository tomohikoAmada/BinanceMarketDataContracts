# ADR-0011: Opaque UTF-8 symbol identity

## Status

ACCEPTED

## Date

2026-08-23

## Context

The Python Domain Contract constrained `Symbol` to 2 through 20 ASCII uppercase letters or
digits. That constraint was an application assumption, not a Protobuf wire requirement. Binance's
official Spot WebSocket and REST documentation records that symbols may contain non-ASCII
characters encoded as UTF-8. The old constraint could therefore reject a valid exchange identity
or change which symbols a Gateway can represent.

`Symbol` is an opaque exchange identity. Contracts must preserve it exactly across the Pydantic
and Protobuf strata rather than interpreting its script, case, or normalization form. This ADR is
numbered 0011 because ADR-0010 was already reserved by the concurrent package-boundary change.

## Decision

The Pydantic `Symbol` contract:

- requires at least one Unicode scalar value;
- preserves the original code-point sequence and case without normalization or case folding;
- rejects U+0000 through U+0020 inclusive and U+007F;
- rejects surrogate code points U+D800 through U+DFFF so every accepted Python value can be
  encoded as strict UTF-8; and
- imposes no arbitrary maximum code-point or byte length.

No broader Unicode whitespace or control-character policy is inferred. In particular, U+0080,
U+00A0, and U+3000 remain valid unless an exchange protocol authority establishes a narrower
rule later.

The JSON Schema exposes the portable subset as `minLength: 1` and the pattern
`^(?![\s\S]*[\u0000-\u0020\u007F])[\s\S]+$`. The negative lookahead avoids ECMAScript's
special end-anchor behavior before a trailing line terminator. The Python Domain Contract uses a
separate pre-validator for surrogates because JSON text cannot carry an unpaired surrogate as a
valid Unicode scalar and JSON Schema regex behavior is not a suitable UTF-8-encoding oracle.

The Protobuf `string` wire fields and field numbers do not change. Domain/wire adapters copy the
symbol value exactly.

## Consequences

- Previously valid symbols remain valid; the accepted identity space is broadened.
- Generated JSON Schemas lose `maxLength: 20` and the ASCII-only pattern. Consumers that copied
  those restrictions must update their local validation.
- A consumer may need its own operational size limit at an input or resource boundary, but such a
  limit is not part of exchange symbol identity and must not rewrite the contract value.
- This ADR changes only `Symbol`; other identifier aliases retain their existing constraints.
- Domain and Wire contract statuses remain PROPOSED or DRAFT. Accepting this semantic decision
  does not promote a contract's status.

## Rejected alternatives

- Preserve the ASCII 2..20 rule: rejected because it excludes official Spot identities.
- Normalize or case-fold symbols: rejected because this can change opaque exchange identity.
- Add Unicode White_Space, C1, or script restrictions: rejected without an exchange-owned rule.
- Validate by catching every UTF-8 encoding error: rejected because it risks masking unrelated
  errors; the validator checks the surrogate range directly.
- Change Protobuf fields: rejected because Protobuf `string` already carries UTF-8 text and no
  wire-shape change is required.

## Source

- Binance Spot WebSocket Streams documents non-ASCII symbol names and UTF-8 stream events:
  <https://developers.binance.com/en/docs/products/spot/web-socket-streams.md>
- Binance Spot REST API documents non-ASCII asset/symbol names and includes the fullwidth-digit
  symbol `１２３４５６` in signed-request examples:
  <https://developers.binance.com/en/docs/products/spot/rest-api.md>

The sources above were acquired for this review at `2026-08-23T07:22:34.921794+00:00`. The local,
ephemeral acquisition manifest was `/private/tmp/gateway-binance-docs-20260823/manifest.json`:

- WebSocket document: 10,370 bytes, SHA-256
  `193aa07cd537b2ccc94662474fb3dda3cb774d550b1e117825919d99f91b725f`.
- REST document: 33,310 bytes, SHA-256
  `3bfe5526b745c976ae2db7c6bffdee14f10663d5fe326d8aa54c8b5f12968775`.

This manifest records local acquisition evidence only. It is not committed, is not a build input,
and is not a remotely reproducible dependency of this contract.
