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
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert RESPONSE_LOCKED is True


def test_empty_correlation_is_safe():
    result = build_defensive_risk_input({})

    assert result["findings"] == []
    assert result["signal_count"] == 0
    assert result["execution_allowed"] is False
    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["response_locked"] is True


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

    assert len(findings) == 3

    for finding in findings:
        assert finding["category"] == "defensive_correlation"
        assert 0 <= finding["score"] <= 100
        assert finding["confidence"] == 1.0
        assert finding["execution_allowed"] is False
        assert finding["read_only"] is True
        assert finding["dry_run"] is True


def test_duplicate_signals_are_removed():
    findings = correlation_to_findings(
        {
            "signals": [
                "ROUTE_CHANGED",
                "ROUTE_CHANGED",
            ]
        }
    )

    assert len(findings) == 1
    assert findings[0]["title"] == "ROUTE_CHANGED"


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

    assert risk["total"] == 3
    assert risk["max_score"] == 70
    assert risk["findings"][0]["severity"] == "high"

    assert adapted["execution_allowed"] is False
    assert adapted["response_locked"] is True
