"""Phase 34 — Defensive Security Release Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityReleaseGate:
    phase_results: Dict[str, bool]
    phases: List[str]
    total_phases: int
    passed_phases: int
    failed_phases: int
    release_ready: bool
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


def build_security_release_gate(
    phase_results: Dict[str, bool],
) -> SecurityReleaseGate:

    normalized = {
        str(key): bool(value)
        for key, value in phase_results.items()
    }

    phases = sorted(normalized.keys())

    total = len(phases)

    passed = sum(
        1 for value in normalized.values()
        if value
    )

    failed = total - passed

    ready = (
        total > 0
        and failed == 0
    )

    payload = {
        "phase_results": normalized,
        "phases": phases,
        "total_phases": total,
        "passed_phases": passed,
        "failed_phases": failed,
        "release_ready": ready,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    return SecurityReleaseGate(
        phase_results=normalized,
        phases=phases,
        total_phases=total,
        passed_phases=passed,
        failed_phases=failed,
        release_ready=ready,
        integrity_digest=_digest(payload),
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "RELEASE_READY_READ_ONLY"
            if ready
            else "RELEASE_HOLD"
        ),
    )


def release_to_dict(
    release: SecurityReleaseGate,
) -> Dict[str, Any]:
    return asdict(release)


def validate_security_release(
    release: SecurityReleaseGate,
) -> bool:
    return (
        isinstance(release, SecurityReleaseGate)
        and release.total_phases == len(release.phases)
        and release.passed_phases
        + release.failed_phases
        == release.total_phases
        and release.release_ready
        == (
            release.total_phases > 0
            and release.failed_phases == 0
        )
        and len(release.integrity_digest) == 64
        and release.mode == "READ_ONLY"
        and release.execution_allowed is False
    )
