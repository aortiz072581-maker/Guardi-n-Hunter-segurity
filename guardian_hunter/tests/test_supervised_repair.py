from dataclasses import replace

import pytest

from guardian_hunter.repair.approval import (
    HumanApproval,
    approve,
    verify_approval,
)
from guardian_hunter.repair.proposal import RepairProposal


def proposal():
    return RepairProposal(
        finding_id="GH-007",
        summary="Example supervised repair.",
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
            "test_supervised_repair",
        ),
    )


def test_proposal_is_fail_closed():
    value = proposal()
    value.validate()

    assert value.automatic_apply is False
    assert value.execution_allowed is False
    assert value.merge_allowed is False
    assert value.human_approval_required is True


def test_proposal_has_stable_sha256():
    value = proposal()

    first = value.proposal_hash
    second = value.proposal_hash

    assert first == second
    assert len(first) == 64


def test_patch_change_changes_hash():
    value = proposal()

    changed = replace(
        value,
        patch=value.patch + "\n# changed\n",
    )

    assert value.proposal_hash != changed.proposal_hash


def test_file_change_changes_hash():
    value = proposal()

    changed = replace(
        value,
        affected_files=(
            "guardian_hunter/analysis/other.py",
        ),
    )

    assert value.proposal_hash != changed.proposal_hash


def test_tests_change_changes_hash():
    value = proposal()

    changed = replace(
        value,
        required_tests=("different_test",),
    )

    assert value.proposal_hash != changed.proposal_hash


def test_human_can_approve_exact_proposal():
    value = proposal()

    approval = approve(
        value,
        decision="APPROVED",
        approver_id="human-test-reviewer",
        baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb",
    )

    assert verify_approval(value, approval, baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb") is True


def test_modified_patch_invalidates_approval():
    value = proposal()

    approval = approve(
        value,
        decision="APPROVED",
        approver_id="human-test-reviewer",
        baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb",
    )

    changed = replace(
        value,
        patch=value.patch + "\nmalicious-change\n",
    )

    with pytest.raises(
        PermissionError,
        match="PROPOSAL_HASH_MISMATCH",
    ):
        verify_approval(changed, approval, baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb")


def test_wrong_finding_invalidates_approval():
    value = proposal()

    approval = approve(
        value,
        decision="APPROVED",
        approver_id="human-test-reviewer",
        baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb",
    )

    bad = HumanApproval(
        finding_id="GH-999",
        proposal_hash=approval.proposal_hash,
        decision=approval.decision,
        approver_id=approval.approver_id,
        nonce=approval.nonce,
        issued_at=approval.issued_at,
        expires_at=approval.expires_at,
        baseline=approval.baseline,
    )

    with pytest.raises(
        PermissionError,
        match="FINDING_ID_MISMATCH",
    ):
        verify_approval(value, bad, baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb")


@pytest.mark.parametrize(
    "field,value,reason",
    (
        (
            "automatic_apply",
            True,
            "AUTOMATIC_APPLY_FORBIDDEN",
        ),
        (
            "execution_allowed",
            True,
            "EXECUTION_FORBIDDEN",
        ),
        (
            "merge_allowed",
            True,
            "MERGE_FORBIDDEN",
        ),
        (
            "human_approval_required",
            False,
            "HUMAN_APPROVAL_REQUIRED",
        ),
    ),
)
def test_proposal_cannot_gain_authority(
    field,
    value,
    reason,
):
    candidate = replace(
        proposal(),
        **{field: value},
    )

    with pytest.raises(
        PermissionError,
        match=reason,
    ):
        candidate.validate()


def test_rejection_does_not_create_approval():
    with pytest.raises(
        PermissionError,
        match="HUMAN_APPROVAL_REQUIRED",
    ):
        approve(
            proposal(),
            decision="REJECTED",
            approver_id="human-test-reviewer",
            baseline="2a44ae3916f629d59dc92fc5099c79f4cf2af4bb",
        )


def test_protected_boundary_is_identified():
    value = replace(
        proposal(),
        affected_files=(
            "guardian_hunter/gate/core.py",
        ),
    )

    assert value.touches_protected_boundary is True


def test_normal_code_not_marked_protected():
    assert proposal().touches_protected_boundary is False


def test_path_traversal_is_rejected():
    value = replace(
        proposal(),
        affected_files=(
            "../guardian_hunter/gate/core.py",
        ),
    )

    with pytest.raises(
        ValueError,
        match="PATH_TRAVERSAL_FORBIDDEN",
    ):
        value.validate()


def test_gate_protects_repair_proposal():
    from guardian_hunter.gate.core import protected_change

    assert protected_change(
        "guardian_hunter/repair/proposal.py"
    ) is True


def test_gate_protects_repair_approval():
    from guardian_hunter.gate.core import protected_change

    assert protected_change(
        "guardian_hunter/repair/approval.py"
    ) is True


def test_repair_cannot_approve_own_boundary_change():
    from guardian_hunter.gate.core import evaluate_candidate

    result = evaluate_candidate(
        ["guardian_hunter/repair/approval.py"]
    )

    assert result.passed is False
    assert result.human_review_required is True
    assert result.agent_merge_allowed is False
    assert result.reason.startswith(
        "PROTECTED_BOUNDARY_CHANGED:"
    )
