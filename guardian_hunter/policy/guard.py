"""Phase 32 — Defensive policy and execution guard."""

ALLOWED_MODES = {
    "READ_ONLY",
    "DRY_RUN",
    "SIMULATION",
}

BLOCKED_ACTIONS = {
    "DELETE",
    "WIPE",
    "DESTROY",
    "PERSIST",
    "CREDENTIAL_CHANGE",
    "UNAUTHORIZED_EXECUTION",
}


def evaluate_policy(
    *,
    action,
    mode="DRY_RUN",
    approved=False,
    execution_requested=False,
):
    action_name = str(action).upper()
    mode_name = str(mode).upper()

    reasons = []

    if action_name in BLOCKED_ACTIONS:
        reasons.append("ACTION_BLOCKED_BY_POLICY")

    if mode_name not in ALLOWED_MODES:
        reasons.append("MODE_NOT_ALLOWED")

    if execution_requested:
        reasons.append("REAL_EXECUTION_DISABLED")

    if approved:
        reasons.append("APPROVAL_DOES_NOT_UNLOCK_EXECUTION")

    allowed = not reasons

    return {
        "action": action_name,
        "mode": mode_name,
        "approved": bool(approved),
        "execution_requested": bool(execution_requested),
        "allowed": allowed,
        "execution_allowed": False,
        "reasons": reasons,
        "dry_run": mode_name == "DRY_RUN",
        "policy_version": "32.1",
    }


def enforce_policy(**kwargs):
    """Return policy result without executing anything."""
    return evaluate_policy(**kwargs)


def policy_safe(result):
    return (
        result.get("execution_allowed") is False
        and result.get("mode") in ALLOWED_MODES
    )
