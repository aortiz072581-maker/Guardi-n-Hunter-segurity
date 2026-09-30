"""Phase 153 — release validation evidence."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TestEvidence:
    suite_name: str
    tests_executed: int
    tests_passed: int
    tests_failed: int
    execution_allowed: bool
    response_locked: bool


def build_test_evidence(
    suite_name: str,
    tests_executed: int,
    tests_passed: int,
    tests_failed: int,
) -> TestEvidence:

    if tests_executed < 0:
        raise ValueError("tests_executed must be non-negative")

    if tests_passed < 0:
        raise ValueError("tests_passed must be non-negative")

    if tests_failed < 0:
        raise ValueError("tests_failed must be non-negative")

    return TestEvidence(
        suite_name=suite_name,
        tests_executed=tests_executed,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        execution_allowed=False,
        response_locked=True,
    )
