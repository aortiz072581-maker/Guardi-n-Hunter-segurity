"""Guardian Hunter F + G: supervised recovery and audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from guardian_hunter.integration.phase_de import (
    build_defensive_response,
)
from guardian_hunter.integration.operational_cycle import (
    build_repair_proposals,
)

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False
HUMAN_APPROVAL_REQUIRED = True


def prepare_phase_fg(assessment: dict) -> dict[str, Any]:
    """Prepare recovery decisions without executing them."""
    result = {
        "schema": "guardian-phase-fg-v1",
        "status": "BLOCKED",
        "reason": "INVALID_ASSESSMENT",
        "incident_count": 0,
        "proposals": [],
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    if not isinstance(assessment, dict):
        return result

    response = build_defensive_response(assessment)
    if response.get("status") not in (
        "MONITORING",
        "INCIDENT_REVIEW_REQUIRED",
    ):
        result["reason"] = "DEFENSIVE_RESPONSE_BLOCKED"
        return result

    for key in (
        "execution_allowed",
        "automatic_repair",
        "merge_allowed",
    ):
        if response.get(key) is not False:
            result["reason"] = "UNSAFE_RESPONSE"
            return result

    if response.get("human_approval_required") is not True:
        result["reason"] = "APPROVAL_REQUIRED"
        return result

    count = response.get("incident_count")
    if type(count) is not int or count < 0:
        result["reason"] = "INVALID_INCIDENT_COUNT"
        return result

    result["incident_count"] = count

    if count == 0:
        result["status"] = "MONITORING"
        result["reason"] = "NO_INCIDENTS"
        return result

    correlation = assessment.get("correlation")
    if not isinstance(correlation, dict):
        result["reason"] = "MISSING_CORRELATION"
        return result

    findings = correlation.get("findings")
    if findings is None:
        # C6 operational nests findings under correlation.correlation.findings
        inner = correlation.get("correlation")
        if isinstance(inner, dict):
            findings = inner.get("findings")
    if not isinstance(findings, list):
        result["reason"] = "MISSING_FINDINGS"
        return result

    try:
        proposals = build_repair_proposals(findings)
        if not isinstance(proposals, list):
            raise ValueError("INVALID_PROPOSALS")
        result["proposals"] = proposals
        result["status"] = "HUMAN_REVIEW_REQUIRED"
        result["reason"] = "SUPERVISED_RECOVERY_ONLY"
    except (ValueError, TypeError, KeyError):
        result["reason"] = "PROPOSAL_PREPARATION_FAILED"

    return result
