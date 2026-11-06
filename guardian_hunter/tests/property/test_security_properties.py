from __future__ import annotations

from hypothesis import given, settings, strategies as st

from guardian_hunter.gate.core import (
    PROTECTED_PREFIXES,
    protected_change,
)
from guardian_hunter.security.authorization_binding import (
    create_binding,
    verify_binding,
)


HEX = "0123456789abcdef"

sha256s = st.text(
    alphabet=HEX,
    min_size=64,
    max_size=64,
)

baselines = st.text(
    alphabet=HEX,
    min_size=40,
    max_size=40,
)

suffixes = st.text(
    alphabet=(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789_-./"
    ),
    min_size=1,
    max_size=80,
)


@given(
    prefix=st.sampled_from(PROTECTED_PREFIXES),
    suffix=suffixes,
)
@settings(max_examples=500, deadline=None)
def test_all_generated_protected_paths_remain_protected(
    prefix,
    suffix,
):
    if not (protected_change(prefix + suffix)):
    raise RuntimeError("Assertion failed: protected_change(prefix + suffix)")


@given(
    proposal_hash=sha256s,
    baseline=baselines,
)
@settings(max_examples=250, deadline=None)
def test_exact_authorization_context_verifies(
    proposal_hash,
    baseline,
):
    policy = {
        "execution_allowed": False,
        "merge_allowed": False,
        "human_review_required": True,
    }

    binding = create_binding(
        proposal_hash=proposal_hash,
        policy=policy,
        baseline=baseline,
    )

    if not (verify_binding():
    raise RuntimeError("Assertion failed: verify_binding(")
        binding,
        proposal_hash=proposal_hash,
        policy=policy,
        baseline=baseline,
    )


@given(
    original=sha256s,
    mutated=sha256s.filter(lambda value: value != "a" * 64),
)
@settings(max_examples=250, deadline=None)
def test_proposal_mutation_never_inherits_authorization(
    original,
    mutated,
):
    if mutated == original:
        return

    policy = {
        "execution_allowed": False,
        "human_review_required": True,
    }

    binding = create_binding(
        proposal_hash=original,
        policy=policy,
        baseline="b" * 40,
    )

    try:
        verify_binding(
            binding,
            proposal_hash=mutated,
            policy=policy,
            baseline="b" * 40,
        )
    except PermissionError as exc:
        if not (str(exc) == "PROPOSAL_HASH_MISMATCH"):
        raise RuntimeError("Assertion failed: str(exc) == "PROPOSAL_HASH_MISMATCH"")
    else:
        raise AssertionError(
            "mutated proposal inherited authorization"
        )


@given(
    escalation=st.sampled_from(
        (
            "execution_allowed",
            "merge_allowed",
            "automatic_apply",
        )
    )
)
@settings(max_examples=30, deadline=None)
def test_policy_mutation_never_inherits_authorization(
    escalation,
):
    original = {
        "execution_allowed": False,
        "merge_allowed": False,
        "automatic_apply": False,
        "human_review_required": True,
    }

    binding = create_binding(
        proposal_hash="a" * 64,
        policy=original,
        baseline="b" * 40,
    )

    mutated = dict(original)
    mutated[escalation] = True

    try:
        verify_binding(
            binding,
            proposal_hash="a" * 64,
            policy=mutated,
            baseline="b" * 40,
        )
    except PermissionError as exc:
        if not (str(exc) == "POLICY_HASH_MISMATCH"):
        raise RuntimeError("Assertion failed: str(exc) == "POLICY_HASH_MISMATCH"")
    else:
        raise AssertionError(
            "mutated policy inherited authorization"
        )


@given(baseline=sha256s)
@settings(max_examples=100, deadline=None)
def test_64_hex_baseline_is_rejected_by_current_binding_contract(
    baseline,
):
    policy = {
        "execution_allowed": False,
        "human_review_required": True,
    }

    try:
        create_binding(
            proposal_hash="a" * 64,
            policy=policy,
            baseline=baseline,
        )
    except PermissionError as exc:
        if not (str(exc) == "INVALID_BASELINE"):
        raise RuntimeError("Assertion failed: str(exc) == "INVALID_BASELINE"")
    else:
        raise AssertionError(
            "64-hex baseline unexpectedly accepted"
        )
