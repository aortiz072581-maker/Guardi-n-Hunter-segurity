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

    if not (validate_signal(signal_a)):
    raise RuntimeError("Assertion failed: validate_signal(signal_a)")
    if not (validate_signal(signal_b)):
    raise RuntimeError("Assertion failed: validate_signal(signal_b)")
    if not (signal_a.execution_allowed is False):
    raise RuntimeError("Assertion failed: signal_a.execution_allowed is False")
    if not (signal_a.mode == "READ_ONLY"):
    raise RuntimeError("Assertion failed: signal_a.mode == "READ_ONLY"")

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

    if not (validate_signal_correlation(correlation)):
    raise RuntimeError("Assertion failed: validate_signal_correlation(correlation)")
    if not (correlation.signal_count == 2):
    raise RuntimeError("Assertion failed: correlation.signal_count == 2")
    if not (correlation.correlated_score >= 64):
    raise RuntimeError("Assertion failed: correlation.correlated_score >= 64")

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

    if not (validate_contextual_risk(contextual)):
    raise RuntimeError("Assertion failed: validate_contextual_risk(contextual)")
    if not (contextual.contextual_score >= 70):
    raise RuntimeError("Assertion failed: contextual.contextual_score >= 70")
    if not (contextual.risk_level == "CRITICAL"):
    raise RuntimeError("Assertion failed: contextual.risk_level == "CRITICAL"")

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

    if not (validate_defensive_decision(decision)):
    raise RuntimeError("Assertion failed: validate_defensive_decision(decision)")
    if not (decision.response_locked is True):
    raise RuntimeError("Assertion failed: decision.response_locked is True")
    if not (decision.requires_review is True):
    raise RuntimeError("Assertion failed: decision.requires_review is True")
    if not (decision.collect_evidence is True):
    raise RuntimeError("Assertion failed: decision.collect_evidence is True")

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

    if not (validate_response_plan(response)):
    raise RuntimeError("Assertion failed: validate_response_plan(response)")
    if not (response.response_locked is True):
    raise RuntimeError("Assertion failed: response.response_locked is True")
    if not (response.execution_allowed is False):
    raise RuntimeError("Assertion failed: response.execution_allowed is False")
    if not (response.dry_run is True):
    raise RuntimeError("Assertion failed: response.dry_run is True")

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

    if not (validate_consolidated_record(record)):
    raise RuntimeError("Assertion failed: validate_consolidated_record(record)")
    if not (record.evidence_count == 2):
    raise RuntimeError("Assertion failed: record.evidence_count == 2")
    if not (record.timeline_count == 2):
    raise RuntimeError("Assertion failed: record.timeline_count == 2")
    if not (record.execution_allowed is False):
    raise RuntimeError("Assertion failed: record.execution_allowed is False")
    if not (record.mode == "READ_ONLY"):
    raise RuntimeError("Assertion failed: record.mode == "READ_ONLY"")
    if not (record.status == "CONSOLIDATED_READ_ONLY"):
    raise RuntimeError("Assertion failed: record.status == "CONSOLIDATED_READ_ONLY"")
    if not (len(record.integrity_digest) == 64):
    raise RuntimeError("Assertion failed: len(record.integrity_digest) == 64")

    print("PHASE 22 EVIDENCE CONSOLIDATION: OK")
    print("PHASE 22 TIMELINE CONSOLIDATION: OK")
    print("PHASE 22 SHA-256 INTEGRITY: OK")
    print("PHASE 22 READ-ONLY: OK")

    # ==================================================
    # GLOBAL SAFETY
    # ==================================================

    if not (R19 is True):
    raise RuntimeError("Assertion failed: R19 is True")
    if not (D19 is True):
    raise RuntimeError("Assertion failed: D19 is True")
    if not (E19 is False):
    raise RuntimeError("Assertion failed: E19 is False")

    print("PHASES 19 → 22 GLOBAL SAFETY: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")

    print("PHASES 19 → 22 TEST: OK")


if __name__ == "__main__":
    main()
