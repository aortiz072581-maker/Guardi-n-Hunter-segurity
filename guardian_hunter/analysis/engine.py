from guardian_hunter.risk import calculate_risk
from guardian_hunter.intelligence.enhanced import build_baseline, compare_baseline


def analyze(findings, previous_baseline=None):
    risk = calculate_risk(findings)

    current_baseline = build_baseline(risk.get("findings", []))

    changes = compare_baseline(
        previous_baseline,
        current_baseline,
    )

    return {
        "risk": risk,
        "baseline": current_baseline,
        "changes": changes,
    }
