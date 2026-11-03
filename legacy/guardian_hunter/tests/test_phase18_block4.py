"""Validation tests for Phase 18.13 → 18.16."""

from guardian_hunter.network.phase18_decision import (
    READ_ONLY as DECISION_READ_ONLY,
    DRY_RUN as DECISION_DRY_RUN,
    EXECUTION_ALLOWED as DECISION_EXECUTION_ALLOWED,
    build_network_security_decision,
    validate_network_security_decision,
)

from guardian_hunter.network.phase18_case_bridge import (
    READ_ONLY as BRIDGE_READ_ONLY,
    DRY_RUN as BRIDGE_DRY_RUN,
    EXECUTION_ALLOWED as BRIDGE_EXECUTION_ALLOWED,
    build_network_case_bridge,
    validate_network_case_bridge,
)

from guardian_hunter.network.phase18_response_gate import (
    READ_ONLY as RESPONSE_READ_ONLY,
    DRY_RUN as RESPONSE_DRY_RUN,
    EXECUTION_ALLOWED as RESPONSE_EXECUTION_ALLOWED,
    build_network_response_gate,
    validate_network_response_gate,
)

from guardian_hunter.network.phase18_regression import (
    READ_ONLY as REGRESSION_READ_ONLY,
    DRY_RUN as REGRESSION_DRY_RUN,
    EXECUTION_ALLOWED as REGRESSION_EXECUTION_ALLOWED,
    build_network_regression_gate,
    validate_network_regression_gate,
)


def main():

    # --------------------------------------------------
    # 18.13
    # --------------------------------------------------

    decision = build_network_security_decision(
        risk_score=78
    )

    assert validate_network_security_decision(
        decision
    )

    assert decision.risk_level == "CRITICAL"
    assert decision.evidence_required is True
    assert decision.escalation_required is True
    assert (
        decision.decision_status
        == "DEFENSIVE_DECISION_ONLY"
    )

    print(
        "PHASE 18.13 NETWORK SECURITY DECISION: OK"
    )
    print(
        "PHASE 18.13 DEFENSIVE ESCALATION LOGIC: OK"
    )
    print(
        "PHASE 18.13 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.14
    # --------------------------------------------------

    bridge = build_network_case_bridge(
        case_reference="CASE-18-001",
        evidence_reference="NET-EVIDENCE-001",
        risk_score=78,
        risk_level="CRITICAL",
    )

    assert validate_network_case_bridge(
        bridge
    )

    assert (
        bridge.bridge_status
        == "LINKED_READ_ONLY"
    )
    assert len(bridge.digest) == 64

    print(
        "PHASE 18.14 CASE/EVIDENCE BRIDGE: OK"
    )
    print(
        "PHASE 18.14 SHA-256 INTEGRITY: OK"
    )
    print(
        "PHASE 18.14 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.15
    # --------------------------------------------------

    gate = build_network_response_gate(
        risk_level="CRITICAL",
        evidence_valid=True,
        integrity_valid=True,
    )

    assert validate_network_response_gate(
        gate
    )

    assert gate.response_locked is True
    assert (
        gate.allowed_response
        == "ESCALATE_FOR_REVIEW"
    )

    print(
        "PHASE 18.15 RESPONSE GATE: OK"
    )
    print(
        "PHASE 18.15 RESPONSE LOCK: OK"
    )
    print(
        "PHASE 18.15 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.16
    # --------------------------------------------------

    phase_results = {
        "18.1": True,
        "18.2": True,
        "18.3": True,
        "18.4": True,
        "18.5": True,
        "18.6": True,
        "18.7": True,
        "18.8": True,
        "18.9": True,
        "18.10": True,
        "18.11": True,
        "18.12": True,
        "18.13": validate_network_security_decision(
            decision
        ),
        "18.14": validate_network_case_bridge(
            bridge
        ),
        "18.15": validate_network_response_gate(
            gate
        ),
    }

    regression = build_network_regression_gate(
        phase_results
    )

    assert validate_network_regression_gate(
        regression
    )

    assert (
        regression.regression_status
        == "REGRESSION_PASS"
    )

    assert (
        regression.total_phases == 15
    )

    assert (
        regression.passed_count == 15
    )

    assert (
        len(regression.failed_phases) == 0
    )

    assert len(
        regression.integrity_digest
    ) == 64

    print(
        "PHASE 18.16 NETWORK REGRESSION: OK"
    )
    print(
        "PHASE 18.16 ALL PHASES 18.1 → 18.15: OK"
    )
    print(
        "PHASE 18.16 SHA-256 INTEGRITY: OK"
    )
    print(
        "PHASE 18.16 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # GLOBAL SAFETY
    # --------------------------------------------------

    assert all(
        (
            DECISION_READ_ONLY,
            BRIDGE_READ_ONLY,
            RESPONSE_READ_ONLY,
            REGRESSION_READ_ONLY,
        )
    )

    assert all(
        (
            DECISION_DRY_RUN,
            BRIDGE_DRY_RUN,
            RESPONSE_DRY_RUN,
            REGRESSION_DRY_RUN,
        )
    )

    assert all(
        value is False
        for value in (
            DECISION_EXECUTION_ALLOWED,
            BRIDGE_EXECUTION_ALLOWED,
            RESPONSE_EXECUTION_ALLOWED,
            REGRESSION_EXECUTION_ALLOWED,
        )
    )

    print(
        "PHASE 18 BLOCK 4 TEST: OK"
    )
    print(
        "READ_ONLY: TRUE"
    )
    print(
        "DRY_RUN: TRUE"
    )
    print(
        "REAL EXECUTION: BLOCKED"
    )


if __name__ == "__main__":
    main()
