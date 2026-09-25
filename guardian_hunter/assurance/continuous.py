"""Phase 36 — Continuous Defensive Security Assurance."""

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_assurance(
    *,
    health: bool,
    policy: bool,
    audit: bool,
    evidence: bool,
    baseline: bool,
    response_locked: bool,
) -> dict[str, Any]:
    controls = {
        "health": bool(health),
        "policy": bool(policy),
        "audit": bool(audit),
        "evidence": bool(evidence),
        "baseline": bool(baseline),
        "response_locked": bool(response_locked),
    }

    passed = sum(controls.values())
    total = len(controls)

    if passed == total:
        status = "ASSURED"
    elif passed >= total - 1:
        status = "REVIEW_REQUIRED"
    else:
        status = "DEGRADED"

    return {
        "timestamp": _utc_now(),
        "status": status,
        "controls": controls,
        "passed": passed,
        "total": total,
        "coverage_percent": round((passed / total) * 100, 2),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def assurance_gate(result: dict[str, Any]) -> bool:
    if result.get("mode") != "READ_ONLY":
        return False

    if result.get("execution_allowed") is not False:
        return False

    return result.get("status") == "ASSURED"


def build_assurance_report(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "CONTINUOUS_SECURITY_ASSURANCE",
        "timestamp": result["timestamp"],
        "status": result["status"],
        "coverage_percent": result["coverage_percent"],
        "controls": result["controls"],
        "read_only": True,
        "execution_blocked": True,
    }
