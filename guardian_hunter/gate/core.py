"""Guardian Gate — fail-closed promotion boundary.

The Gate evaluates a candidate workspace.
It never approves its own changes and never performs a merge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256


PROTECTED_PREFIXES = (
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/evidence/",
    "guardian_hunter/gate/",
)

HUMAN_REVIEW_REQUIRED = True
AGENT_MERGE_ALLOWED = False
FAIL_CLOSED = True


@dataclass(frozen=True)
class GateResult:
    passed: bool
    reason: str
    human_review_required: bool = True
    agent_merge_allowed: bool = False


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def protected_change(path: str) -> bool:
    clean = path.replace("\\", "/").lstrip("./")
    return any(clean.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def evaluate_candidate(changed_files: list[str]) -> GateResult:
    if not FAIL_CLOSED:
        return GateResult(False, "GATE_FAIL_CLOSED_DISABLED")

    if not HUMAN_REVIEW_REQUIRED:
        return GateResult(False, "HUMAN_REVIEW_DISABLED")

    if AGENT_MERGE_ALLOWED:
        return GateResult(False, "AGENT_MERGE_FORBIDDEN")

    protected = sorted(
        path for path in changed_files
        if protected_change(path)
    )

    if protected:
        return GateResult(
            False,
            "PROTECTED_BOUNDARY_CHANGED:" + ",".join(protected),
        )

    return GateResult(
        True,
        "CANDIDATE_ACCEPTABLE_FOR_HUMAN_REVIEW",
    )
