"""Phase 175 — Final Release Manifest."""

RELEASE_MANIFEST = {
    "product": "Guardian Hunter",
    "release": "1.0-RC",
    "classification": "DEFENSIVE_EVALUATION",
    "execution_mode": "BLOCKED",
    "data_mode": "SYNTHETIC_OR_AUTHORIZED",
    "review_mode": "HUMAN_REQUIRED",
    "response_mode": "LOCKED",
    "audit": "ENABLED",
    "traceability": "ENABLED",
}


def validate_release_manifest():
    assert RELEASE_MANIFEST["product"] == "Guardian Hunter"
    assert RELEASE_MANIFEST["release"] == "1.0-RC"
    assert RELEASE_MANIFEST["classification"] == "DEFENSIVE_EVALUATION"
    assert RELEASE_MANIFEST["execution_mode"] == "BLOCKED"
    assert RELEASE_MANIFEST["data_mode"] == "SYNTHETIC_OR_AUTHORIZED"
    assert RELEASE_MANIFEST["review_mode"] == "HUMAN_REQUIRED"
    assert RELEASE_MANIFEST["response_mode"] == "LOCKED"
    assert RELEASE_MANIFEST["audit"] == "ENABLED"
    assert RELEASE_MANIFEST["traceability"] == "ENABLED"

    return True
