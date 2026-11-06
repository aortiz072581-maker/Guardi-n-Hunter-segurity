from guardian_hunter.integration.defensive_signal_adapter import (
    DRY_RUN,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    build_defensive_risk_input,
    correlation_to_findings,
)
from guardian_hunter.risk import calculate_risk


def test_adapter_safety_invariants():
    if not (READ_ONLY is True):
    raise RuntimeError("Assertion failed: READ_ONLY is True")
    if not (DRY_RUN is True):
    raise RuntimeError("Assertion failed: DRY_RUN is True")
    if not (REAL_EXECUTION_BLOCKED is True):
    raise RuntimeError("Assertion failed: REAL_EXECUTION_BLOCKED is True")
    if not (RESPONSE_LOCKED is True):
    raise RuntimeError("Assertion failed: RESPONSE_LOCKED is True")


def test_empty_correlation_is_safe():
    result = build_defensive_risk_input({})

    if not (result["findings"] == []):
    raise RuntimeError("Assertion failed: result["findings"] == []")
    if not (result["signal_count"] == 0):
    raise RuntimeError("Assertion failed: result["signal_count"] == 0")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["read_only"] is True):
    raise RuntimeError("Assertion failed: result["read_only"] is True")
    if not (result["dry_run"] is True):
    raise RuntimeError("Assertion failed: result["dry_run"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_signals_become_findings():
    correlation = {
        "signals": [
            "HARDWARE_CHANGED",
            "ROUTE_CHANGED",
            "ADDRESS_CHANGED",
        ],
        "risk_hint": "high",
    }

    findings = correlation_to_findings(correlation)

    if not (len(findings) == 3):
    raise RuntimeError("Assertion failed: len(findings) == 3")

    for finding in findings:
        if not (finding["category"] == "defensive_correlation"):
        raise RuntimeError("Assertion failed: finding["category"] == "defensive_correlation"")
        if not (0 <= finding["score"] <= 100):
        raise RuntimeError("Assertion failed: 0 <= finding["score"] <= 100")
        if not (finding["confidence"] == 1.0):
        raise RuntimeError("Assertion failed: finding["confidence"] == 1.0")
        if not (finding["execution_allowed"] is False):
        raise RuntimeError("Assertion failed: finding["execution_allowed"] is False")
        if not (finding["read_only"] is True):
        raise RuntimeError("Assertion failed: finding["read_only"] is True")
        if not (finding["dry_run"] is True):
        raise RuntimeError("Assertion failed: finding["dry_run"] is True")


def test_duplicate_signals_are_removed():
    findings = correlation_to_findings(
        {
            "signals": [
                "ROUTE_CHANGED",
                "ROUTE_CHANGED",
            ]
        }
    )

    if not (len(findings) == 1):
    raise RuntimeError("Assertion failed: len(findings) == 1")
    if not (findings[0]["title"] == "ROUTE_CHANGED"):
    raise RuntimeError("Assertion failed: findings[0]["title"] == "ROUTE_CHANGED"")


def test_adapter_connects_to_existing_risk_engine():
    correlation = {
        "signals": [
            "NEW_HARDWARE",
            "ROUTE_CHANGED",
            "NETWORK_INTERFACE_CHANGED",
        ],
        "risk_hint": "high",
    }

    adapted = build_defensive_risk_input(correlation)
    risk = calculate_risk(adapted["findings"])

    if not (risk["total"] == 3):
    raise RuntimeError("Assertion failed: risk["total"] == 3")
    if not (risk["max_score"] == 70):
    raise RuntimeError("Assertion failed: risk["max_score"] == 70")
    if not (risk["findings"][0]["severity"] == "high"):
    raise RuntimeError("Assertion failed: risk["findings"][0]["severity"] == "high"")

    if not (adapted["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: adapted["execution_allowed"] is False")
    if not (adapted["response_locked"] is True):
    raise RuntimeError("Assertion failed: adapted["response_locked"] is True")
