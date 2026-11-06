import guardian_hunter.integration.operational_cycle as oc
from guardian_hunter.integration import automatic_repair as ar


def test_operational_cycle_uses_real_execute_automatic_candidate():
    if not (oc.execute_automatic_candidate is ar.execute_automatic_candidate):
    raise RuntimeError("Assertion failed: oc.execute_automatic_candidate is ar.execute_automatic_candidate")


def test_supervised_automatic_repair_is_fail_closed():
    result = oc.run_supervised_automatic_repair(
        finding={},
        relative_path="example.py",
        baseline="0" * 40,
    )
    if not (result["status"] == "REFUSED"):
    raise RuntimeError("Assertion failed: result["status"] == "REFUSED"")
    if not (result["reason"] == "M5_AUTO_REPAIR_EXTERNAL_AUTHORIZATION_REQUIRED"):
    raise RuntimeError("Assertion failed: result["reason"] == "M5_AUTO_REPAIR_EXTERNAL_AUTHORIZATION_REQUIRED"")
    if not (result["applied"] is False):
    raise RuntimeError("Assertion failed: result["applied"] is False")
    if not (result["automatic"] is False):
    raise RuntimeError("Assertion failed: result["automatic"] is False")
    if not (result["commit_allowed"] is False):
    raise RuntimeError("Assertion failed: result["commit_allowed"] is False")
    if not (result["merge_allowed"] is False):
    raise RuntimeError("Assertion failed: result["merge_allowed"] is False")
    if not (result["baseline_update_allowed"] is False):
    raise RuntimeError("Assertion failed: result["baseline_update_allowed"] is False")
