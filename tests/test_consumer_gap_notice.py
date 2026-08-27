"""Test the ConsumerGapNotice reason-to-recovery-action invariant."""

import pytest
from pydantic import ValidationError

from binance_market_data.common.v1 import enums_pb2 as pb_enums
from binance_market_data.gateway.v1 import gateway_messages_pb2 as pb_gw
from binance_market_data_contracts.enums import ConsumerGapReason, RecoveryAction
from binance_market_data_contracts.gateway import ConsumerGapNotice
from binance_market_data_contracts.identifiers import SubscriptionId
from binance_market_data_contracts.wire.adapters import (
    consumer_gap_notice_from_pb,
    consumer_gap_notice_to_pb,
)

EXPECTED_ACTION_BY_REASON = {
    ConsumerGapReason.SLOW_CONSUMER: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.RESUME_NOT_AVAILABLE: RecoveryAction.REQUEST_NEW_SNAPSHOT,
    ConsumerGapReason.UPSTREAM_SEQUENCE_GAP: RecoveryAction.REQUEST_NEW_SNAPSHOT,
    ConsumerGapReason.GATEWAY_RESTART: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.CONNECTION_GENERATION_CHANGED: RecoveryAction.RESUBSCRIBE,
    ConsumerGapReason.SUBSCRIPTION_RECONFIGURED: RecoveryAction.RESUBSCRIBE,
}

FORBIDDEN_PAIRS = tuple(
    (reason, action)
    for reason, expected_action in EXPECTED_ACTION_BY_REASON.items()
    for action in RecoveryAction
    if action != expected_action
)

PB_REASON_BY_REASON = {
    ConsumerGapReason.SLOW_CONSUMER: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SLOW_CONSUMER,
    ConsumerGapReason.RESUME_NOT_AVAILABLE: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_RESUME_NOT_AVAILABLE,
    ConsumerGapReason.UPSTREAM_SEQUENCE_GAP: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_UPSTREAM_SEQUENCE_GAP,
    ConsumerGapReason.GATEWAY_RESTART: pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_GATEWAY_RESTART,
    ConsumerGapReason.CONNECTION_GENERATION_CHANGED: (
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_CONNECTION_GENERATION_CHANGED
    ),
    ConsumerGapReason.SUBSCRIPTION_RECONFIGURED: (
        pb_enums.ConsumerGapReason.CONSUMER_GAP_REASON_SUBSCRIPTION_RECONFIGURED
    ),
}

PB_ACTION_BY_ACTION = {
    RecoveryAction.NONE: pb_enums.RecoveryAction.RECOVERY_ACTION_NONE,
    RecoveryAction.RESUBSCRIBE: pb_enums.RecoveryAction.RECOVERY_ACTION_RESUBSCRIBE,
    RecoveryAction.REQUEST_NEW_SNAPSHOT: pb_enums.RecoveryAction.RECOVERY_ACTION_REQUEST_NEW_SNAPSHOT,
}


def _notice(reason: ConsumerGapReason, action: RecoveryAction) -> ConsumerGapNotice:
    return ConsumerGapNotice(
        schema_version="consumer-gap-notice.v1",
        subscription_id=SubscriptionId("sub-1"),
        detected_time_utc_ns=1,
        reason=reason,
        recovery_action=action,
    )


@pytest.mark.parametrize("reason,action", EXPECTED_ACTION_BY_REASON.items())
def test_every_allowed_reason_action_pair_is_accepted(reason, action):
    assert _notice(reason, action).recovery_action == action


@pytest.mark.parametrize("reason,action", FORBIDDEN_PAIRS)
def test_every_forbidden_reason_action_pair_is_rejected(reason, action):
    with pytest.raises(ValidationError, match="requires recovery action"):
        _notice(reason, action)


def test_rejects_previously_accepted_non_none_pair():
    with pytest.raises(ValidationError, match=r"SLOW_CONSUMER.*RESUBSCRIBE"):
        _notice(ConsumerGapReason.SLOW_CONSUMER, RecoveryAction.REQUEST_NEW_SNAPSHOT)


@pytest.mark.parametrize("reason,action", EXPECTED_ACTION_BY_REASON.items())
def test_allowed_pairs_round_trip_domain_to_wire_and_back(reason, action):
    notice = _notice(reason, action)
    wire = consumer_gap_notice_to_pb(notice)
    encoded = wire.SerializeToString()
    parsed = pb_gw.ConsumerGapNotice()
    parsed.ParseFromString(encoded)

    restored = consumer_gap_notice_from_pb(parsed)
    assert restored.reason == reason
    assert restored.recovery_action == action


@pytest.mark.parametrize("reason,action", FORBIDDEN_PAIRS)
def test_forbidden_wire_pairs_are_rejected_by_domain_adapter(reason, action):
    wire = pb_gw.ConsumerGapNotice(
        schema_version="consumer-gap-notice.v1",
        subscription_id="sub-1",
        detected_time_utc_ns=1,
        reason=PB_REASON_BY_REASON[reason],
        recovery_action=PB_ACTION_BY_ACTION[action],
    )

    with pytest.raises(ValidationError, match="requires recovery action"):
        consumer_gap_notice_from_pb(wire)
