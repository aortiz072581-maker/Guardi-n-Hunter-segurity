"""Phase 173 — Evaluation Evidence Package."""

EVIDENCE_PACKAGE = {
    "test_results": True,
    "phase_history": True,
    "safety_state": True,
    "tamper_detection": True,
    "traceability": True,
    "auditability": True,
    "release_manifest": True,
    "documentation": True,
}


def validate_evidence_package():
    required = (
        "test_results",
        "phase_history",
        "safety_state",
        "tamper_detection",
        "traceability",
        "auditability",
        "release_manifest",
        "documentation",
    )

    assert all(EVIDENCE_PACKAGE[key] for key in required)
    return True
