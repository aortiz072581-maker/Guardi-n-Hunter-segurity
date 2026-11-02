"""Read-only adapters for local defensive security sensors."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from guardian_hunter.auditor.findings import (
    Confidence,
    Finding,
    Severity,
    validate_findings,
)


def _run(command: list[str], timeout: int = 180):
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _finding(sensor: str, index: int, title: str,
             affected: str, evidence: str) -> Finding:
    finding = Finding(
        finding_id=f"GH-{sensor}-{index:06d}",
        severity=Severity.HIGH,
        confidence=Confidence.LIKELY,
        title=title,
        description=f"Defensive finding from {sensor}",
        risk="Security review required",
        evidence=(evidence,),
        affected_files=(affected,),
        proposed_fix="Review and remediate under human supervision",
        required_tests=("Re-run the relevant security sensor",),
    )
    finding.validate()
    return finding


def assess_security_sensors(
    root: str | Path,
    *,
    gitleaks_binary: str | Path,
    osv_binary: str | Path,
) -> dict:
    root = Path(root).resolve(strict=True)

    if not root.is_dir():
        raise ValueError("SCAN_ROOT_MUST_BE_DIRECTORY")

    findings = []
    states = {}

    gitleaks = _run([
        str(gitleaks_binary),
        "dir",
        str(root),
        "--no-banner",
        "--report-format",
        "json",
        "--report-path",
        "/dev/stdout",
        "--exit-code",
        "42",
    ])

    if gitleaks is None or gitleaks.returncode not in (0, 42):
        states["gitleaks"] = "ERROR"
    else:
        try:
            records = json.loads(gitleaks.stdout or "[]")
            if not isinstance(records, list):
                raise ValueError("INVALID_GITLEAKS_REPORT")

            for index, record in enumerate(records, 1):
                if not isinstance(record, dict):
                    raise ValueError("INVALID_GITLEAKS_RECORD")

                rule = str(record.get("RuleID", "unknown"))
                location = str(record.get("File", "unknown"))

                if (
                    len(rule) > 120
                    or len(location) > 512
                    or any(ord(c) < 32 for c in rule + location)
                ):
                    raise ValueError("UNSAFE_GITLEAKS_METADATA")

                findings.append(_finding(
                    "GITLEAKS",
                    index,
                    f"Potential secret: {rule}",
                    location,
                    f"rule={rule}",
                ))

            if (gitleaks.returncode == 42) != bool(records):
                raise ValueError("GITLEAKS_RESULT_MISMATCH")

            states["gitleaks"] = (
                "FINDINGS" if records else "CLEAN"
            )
        except (ValueError, TypeError):
            states["gitleaks"] = "ERROR"

    osv = _run([
        str(osv_binary),
        "scan",
        "source",
        "--format",
        "json",
        str(root),
    ])

    if osv is None or osv.returncode not in (0, 1):
        states["osv"] = "ERROR"
    else:
        try:
            report = json.loads(osv.stdout)
            if not isinstance(report, dict):
                raise ValueError("INVALID_OSV_REPORT")

            index = 0
            for result in report.get("results", []):
                for package in result.get("packages", []):
                    info = package.get("package", {})
                    name = str(info.get("name", "unknown"))
                    version = str(info.get("version", "unknown"))

                    for vulnerability in package.get(
                        "vulnerabilities", []
                    ):
                        index += 1
                        vuln_id = str(
                            vulnerability.get("id", "unknown")
                        )

                        if (
                            any(len(x) > 160 for x in (
                                name, version, vuln_id
                            ))
                            or any(
                                ord(c) < 32
                                for x in (name, version, vuln_id)
                                for c in x
                            )
                        ):
                            raise ValueError("UNSAFE_OSV_METADATA")
                        findings.append(_finding(
                            "OSV",
                            index,
                            f"Vulnerable dependency: {name}",
                            f"{name}@{version}",
                            f"vulnerability={vuln_id}",
                        ))

            if (osv.returncode == 1) != bool(index):
                raise ValueError("OSV_RESULT_MISMATCH")

            states["osv"] = (
                "FINDINGS" if index else "CLEAN"
            )
        except (ValueError, TypeError, AttributeError):
            states["osv"] = "ERROR"

    validate_findings(tuple(findings))

    summary = {
        "schema": "guardian-security-sensors-v1",
        "states": states,
        "finding_count": len(findings),
        "findings": [
            {
                "id": f.finding_id,
                "title": f.title,
                "evidence": list(f.evidence),
                "affected_files": list(f.affected_files),
                "execution_allowed": f.execution_allowed,
                "automatic_repair": f.automatic_repair,
                "merge_allowed": f.merge_allowed,
            }
            for f in findings
        ],
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    summary["assessment_complete"] = all(
        state != "ERROR" for state in states.values()
    )

    encoded = json.dumps(
        summary,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    summary["sha256"] = hashlib.sha256(encoded).hexdigest()

    return summary
