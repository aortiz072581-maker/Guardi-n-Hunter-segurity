from guardian_hunter.integration import e2e_diagnostic_flow as module


def test_diagnostic_flow_exports_safety_invariants():
    if not (module.READ_ONLY is True):
    raise RuntimeError("Assertion failed: module.READ_ONLY is True")
    if not (module.DRY_RUN is True):
    raise RuntimeError("Assertion failed: module.DRY_RUN is True")
    if not (module.REAL_EXECUTION_BLOCKED is True):
    raise RuntimeError("Assertion failed: module.REAL_EXECUTION_BLOCKED is True")
    if not (module.RESPONSE_LOCKED is True):
    raise RuntimeError("Assertion failed: module.RESPONSE_LOCKED is True")


def test_diagnostic_engine_is_locked(monkeypatch):
    base_result = {
        "status": "review_required",
        "stage": "human_review",
        "assessment": {
            "report": {
                "categories": ["network", "hardware"],
            }
        },
        "risk": {
            "max_score": 78.0,
        },
        "execution_allowed": False,
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "response_locked": True,
    }

    monkeypatch.setattr(
        module,
        "run_defensive_flow",
        lambda **kwargs: dict(base_result),
    )

    result = module.run_diagnostic_defensive_flow(
        target="example.test",
        asset_manager=object(),
        evidence_store=object(),
        actor_id="operator",
        request_id="request",
        authorization_id="authorization",
        nonce="nonce",
    )

    diagnosis = result["diagnosis"]

    if not (diagnosis is not None):
    raise RuntimeError("Assertion failed: diagnosis is not None")
    if not (diagnosis["problem_detected"] is True):
    raise RuntimeError("Assertion failed: diagnosis["problem_detected"] is True")
    if not (diagnosis["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: diagnosis["risk_level"] == "CRITICAL"")
    if not (diagnosis["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: diagnosis["execution_allowed"] is False")
    if not (diagnosis["dry_run"] is True):
    raise RuntimeError("Assertion failed: diagnosis["dry_run"] is True")
    if not ("KEEP_RESPONSE_LOCKED" in diagnosis["recommendations"]):
    raise RuntimeError("Assertion failed: "KEEP_RESPONSE_LOCKED" in diagnosis["recommendations"]")

    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["read_only"] is True):
    raise RuntimeError("Assertion failed: result["read_only"] is True")
    if not (result["dry_run"] is True):
    raise RuntimeError("Assertion failed: result["dry_run"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_blocked_flow_remains_blocked(monkeypatch):
    monkeypatch.setattr(
        module,
        "run_defensive_flow",
        lambda **kwargs: {
            "status": "blocked",
            "stage": "asset_authorization",
            "execution_allowed": False,
            "response_locked": True,
        },
    )

    result = module.run_diagnostic_defensive_flow(
        target="example.test",
        asset_manager=object(),
        evidence_store=object(),
        actor_id="operator",
        request_id="request",
        authorization_id="authorization",
        nonce="nonce",
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")
    if not (result["diagnosis"] is None):
    raise RuntimeError("Assertion failed: result["diagnosis"] is None")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
