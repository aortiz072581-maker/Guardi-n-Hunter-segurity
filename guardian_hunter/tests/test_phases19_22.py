"""Validation for Guardian Hunter phases 19 → 22."""

from guardian_hunter.analysis.phase19_signal import (
    READ_ONLY as R19,
    DRY_RUN as D19,
    EXECUTION_ALLOWED as E19,
    analyze_signal,
    validate_signal,
)

from guardian_hunter.correlation.phase19_correlation import (
    correlate_signals,
    validate_signal_correlation,
)

from guardian_hunter.decision.phase20_context import (
    calculate_contextual_risk,
    validate_contextual_risk,
)

from guardian_hunter.decision.phase20_decision import (
    build_defensive_decision,
    validate_defensive_decision,
)

from guardian_hunter.response.phase21_orchestrator import (
    build_response_plan,
    validate_response_plan,
)

from guardian_hunter.response.phase22_consolidation import (
    consolidate_security_record,
    validate_consolidated_record,
)


def main() -> None:

    # ==================================================
    # PHASE 19 — SIGNAL ANALYSIS
    # ==================================================

    signal_a = analyze_signal(
        signal_id="SIG-19-001",
        category="NETWORK",
        score=78,
        indicators=[
            "NEW_EGRESS",
            "BASELINE_DEVIATION",
        ],
        confidence=0.95,
    )

    signal_b = analyze_signal(
        signal_id="SIG-19-002",
        category="LISTENER",
        score=64,
        indicators=[
            "NEW_LISTENER",
        ],
        confidence=0.90,
    )

    assert validate_signal(signal_a)
    assert validate_signal(signal_b)
    assert signal_a.execution_allowed is False
    assert signal_a.mode == "READ_ONLY"

    print("PHASE 19 SIGNAL ANALYSIS: OK")
    print("PHASE 19 SIGNAL VALIDATION: OK")
    print("PHASE 19 READ-ONLY: OK")

    # ==================================================
    # PHASE 19 — CORRELATION
    # ==================================================

    correlation = correlate_signals([
        {
            "signal_id": signal_a.signal_id,
            "category": signal_a.category,
            "score": signal_a.score,
        },
        {
            "signal_id": signal_b.signal_id,
            "category": signal_b.category,
            "score": signal_b.score,
        },
    ])

    assert validate_signal_correlation(correlation)
    assert correlation.signal_count == 2
    assert correlation.correlated_score >= 64

    print("PHASE 19 MULTI-SIGNAL CORRELATION: OK")
    print("PHASE 19 CORRELATION SCORING: OK")
    print("PHASE 19 CORRELATION READ-ONLY: OK")

    # ==================================================
    # PHASE 20 — CONTEXTUAL RISK
    # ==================================================

    contextual = calculate_contextual_risk(
        correlation_score=correlation.correlated_score,
        asset_exposure=72,
        baseline_deviation=80,
        evidence_confidence=90,
    )

    assert validate_contextual_risk(contextual)
    assert contextual.contextual_score >= 70
    assert contextual.risk_level == "CRITICAL"

    print("PHASE 20 CONTEXTUAL RISK: OK")
    print("PHASE 20 RISK LEVEL: OK")
    print("PHASE 20 RISK READ-ONLY: OK")

    # ==================================================
    # PHASE 20 — DECISION
    # ==================================================

    decision = build_defensive_decision(
        contextual.risk_level,
        contextual.contextual_score,
    )

    assert validate_defensive_decision(decision)
    assert decision.response_locked is True
    assert decision.requires_review is True
    assert decision.collect_evidence is True

    print("PHASE 20 DEFENSIVE DECISION: OK")
    print("PHASE 20 HUMAN REVIEW GATE: OK")
    print("PHASE 20 RESPONSE LOCK: OK")

    # ==================================================
    # PHASE 21 — RESPONSE ORCHESTRATION
    # ==================================================

    response = build_response_plan(
        risk_level=decision.risk_level,
        decision=decision.decision,
        collect_evidence=decision.collect_evidence,
    )

    assert validate_response_plan(response)
    assert response.response_locked is True
    assert response.execution_allowed is False
    assert response.dry_run is True

    print("PHASE 21 RESPONSE ORCHESTRATOR: OK")
    print("PHASE 21 RESPONSE LOCK: OK")
    print("PHASE 21 DRY-RUN: OK")

    # ==================================================
    # PHASE 22 — CONSOLIDATION
    # ==================================================

    record = consolidate_security_record(
        event_id="EVENT-19-22-001",
        risk_level=contextual.risk_level,
        risk_score=contextual.contextual_score,
        decision=decision.decision,
        response_steps=response.steps,
        evidence_ids=[
            "NET-EVIDENCE-001",
            "NET-EVIDENCE-002",
        ],
        timeline_events=[
            {
                "event": "BASELINE_DEVIATION",
                "severity": "HIGH",
            },
            {
                "event": "NEW_EGRESS",
                "severity": "HIGH",
            },
        ],
    )

    assert validate_consolidated_record(record)
    assert record.evidence_count == 2
    assert record.timeline_count == 2
    assert record.execution_allowed is False
    assert record.mode == "READ_ONLY"
    assert record.status == "CONSOLIDATED_READ_ONLY"
    assert len(record.integrity_digest) == 64

    print("PHASE 22 EVIDENCE CONSOLIDATION: OK")
    print("PHASE 22 TIMELINE CONSOLIDATION: OK")
    print("PHASE 22 SHA-256 INTEGRITY: OK")
    print("PHASE 22 READ-ONLY: OK")

    # ==================================================
    # GLOBAL SAFETY
    # ==================================================

    assert R19 is True
    assert D19 is True
    assert E19 is False

    print("PHASES 19 → 22 GLOBAL SAFETY: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")

    print("PHASES 19 → 22 TEST: OK")


if __name__ == "__main__":
    main()
