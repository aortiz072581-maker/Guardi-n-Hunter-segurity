def generate_alerts(risk_result, history=None):
    alerts = []

    for finding in risk_result.get("findings", []):
        severity = finding.get("severity")

        if severity not in {"critical", "high"}:
            continue

        alert = {
            "severity": severity,
            "title": finding.get(
                "title",
                "Security finding",
            ),
            "message": finding.get(
                "evidence",
                "",
            ),
            "source": "risk_engine",
        }

        alerts.append(alert)

        if history is not None:
            history.add(
                severity=alert["severity"],
                title=alert["title"],
                message=alert["message"],
                source=alert["source"],
            )

    return alerts


def alert_summary(alerts):
    summary = {
        "critical": 0,
        "high": 0,
        "total": 0,
    }

    for alert in alerts or []:
        severity = alert.get("severity")

        if severity in summary:
            summary[severity] += 1

    summary["total"] = len(alerts or [])

    return summary
