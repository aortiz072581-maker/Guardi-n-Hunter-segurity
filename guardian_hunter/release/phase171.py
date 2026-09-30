"""Phase 171 — Release Candidate Profile."""

RELEASE_CANDIDATE = {
    "product": "Guardian Hunter",
    "release_channel": "EVALUATION",
    "profile": "DEFENSIVE_READ_ONLY",
    "version": "1.0-RC",
    "READ_ONLY": True,
    "DRY_RUN": True,
    "REAL_EXECUTION_BLOCKED": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "RESPONSE_LOCKED": True,
}


def validate_release_candidate():
    assert RELEASE_CANDIDATE["product"] == "Guardian Hunter"
    assert RELEASE_CANDIDATE["release_channel"] == "EVALUATION"
    assert RELEASE_CANDIDATE["profile"] == "DEFENSIVE_READ_ONLY"
    assert RELEASE_CANDIDATE["version"] == "1.0-RC"

    assert RELEASE_CANDIDATE["READ_ONLY"] is True
    assert RELEASE_CANDIDATE["DRY_RUN"] is True
    assert RELEASE_CANDIDATE["REAL_EXECUTION_BLOCKED"] is True
    assert RELEASE_CANDIDATE["HUMAN_REVIEW_REQUIRED"] is True
    assert RELEASE_CANDIDATE["RESPONSE_LOCKED"] is True

    return True
