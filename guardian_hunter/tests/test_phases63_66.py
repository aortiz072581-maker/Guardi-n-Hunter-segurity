from guardian_hunter.governance.phase63_threat_continuity import (
    build_threat_continuity,
    validate_threat_continuity,
)

from guardian_hunter.verification.phase64_risk_continuity import (
    build_risk_continuity,
    validate_risk_continuity,
)

from guardian_hunter.governance.phase65_decision_continuity import (
    build_decision_continuity,
    validate_decision_continuity,
)

from guardian_hunter.governance.phase66_response_gate import (
    build_threat_response_gate,
    validate_threat_response_gate,
)


def test_phase63():
    threat = build_threat_continuity(
        signal_count=5,
        threat_analysis_valid=True,
        correlation_valid=True,
        risk_valid=True,
    )

    assert threat.continuity_valid is True
    assert threat.execution_blocked is True
    assert validate_threat_continuity(threat) is True


def test_phase64():
    risk = build_risk_continuity(
        risk_score=35,
        risk_valid=True,
        decision_valid=True,
        escalation_tracked=True,
    )

    assert risk.continuity_valid is True
    assert risk.risk_score == 35
    assert risk.execution_blocked is True
    assert validate_risk_continuity(risk) is True


def test_phase65():
    decision = build_decision_continuity(
        decision_valid=True,
        policy_valid=True,
        human_review_required=False,
        response_locked=True,
    )

    assert decision.continuity_valid is True
    assert decision.response_locked is True
    assert decision.decision_state == (
        "DEFENSIVE_DECISION_READY"
    )
    assert validate_decision_continuity(decision) is True


def test_phase66():
    gate = build_threat_response_gate(
        True,
        True,
        True,
        True,
    )

    assert gate.gate_score == 100
    assert gate.response_state == (
        "RESPONSE_READY_FOR_REVIEW"
    )
    assert gate.response_locked is True
    assert gate.human_review_required is True
    assert gate.execution_blocked is True
    assert validate_threat_response_gate(gate) is True


if __name__ == "__main__":
    test_phase63()
    test_phase64()
    test_phase65()
    test_phase66()

    print("PHASE 63: OK")
    print("PHASE 64: OK")
    print("PHASE 65: OK")
    print("PHASE 66: OK")
    print("63 → 66 TEST: OK")
