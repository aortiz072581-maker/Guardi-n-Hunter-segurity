from guardian_hunter.hardening.phase20 import (
    baseline_fingerprint,
    compare_baseline,
    system_baseline,
)

from guardian_hunter.response.phase19 import (
    create_plan,
    rollback_plan,
    verify_plan,
)


def security_gate(incident_id: str, target: str) -> dict:
    baseline = system_baseline()
    fingerprint = baseline_fingerprint(baseline)

    plan = create_plan(
        incident_id=incident_id,
        target=target,
        action="QUARANTINE_ASSET",
        reason="Phase 21 controlled response",
    )

    verification = verify_plan(plan)
    rollback = rollback_plan(plan)

    return {
        "phase": 21,
        "baseline": baseline,
        "baseline_fingerprint": fingerprint,
        "response": plan,
        "verification": verification,
        "rollback": rollback,

        # Final safety invariant.
        "execution_allowed": False,
        "status": (
            "READY"
            if verification["verified"]
            and rollback["rollback_available"]
            and not plan["executed"]
            else "BLOCKED"
        ),
    }
