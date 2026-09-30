"""Phase 151 — deterministic Guardian Hunter release manifest."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseManifest:
    product: str
    release_stage: str
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool
    execution_allowed: bool


def build_release_manifest() -> ReleaseManifest:
    return ReleaseManifest(
        product="Guardian Hunter",
        release_stage="BUYER_EVALUATION",
        read_only=True,
        dry_run=True,
        real_execution_blocked=True,
        human_review_required=True,
        response_locked=True,
        execution_allowed=False,
    )
