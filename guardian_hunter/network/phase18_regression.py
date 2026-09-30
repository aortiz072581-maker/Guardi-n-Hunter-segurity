"""Phase 18.16 — Final Network Regression Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkRegressionGate:
    phases_checked: List[str]
    passed_phases: List[str]
    failed_phases: List[str]
    total_phases: int
    passed_count: int
    regression_status: str
    integrity_digest: str
    phase: str = "18.16"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _canonical(payload: Dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _digest(payload: Dict[str, Any]) -> str:
    return sha256(
        _canonical(payload).encode("utf-8")
    ).hexdigest()


def build_network_regression_gate(
    phase_results: Dict[str, Any],
) -> NetworkRegressionGate:

    results = {
        str(key): bool(value)
        for key, value in dict(phase_results).items()
    }

    phases = list(results.keys())
    passed = [
        phase
        for phase, status in results.items()
        if status
    ]
    failed = [
        phase
        for phase, status in results.items()
        if not status
    ]

    payload = {
        "phases_checked": phases,
        "passed_phases": passed,
        "failed_phases": failed,
        "total_phases": len(phases),
        "passed_count": len(passed),
    }

    digest = _digest(payload)

    return NetworkRegressionGate(
        phases_checked=phases,
        passed_phases=passed,
        failed_phases=failed,
        total_phases=len(phases),
        passed_count=len(passed),
        regression_status=(
            "REGRESSION_PASS"
            if not failed and phases
            else "REGRESSION_FAIL"
        ),
        integrity_digest=digest,
    )


def regression_to_dict(
    gate: NetworkRegressionGate,
) -> Dict[str, Any]:
    return asdict(gate)


def validate_network_regression_gate(
    gate: NetworkRegressionGate,
) -> bool:

    if not isinstance(gate, NetworkRegressionGate):
        return False

    payload = {
        "phases_checked": gate.phases_checked,
        "passed_phases": gate.passed_phases,
        "failed_phases": gate.failed_phases,
        "total_phases": gate.total_phases,
        "passed_count": gate.passed_count,
    }

    return (
        gate.total_phases
        == len(gate.phases_checked)
        and gate.passed_count
        == len(gate.passed_phases)
        and gate.regression_status in {
            "REGRESSION_PASS",
            "REGRESSION_FAIL",
        }
        and gate.integrity_digest == _digest(payload)
        and gate.phase == "18.16"
        and gate.mode == "READ_ONLY"
        and gate.execution_allowed is False
    )
