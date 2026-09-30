"""Phase 172 — Reproducible Defensive Demonstration."""

DEMO_CONTRACT = {
    "deterministic": True,
    "synthetic_input": True,
    "read_only": True,
    "dry_run": True,
    "real_execution": False,
    "human_review": True,
    "response_locked": True,
}


def run_demo():
    return {
        "demo": "Guardian Hunter Defensive Evaluation",
        "input": "SYNTHETIC_SECURITY_EVENT",
        "detection": "SIMULATED_DEFENSIVE_DETECTION",
        "action": "NO_REAL_EXECUTION",
        "state": "REVIEW_REQUIRED",
        "locked": True,
    }


def validate_demo():
    result = run_demo()

    assert DEMO_CONTRACT["deterministic"] is True
    assert DEMO_CONTRACT["synthetic_input"] is True
    assert DEMO_CONTRACT["read_only"] is True
    assert DEMO_CONTRACT["dry_run"] is True
    assert DEMO_CONTRACT["real_execution"] is False
    assert DEMO_CONTRACT["human_review"] is True
    assert DEMO_CONTRACT["response_locked"] is True

    assert result["action"] == "NO_REAL_EXECUTION"
    assert result["state"] == "REVIEW_REQUIRED"
    assert result["locked"] is True

    return result
