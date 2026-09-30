"""Phase 190 — Master Delivery State."""

from .phase189 import build_delivery_attestation


def build_master_delivery_state():
    result = build_delivery_attestation()

    if result["state"] != "FINAL_EVALUATION_PACKAGE_READY":
        return {
            "state": "DELIVERY_NOT_READY",
            "score": result["score"],
            "release_allowed": False,
            "READ_ONLY": True,
            "DRY_RUN": True,
            "REAL_EXECUTION_BLOCKED": True,
            "HUMAN_REVIEW_REQUIRED": True,
            "RESPONSE_LOCKED": True,
        }

    return {
        "state": "FINAL_EVALUATION_PACKAGE_READY",
        "score": 100,
        "release_allowed": False,
        "READ_ONLY": True,
        "DRY_RUN": True,
        "REAL_EXECUTION_BLOCKED": True,
        "HUMAN_REVIEW_REQUIRED": True,
        "RESPONSE_LOCKED": True,
    }
