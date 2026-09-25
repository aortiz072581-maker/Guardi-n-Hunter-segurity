"""Phase 38 — Defensive Security Control Validation."""

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


REQUIRED_CONTROLS = (
    "policy_guard",
    "audit_integrity",
    "evidence_integrity",
    "baseline_integrity",
    "health_monitor",
    "response_lock",
)


def validate_controls(
    controls: dict[str, bool],
) -> dict[str, Any]:
    normalized = {
        name: bool(controls.get(name, False))
        for name in REQUIRED_CONTROLS
    }

    passed = sum(normalized.values())
    total = len(REQUIRED_CONTROLS)

    if passed == total:
        status = "PASS"
    elif passed >= total - 1:
        status = "REVIEW_REQUIRED"
    else:
        status = "FAIL"

    return {
        "timestamp": _utc_now(),
        "status": status,
        "controls": normalized,
        "passed": passed,
        "total": total,
        "coverage_percent": round((passed / total) * 100, 2),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def control_gate(result: dict[str, Any]) -> bool:
    return (
        result.get("status") == "PASS"
        and result.get("mode") == "READ_ONLY"
        and result.get("execution_allowed") is False
    )


def validate_execution_safety(
    *,
    execution_allowed: bool,
    dry_run: bool,
    read_only: bool,
) -> bool:
    return (
        execution_allowed is False
        and dry_run is True
        and read_only is True
    )


def build_control_report(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "SECURITY_CONTROL_VALIDATION",
        "timestamp": result["timestamp"],
        "status": result["status"],
        "coverage_percent": result["coverage_percent"],
        "controls": result["controls"],
        "read_only": True,
        "execution_blocked": True,
    }
