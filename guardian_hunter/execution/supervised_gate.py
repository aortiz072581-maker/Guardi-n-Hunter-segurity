"""
Guardian Hunter supervised real-execution gate.

This module does NOT enable global execution.

It exposes one narrow path to the already existing transactional
repair executor.

Properties:
- fail closed
- explicit human approval required
- trusted baseline binding required
- single transactional repair only
- reverification required by transactional executor
- rollback remains controlled by transactional executor
- no commit authority
- no merge authority
- no trusted-baseline update authority
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from guardian_hunter.repair.proposal import RepairProposal
from guardian_hunter.repair.executor import RepairAction
from guardian_hunter.repair.approval import (
    HumanApproval,
    ApprovalLedger,
)
from guardian_hunter.integration.operational_cycle import (
    run_transactional_repair,
)


REAL_EXECUTION_ALLOWED = False
GLOBAL_EXECUTION_ALLOWED = False

COMMIT_ALLOWED = False
MERGE_ALLOWED = False
BASELINE_UPDATE_ALLOWED = False

SUPERVISED_TRANSACTION_ALLOWED = True


class SupervisedExecutionRefused(RuntimeError):
    """Raised when the supervised execution contract is not satisfied."""


def execute_supervised_transaction(
    *,
    proposal: RepairProposal,
    action: RepairAction,
    baseline: str,
    approval: HumanApproval,
    approval_ledger: ApprovalLedger,
    root: Path,
    reverify: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """
    Execute exactly one supervised repair transaction.

    This is intentionally NOT a general execution switch.

    The underlying transactional executor remains responsible for:
      * proposal/action binding
      * protected-file authorization
      * approval verification
      * single-use approval consumption
      * precondition hash verification
      * exact backup
      * atomic repair
      * post-write verification
      * rollback on failed reverification

    This gate never grants commit, merge, or trusted-baseline mutation.
    """

    if not baseline or not isinstance(baseline, str):
        raise SupervisedExecutionRefused("BASELINE_REQUIRED")

    if approval is None:
        raise SupervisedExecutionRefused("HUMAN_APPROVAL_REQUIRED")

    if approval_ledger is None:
        raise SupervisedExecutionRefused("APPROVAL_LEDGER_REQUIRED")

    if reverify is None or not callable(reverify):
        raise SupervisedExecutionRefused("REVERIFIER_REQUIRED")

    root = Path(root).resolve()

    result = run_transactional_repair(
        proposal=proposal,
        action=action,
        baseline=baseline,
        approval=approval,
        approval_ledger=approval_ledger,
        root=root,
        reverifier=reverify,
    )

    # Defense in depth: this gate must never acquire repository authority.
    result["commit_allowed"] = False
    result["merge_allowed"] = False
    result["baseline_update_allowed"] = False

    result["global_execution_allowed"] = False
    result["supervised_transaction"] = True

    return result
