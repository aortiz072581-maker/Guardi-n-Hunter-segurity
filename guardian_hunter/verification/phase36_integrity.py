"""Phase 36 — Defensive Integrity Verification."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityIntegrityCheck:
    components: Dict[str, bool]
    total_components: int
    valid_components: int
    invalid_components: int
    integrity_score: int
    integrity_valid: bool
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


def verify_security_integrity(
    components: Dict[str, bool],
) -> SecurityIntegrityCheck:

    normalized = {
        str(key): bool(value)
        for key, value in components.items()
    }

    total = len(normalized)
    valid = sum(
        1 for value in normalized.values()
        if value
    )
    invalid = total - valid

    score = (
        int((valid / total) * 100)
        if total
        else 0
    )

    integrity_valid = (
        total > 0
        and invalid == 0
    )

    payload = {
        "components": normalized,
        "total_components": total,
        "valid_components": valid,
        "invalid_components": invalid,
        "integrity_score": score,
        "integrity_valid": integrity_valid,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    return SecurityIntegrityCheck(
        components=normalized,
        total_components=total,
        valid_components=valid,
        invalid_components=invalid,
        integrity_score=score,
        integrity_valid=integrity_valid,
        digest=_digest(payload),
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "INTEGRITY_VALID"
            if integrity_valid
            else "INTEGRITY_HOLD"
        ),
    )


def integrity_to_dict(
    integrity: SecurityIntegrityCheck,
) -> Dict[str, Any]:
    return asdict(integrity)


def validate_security_integrity(
    integrity: SecurityIntegrityCheck,
) -> bool:
    return (
        isinstance(integrity, SecurityIntegrityCheck)
        and integrity.total_components
        == len(integrity.components)
        and integrity.valid_components
        + integrity.invalid_components
        == integrity.total_components
        and 0 <= integrity.integrity_score <= 100
        and integrity.integrity_valid
        == (
            integrity.total_components > 0
            and integrity.invalid_components == 0
        )
        and len(integrity.digest) == 64
        and integrity.mode == "READ_ONLY"
        and integrity.execution_allowed is False
    )
