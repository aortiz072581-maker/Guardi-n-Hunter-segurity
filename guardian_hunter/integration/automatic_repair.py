"""Fail-closed automatic repair orchestration.

This layer may automatically execute only an exact RepairAction for an
ordinary, non-protected path. It cannot approve protected repairs, commit,
merge, modify the trusted baseline, or turn free-form diagnostic text into
filesystem mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from guardian_hunter.repair.executor import RepairAction
from guardian_hunter.repair.proposal import RepairProposal


@dataclass(frozen=True)
class AutomaticRepairCandidate:
    proposal: RepairProposal
    action: RepairAction

    def validate(self) -> None:
        self.proposal.validate()

        if self.action.relative_path not in self.proposal.affected_files:
            raise ValueError("ACTION_NOT_IN_PROPOSAL")

        if not isinstance(self.action.replacement, bytes):
            raise TypeError("REPLACEMENT_MUST_BE_BYTES")

        if (
            self.action.expected_sha256 is not None
            and (
                len(self.action.expected_sha256) != 64
                or any(
                    c not in "0123456789abcdef"
                    for c in self.action.expected_sha256
                )
            )
        ):
            raise ValueError("INVALID_EXPECTED_SHA256")


def execute_automatic_candidate(
    *,
    candidate: AutomaticRepairCandidate,
    baseline: str,
    transaction_runner: Callable[..., dict[str, Any]],
    authority_classifier: Callable[..., dict[str, Any]],
    root: Path,
    reverifier=None,
) -> dict[str, Any]:
    """Execute one exact low-risk candidate or fail closed."""

    try:
        candidate.validate()
    except Exception as exc:
        return {
            "status": "REFUSED",
            "reason": f"INVALID_CANDIDATE:{type(exc).__name__}:{exc}",
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
        }

    proposal = candidate.proposal
    action = candidate.action

    authority = authority_classifier(
        list(proposal.affected_files)
    )

    if action.relative_path in authority["protected_files"]:
        return {
            "status": "APPROVAL_REQUIRED",
            "reason": "PROTECTED_REPAIR_REQUIRES_HUMAN_APPROVAL",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    # Mixed proposals are also refused. Automatic authority must never be
    # inherited from one ordinary file while another affected file is
    # protected.
    if authority["protected_files"]:
        return {
            "status": "APPROVAL_REQUIRED",
            "reason": "PROPOSAL_TOUCHES_PROTECTED_BOUNDARY",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    result = transaction_runner(
        proposal=proposal,
        action=action,
        baseline=baseline,
        root=root,
        reverifier=reverifier,
    )

    # Authority is narrowed here regardless of what a future transaction
    # implementation returns.
    result = dict(result)
    result["automatic"] = True
    result["commit_allowed"] = False
    result["merge_allowed"] = False
    result["baseline_update_allowed"] = False

    return result


def execute_candidate_batch(
    *,
    candidates: tuple[AutomaticRepairCandidate, ...],
    baseline: str,
    transaction_runner: Callable[..., dict[str, Any]],
    authority_classifier: Callable[..., dict[str, Any]],
    root: Path,
    reverifier=None,
) -> dict[str, Any]:
    """Process candidates sequentially and stop on unsafe transaction state."""

    results: list[dict[str, Any]] = []

    for candidate in candidates:
        result = execute_automatic_candidate(
            candidate=candidate,
            baseline=baseline,
            transaction_runner=transaction_runner,
            authority_classifier=authority_classifier,
            root=root,
            reverifier=reverifier,
        )

        results.append(result)

        # A failed rollback means filesystem state is uncertain. Nothing else
        # may be modified automatically in this cycle.
        if result.get("status") == "ROLLBACK_FAILED":
            break

    changed = any(
        bool(result.get("applied"))
        for result in results
    )

    uncertain = any(
        result.get("status") == "ROLLBACK_FAILED"
        for result in results
    )

    return {
        "candidate_count": len(candidates),
        "processed_count": len(results),
        "results": results,
        "filesystem_changed": changed,
        "filesystem_state_uncertain": uncertain,
        "automatic_commit": False,
        "automatic_merge": False,
        "automatic_baseline_update": False,
    }
