"""Fail-closed, read-only security sensor correlation bridge."""

import hashlib
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False

SEVERITIES = {"critical", "high", "medium", "low", "info"}

def _digest(value):
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()

def correlate_sensor_report(report):
    if not isinstance(report, dict):
        raise ValueError("INVALID_REPORT")

    findings = report.get("findings")
    states = report.get("states")

    if not isinstance(findings, list):
        raise ValueError("INVALID_FINDINGS")
    if not isinstance(states, dict):
        raise ValueError("INVALID_STATES")
    if set(states) != {"gitleaks", "osv"}:
        raise ValueError("INVALID_SENSOR_SET")
    if any(v not in {"CLEAN", "FINDINGS"} for v in states.values()):
        raise ValueError("INCOMPLETE_SENSOR_ASSESSMENT")
    if report.get("assessment_complete") is not True:
        raise ValueError("ASSESSMENT_INCOMPLETE")
    if report.get("finding_count") != len(findings):
        raise ValueError("COUNT_MISMATCH")
    if report.get("human_approval_required") is not True:
        raise ValueError("APPROVAL_REQUIRED")
    for key in ("execution_allowed", "automatic_repair", "merge_allowed"):
        if report.get(key) is not False:
            raise ValueError("UNSAFE_REPORT_AUTHORITY")

    output = []
    seen = set()

    for item in findings:
        if not isinstance(item, dict):
            raise ValueError("INVALID_FINDING")

        identifier = item.get("id")
        title = item.get("title")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("INVALID_IDENTIFIER")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("INVALID_TITLE")
        if identifier in seen:
            raise ValueError("DUPLICATE_IDENTIFIER")
        seen.add(identifier)

        for key in ("execution_allowed", "automatic_repair", "merge_allowed"):
            if item.get(key) is not False:
                raise ValueError("UNSAFE_FINDING_AUTHORITY")

        if identifier.startswith("GH-GITLEAKS-"):
            sensor = "gitleaks"
        elif identifier.startswith("GH-OSV-"):
            sensor = "osv"
        else:
            raise ValueError("UNKNOWN_SENSOR_ORIGIN")

        if states[sensor] != "FINDINGS":
            raise ValueError("SENSOR_STATE_CONTRADICTION")

        severity = item.get("severity", "unknown")
        if severity is None:
            severity = "unknown"
        if not isinstance(severity, str):
            raise ValueError("INVALID_SEVERITY")
        if severity not in SEVERITIES | {"unknown"}:
            raise ValueError("INVALID_SEVERITY")

        evidence = item.get("evidence")
        affected = item.get("affected_files")

        if not isinstance(evidence, (list, tuple)):
            raise ValueError("INVALID_EVIDENCE")
        if not isinstance(affected, (list, tuple)):
            raise ValueError("INVALID_AFFECTED_FILES")
        if not all(isinstance(x, str) for x in evidence):
            raise ValueError("INVALID_EVIDENCE")
        if not all(isinstance(x, str) for x in affected):
            raise ValueError("INVALID_AFFECTED_FILES")

        output.append({
            "id": identifier,
            "sensor": sensor,
            "title": title,
            "severity": severity,
            "classification_required": severity == "unknown",
            "evidence_sha256": _digest(list(evidence)),
            "affected_files_sha256": _digest(list(affected)),
            "execution_allowed": False,
            "automatic_repair": False,
            "merge_allowed": False,
            "human_approval_required": True,
        })

    if any(states[s] == "FINDINGS" for s in states) and not output:
        raise ValueError("MISSING_FINDINGS")

    result = {
        "schema": "guardian-c6-sensor-correlation-v1",
        "source_report_sha256": _digest(report),
        "findings": sorted(output, key=lambda x: x["id"]),
        "finding_count": len(output),
        "classification_complete": all(
            not f["classification_required"] for f in output
        ),
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }
    result["sha256"] = _digest(result)
    return result
