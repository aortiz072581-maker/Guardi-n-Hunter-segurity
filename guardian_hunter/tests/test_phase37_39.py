"""Tests for phases 37-39."""

from guardian_hunter.threatintel.fusion import (
    normalize_indicator,
    fuse_indicators,
    correlate_indicator,
)
from guardian_hunter.validation.controls import (
    validate_controls,
    control_gate,
    validate_execution_safety,
    build_control_report,
)
from guardian_hunter.metrics.security import (
    calculate_metrics,
    compare_metrics,
    metrics_gate,
)


def main() -> None:
    # ----------------------------------------------
    # PHASE 37
    # ----------------------------------------------

    first = normalize_indicator(
        "  EXAMPLE.COM ",
        "DOMAIN",
        "local-test",
        80,
        "medium",
    )

    duplicate = normalize_indicator(
        "example.com",
        "DOMAIN",
        "second-source",
        90,
        "high",
    )

    fused = fuse_indicators([first, duplicate])

    assert fused["indicator_count"] == 1
    assert fused["mode"] == "READ_ONLY"
    assert fused["execution_allowed"] is False

    events = [
        {
            "event": "DNS observation",
            "domain": "example.com",
        },
        {
            "event": "unrelated event",
            "domain": "safe.local",
        },
    ]

    matches = correlate_indicator(first, events)

    assert len(matches) == 1

    print("PHASE 37 THREAT INTELLIGENCE FUSION: OK")
    print("PHASE 37 INDICATOR CORRELATION: OK")
    print("PHASE 37 READ-ONLY: OK")

    # ----------------------------------------------
    # PHASE 38
    # ----------------------------------------------

    controls = {
        "policy_guard": True,
        "audit_integrity": True,
        "evidence_integrity": True,
        "baseline_integrity": True,
        "health_monitor": True,
        "response_lock": True,
    }

    validation = validate_controls(controls)

    assert validation["status"] == "PASS"
    assert validation["coverage_percent"] == 100.0
    assert control_gate(validation)

    assert validate_execution_safety(
        execution_allowed=False,
        dry_run=True,
        read_only=True,
    )

    report = build_control_report(validation)

    assert report["read_only"] is True
    assert report["execution_blocked"] is True

    print("PHASE 38 SECURITY CONTROL VALIDATION: OK")
    print("PHASE 38 CONTROL GATE: OK")
    print("PHASE 38 EXECUTION SAFETY: OK")

    # ----------------------------------------------
    # PHASE 39
    # ----------------------------------------------

    previous = calculate_metrics(
        incidents=2,
        alerts=8,
        critical_alerts=1,
        evidence_items=10,
        evidence_verified=10,
        controls_passed=6,
        controls_total=6,
        health_percent=98,
    )

    current = calculate_metrics(
        incidents=3,
        alerts=10,
        critical_alerts=2,
        evidence_items=12,
        evidence_verified=12,
        controls_passed=6,
        controls_total=6,
        health_percent=100,
    )

    assert current["evidence_integrity_percent"] == 100.0
    assert current["control_coverage_percent"] == 100.0
    assert metrics_gate(current)

    trend = compare_metrics(previous, current)

    assert trend["changes"]["incidents"] == 1.0
    assert trend["changes"]["alerts"] == 2.0
    assert trend["execution_allowed"] is False

    print("PHASE 39 SECURITY METRICS: OK")
    print("PHASE 39 TREND ANALYSIS: OK")
    print("PHASE 39 EXECUTION BLOCK: OK")

    print("PHASE 37-39 TEST: OK")


if __name__ == "__main__":
    main()
