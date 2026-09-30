"""Phase 145 — measurable product KPIs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductMetrics:
    scenarios_tested: int
    tests_passed: int
    safety_invariants_verified: int
    execution_attempts_allowed: int
    human_review_required: bool
    response_locked: bool


def build_metrics(
    scenarios_tested: int,
    tests_passed: int,
) -> ProductMetrics:

    if scenarios_tested < 0:
        raise ValueError("scenarios_tested must be non-negative")

    if tests_passed < 0:
        raise ValueError("tests_passed must be non-negative")

    return ProductMetrics(
        scenarios_tested=scenarios_tested,
        tests_passed=tests_passed,
        safety_invariants_verified=5,
        execution_attempts_allowed=0,
        human_review_required=True,
        response_locked=True,
    )
