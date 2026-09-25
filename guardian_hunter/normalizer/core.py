from datetime import datetime, timezone


SCHEMA_VERSION = "1.0"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def normalize_finding(finding):
    if not isinstance(finding, dict):
        return None

    try:
        score = int(finding.get("score", 0))
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(100, score))

    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": finding.get("timestamp", utc_now()),
        "category": str(
            finding.get("category", "unknown")
        ).strip().lower(),
        "title": str(
            finding.get("title", "Unnamed finding")
        ).strip(),
        "score": score,
        "severity": finding.get("severity"),
        "evidence": str(
            finding.get("evidence", "")
        ).strip(),
        "recommendation": str(
            finding.get("recommendation", "")
        ).strip(),
        "source": str(
            finding.get("source", "assessment")
        ).strip(),
    }


def normalize_assessment(findings):
    normalized = []

    for finding in findings or []:
        item = normalize_finding(finding)

        if item is not None:
            normalized.append(item)

    return normalized


def normalize_result(result):
    if not isinstance(result, dict):
        return {
            "schema_version": SCHEMA_VERSION,
            "timestamp": utc_now(),
            "findings": [],
            "errors": ["Resultado inválido."],
        }

    findings = normalize_assessment(
        result.get("findings", [])
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": result.get(
            "timestamp",
            utc_now(),
        ),
        "target": result.get("target"),
        "findings": findings,
        "errors": result.get("errors", []),
    }
