"""Phase 18.11 — Network Evidence Packaging."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkEvidencePackage:
    evidence_id: str
    source_phase: str
    evidence_type: str
    payload: Dict[str, Any]
    digest: str
    evidence_count: int
    phase: str = "18.11"
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


def build_network_evidence(
    evidence: Any,
    evidence_type: str = "NETWORK_DEFENSE",
    source_phase: str = "18",
) -> NetworkEvidencePackage:

    if isinstance(evidence, list):
        records = [
            item
            for item in evidence
            if isinstance(item, dict)
        ]
    elif isinstance(evidence, dict):
        records = [dict(evidence)]
    else:
        records = []

    payload = {
        "source_phase": str(source_phase),
        "evidence_type": str(evidence_type),
        "records": records,
        "read_only": READ_ONLY,
        "dry_run": DRY_RUN,
        "execution_allowed": EXECUTION_ALLOWED,
    }

    digest = _digest(payload)

    evidence_id = "NET-EVIDENCE-" + digest[:16]

    return NetworkEvidencePackage(
        evidence_id=evidence_id,
        source_phase=str(source_phase),
        evidence_type=str(evidence_type),
        payload=payload,
        digest=digest,
        evidence_count=len(records),
    )


def evidence_to_dict(
    package: NetworkEvidencePackage,
) -> Dict[str, Any]:
    return asdict(package)


def validate_network_evidence(
    package: NetworkEvidencePackage,
) -> bool:

    if not isinstance(package, NetworkEvidencePackage):
        return False

    if package.phase != "18.11":
        return False

    if package.mode != "READ_ONLY":
        return False

    if package.execution_allowed is not False:
        return False

    if not isinstance(package.payload, dict):
        return False

    expected = _digest(package.payload)

    return (
        package.digest == expected
        and package.evidence_id == "NET-EVIDENCE-" + expected[:16]
        and package.evidence_count == len(
            package.payload.get("records", [])
        )
    )
