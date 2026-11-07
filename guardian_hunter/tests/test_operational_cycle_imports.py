import guardian_hunter.integration.operational_cycle as oc
from guardian_hunter.integration import automatic_repair as ar


def test_operational_cycle_uses_real_execute_automatic_candidate():
    assert oc.execute_automatic_candidate is ar.execute_automatic_candidate


def test_supervised_automatic_repair_is_fail_closed():
    result = oc.run_supervised_automatic_repair(
        finding={},
        relative_path="example.py",
        baseline="0" * 40,
    )
    assert result["status"] == "REFUSED"
    assert result["reason"] == "M5_AUTO_REPAIR_EXTERNAL_AUTHORIZATION_REQUIRED"
    assert result["applied"] is False
    assert result["automatic"] is False
    assert result["commit_allowed"] is False
    assert result["merge_allowed"] is False
    assert result["baseline_update_allowed"] is False
