"""Human approval bound to an exact repair proposal hash.

Approval here records authorization intent only.
It does not apply, execute, merge, or modify code.
"""

from __future__ import annotations

from dataclasses import dataclass
import hmac
import re

from guardian_hunter.repair.proposal import RepairProposal


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class HumanApproval:
    finding_id: str
    proposal_hash: str
    decision: str

    automatic_apply: bool = False
    execution_allowed: bool = False
    merge_allowed: bool = False

    def validate(self) -> None:
        if self.decision != "APPROVED":
            raise PermissionError("PROPOSAL_NOT_APPROVED")

        if not SHA256_RE.fullmatch(self.proposal_hash):
            raise ValueError("INVALID_PROPOSAL_HASH")

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
) -> HumanApproval:
    proposal.validate()

    if decision != "APPROVED":
        raise PermissionError("HUMAN_APPROVAL_REQUIRED")

    approval = HumanApproval(
        finding_id=proposal.finding_id,
        proposal_hash=proposal.proposal_hash,
        decision=decision,
    )

    approval.validate()
    return approval


def verify_approval(
    proposal: RepairProposal,
    approval: HumanApproval,
) -> bool:
    proposal.validate()
    approval.validate()

    if approval.finding_id != proposal.finding_id:
        raise PermissionError("FINDING_ID_MISMATCH")

    if not hmac.compare_digest(
        approval.proposal_hash,
        proposal.proposal_hash,
    ):
        raise PermissionError("PROPOSAL_HASH_MISMATCH")

    return True
