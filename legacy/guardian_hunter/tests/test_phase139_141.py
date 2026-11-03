"""Phase 139→141 — Node.js defensive runtime validation."""

from guardian_hunter.runtime.node_runtime import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    build_runtime_state,
    runtime_contract,
)


def test_phase139_runtime_contract():
    contract = runtime_contract()

    assert contract["READ_ONLY"] is True
    assert contract["DRY_RUN"] is True
    assert contract["REAL_EXECUTION_BLOCKED"] is True
    assert contract["HUMAN_REVIEW_REQUIRED"] is True
    assert contract["RESPONSE_LOCKED"] is True
    assert contract["EXECUTION_ALLOWED"] is False


def test_phase140_runtime_state_is_fail_closed():
    state = build_runtime_state(
        node_available=True,
        node_version="v24.18.0",
    )

    assert state.available is True
    assert state.version == "v24.18.0"

    assert state.read_only is True
    assert state.dry_run is True
    assert state.real_execution_blocked is True
    assert state.human_review_required is True
    assert state.response_locked is True

    assert state.execution_allowed is False


def test_phase141_runtime_unavailable_remains_safe():
    state = build_runtime_state(
        node_available=False,
        node_version=None,
    )

    assert state.available is False
    assert state.version is None

    assert state.read_only is True
    assert state.dry_run is True
    assert state.real_execution_blocked is True
    assert state.human_review_required is True
    assert state.response_locked is True

    assert state.execution_allowed is False


def test_global_safety_invariants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def test_runtime_never_grants_execution_permission():
    state = build_runtime_state(
        node_available=True,
        node_version="v24.18.0",
    )

    assert state.execution_allowed is False
    assert state.real_execution_blocked is True
    assert state.human_review_required is True
    assert state.response_locked is True
