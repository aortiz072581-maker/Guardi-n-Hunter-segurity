"""Phase 18.5 — DNS Intelligence
READ_ONLY / DRY_RUN / no network activity.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
PHASE = 18.5


def _norm(value: Any) -> str:
    return str(value).strip().lower()


def _dns_items(values: Optional[Sequence[Any]]) -> List[str]:
    if not values:
        return []

    result = []

    for item in values:
        if isinstance(item, dict):
            value = (
                item.get("server")
                or item.get("address")
                or item.get("dns")
                or item.get("ip")
            )
        else:
            value = item

        if value is not None:
            normalized = _norm(value)
            if normalized and normalized not in result:
                result.append(normalized)

    return sorted(result)


@dataclass(frozen=True)
class DNSIntelligence:
    baseline_servers: List[str]
    current_servers: List[str]
    added_servers: List[str]
    removed_servers: List[str]
    changed: bool
    status: str
    observations: List[Dict[str, Any]]
    phase: float = PHASE
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def analyze_dns_intelligence(
    baseline_servers: Optional[Sequence[Any]] = None,
    current_servers: Optional[Sequence[Any]] = None,
    dns_queries: Optional[Sequence[Any]] = None,
) -> DNSIntelligence:
    baseline = _dns_items(baseline_servers)
    current = _dns_items(current_servers)

    added = sorted(set(current) - set(baseline))
    removed = sorted(set(baseline) - set(current))

    observations: List[Dict[str, Any]] = []

    for server in current:
        if server in added:
            status = "NEW"
        else:
            status = "KNOWN"

        observations.append(
            {
                "server": server,
                "status": status,
                "read_only": True,
            }
        )

    for server in removed:
        observations.append(
            {
                "server": server,
                "status": "REMOVED",
                "read_only": True,
            }
        )

    if not baseline and current:
        status = "NEW_BASELINE"
    elif added or removed:
        status = "CHANGED"
    else:
        status = "KNOWN"

    if dns_queries:
        for query in dns_queries:
            if isinstance(query, dict):
                domain = (
                    query.get("domain")
                    or query.get("name")
                    or query.get("query")
                )
                answer = query.get("answer")
            else:
                domain = query
                answer = None

            if domain:
                observations.append(
                    {
                        "domain": _norm(domain),
                        "answer": answer,
                        "status": "OBSERVED",
                        "read_only": True,
                    }
                )

    return DNSIntelligence(
        baseline_servers=baseline,
        current_servers=current,
        added_servers=added,
        removed_servers=removed,
        changed=bool(added or removed),
        status=status,
        observations=observations,
    )


def dns_intelligence_to_dict(result: DNSIntelligence) -> Dict[str, Any]:
    return asdict(result)


def validate_dns_intelligence(result: DNSIntelligence) -> bool:
    return (
        isinstance(result, DNSIntelligence)
        and result.phase == PHASE
        and result.mode == "READ_ONLY"
        and result.execution_allowed is False
        and isinstance(result.baseline_servers, list)
        and isinstance(result.current_servers, list)
        and isinstance(result.added_servers, list)
        and isinstance(result.removed_servers, list)
        and isinstance(result.observations, list)
        and result.changed
        == bool(result.added_servers or result.removed_servers)
    )
