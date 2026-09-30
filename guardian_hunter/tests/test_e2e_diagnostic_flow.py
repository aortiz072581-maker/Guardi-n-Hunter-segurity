from guardian_hunter.integration import e2e_diagnostic_flow as module


def test_diagnostic_flow_exports_safety_invariants():
    assert module.READ_ONLY is True
    assert module.DRY_RUN is True
    assert module.REAL_EXECUTION_BLOCKED is True
    assert module.RESPONSE_LOCKED is True


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

    assert diagnosis is not None
    assert diagnosis["problem_detected"] is True
    assert diagnosis["risk_level"] == "CRITICAL"
    assert diagnosis["execution_allowed"] is False
    assert diagnosis["dry_run"] is True
    assert "KEEP_RESPONSE_LOCKED" in diagnosis["recommendations"]

    assert result["execution_allowed"] is False
    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["response_locked"] is True


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

    assert result["status"] == "blocked"
    assert result["diagnosis"] is None
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
