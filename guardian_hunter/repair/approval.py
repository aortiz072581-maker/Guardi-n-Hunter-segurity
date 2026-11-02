"""Human approval bound to an exact repair proposal.

Approval records human authorization intent only.
It never grants execution, merge, or automatic application authority.

Consumption is explicit, persistent and single-use.
"""

from __future__ import annotations

from dataclasses import dataclass
import fcntl
import hmac
import json
import os
from pathlib import Path
import re
import secrets
from time import time

from guardian_hunter.repair.proposal import RepairProposal
from guardian_hunter.security.authorization_binding import canonical_hash


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
BASELINE_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DEFAULT_APPROVAL_TTL = 900.0


@dataclass(frozen=True)
class HumanApproval:
    finding_id: str
    proposal_hash: str
    decision: str
    approver_id: str
    nonce: str
    issued_at: float
    expires_at: float
    baseline: str
    policy_hash: str = ""

    automatic_apply: bool = False
    execution_allowed: bool = False
    merge_allowed: bool = False

    def validate(self) -> None:
        if self.decision != "APPROVED":
            raise PermissionError("PROPOSAL_NOT_APPROVED")

        if not SHA256_RE.fullmatch(self.proposal_hash):
            raise ValueError("INVALID_PROPOSAL_HASH")

        if not self.approver_id:
            raise ValueError("APPROVER_ID_REQUIRED")

        if not self.nonce:
            raise ValueError("APPROVAL_NONCE_REQUIRED")

        if self.expires_at <= self.issued_at:
            raise ValueError("INVALID_APPROVAL_LIFETIME")

        if not BASELINE_RE.fullmatch(self.baseline):
            raise ValueError("INVALID_BASELINE")

        if not SHA256_RE.fullmatch(self.policy_hash):
            raise ValueError("POLICY_HASH_REQUIRED")

        if self.automatic_apply:
            raise PermissionError("AUTOMATIC_APPLY_FORBIDDEN")

        if self.execution_allowed:
            raise PermissionError("EXECUTION_FORBIDDEN")

        if self.merge_allowed:
            raise PermissionError("MERGE_FORBIDDEN")


def approve(
    proposal: RepairProposal,
    *,
    decision: str,
    approver_id: str,
    baseline: str,
    now: float | None = None,
    ttl: float = DEFAULT_APPROVAL_TTL,
    policy=None,
) -> HumanApproval:
    proposal.validate()
    if policy is None:
        raise PermissionError("POLICY_CONTEXT_REQUIRED")

    if decision != "APPROVED":
        raise PermissionError("HUMAN_APPROVAL_REQUIRED")

    if ttl <= 0:
        raise ValueError("INVALID_APPROVAL_TTL")

    issued = time() if now is None else float(now)

    approval = HumanApproval(
        finding_id=proposal.finding_id,
        proposal_hash=proposal.proposal_hash,
        decision=decision,
        approver_id=approver_id,
        nonce=secrets.token_hex(32),
        issued_at=issued,
        expires_at=issued + ttl,
        baseline=baseline,
        policy_hash=canonical_hash(policy),
    )

    approval.validate()
    return approval


def verify_approval(
    proposal: RepairProposal,
    approval: HumanApproval,
    *,
    baseline: str,
    now: float | None = None,
    policy=None,
) -> bool:
    proposal.validate()
    approval.validate()
    if policy is None:
        raise PermissionError("POLICY_CONTEXT_REQUIRED")

    current = time() if now is None else float(now)

    if current < approval.issued_at:
        raise PermissionError("APPROVAL_NOT_YET_VALID")

    if current >= approval.expires_at:
        raise PermissionError("APPROVAL_EXPIRED")

    if approval.finding_id != proposal.finding_id:
        raise PermissionError("FINDING_ID_MISMATCH")

    if not hmac.compare_digest(
        approval.proposal_hash,
        proposal.proposal_hash,
    ):
        raise PermissionError("PROPOSAL_HASH_MISMATCH")

    if not hmac.compare_digest(
        approval.baseline,
        baseline,
    ):
        raise PermissionError("BASELINE_MISMATCH")

    current_policy_hash = canonical_hash(policy)
    if not hmac.compare_digest(approval.policy_hash, current_policy_hash):
        raise PermissionError("POLICY_HASH_MISMATCH")

    return True


class ApprovalLedger:
    """Persistent fail-closed single-use approval ledger."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def consume(
        self,
        proposal: RepairProposal,
        approval: HumanApproval,
        *,
        baseline: str,
        now: float | None = None,
        policy=None,
    ) -> bool:
        verify_approval(
            proposal,
            approval,
            baseline=baseline,
            now=now,
            policy=policy,
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
            mode=0o700,
        )

        flags = (
            os.O_RDWR
            | os.O_CREAT
            | os.O_NOFOLLOW
            | os.O_CLOEXEC
        )

        try:
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise RuntimeError(
                "APPROVAL_LEDGER_OPEN_FAILED"
            ) from exc

        try:
            fcntl.flock(fd, fcntl.LOCK_EX)

            with os.fdopen(
                os.dup(fd),
                "r",
                encoding="utf-8",
            ) as handle:
                consumed = {
                    line.strip()
                    for line in handle
                    if line.strip()
                }

            if approval.nonce in consumed:
                raise PermissionError("APPROVAL_REPLAYED")

            os.lseek(fd, 0, os.SEEK_END)

            payload = approval.nonce + "\n"
            data = payload.encode("utf-8")

            written = os.write(fd, data)

            if written != len(data):
                raise RuntimeError(
                    "APPROVAL_LEDGER_WRITE_FAILED"
                )

            os.fsync(fd)
            return True

        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
