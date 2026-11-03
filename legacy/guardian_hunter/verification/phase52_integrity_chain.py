"""Phase 52 — Defensive Integrity Chain."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class IntegrityChain:
    control_digest: str
    previous_digest: str
    chain_valid: bool
    execution_blocked: bool
    digest: str = ""


def _canonical(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _digest(data):
    clean = dict(data)
    clean.pop("digest", None)
    return sha256(_canonical(clean).encode()).hexdigest()


def build_integrity_chain(control_digest, previous_digest=""):
    valid = bool(control_digest) and (
        previous_digest == "" or bool(previous_digest)
    )

    payload = IntegrityChain(
        control_digest=control_digest,
        previous_digest=previous_digest,
        chain_valid=valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return IntegrityChain(**data)


def integrity_to_dict(chain):
    return asdict(chain)


def validate_integrity_chain(chain):
    if not isinstance(chain, IntegrityChain):
        return False

    data = asdict(chain)

    if not chain.control_digest:
        return False

    if chain.execution_blocked is not True:
        return False

    if chain.chain_valid is not True:
        return False

    return chain.digest == _digest(data)
