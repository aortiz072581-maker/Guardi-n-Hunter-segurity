"""Phase 163 — Safe Demonstration Profile."""

DEMO_PROFILE = {
    "mode": "SIMULATION",
    "read_only": True,
    "dry_run": True,
    "real_execution": False,
    "human_review": True,
    "response_locked": True,
    "synthetic_data": True,
}


def validate_demo_profile():
    assert DEMO_PROFILE["mode"] == "SIMULATION"
    assert DEMO_PROFILE["read_only"] is True
    assert DEMO_PROFILE["dry_run"] is True
    assert DEMO_PROFILE["real_execution"] is False
    assert DEMO_PROFILE["human_review"] is True
    assert DEMO_PROFILE["response_locked"] is True
    assert DEMO_PROFILE["synthetic_data"] is True
    return True
