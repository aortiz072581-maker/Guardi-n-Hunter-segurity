"""Tests for phases 40-42."""

from guardian_hunter.soc.operations import (
    build_soc_status,
    build_soc_snapshot,
    correlate_alerts,
)
from guardian_hunter.incident_intel.context import (
    build_incident_context,
    build_investigation_report,
    build_investigation_timeline,
)
from guardian_hunter.governance.response import (
    create_governance_record,
    evaluate_governance,
    governance_gate,
    build_governance_chain,
)


def main():
    # PHASE 40
    alerts = [
        {"asset": "phone", "category": "network"},
        {"asset": "phone", "category": "network"},
        {"asset": "phone", "category": "process"},
    ]

    correlations = correlate_alerts(alerts)

    assert len(correlations) == 2
    assert all(item["execution_allowed"] is False for item in correlations)

    status = build_soc_status(
        risk_score=25,
        active_incidents=1,
        alerts=3,
        critical_alerts=0,
    )

    assert status.status == "OPERATIONAL"
    assert status.mode == "READ_ONLY"
    assert status.execution_allowed is False

    snapshot = build_soc_snapshot(status, correlations)

    assert snapshot["phase"] == 40
    assert snapshot["execution_allowed"] is False

    print("PHASE 40 SECURITY OPERATIONS CENTER: OK")
    print("PHASE 40 CORRELATION: OK")
    print("PHASE 40 READ-ONLY: OK")

    # PHASE 41
    context = build_incident_context(
        incident_id="INC-40",
        asset="phone",
        category="network",
        severity="HIGH",
        risk_score=75,
        confidence=90,
        evidence_count=4,
        related_alerts=3,
    )

    assert context.priority in {"P1", "P2", "P3", "P4"}
    assert context.execution_allowed is False

    timeline = build_investigation_timeline(
        [
            {"timestamp": "2026-09-25T10:02:00Z", "event": "ALERT"},
            {"timestamp": "2026-09-25T10:01:00Z", "event": "DETECTION"},
        ]
    )

    assert timeline[0]["event"] == "DETECTION"

    report = build_investigation_report(context, timeline)

    assert report["phase"] == 41
    assert report["execution_allowed"] is False

    print("PHASE 41 INCIDENT INTELLIGENCE: OK")
    print("PHASE 41 PRIORITIZATION: OK")
    print("PHASE 41 INVESTIGATION TIMELINE: OK")
    print("PHASE 41 READ-ONLY: OK")

    # PHASE 42
    blocked = evaluate_governance(
        action="DELETE",
        mode="DRY_RUN",
        approved=True,
        traceable=True,
    )

    assert blocked.policy_status == "BLOCKED"
    assert blocked.execution_allowed is False
    assert governance_gate(blocked) is False

    reviewed = evaluate_governance(
        action="CONTAINMENT_REVIEW",
        mode="DRY_RUN",
        approved=True,
        traceable=True,
    )

    assert reviewed.policy_status == "REVIEW_ONLY"
    assert reviewed.execution_allowed is False
    assert governance_gate(reviewed) is False

    record = create_governance_record(
        reviewed,
        incident_id="INC-40",
        operator="guardian-hunter",
    )

    chain = build_governance_chain([record])

    assert chain["integrity"] == "TRACEABLE"
    assert chain["execution_allowed"] is False

    print("PHASE 42 RESPONSE GOVERNANCE: OK")
    print("PHASE 42 POLICY BLOCK: OK")
    print("PHASE 42 TRACEABILITY: OK")
    print("PHASE 42 EXECUTION GATE: OK")
    print("PHASE 40-42 TEST: OK")


if __name__ == "__main__":
    main()
