"""Phase 18.7 — Connection and Egress Intelligence
Observation-only network connection analysis.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
PHASE = 18.7


def _normalize_item(value: Any) -> str:
    if isinstance(value, dict):
        protocol = value.get("protocol", "")
        local = (
            value.get("local")
            or value.get("local_address")
            or value.get("source")
            or ""
        )
        remote = (
            value.get("remote")
            or value.get("remote_address")
            or value.get("destination")
            or ""
        )
        state = value.get("state", "")

        return "|".join(
            str(part).strip().lower()
            for part in (protocol, local, remote, state)
            if str(part).strip() != ""
        )

    return str(value).strip().lower()


def _normalize_items(values: Optional[Sequence[Any]]) -> List[str]:
    if not values:
        return []

    result = []

    for value in values:
        item = _normalize_item(value)
        if item and item not in result:
            result.append(item)

    return sorted(result)


def _score(new_connections: int, new_egress: int) -> int:
    return min(100, (new_connections * 20) + (new_egress * 25))


@dataclass(frozen=True)
class ConnectionEgressIntelligence:
    baseline_connections: List[str]
    current_connections: List[str]
    new_connections: List[str]
    removed_connections: List[str]
    baseline_egress: List[str]
    current_egress: List[str]
    new_egress: List[str]
    removed_egress: List[str]
    egress_score: int
    status: str
    observations: List[Dict[str, Any]]
    phase: float = PHASE
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def analyze_connection_egress(
    baseline_connections: Optional[Sequence[Any]] = None,
    current_connections: Optional[Sequence[Any]] = None,
    baseline_egress: Optional[Sequence[Any]] = None,
    current_egress: Optional[Sequence[Any]] = None,
) -> ConnectionEgressIntelligence:

    baseline_conn = _normalize_items(baseline_connections)
    current_conn = _normalize_items(current_connections)

    baseline_out = _normalize_items(baseline_egress)
    current_out = _normalize_items(current_egress)

    new_conn = sorted(set(current_conn) - set(baseline_conn))
    removed_conn = sorted(set(baseline_conn) - set(current_conn))

    new_out = sorted(set(current_out) - set(baseline_out))
    removed_out = sorted(set(baseline_out) - set(current_out))

    observations: List[Dict[str, Any]] = []

    for value in new_conn:
        observations.append(
            {
                "type": "CONNECTION",
                "value": value,
                "status": "NEW_CONNECTION",
                "severity": "MEDIUM",
                "read_only": True,
            }
        )

    for value in new_out:
        observations.append(
            {
                "type": "EGRESS",
                "value": value,
                "status": "NEW_EGRESS",
                "severity": "HIGH",
                "read_only": True,
            }
        )

    for value in removed_conn:
        observations.append(
            {
                "type": "CONNECTION",
                "value": value,
                "status": "REMOVED_CONNECTION",
                "severity": "LOW",
                "read_only": True,
            }
        )

    for value in removed_out:
        observations.append(
            {
                "type": "EGRESS",
                "value": value,
                "status": "REMOVED_EGRESS",
                "severity": "LOW",
                "read_only": True,
            }
        )

    score = _score(len(new_conn), len(new_out))

    if score >= 70:
        status = "HIGH"
    elif score >= 40:
        status = "WATCH"
    elif score > 0:
        status = "OBSERVED"
    else:
        status = "NORMAL"

    return ConnectionEgressIntelligence(
        baseline_connections=baseline_conn,
        current_connections=current_conn,
        new_connections=new_conn,
        removed_connections=removed_conn,
        baseline_egress=baseline_out,
        current_egress=current_out,
        new_egress=new_out,
        removed_egress=removed_out,
        egress_score=score,
        status=status,
        observations=observations,
    )


def connection_egress_to_dict(
    result: ConnectionEgressIntelligence,
) -> Dict[str, Any]:
    return asdict(result)


def validate_connection_egress(
    result: ConnectionEgressIntelligence,
) -> bool:
    return (
        isinstance(result, ConnectionEgressIntelligence)
        and result.phase == PHASE
        and result.mode == "READ_ONLY"
        and result.execution_allowed is False
        and isinstance(result.new_connections, list)
        and isinstance(result.new_egress, list)
        and isinstance(result.observations, list)
        and 0 <= result.egress_score <= 100
        and result.status in {"NORMAL", "OBSERVED", "WATCH", "HIGH"}
    )
