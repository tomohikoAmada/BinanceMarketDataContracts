# Identity and Ordering

Contracts defines identity and ordering **field semantics**; it does not own a
producer's deduplication policy or a replay engine's scheduling policy.

## Identity

- Raw capture may contain duplicates; absence of deduplication at the Raw layer
  is intentional.
- Producers/replay layers choose explicit identity keys per stream and record
  their version. "Looks the same" is not an identity rule.
- The same identity with different content is an `IDENTITY_CONFLICT` fact, not
  silent overwrite.
- `Symbol` is an opaque exchange identity (ADR-0011); no case folding or
  normalization.

## Ordering and gaps

- Binance `U/u/pu`, Projection `last_update_id`, `connection_generation`,
  `gateway_instance_id` and `session_sequence` are distinct domains and must not
  be substituted for one another.
- Stream-specific ordering and gap classification are owned by Projection;
  Recorder owns its capture/replay ordering evidence.
- Contracts represents gap and recovery facts explicitly. Gaps are never
  silently filled, forward-filled or presented as continuous.
- A replay engine's choice of receive-time vs exchange-time ordering, and its
  missing-time/gap policy, is an implementation policy outside Contracts.
