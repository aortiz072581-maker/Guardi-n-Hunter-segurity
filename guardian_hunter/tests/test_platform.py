from guardian_hunter.alerts import (
    alert_summary,
    generate_alerts,
)
from guardian_hunter.assets import AssetManager
from guardian_hunter.intelligence import (
    correlate,
)
from guardian_hunter.normalizer import (
    normalize_assessment,
)
from guardian_hunter.pipeline import (
    SecurityPipeline,
)
from guardian_hunter.reports import (
    export_bundle,
)
from guardian_hunter.risk import (
    calculate_risk,
    classify_score,
    risk_level,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


# NORMALIZER
findings = normalize_assessment([
    {
        "category": "headers",
        "title": "Test finding",
        "score": 85,
        "evidence": "internal test",
        "recommendation": "review",
    }
])

check(
    len(findings) == 1,
    "Normalizer failed",
)

check(
    findings[0]["score"] == 85,
    "Normalizer score failed",
)

print("NORMALIZER ADVANCED: OK")


# RISK
risk = calculate_risk(findings)

check(
    risk["total"] == 1,
    "Risk total failed",
)

check(
    risk["findings"][0]["severity"] == "high",
    "Risk severity failed",
)

check(
    classify_score(95) == "critical",
    "Critical classification failed",
)

check(
    risk_level(risk) == "high",
    "Risk level failed",
)

print("RISK ENGINE ADVANCED: OK")


# INTELLIGENCE
intel = correlate(
    technologies=["nginx"],
    technology_catalog=[
        {
            "name": "nginx",
            "version": "1.0",
            "source": "test",
        }
    ],
    cve_catalog=[
        {
            "id": "CVE-TEST-0001",
            "severity": "high",
            "description": "nginx test issue",
        }
    ],
)

check(
    len(intel["technology_matches"]) == 1,
    "Technology correlation failed",
)

check(
    len(intel["cve_matches"]) == 1,
    "CVE correlation failed",
)

print("INTELLIGENCE CORRELATION: OK")


# ALERTS
alerts = generate_alerts(risk)

check(
    len(alerts) == 1,
    "Alert generation failed",
)

summary = alert_summary(alerts)

check(
    summary["high"] == 1,
    "Alert summary failed",
)

print("ALERT ENGINE ADVANCED: OK")


# REPORTS
bundle = export_bundle(
    {
        "findings": findings,
        "risk": risk,
        "alerts": alerts,
    },
    "_internal_platform_test",
)

check(
    bundle["json"] is not None,
    "JSON report failed",
)

check(
    bundle["csv"] is not None,
    "CSV report failed",
)

print("REPORT ENGINE ADVANCED: OK")


# ASSET AUTHORIZATION
assets = AssetManager(
    path="data/test_asset_registry.json"
)

assets.add_authorized(
    "internal.test"
)

pipeline = SecurityPipeline(
    assets
)

try:
    pipeline.assess(
        "unauthorized.test"
    )

except PermissionError:
    print("AUTHORIZATION GATE: OK")

else:
    raise AssertionError(
        "Authorization gate failed"
    )


# No network assessment is executed.
print("NETWORK-SAFE TEST: OK")
print("FULL ADVANCED PLATFORM TEST: OK")
