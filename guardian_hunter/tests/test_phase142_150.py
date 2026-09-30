"""Phases 142→150 productization validation."""

from guardian_hunter.product.demo import run_demo_scenario
from guardian_hunter.product.api_contract import (
    DetectionRequest,
    analyze,
)
from guardian_hunter.product.metrics import build_metrics
from guardian_hunter.product.readiness import audit_readiness


def test_phase142_demo():
    result = run_demo_scenario("suspicious_attachment")

    assert result.detection is True
    assert result.response_generated is True
    assert result.execution_allowed is False
    assert result.human_review_required is True
    assert result.response_locked is True


def test_phase143_api():
    result = analyze(
        DetectionRequest(
            subject="attachment:suspicious.exe",
            risk_level="HIGH",
        )
    )

    assert result.detected is True
    assert result.risk_level == "HIGH"
    assert result.execution_allowed is False
    assert result.human_review_required is True
    assert result.response_locked is True


def test_phase145_metrics():
    metrics = build_metrics(
        scenarios_tested=10,
        tests_passed=10,
    )

    assert metrics.scenarios_tested == 10
    assert metrics.tests_passed == 10
    assert metrics.safety_invariants_verified == 5
    assert metrics.execution_attempts_allowed == 0
    assert metrics.human_review_required is True
    assert metrics.response_locked is True


def test_phase150_readiness():
    result = audit_readiness()

    assert result.ready is True
    assert result.completed_items == result.required_items
    assert result.execution_allowed is False
    assert result.human_review_required is True
    assert result.response_locked is True


def test_global_safety_invariants():
    from guardian_hunter.runtime.node_runtime import (
        READ_ONLY,
        DRY_RUN,
        REAL_EXECUTION_BLOCKED,
        HUMAN_REVIEW_REQUIRED,
        RESPONSE_LOCKED,
    )

    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True
