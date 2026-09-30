"""Phase 35 — Defensive Security Control Matrix."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False

REQUIRED_CONTROLS = [
    "governance",
    "verification",
    "health",
    "audit",
    "evidence",
    "baseline",
    "response_lock",
    "dry_run",
]


@dataclass
class SecurityControlMatrix:
    controls: Dict[str, bool]
    total_controls: int
    passed_controls: int
    failed_controls: int
    coverage_percent: int
    complete: bool
    response_locked: bool
    mode: str
    execution_allowed: bool
    status: str


def build_control_matrix(
    controls: Dict[str, bool] | None = None,
) -> SecurityControlMatrix:

    source = controls or {
        name: True
        for name in REQUIRED_CONTROLS
    }

    normalized = {
        str(key): bool(value)
        for key, value in source.items()
    }

    total = len(normalized)
    passed = sum(
        1 for value in normalized.values()
        if value
    )
    failed = total - passed

    coverage = (
        int((passed / total) * 100)
        if total
        else 0
    )

    complete = (
        total == len(REQUIRED_CONTROLS)
        and all(
            normalized.get(name) is True
            for name in REQUIRED_CONTROLS
        )
    )

    return SecurityControlMatrix(
        controls=normalized,
        total_controls=total,
        passed_controls=passed,
        failed_controls=failed,
        coverage_percent=coverage,
        complete=complete,
        response_locked=True,
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "CONTROL_MATRIX_COMPLETE"
            if complete
            else "CONTROL_MATRIX_HOLD"
        ),
    )


def controls_to_dict(
    matrix: SecurityControlMatrix,
) -> Dict[str, Any]:
    return asdict(matrix)


def validate_control_matrix(
    matrix: SecurityControlMatrix,
) -> bool:
    return (
        isinstance(matrix, SecurityControlMatrix)
        and matrix.total_controls
        == len(matrix.controls)
        and matrix.passed_controls
        + matrix.failed_controls
        == matrix.total_controls
        and 0 <= matrix.coverage_percent <= 100
        and matrix.complete
        == (
            matrix.total_controls == len(REQUIRED_CONTROLS)
            and all(
                matrix.controls.get(name) is True
                for name in REQUIRED_CONTROLS
            )
        )
        and matrix.response_locked is True
        and matrix.mode == "READ_ONLY"
        and matrix.execution_allowed is False
    )
