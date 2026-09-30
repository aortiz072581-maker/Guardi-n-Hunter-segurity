"""Phase 142 — Guardian Hunter reproducible product demo.

The demo is descriptive and defensive only.
It never performs real execution or remediation.
"""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass(frozen=True)
class DemoResult:
    scenario: str
    detection: bool
    response_generated: bool
    execution_allowed: bool
    human_review_required: bool
    response_locked: bool


def run_demo_scenario(scenario: str) -> DemoResult:
    """Simulate a defensive detection/response scenario."""

    if not scenario:
        raise ValueError("scenario is required")

    return DemoResult(
        scenario=scenario,
        detection=True,
        response_generated=True,
        execution_allowed=False,
        human_review_required=True,
        response_locked=True,
    )
