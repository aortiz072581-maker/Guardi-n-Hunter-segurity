"""Phase 41 — Defensive Security Audit Package."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityAuditPackage:
    controls: Dict[str, bool]
    passed: int
    failed: int
    total: int
    audit_valid: bool
    evidence_preserved: bool
    response_locked: bool
    digest: str
    mode: str
    execution_allowed: bool
    status: str


def _canonical(data: Dict[str, Any]) -> str:
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


def build_security_audit(
    controls: Dict[str, bool],
) -> SecurityAuditPackage:

    normalized = {
        str(key): bool(value)
        for key, value in controls.items()
    }

    total = len(normalized)
    passed = sum(
        1 for value in normalized.values()
        if value
    )
    failed = total - passed

    valid = total > 0 and failed == 0

    payload = {
        "controls": normalized,
        "passed": passed,
        "failed": failed,
        "total": total,
        "audit_valid": valid,
        "evidence_preserved": True,
        "response_locked": True,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    return SecurityAuditPackage(
        controls=normalized,
        passed=passed,
        failed=failed,
        total=total,
        audit_valid=valid,
        evidence_preserved=True,
        response_locked=True,
        digest=_digest(payload),
        mode="READ_ONLY",
        execution_allowed=False,
        status="AUDIT_VALID" if valid else "AUDIT_HOLD",
    )


def audit_to_dict(
    audit: SecurityAuditPackage,
) -> Dict[str, Any]:
    return asdict(audit)


def validate_security_audit(
    audit: SecurityAuditPackage,
) -> bool:
    return (
        isinstance(audit, SecurityAuditPackage)
        and audit.total == len(audit.controls)
        and audit.passed + audit.failed == audit.total
        and audit.audit_valid == (
            audit.total > 0
            and audit.failed == 0
        )
        and audit.evidence_preserved is True
        and audit.response_locked is True
        and len(audit.digest) == 64
        and audit.mode == "READ_ONLY"
        and audit.execution_allowed is False
    )
