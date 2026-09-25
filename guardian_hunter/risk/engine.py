from dataclasses import dataclass


@dataclass
class RiskFinding:
    category: str
    title: str
    severity: str
    score: int
    evidence: str
    recommendation: str


SEVERITY_THRESHOLDS = {
    "critical": 90,
    "high": 70,
    "medium": 40,
    "low": 1,
}


def classify_score(score):
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(100, score))

    if score >= 90:
        return "critical"

    if score >= 70:
        return "high"

    if score >= 40:
        return "medium"

    if score > 0:
        return "low"

    return "informational"


def calculate_context_score(
    base_score,
    confidence=1.0,
    asset_criticality=1.0,
    exposure=1.0,
):
    try:
        base_score = float(base_score)
        confidence = float(confidence)
        asset_criticality = float(
            asset_criticality
        )
        exposure = float(exposure)
    except (TypeError, ValueError):
        return 0

    confidence = max(
        0.0,
        min(1.0, confidence),
    )

    asset_criticality = max(
        0.5,
        min(1.5, asset_criticality),
    )

    exposure = max(
        0.5,
        min(1.5, exposure),
    )

    score = (
        base_score
        * confidence
        * asset_criticality
        * exposure
    )

    return max(
        0,
        min(100, round(score)),
    )


def calculate_risk(findings):
    normalized = []

    for finding in findings or []:
        if not isinstance(finding, dict):
            continue

        try:
            base_score = int(
                finding.get("score", 0)
            )
        except (TypeError, ValueError):
            base_score = 0

        score = calculate_context_score(
            base_score,
            finding.get(
                "confidence",
                1.0,
            ),
            finding.get(
                "asset_criticality",
                1.0,
            ),
            finding.get(
                "exposure",
                1.0,
            ),
        )

        normalized.append({
            **finding,
            "base_score": base_score,
            "score": score,
            "severity": classify_score(
                score
            ),
        })

    normalized.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
    }

    for finding in normalized:
        summary[
            finding["severity"]
        ] += 1

    max_score = (
        normalized[0]["score"]
        if normalized
        else 0
    )

    return {
        "total": len(normalized),
        "max_score": max_score,
        "summary": summary,
        "findings": normalized,
    }


def risk_level(result):
    return classify_score(
        result.get(
            "max_score",
            0,
        )
    )
