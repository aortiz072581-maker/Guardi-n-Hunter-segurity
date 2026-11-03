"""Phase 180 — Master Release Attestation."""

from .phase179 import run_release_gate


def build_master_release_attestation():
    result = run_release_gate()

    if not result["release_candidate_ready"]:
        return {
            "state": "RELEASE_CANDIDATE_FAILED",
            "score": result["score"],
            "release_allowed": False,
            "READ_ONLY": True,
            "DRY_RUN": True,
            "REAL_EXECUTION_BLOCKED": True,
            "HUMAN_REVIEW_REQUIRED": True,
            "RESPONSE_LOCKED": True,
        }

    return {
        "state": "RELEASE_CANDIDATE_READY",
        "score": 100,
        "release_allowed": False,
        "READ_ONLY": True,
        "DRY_RUN": True,
        "REAL_EXECUTION_BLOCKED": True,
        "HUMAN_REVIEW_REQUIRED": True,
        "RESPONSE_LOCKED": True,
    }
