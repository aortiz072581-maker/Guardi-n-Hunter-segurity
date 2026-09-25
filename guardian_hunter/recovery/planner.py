"""Phase 35 — Defensive Recovery and Resilience Planner."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RecoveryStep:
    name: str
    category: str
    status: str = "PLANNED"
    executed: bool = False
    notes: str = ""


@dataclass
class RecoveryPlan:
    incident_id: str
    mode: str = "SIMULATION"
    execution_allowed: bool = False
    steps: list[RecoveryStep] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def add_step(
        self,
        name: str,
        category: str,
        notes: str = "",
    ) -> RecoveryStep:
        step = RecoveryStep(
            name=name,
            category=category,
            status="PLANNED",
            executed=False,
            notes=notes,
        )
        self.steps.append(step)
        return step

    def simulate(self) -> dict[str, Any]:
        results = []

        for step in self.steps:
            step.status = "SIMULATED"
            step.executed = False

            results.append({
                "name": step.name,
                "category": step.category,
                "status": step.status,
                "executed": False,
            })

        return {
            "incident_id": self.incident_id,
            "mode": "SIMULATION",
            "execution_allowed": False,
            "executed": False,
            "steps": results,
        }


def create_recovery_plan(incident_id: str) -> RecoveryPlan:
    if not incident_id:
        raise ValueError("incident_id required")

    return RecoveryPlan(
        incident_id=incident_id,
        mode="SIMULATION",
        execution_allowed=False,
    )


def validate_recovery(plan: RecoveryPlan) -> bool:
    if plan.mode != "SIMULATION":
        return False

    if plan.execution_allowed:
        return False

    if any(step.executed for step in plan.steps):
        return False

    return True


def resilience_check(
    *,
    evidence_integrity: bool,
    baseline_integrity: bool,
    audit_integrity: bool,
    health_ok: bool,
) -> dict[str, Any]:
    controls = {
        "evidence_integrity": bool(evidence_integrity),
        "baseline_integrity": bool(baseline_integrity),
        "audit_integrity": bool(audit_integrity),
        "health_ok": bool(health_ok),
    }

    passed = all(controls.values())

    return {
        "timestamp": _utc_now(),
        "status": "RESILIENT" if passed else "REVIEW_REQUIRED",
        "controls": controls,
        "all_controls_passed": passed,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
