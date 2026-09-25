from datetime import datetime


def build_dashboard(
    assets=0,
    executions=0,
    findings=0,
    alerts=0,
    critical=0,
    high=0,
    medium=0,
    low=0,
    changes=0,
):
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "assets": assets,
        "executions": executions,
        "findings": findings,
        "alerts": alerts,
        "risk": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "changes": changes,
    }


def render_dashboard(data):
    lines = [
        "GUARDIAN HUNTER",
        "=" * 32,
        f"Assets:      {data.get('assets', 0)}",
        f"Executions:  {data.get('executions', 0)}",
        f"Findings:    {data.get('findings', 0)}",
        f"Alerts:      {data.get('alerts', 0)}",
        "",
        "RISK",
        "-" * 32,
    ]

    risk = data.get("risk", {})

    for level in ("critical", "high", "medium", "low"):
        lines.append(
            f"{level.upper():12} {risk.get(level, 0)}"
        )

    lines.extend([
        "",
        f"Changes:     {data.get('changes', 0)}",
        "=" * 32,
    ])

    return "\n".join(lines)
