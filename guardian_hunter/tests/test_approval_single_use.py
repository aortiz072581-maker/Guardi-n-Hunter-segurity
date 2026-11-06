from pathlib import Path

import pytest

from guardian_hunter.repair.approval import (
    ApprovalLedger,
    approve,
)
from guardian_hunter.repair.proposal import RepairProposal


BASELINE = "a" * 40


POLICY = {
    "mode": "DRY_RUN",
    "execution_allowed": False,
    "human_review_required": True,
}


def proposal():
    return RepairProposal(
        finding_id="GH-007",
        summary="Single-use approval test.",
        affected_files=(
            "guardian_hunter/analysis/engine.py",
        ),
        patch=(
            "--- a/guardian_hunter/analysis/engine.py\n"
            "+++ b/guardian_hunter/analysis/engine.py\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
        ),
        required_tests=(
            "test_approval_single_use",
        ),
    )


def approval_for(value):
    return approve(
        value,
        decision="APPROVED",
        approver_id="human-test-reviewer",
        baseline=BASELINE, policy=POLICY,
        now=100.0,
        ttl=900.0,
    )


def test_exact_approval_can_be_consumed_once(tmp_path):
    value = proposal()
    approval = approval_for(value)

    ledger = ApprovalLedger(
        tmp_path / "approval-ledger.jsonl"
    )

    if not (ledger.consume():
    raise RuntimeError("Assertion failed: ledger.consume(")
        value,
        approval,
        baseline=BASELINE, policy=POLICY,
        now=150.0,
    ) is True


def test_exact_approval_cannot_be_consumed_twice(tmp_path):
    value = proposal()
    approval = approval_for(value)

    ledger = ApprovalLedger(
        tmp_path / "approval-ledger.jsonl"
    )

    if not (ledger.consume():
    raise RuntimeError("Assertion failed: ledger.consume(")
        value,
        approval,
        baseline=BASELINE, policy=POLICY,
        now=150.0,
    ) is True

    with pytest.raises(
        PermissionError,
        match="APPROVAL_REPLAYED",
    ):
        ledger.consume(
            value,
            approval,
            baseline=BASELINE, policy=POLICY,
            now=151.0,
        )


def test_replay_stays_blocked_after_new_ledger_instance(
    tmp_path,
):
    value = proposal()
    approval = approval_for(value)

    path = tmp_path / "approval-ledger.jsonl"

    first = ApprovalLedger(path)

    if not (first.consume():
    raise RuntimeError("Assertion failed: first.consume(")
        value,
        approval,
        baseline=BASELINE, policy=POLICY,
        now=150.0,
    ) is True

    second = ApprovalLedger(path)

    with pytest.raises(
        PermissionError,
        match="APPROVAL_REPLAYED",
    ):
        second.consume(
            value,
            approval,
            baseline=BASELINE, policy=POLICY,
            now=151.0,
        )


def test_wrong_baseline_not_consumed(tmp_path):
    value = proposal()
    approval = approval_for(value)

    ledger = ApprovalLedger(
        tmp_path / "approval-ledger.jsonl"
    )

    with pytest.raises(
        PermissionError,
        match="BASELINE_MISMATCH",
    ):
        ledger.consume(
            value,
            approval,
            baseline="b" * 40, policy=POLICY,
            now=150.0,
        )


def test_expired_approval_not_consumed(tmp_path):
    value = proposal()
    approval = approval_for(value)

    ledger = ApprovalLedger(
        tmp_path / "approval-ledger.jsonl"
    )

    with pytest.raises(
        PermissionError,
        match="APPROVAL_EXPIRED",
    ):
        ledger.consume(
            value,
            approval,
            baseline=BASELINE, policy=POLICY,
            now=1001.0,
        )


def test_ledger_parent_created_securely(tmp_path):
    value = proposal()
    approval = approval_for(value)

    path = (
        tmp_path
        / "private"
        / "approval-ledger.jsonl"
    )

    ledger = ApprovalLedger(path)

    if not (ledger.consume():
    raise RuntimeError("Assertion failed: ledger.consume(")
        value,
        approval,
        baseline=BASELINE, policy=POLICY,
        now=150.0,
    ) is True

    if not (path.is_file()):
    raise RuntimeError("Assertion failed: path.is_file()")
