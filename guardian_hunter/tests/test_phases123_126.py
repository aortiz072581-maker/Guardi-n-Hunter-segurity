"""Integration tests for Guardian Hunter phases 123 → 126."""

from guardian_hunter.governance.phase123_baseline import build_baseline
from guardian_hunter.verification.phase124_drift import check_baseline
from guardian_hunter.governance.phase125_policy_lock import build_policy_lock
from guardian_hunter.governance.phase126_continuity_gate import (
    build_continuity_gate,
)


def test_phase123_baseline():
    baseline = build_baseline()

    assert baseline.state == "DEFENSIVE_OPERATIONAL_BASELINE_VALID"
    assert baseline.score == 100
    assert baseline.read_only is True
    assert baseline.dry_run is True
    assert baseline.human_review_required is True
    assert baseline.response_locked is True
    assert baseline.real_execution_blocked is True


def test_phase124_drift():
    baseline = build_baseline()

    drift = check_baseline(
        baseline_state=baseline.state,
        baseline_score=baseline.score,
    )

    assert drift.state == "DEFENSIVE_BASELINE_DRIFT_FREE"
    assert drift.score == 100


def test_phase125_policy():
    policy = build_policy_lock()

    assert policy.state == "DEFENSIVE_POLICY_LOCK_VALID"
    assert policy.score == 100
    assert policy.read_only is True
    assert policy.dry_run is True
    assert policy.human_review_required is True
    assert policy.response_locked is True
    assert policy.real_execution_blocked is True


def test_phase126_gate():
    baseline = build_baseline()

    drift = check_baseline(
        baseline_state=baseline.state,
        baseline_score=baseline.score,
    )

    policy = build_policy_lock()

    gate = build_continuity_gate(
        baseline_state=baseline.state,
        drift_state=drift.state,
        policy_state=policy.state,
    )

    assert gate.state == "DEFENSIVE_CONTINUITY_GATE_READY"
    assert gate.score == 100
    assert gate.response_score == 100
    assert gate.read_only is True
    assert gate.dry_run is True
    assert gate.human_review_required is True
    assert gate.response_locked is True
    assert gate.real_execution_blocked is True


def test_real_execution_remains_blocked():
    baseline = build_baseline()
    policy = build_policy_lock()

    assert baseline.real_execution_blocked is True
    assert policy.real_execution_blocked is True
