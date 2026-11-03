from guardian_hunter.response import (
    build_policy_decision,
    create_incident,
    response_summary,
)


# LOW
low = build_policy_decision(
    "low",
    "baseline change",
    authorized=False,
)

assert low["response"] == "LOG"
assert low["execution_allowed"] is False


# MEDIUM
medium = build_policy_decision(
    "medium",
    "new network destination",
    authorized=False,
)

assert medium["response"] == "ALERT"
assert medium["execution_allowed"] is False


# HIGH, unauthorized
high_review = build_policy_decision(
    "high",
    "unexpected listener",
    authorized=False,
)

assert high_review["response"] == "CONTAINMENT_REVIEW"
assert high_review["execution_allowed"] is False


# HIGH, authorized
high_authorized = build_policy_decision(
    "high",
    "unexpected listener",
    authorized=True,
)

assert high_authorized["response"] == "CONTAINMENT_PENDING"
assert high_authorized["execution_allowed"] is False


# CRITICAL, authorized
incident = create_incident(
    risk_level="critical",
    reason="unexpected network behavior",
    target="test-interface",
    authorized=True,
    risk_data={
        "level": "critical",
        "score": 95,
    },
)

assert incident["incident_id"].startswith("GH-INC-")
assert incident["containment"]["mode"] == "DRY_RUN"
assert incident["containment"]["executed"] is False
assert incident["verification"]["verified"] is True
assert incident["rollback"]["rollback_available"] is True
assert incident["policy"]["execution_allowed"] is False

summary = response_summary(incident)

assert summary["risk_level"] == "critical"
assert summary["authorized"] is True
assert summary["execution_allowed"] is False
assert summary["containment_status"] == "PLANNED"
assert summary["verification"] == "VERIFIED"
assert summary["rollback"] == "ROLLBACK_READY"

print("PHASE 18 RESPONSE: OK")
print("DRY-RUN CONTAINMENT: OK")
print("VERIFICATION: OK")
print("ROLLBACK: OK")
print("EXECUTION GATE: SAFE")
