"""Phase 18.19 — Network Recovery Verification.

Verification only. Does not perform recovery actions.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkRecoveryVerification:
    baseline_integrity: bool
    evidence_integrity: bool
    response_lock: bool
    post_event_stable: bool
    recovery_ready: bool
    execution_allowed: bool
    mode: str
    status: str


def verify_network_recovery(
    baseline_integrity: bool,
    evidence_integrity: bool,
    response_lock: bool,
    post_event_stable: bool,
) -> NetworkRecoveryVerification:

    ready = all(
        [
            bool(baseline_integrity),
            bool(evidence_integrity),
            bool(response_lock),
            bool(post_event_stable),
        ]
    )

    return NetworkRecoveryVerification(
        baseline_integrity=bool(baseline_integrity),
        evidence_integrity=bool(evidence_integrity),
        response_lock=bool(response_lock),
        post_event_stable=bool(post_event_stable),
        recovery_ready=ready,
        execution_allowed=False,
        mode="READ_ONLY",
        status="RECOVERY_VERIFIED" if ready else "RECOVERY_HOLD",
    )


def recovery_to_dict(
    recovery: NetworkRecoveryVerification,
) -> Dict[str, Any]:
    return asdict(recovery)


def validate_network_recovery(
    recovery: NetworkRecoveryVerification,
) -> bool:
    expected = (
        recovery.baseline_integrity
        and recovery.evidence_integrity
        and recovery.response_lock
        and recovery.post_event_stable
    )

    return (
        isinstance(recovery, NetworkRecoveryVerification)
        and recovery.recovery_ready == expected
        and recovery.execution_allowed is False
        and recovery.mode == "READ_ONLY"
        and recovery.status in {
            "RECOVERY_VERIFIED",
            "RECOVERY_HOLD",
        }
    )
