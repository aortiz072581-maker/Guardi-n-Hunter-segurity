from guardian_hunter.response.phase19 import (
    create_plan,
    verify_plan,
    approve_plan,
    rollback_plan,
)

from guardian_hunter.hardening.phase20 import (
    system_baseline,
    baseline_fingerprint,
    compare_baseline,
    integrity_manifest,
)

from guardian_hunter.hardening.phase21 import (
    security_gate,
)


# --------------------------------------------------
# PHASE 19
# --------------------------------------------------

plan = create_plan(
    incident_id="GH-TEST-19",
    target="test-asset",
    action="QUARANTINE_ASSET",
    reason="integration test",
)

assert plan["mode"] == "DRY_RUN"
assert plan["executed"] is False
assert plan["execution_gate"] is False
assert plan["reversible"] is True

verification = verify_plan(plan)

assert verification["verified"] is True
assert verification["status"] == "VERIFIED"

approved = approve_plan(
    plan,
    approver="TEST_OPERATOR",
)

assert approved["approved"] is True
assert approved["execution_gate"] is False
assert approved["executed"] is False

rollback = rollback_plan(approved)

assert rollback["rollback_available"] is True
assert rollback["status"] == "ROLLBACK_READY"

print("PHASE 19 RESPONSE CONTROL: OK")


# --------------------------------------------------
# PHASE 20
# --------------------------------------------------

baseline = system_baseline()

assert "platform" in baseline
assert "network_interfaces" in baseline
assert "environment" in baseline

fingerprint = baseline_fingerprint(baseline)

assert isinstance(fingerprint, str)
assert len(fingerprint) == 64

comparison = compare_baseline(
    baseline,
    baseline,
)

assert comparison["changed"] is False
assert comparison["status"] == "UNCHANGED"

manifest = integrity_manifest([
    "guardian_hunter/response/phase19.py",
    "guardian_hunter/hardening/phase20.py",
    "guardian_hunter/hardening/phase21.py",
])

assert all(value for value in manifest.values())

print("PHASE 20 HARDENING BASELINE: OK")
print("PHASE 20 INTEGRITY MANIFEST: OK")


# --------------------------------------------------
# PHASE 21
# --------------------------------------------------

gate = security_gate(
    incident_id="GH-TEST-21",
    target="test-target",
)

assert gate["phase"] == 21
assert gate["status"] == "READY"
assert gate["execution_allowed"] is False

assert gate["response"]["mode"] == "DRY_RUN"
assert gate["response"]["executed"] is False

assert gate["verification"]["verified"] is True
assert gate["rollback"]["rollback_available"] is True

print("PHASE 21 SECURITY GATE: OK")
print("PHASE 21 EXECUTION SAFETY: OK")
print("PHASE 19-21 TEST: OK")
