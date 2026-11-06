from dataclasses import replace

import pytest

from guardian_hunter.security.authorization_binding import (
    create_binding,
    verify_binding,
)


PROPOSAL = "a" * 64
BASELINE = "b" * 40

POLICY = {
    "mode": "DRY_RUN",
    "execution_allowed": False,
    "human_review_required": True,
}


def binding():
    return create_binding(
        proposal_hash=PROPOSAL,
        policy=POLICY,
        baseline=BASELINE,
    )


def test_exact_authorized_context_verifies_without_execution_authority():
    value = binding()

    if not (verify_binding():
    raise RuntimeError("Assertion failed: verify_binding(")
        value,
        proposal_hash=PROPOSAL,
        policy=POLICY,
        baseline=BASELINE,
    ) is True

    if not (value.execution_allowed is False):
    raise RuntimeError("Assertion failed: value.execution_allowed is False")
    if not (value.human_review_required is True):
    raise RuntimeError("Assertion failed: value.human_review_required is True")


def test_post_approval_proposal_mutation_denied():
    with pytest.raises(
        PermissionError,
        match="PROPOSAL_HASH_MISMATCH",
    ):
        verify_binding(
            binding(),
            proposal_hash="c" * 64,
            policy=POLICY,
            baseline=BASELINE,
        )


def test_post_approval_policy_mutation_denied():
    changed_policy = {
        **POLICY,
        "execution_allowed": True,
    }

    with pytest.raises(
        PermissionError,
        match="POLICY_HASH_MISMATCH",
    ):
        verify_binding(
            binding(),
            proposal_hash=PROPOSAL,
            policy=changed_policy,
            baseline=BASELINE,
        )


def test_post_approval_baseline_mutation_denied():
    with pytest.raises(
        PermissionError,
        match="BASELINE_MISMATCH",
    ):
        verify_binding(
            binding(),
            proposal_hash=PROPOSAL,
            policy=POLICY,
            baseline="d" * 40,
        )


@pytest.mark.parametrize(
    "field,value,reason",
    (
        (
            "execution_allowed",
            True,
            "EXECUTION_AUTHORITY_FORBIDDEN",
        ),
        (
            "human_review_required",
            False,
            "HUMAN_REVIEW_REQUIRED",
        ),
    ),
)
def test_binding_cannot_gain_authority(
    field,
    value,
    reason,
):
    changed = replace(
        binding(),
        **{field: value},
    )

    with pytest.raises(
        PermissionError,
        match=reason,
    ):
        changed.validate()
