"""Integration tests for phases 22-24."""

from guardian_hunter.decision.engine import (
    explain_decision,
    make_decision,
)
from guardian_hunter.correlation.advanced import (
    build_timeline,
    correlate_events,
)
from guardian_hunter.evidence.incident import (
    append_evidence,
    create_incident_record,
    verify_incident_record,
)


def main() -> None:
    events = [
        {
            "timestamp": "2026-09-25T10:00:00+00:00",
            "asset_id": "asset-01",
            "category": "network",
            "summary": "network signal",
        },
        {
            "timestamp": "2026-09-25T10:01:00+00:00",
            "asset_id": "asset-01",
            "category": "network",
            "summary": "repeated network signal",
        },
        {
            "timestamp": "2026-09-25T10:02:00+00:00",
            "asset_id": "asset-02",
            "category": "system",
            "summary": "system signal",
        },
    ]

    # Phase 22
    decision = make_decision(
        {"risk_score": 85},
        confidence=0.91,
        context={
            "known_asset": False,
            "repeated_signal": True,
        },
    )

    assert decision["decision"] == "CONTAINMENT_REVIEW"
    assert decision["priority"] == "CRITICAL"
    assert decision["requires_approval"] is True
    assert decision["execution_allowed"] is False
    assert decision["mode"] == "DRY_RUN"
    assert explain_decision(decision)

    print("PHASE 22 DECISION ENGINE: OK")
    print("PHASE 22 EXECUTION LOCK: OK")

    # Phase 23
    correlation = correlate_events(events)

    assert correlation["event_count"] == 3
    assert correlation["incident_count"] == 2

    timeline = build_timeline(events)

    assert len(timeline) == 3
    assert timeline[0]["sequence"] == 1
    assert timeline[-1]["sequence"] == 3

    print("PHASE 23 ADVANCED CORRELATION: OK")
    print("PHASE 23 TIMELINE: OK")

    # Phase 24
    evidence = append_evidence(
        [],
        {
            "type": "network_signal",
            "source": "test",
            "details": "safe validation evidence",
        },
    )

    assert len(evidence) == 1
    assert len(evidence[0]["hash"]) == 64

    incident = create_incident_record(
        incident_id="INC-TEST-001",
        decision=decision,
        correlation=correlation,
        timeline=timeline,
        evidence=evidence,
    )

    assert incident["incident_id"] == "INC-TEST-001"
    assert len(incident["evidence_hash"]) == 64
    assert verify_incident_record(incident) is True

    print("PHASE 24 EVIDENCE HASH: OK")
    print("PHASE 24 INCIDENT TIMELINE: OK")
    print("PHASE 22-24 TEST: OK")


if __name__ == "__main__":
    main()
