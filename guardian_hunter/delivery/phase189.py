"""Phase 189 — Final Package Attestation."""

from .phase188 import run_delivery_gate


def build_delivery_attestation():
    result = run_delivery_gate()

    if not result["delivery_ready"]:
        return {
            "state": "DELIVERY_PACKAGE_FAILED",
            "score": result["score"],
            "release_allowed": False,
            "real_execution_blocked": True,
            "human_review_required": True,
            "response_locked": True,
        }

    return {
        "state": "FINAL_EVALUATION_PACKAGE_READY",
        "score": 100,
        "release_allowed": False,
        "real_execution_blocked": True,
        "human_review_required": True,
        "response_locked": True,
    }
