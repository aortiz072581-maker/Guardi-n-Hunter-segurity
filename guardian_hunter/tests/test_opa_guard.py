from __future__ import annotations

from copy import deepcopy

from guardian_hunter.policy.opa_guard import evaluate_opa


PROPOSAL = "a" * 64
POLICY = "b" * 64
BASELINE = "c" * 40


def valid_context():
    return {
        "human_review_required": True,

        "execution_allowed": False,
        "merge_allowed": False,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "global_execution_allowed": False,

        "proposal_hash": PROPOSAL,
        "policy_hash": POLICY,
        "baseline": BASELINE,

        "approved_proposal_hash": PROPOSAL,
        "approved_policy_hash": POLICY,
        "approved_baseline": BASELINE,
    }


def test_opa_accepts_only_exact_safe_context():
    decision = evaluate_opa(valid_context())

    assert decision.allowed is True
    assert decision.reason == "OPA_ALLOW"


def test_opa_denies_execution_escalation():
    context = valid_context()
    context["execution_allowed"] = True

    decision = evaluate_opa(context)

    assert decision.allowed is False
    assert decision.reason == "OPA_DENY"


def test_opa_denies_proposal_mutation():
    context = valid_context()
    context["proposal_hash"] = "d" * 64

    assert evaluate_opa(context).allowed is False


def test_opa_denies_policy_mutation():
    context = valid_context()
    context["policy_hash"] = "e" * 64

    assert evaluate_opa(context).allowed is False


def test_opa_denies_baseline_mutation():
    context = valid_context()
    context["baseline"] = "f" * 40

    assert evaluate_opa(context).allowed is False


def test_opa_missing_engine_fails_closed():
    decision = evaluate_opa(
        valid_context(),
        opa_binary="/definitely/not/an/opa/binary",
    )

    assert decision.allowed is False
    assert decision.reason.startswith(
        "OPA_ENGINE_ERROR:"
    )


def test_opa_context_is_not_mutated():
    context = valid_context()
    original = deepcopy(context)

    evaluate_opa(context)

    assert context == original

def test_opa_rejects_64_hex_baseline_contract():
    context = {
        "human_review_required": True,
        "execution_allowed": False,
        "merge_allowed": False,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "global_execution_allowed": False,
        "proposal_hash": "a" * 64,
        "approved_proposal_hash": "a" * 64,
        "policy_hash": "b" * 64,
        "approved_policy_hash": "b" * 64,
        "baseline": "c" * 64,
        "approved_baseline": "c" * 64,
    }

    decision = evaluate_opa(context)

    assert decision.allowed is False

