
"""Guardian Hunter Phase C: supervised defensive assessment."""

from __future__ import annotations

from collections import Counter
from importlib.util import find_spec

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
HUMAN_APPROVAL_REQUIRED = True

SEVERITIES = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}

def inventory(modules):
    result = {}

    for label, name in modules.items():
        try:
            available = find_spec(name) is not None
        except (ImportError, AttributeError, ValueError):
            available = False

        result[label] = {
            "module": name,
            "available": available,
        }

    return result


def correlate(findings):
    if not isinstance(findings, list):
        raise ValueError("INVALID_FINDINGS")

    normalized = []
    seen = set()

    for item in findings:
        if not isinstance(item, dict):
            raise ValueError("INVALID_FINDING")

        category = item.get("category")
        title = item.get("title")
        severity = item.get("severity", "medium")

        if (
            not isinstance(category, str)
            or not category.strip()
            or not isinstance(title, str)
            or not title.strip()
            or severity not in SEVERITIES
        ):
            raise ValueError("INVALID_FINDING_FIELDS")

        category = category.strip()[:100]
        title = title.strip()[:200]

        key = (category, title)

        if key in seen:
            continue

        seen.add(key)

        normalized.append({
            "category": category,
            "title": title,
            "severity": severity,
            "priority": SEVERITIES[severity],
        })

    normalized.sort(
        key=lambda x: (
            -x["priority"],
            x["category"],
            x["title"],
        )
    )

    return {
        "findings": normalized,
        "finding_count": len(normalized),
        "categories": dict(
            Counter(x["category"] for x in normalized)
        ),
        "execution_allowed": False,
    }


def diagnose(correlation):
    if not isinstance(correlation, dict):
        raise ValueError("INVALID_CORRELATION")

    findings = correlation.get("findings")

    if not isinstance(findings, list):
        raise ValueError("INVALID_FINDINGS")

    proposals = []

    for finding in findings:
        if (
            not isinstance(finding, dict)
            or finding.get("severity") not in SEVERITIES
            or not isinstance(finding.get("title"), str)
        ):
            raise ValueError("INVALID_FINDING")

        proposals.append({
            "problem": finding["title"],
            "category": finding["category"],
            "priority": finding["severity"],
            "probable_cause": "REQUIRES_INVESTIGATION",
            "recommendation": (
                "Revisar evidencia, confirmar causa "
                "y preparar propuesta supervisada."
            ),
            "status": "HUMAN_REVIEW_REQUIRED",
            "automatic_repair": False,
            "execution_allowed": False,
        })

    return {
        "problem_count": len(proposals),
        "proposals": proposals,
        "automatic_repair": False,
        "execution_allowed": False,
        "human_approval_required": True,
    }


def run_phase_c(modules, findings):
    assets = inventory(modules)
    correlation = correlate(findings)
    diagnosis = diagnose(correlation)

    return {
        "phase": "C1_C2_C3",
        "inventory": assets,
        "correlation": correlation,
        "diagnosis": diagnosis,
        "read_only": True,
        "dry_run": True,
        "execution_allowed": False,
        "automatic_repair": False,
        "human_approval_required": True,
    }
