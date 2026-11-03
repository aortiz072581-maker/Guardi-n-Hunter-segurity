"""Phase 48 — Defensive Compliance Validation."""

from dataclasses import dataclass


@dataclass
class ComplianceResult:
    controls_checked: int
    controls_passed: int
    controls_failed: int
    compliance: str
    execution_allowed: bool = False


def assess_compliance(controls: dict) -> ComplianceResult:
    total = len(controls)
    passed = sum(bool(value) for value in controls.values())
    failed = total - passed

    if failed == 0:
        status = "COMPLIANT"
    elif passed > 0:
        status = "PARTIAL"
    else:
        status = "NON_COMPLIANT"

    return ComplianceResult(
        controls_checked=total,
        controls_passed=passed,
        controls_failed=failed,
        compliance=status,
        execution_allowed=False,
    )


def validate_compliance(result: ComplianceResult) -> bool:
    return (
        result.controls_checked
        == result.controls_passed + result.controls_failed
        and result.controls_checked >= 0
        and result.controls_passed >= 0
        and result.controls_failed >= 0
        and result.execution_allowed is False
    )


def build_compliance_report(result: ComplianceResult) -> dict:
    return {
        "phase": 48,
        "controls_checked": result.controls_checked,
        "controls_passed": result.controls_passed,
        "controls_failed": result.controls_failed,
        "compliance": result.compliance,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
