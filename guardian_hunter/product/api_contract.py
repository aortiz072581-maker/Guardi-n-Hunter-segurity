"""Phase 143 — stable defensive API contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionRequest:
    subject: str
    risk_level: str


@dataclass(frozen=True)
class DetectionResponse:
    detected: bool
    risk_level: str
    response_state: str
    execution_allowed: bool
    human_review_required: bool
    response_locked: bool


def analyze(request: DetectionRequest) -> DetectionResponse:
    """Return a deterministic defensive analysis."""

    if not request.subject:
        raise ValueError("subject is required")

    return DetectionResponse(
        detected=True,
        risk_level=request.risk_level,
        response_state="DEFENSIVE_REVIEW_REQUIRED",
        execution_allowed=False,
        human_review_required=True,
        response_locked=True,
    )
