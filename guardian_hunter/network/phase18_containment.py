"""Phase 18.18 — Defensive Containment Simulation.

Simulation only. No firewall, routing, process, interface or network changes.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkContainmentSimulation:
    risk_level: str
    proposed_controls: List[str]
    simulated: bool
    changes_applied: bool
    execution_allowed: bool
    mode: str
    status: str


def _controls(risk_level: str) -> List[str]:
    level = str(risk_level).upper()

    if level == "CRITICAL":
        return [
            "SIMULATE_EGRESS_RESTRICTION",
            "SIMULATE_LISTENER_ISOLATION",
            "SIMULATE_DNS_REVIEW",
            "SIMULATE_CONNECTION_REVIEW",
        ]

    if level == "HIGH":
        return [
            "SIMULATE_EGRESS_REVIEW",
            "SIMULATE_LISTENER_REVIEW",
            "SIMULATE_DNS_REVIEW",
        ]

    if level == "WATCH":
        return [
            "SIMULATE_ENHANCED_MONITORING",
            "SIMULATE_EGRESS_REVIEW",
        ]

    return [
        "SIMULATE_CONTINUED_MONITORING",
    ]


def simulate_network_containment(
    risk_level: str,
) -> NetworkContainmentSimulation:
    return NetworkContainmentSimulation(
        risk_level=str(risk_level).upper(),
        proposed_controls=_controls(risk_level),
        simulated=True,
        changes_applied=False,
        execution_allowed=False,
        mode="READ_ONLY",
        status="SIMULATION_ONLY",
    )


def containment_to_dict(
    simulation: NetworkContainmentSimulation,
) -> Dict[str, Any]:
    return asdict(simulation)


def validate_network_containment(
    simulation: NetworkContainmentSimulation,
) -> bool:
    return (
        isinstance(simulation, NetworkContainmentSimulation)
        and simulation.simulated is True
        and simulation.changes_applied is False
        and simulation.execution_allowed is False
        and simulation.mode == "READ_ONLY"
        and simulation.status == "SIMULATION_ONLY"
        and bool(simulation.proposed_controls)
    )
