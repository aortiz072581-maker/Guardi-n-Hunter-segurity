"""Phase 18.20 — Final Network Defense Integration.

Final read-only gate for Phase 18.
"""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkFinalIntegration:
    phases: List[str]
    total_phases: int
    passed_phases: int
    failed_phases: int
    regression_pass: bool
    integrity_digest: str
    mode: str
    execution_allowed: bool
    status: str


def _canonical(data: Dict[str, Any]) -> str:
    import json
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _digest(data: Dict[str, Any]) -> str:
    return sha256(
        _canonical(data).encode("utf-8")
    ).hexdigest()


def build_network_final_integration(
    phase_results: Dict[str, bool],
) -> NetworkFinalIntegration:

    phases = sorted(str(k) for k in phase_results.keys())
    total = len(phases)
    passed = sum(
        1 for value in phase_results.values()
        if bool(value)
    )
    failed = total - passed

    regression_pass = (
        total > 0
        and failed == 0
    )

    payload = {
        "phases": phases,
        "total_phases": total,
        "passed_phases": passed,
        "failed_phases": failed,
        "regression_pass": regression_pass,
        "mode": "READ_ONLY",
        "execution_allowed": False,
        "status": (
            "NETWORK_DEFENSE_READY"
            if regression_pass
            else "NETWORK_DEFENSE_HOLD"
        ),
    }

    return NetworkFinalIntegration(
        phases=phases,
        total_phases=total,
        passed_phases=passed,
        failed_phases=failed,
        regression_pass=regression_pass,
        integrity_digest=_digest(payload),
        mode="READ_ONLY",
        execution_allowed=False,
        status=payload["status"],
    )


def final_to_dict(
    final: NetworkFinalIntegration,
) -> Dict[str, Any]:
    return asdict(final)


def validate_network_final_integration(
    final: NetworkFinalIntegration,
) -> bool:

    return (
        isinstance(final, NetworkFinalIntegration)
        and final.total_phases == len(final.phases)
        and final.passed_phases + final.failed_phases
        == final.total_phases
        and final.execution_allowed is False
        and final.mode == "READ_ONLY"
        and final.status in {
            "NETWORK_DEFENSE_READY",
            "NETWORK_DEFENSE_HOLD",
        }
        and bool(final.integrity_digest)
    )
