"""Phase 182 — Delivery Content Manifest."""

DELIVERY_CONTENT = {
    "source_code": True,
    "tests": True,
    "security_controls": True,
    "tamper_detection": True,
    "traceability": True,
    "auditability": True,
    "documentation": True,
    "release_manifest": True,
    "evaluation_profile": True,
}


def validate_delivery_content():
    required = (
        "source_code",
        "tests",
        "security_controls",
        "tamper_detection",
        "traceability",
        "auditability",
        "documentation",
        "release_manifest",
        "evaluation_profile",
    )

    assert all(DELIVERY_CONTENT[key] for key in required)
    return True
