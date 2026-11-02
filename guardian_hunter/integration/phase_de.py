"""Guardian Hunter D+E: supervised defensive orchestration."""

from __future__ import annotations

from pathlib import Path
import shutil

from guardian_hunter.integration.security_sensor_adapter import (
    assess_security_sensors,
)
from guardian_hunter.integration.c6_operational import (
    run_c6_operational,
)
from guardian_hunter.integration.health_recovery import (
    run_health_recovery,
)

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False
HUMAN_APPROVAL_REQUIRED = True


def run_phase_de(root: str | Path) -> dict:
    """Assess sensors and prepare a non-executing defensive report."""
    root = Path(root).resolve()

    result = {
        "schema": "guardian-phase-de-v1",
        "status": "BLOCKED",
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
        "sensor_report": None,
        "correlation": None,
        "health": None,
    }

    try:
        gitleaks = shutil.which("gitleaks")
        osv = shutil.which("osv-scanner")

        if not gitleaks or not osv:
            result["reason"] = "MISSING_SENSOR"
            return result

        sensors = assess_security_sensors(
            root,
            gitleaks_binary=gitleaks,
            osv_binary=osv,
        )
        result["sensor_report"] = sensors

        if sensors.get("assessment_complete") is not True:
            result["reason"] = "INCOMPLETE_ASSESSMENT"
            return result

        if any(
            state == "ERROR"
            for state in sensors.get("states", {}).values()
        ):
            result["reason"] = "SENSOR_ERROR"
            return result

        correlation = run_c6_operational(sensors)
        result["correlation"] = correlation

        health = run_health_recovery()
        result["health"] = health

        result["status"] = "REVIEW_REQUIRED"
        result["reason"] = "HUMAN_REVIEW_REQUIRED"
        return result

    except Exception as exc:
        result["reason"] = "DEFENSIVE_ASSESSMENT_ERROR"
        result["error_type"] = type(exc).__name__
        return result



def build_defensive_response(assessment: dict) -> dict:
    """Classify verified assessment without granting authority."""
    result = {
        "schema": "guardian-defensive-response-v1",
        "status": "BLOCKED",
        "incident_detected": False,
        "incident_count": 0,
        "recommended_action": "MANUAL_REVIEW",
        "isolation_mode": "LOGICAL_ONLY",
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    if not isinstance(assessment, dict):
        result["reason"] = "INVALID_ASSESSMENT"
        return result

    if assessment.get("status") != "REVIEW_REQUIRED":
        result["reason"] = "ASSESSMENT_NOT_READY"
        return result

    sensors = assessment.get("sensor_report")
    correlation = assessment.get("correlation")

    if not isinstance(sensors, dict) or not isinstance(correlation, dict):
        result["reason"] = "MISSING_EVIDENCE"
        return result

    states = sensors.get("states")
    if (
        not isinstance(states, dict)
        or set(states) != {"gitleaks", "osv"}
        or any(v not in ("CLEAN", "FINDINGS") for v in states.values())
        or sensors.get("assessment_complete") is not True
    ):
        result["reason"] = "INVALID_SENSOR_STATES"
        return result

    for report in (assessment, sensors, correlation):
        for key in ("execution_allowed", "automatic_repair", "merge_allowed"):
            if report.get(key) is not False:
                result["reason"] = "UNSAFE_AUTHORITY"
                return result

    sensor_count = sensors.get("finding_count")
    correlated_count = correlation.get("finding_count")

    if (
        type(sensor_count) is not int
        or type(correlated_count) is not int
        or sensor_count < 0
        or correlated_count < 0
        or correlated_count > sensor_count
    ):
        result["reason"] = "INVALID_FINDING_COUNT"
        return result

    if sensor_count == 0 and any(v == "FINDINGS" for v in states.values()):
        result["reason"] = "SENSOR_CONTRADICTION"
        return result

    if sensor_count > 0 and all(v == "CLEAN" for v in states.values()):
        result["reason"] = "SENSOR_CONTRADICTION"
        return result

    if sensor_count > 0 and correlated_count == 0:
        result["reason"] = "CORRELATION_LOSS"
        return result

    result["incident_count"] = correlated_count
    result["incident_detected"] = correlated_count > 0

    if correlated_count:
        result["status"] = "INCIDENT_REVIEW_REQUIRED"
        result["recommended_action"] = "INVESTIGATE_AND_ISOLATE_LOGICALLY"
    else:
        result["status"] = "MONITORING"
        result["recommended_action"] = "CONTINUE_DEFENSIVE_MONITORING"

    return result
