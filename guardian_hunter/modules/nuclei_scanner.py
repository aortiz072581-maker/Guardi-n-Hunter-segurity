"""Authorized defensive Nuclei integration for Guardian Hunter."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


READ_ONLY = True
RESPONSE_EXECUTION_ALLOWED = False


_SEVERITY_SCORES = {
    "info": 5,
    "unknown": 10,
    "low": 25,
    "medium": 50,
    "high": 75,
    "critical": 95,
}


def _finding_from_nuclei(item: dict[str, Any]) -> dict[str, Any]:
    info = item.get("info") if isinstance(item.get("info"), dict) else {}

    severity = str(info.get("severity", "unknown")).strip().lower()
    score = _SEVERITY_SCORES.get(severity, 10)

    template_id = str(
        item.get("template-id")
        or item.get("template_id")
        or "nuclei-finding"
    )

    name = str(info.get("name") or template_id)
    matched = str(
        item.get("matched-at")
        or item.get("matched")
        or item.get("host")
        or ""
    )

    return {
        "category": "vulnerability",
        "title": name,
        "score": score,
        "severity": severity,
        "confidence": 1.0,
        "asset_criticality": 1.0,
        "exposure": 1.0,
        "evidence": matched,
        "recommendation": "REVIEW_AND_VALIDATE",
        "source": "nuclei",
        "template_id": template_id,
        "execution_allowed": False,
        "read_only": True,
    }


def parse_nuclei_jsonl(output: str) -> list[dict[str, Any]]:
    findings = []

    for line in (output or "").splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue

        if isinstance(item, dict):
            findings.append(_finding_from_nuclei(item))

    return findings


def run_nuclei_authorized(
    target: str,
    *,
    asset_manager,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run Nuclei only after AssetManager authorization."""

    result = {
        "target": target,
        "source": "nuclei",
        "status": "blocked",
        "authorized": False,
        "findings": [],
        "errors": [],
        "execution_allowed": False,
        "response_locked": True,
    }

    if asset_manager is None:
        result["errors"].append("AssetManager requerido.")
        return result

    # Critical boundary: authorization occurs before binary lookup/run.
    if not asset_manager.is_authorized(target):
        result["errors"].append("Objetivo no autorizado para Nuclei.")
        return result

    result["authorized"] = True

    binary = shutil.which("nuclei")
    if not binary:
        result["status"] = "error"
        result["errors"].append("Nuclei no está disponible en PATH.")
        return result

    try:
        completed = subprocess.run(
            [
                binary,
                "-u",
                target,
                "-jsonl",
                "-silent",
            ],
            capture_output=True,
            text=True,
            timeout=max(1, min(int(timeout), 300)),
            check=False,
        )
    except subprocess.TimeoutExpired:
        result["status"] = "error"
        result["errors"].append("Nuclei agotó el tiempo permitido.")
        return result
    except OSError as exc:
        result["status"] = "error"
        result["errors"].append(str(exc))
        return result

    findings = parse_nuclei_jsonl(completed.stdout)

    result["findings"] = findings

    if completed.returncode == 0:
        result["status"] = "ok"
    else:
        result["status"] = "error"
        result["errors"].append(
            completed.stderr.strip()
            or f"Nuclei terminó con código {completed.returncode}."
        )

    return result


__all__ = [
    "READ_ONLY",
    "RESPONSE_EXECUTION_ALLOWED",
    "parse_nuclei_jsonl",
    "run_nuclei_authorized",
]
