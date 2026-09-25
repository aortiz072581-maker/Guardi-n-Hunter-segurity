"""Phase 34 — Defensive Incident Lifecycle."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


VALID_STATES = (
    "DETECTED",
    "INVESTIGATING",
    "CONTAINMENT_REVIEW",
    "RECOVERY_REVIEW",
    "CLOSED",
)


@dataclass
class IncidentLifecycle:
    incident_id: str
    state: str = "DETECTED"
    mode: str = "DRY_RUN"
    execution_allowed: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)

    def transition(self, new_state: str, reason: str = "") -> dict[str, Any]:
        if new_state not in VALID_STATES:
            raise ValueError(f"invalid incident state: {new_state}")

        event = {
            "timestamp": _utc_now(),
            "incident_id": self.incident_id,
            "from": self.state,
            "to": new_state,
            "reason": reason,
            "mode": "DRY_RUN",
            "execution_allowed": False,
        }

        self.state = new_state
        self.history.append(event)
        return event

    def snapshot(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "state": self.state,
            "mode": "DRY_RUN",
            "execution_allowed": False,
            "history_length": len(self.history),
        }


def create_incident(incident_id: str) -> IncidentLifecycle:
    if not incident_id:
        raise ValueError("incident_id required")

    return IncidentLifecycle(
        incident_id=incident_id,
        state="DETECTED",
        mode="DRY_RUN",
        execution_allowed=False,
    )


def close_incident(incident: IncidentLifecycle, reason: str = "") -> dict[str, Any]:
    return incident.transition("CLOSED", reason)


def validate_lifecycle(incident: IncidentLifecycle) -> bool:
    if incident.mode != "DRY_RUN":
        return False

    if incident.execution_allowed:
        return False

    if incident.state not in VALID_STATES:
        return False

    for event in incident.history:
        if event.get("execution_allowed") is not False:
            return False

    return True
