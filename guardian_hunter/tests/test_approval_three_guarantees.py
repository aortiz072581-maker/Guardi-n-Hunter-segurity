from dataclasses import replace

import pytest

from guardian_hunter.repair.approval import (
    approve,
    verify_approval,
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
        summary="Three-guarantee binding test.",
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
            "test_approval_three_guarantees",
        ),
    )


def approval_for(value):
    return approve(
        value,
        decision="APPROVED",
        approver_id="human-test-reviewer",
        baseline=BASELINE,
        policy=POLICY,
        now=100.0,
        ttl=100.0,
    )


def test_exact_three_guarantee_context_is_valid():
    value = proposal()
    approval = approval_for(value)

    assert verify_approval(
        value,
        approval,
        baseline=BASELINE,
        policy=POLICY,
        now=150.0,
    ) is True


def test_post_approval_proposal_mutation_is_denied():
    value = proposal()
    approval = approval_for(value)

    changed = replace(
        value,
        patch=value.patch + "\n# mutation\n",
    )

    with pytest.raises(
        PermissionError,
        match="PROPOSAL_HASH_MISMATCH",
    ):
        verify_approval(
            changed,
            approval,
            baseline=BASELINE,
            policy=POLICY,
            now=150.0,
        )


def test_post_approval_policy_mutation_is_denied():
    value = proposal()
    approval = approval_for(value)

    changed_policy = dict(POLICY)
    changed_policy["execution_allowed"] = True

    with pytest.raises(
        PermissionError,
        match="POLICY_HASH_MISMATCH",
    ):
        verify_approval(
            value,
            approval,
            baseline=BASELINE,
            policy=changed_policy,
            now=150.0,
        )


def test_post_approval_baseline_mutation_is_denied():
    value = proposal()
    approval = approval_for(value)

    with pytest.raises(
        PermissionError,
        match="BASELINE_MISMATCH",
    ):
        verify_approval(
            value,
            approval,
            baseline="b" * 40,
            policy=POLICY,
            now=150.0,
        )


def test_bound_approval_requires_policy_context():
    value = proposal()
    approval = approval_for(value)

    with pytest.raises(
        PermissionError,
        match="POLICY_CONTEXT_REQUIRED",
    ):
        verify_approval(
            value,
            approval,
            baseline=BASELINE,
            now=150.0,
        )


def test_approval_still_grants_no_execution_authority():
    value = proposal()
    approval = approval_for(value)

    assert approval.automatic_apply is False
    assert approval.execution_allowed is False
    assert approval.merge_allowed is False
