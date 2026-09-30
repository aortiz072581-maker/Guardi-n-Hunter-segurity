"""Phase 159 — buyer release readiness."""

from dataclasses import dataclass


RELEASE_REQUIREMENTS = {
    "release_manifest": True,
    "sbom_policy": True,
    "test_evidence": True,
    "reproducibility": True,
    "deployment_model": True,
    "buyer_demo": True,
    "limitations": True,
    "evidence_index": True,
}


@dataclass(frozen=True)
class ReleaseReadiness:
    ready: bool
    completed: int
    required: int
    execution_allowed: bool
    human_review_required: bool
    response_locked: bool


def audit_release() -> ReleaseReadiness:
    completed = sum(
        bool(value)
        for value in RELEASE_REQUIREMENTS.values()
    )

    required = len(RELEASE_REQUIREMENTS)

    return ReleaseReadiness(
        ready=completed == required,
        completed=completed,
        required=required,
        execution_allowed=False,
        human_review_required=True,
        response_locked=True,
    )
