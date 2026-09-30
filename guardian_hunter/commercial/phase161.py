"""Phase 161 — Product Boundary."""

PRODUCT_NAME = "Guardian Hunter"
PRODUCT_MODE = "DEFENSIVE_SECURITY_PLATFORM"

SAFETY_STATE = {
    "READ_ONLY": True,
    "DRY_RUN": True,
    "REAL_EXECUTION_BLOCKED": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "RESPONSE_LOCKED": True,
}

PRODUCT_BOUNDARY = {
    "authorized_targets_only": True,
    "defensive_detection": True,
    "auditability": True,
    "traceability": True,
    "human_governance": True,
    "real_execution": False,
}


def validate_product_boundary():
    assert PRODUCT_NAME == "Guardian Hunter"
    assert PRODUCT_MODE == "DEFENSIVE_SECURITY_PLATFORM"
    assert SAFETY_STATE["READ_ONLY"] is True
    assert SAFETY_STATE["DRY_RUN"] is True
    assert SAFETY_STATE["REAL_EXECUTION_BLOCKED"] is True
    assert SAFETY_STATE["HUMAN_REVIEW_REQUIRED"] is True
    assert SAFETY_STATE["RESPONSE_LOCKED"] is True
    assert PRODUCT_BOUNDARY["real_execution"] is False
    return True
