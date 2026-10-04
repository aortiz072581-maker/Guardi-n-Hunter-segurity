"""Guardian Hunter supervised operational cycle.

Connects the existing defensive components without granting autonomous
authority over trust boundaries, commits, merges, or trusted baselines.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from guardian_hunter.auditor.engine import audit_extended_security
from guardian_hunter.integration.health_recovery import run_health_recovery
from guardian_hunter.integration.problem_advisor import advise_health_result
from guardian_hunter.repair.proposal import RepairProposal


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROTECTED_PREFIXES = (
    ".git/",
    ".guardian/",
    "guardian_hunter/gate/",
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
    "guardian_hunter/auditor/",
    "guardian_hunter/repair/",
    "guardian_hunter/runner/",
)

AUTOMATIC_COMMIT = False
AUTOMATIC_BASELINE_UPDATE = False
AUTOMATIC_MERGE = False
HUMAN_APPROVAL_FOR_PROTECTED = True


def _tool(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {
        "name": name,
        "available": path is not None,
        "path": path,
    }


def discover_tools() -> dict[str, dict[str, Any]]:
    names = (
        "python",
        "python3",
        "pytest",
        "git",
        "nuclei",
        "semgrep",
        "bandit",
        "ruff",
        "mypy",
        "shellcheck",
        "trivy",
        "gitleaks",
        "claude",
        "aider",
        "codex",
    )
    return {name: _tool(name) for name in names}


def _is_protected(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


def classify_repair_authority(
    affected_files: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    protected = tuple(path for path in affected_files if _is_protected(path))

    return {
        "affected_files": tuple(affected_files),
        "protected_files": protected,
        "low_risk_candidate": not protected,
        "automatic_apply_allowed": False,
        "human_approval_required": True,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "merge_allowed": False,
    }


def _finding_to_dict(finding: Any) -> dict[str, Any]:
    if hasattr(finding, "__dataclass_fields__"):
        return {
            name: getattr(finding, name)
            for name in finding.__dataclass_fields__
        }

    if isinstance(finding, dict):
        return dict(finding)

    return {
        "finding_id": getattr(finding, "finding_id", "UNKNOWN"),
        "severity": str(getattr(finding, "severity", "UNKNOWN")),
        "summary": getattr(
            finding,
            "summary",
            getattr(finding, "title", repr(finding)),
        ),
    }


def run_internal_review() -> dict[str, Any]:
    findings = tuple(audit_extended_security())

    return {
        "engine": "guardian_hunter.auditor",
        "executed": True,
        "finding_count": len(findings),
        "findings": [_finding_to_dict(finding) for finding in findings],
    }


def external_ai_status(
    tools: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tools = tools or discover_tools()

    providers = {
        name: tools[name]
        for name in ("claude", "aider", "codex")
    }

    available = [
        name
        for name, state in providers.items()
        if state["available"]
    ]

    return {
        "requested": True,
        "available_providers": available,
        "providers": providers,
        "executed": False,
        "reason": (
            "NO_EXTERNAL_AI_PROVIDER_AVAILABLE"
            if not available
            else "PROVIDER_AVAILABLE_BUT_SUPERVISED_LAUNCH_REQUIRED"
        ),
        "containment_required": True,
        "git_access_allowed": False,
        "baseline_modification_allowed": False,
        "automatic_merge_allowed": False,
    }


def nuclei_status(
    *,
    target: str | None = None,
    authorized: bool = False,
    tools: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tools = tools or discover_tools()
    installed = tools["nuclei"]["available"]

    if not installed:
        reason = "NUCLEI_UNAVAILABLE"
    elif not target:
        reason = "NO_AUTHORIZED_TARGET"
    elif not authorized:
        reason = "TARGET_NOT_AUTHORIZED"
    else:
        reason = "AUTHORIZED_TARGET_READY"

    return {
        "available": installed,
        "target": target,
        "authorized": bool(target and authorized),
        "executed": False,
        "reason": reason,
    }


def build_repair_proposals(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []

    for finding in findings:
        affected = finding.get("affected_files", ())
        if isinstance(affected, str):
            affected = (affected,)
        else:
            affected = tuple(affected or ())

        authority = classify_repair_authority(affected)

        proposals.append(
            {
                "finding_id": finding.get("finding_id", "UNKNOWN"),
                "summary": finding.get(
                    "summary",
                    finding.get("title", "Security finding"),
                ),
                "affected_files": affected,
                "authority": authority,
                "proposal_class": RepairProposal.__name__,
                "prepared": True,
                "applied": False,
                "human_approval_required": True,
            }
        )

    return proposals


def run_operational_cycle(
    *,
    target: str | None = None,
    target_authorized: bool = False,
) -> dict[str, Any]:
    """Run one fail-closed operational review cycle."""

    tools = discover_tools()

    health = run_health_recovery()
    advice = advise_health_result(health)

    review = run_internal_review()
    proposals = build_repair_proposals(review["findings"])

    ai = external_ai_status(tools)
    nuclei = nuclei_status(
        target=target,
        authorized=target_authorized,
        tools=tools,
    )

    blocked = (
        health.get("status") != "HEALTHY"
        or review["finding_count"] > 0
    )

    return {
        "status": "REVIEW_REQUIRED" if blocked else "HEALTHY",
        "trust_policy": {
            "automatic_commit": False,
            "automatic_baseline_update": False,
            "automatic_merge": False,
            "human_approval_for_protected": True,
        },
        "tools": tools,
        "health": health,
        "diagnosis": advice,
        "audit": review,
        "ai": ai,
        "repair": {
            "proposal_count": len(proposals),
            "proposals": proposals,
            "automatic_apply": False,
            "human_approval_required": True,
        },
        "nuclei": nuclei,
        "reverification": {
            "required_after_change": True,
            "pytest_required": True,
            "auditor_required": True,
            "diff_check_required": True,
        },
        "evidence": {
            "final_evidence_required": True,
        },
        "execution_allowed": False,
    }


__all__ = [
    "AUTOMATIC_COMMIT",
    "AUTOMATIC_BASELINE_UPDATE",
    "AUTOMATIC_MERGE",
    "HUMAN_APPROVAL_FOR_PROTECTED",
    "discover_tools",
    "classify_repair_authority",
    "run_internal_review",
    "external_ai_status",
    "nuclei_status",
    "build_repair_proposals",
    "run_operational_cycle",
]


# ---------------------------------------------------------------------------
# Supervised transactional repair
# ---------------------------------------------------------------------------

from guardian_hunter.repair.approval import (
    ApprovalLedger,
    HumanApproval,
)
from guardian_hunter.repair.executor import (
    RepairAction,
    apply_repair,
    capture_backup,
    rollback_repair,
)


def _transaction_reverification() -> dict[str, Any]:
    """Run the existing Guardian Hunter verification after a real repair."""

    import subprocess
    import sys

    pytest_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )

    pytest_output = (
        pytest_result.stdout.strip()
        or pytest_result.stderr.strip()
    )

    try:
        audit_findings = tuple(audit_extended_security())
        auditor_ok = len(audit_findings) == 0
        auditor_error = None
    except Exception as exc:
        audit_findings = ()
        auditor_ok = False
        auditor_error = f"{type(exc).__name__}: {exc}"

    diff_result = subprocess.run(
        ["git", "diff", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    passed = (
        pytest_result.returncode == 0
        and auditor_ok
        and diff_result.returncode == 0
    )

    return {
        "passed": passed,
        "pytest": {
            "passed": pytest_result.returncode == 0,
            "returncode": pytest_result.returncode,
            "summary": pytest_output[-2000:],
        },
        "auditor": {
            "passed": auditor_ok,
            "finding_count": len(audit_findings),
            "error": auditor_error,
        },
        "diff_check": {
            "passed": diff_result.returncode == 0,
            "returncode": diff_result.returncode,
            "output": (
                diff_result.stdout.strip()
                or diff_result.stderr.strip()
            ),
        },
    }


def run_transactional_repair(
    *,
    proposal: RepairProposal,
    action: RepairAction,
    baseline: str,
    approval: HumanApproval | None = None,
    approval_ledger: ApprovalLedger | None = None,
    root: Path = PROJECT_ROOT,
    reverifier=None,
) -> dict[str, Any]:
    """Execute one supervised repair transaction.

    Flow:
        proposal
        -> authority classification
        -> approval when protected
        -> exact backup
        -> real repair
        -> reverification
        -> retain for human review on PASS
        -> automatic rollback on FAIL

    This function has no authority to commit, merge, or update the
    trusted baseline.
    """

    root = root.resolve()

    authority = classify_repair_authority(
        list(proposal.affected_files)
    )

    relative_path = action.relative_path

    if relative_path not in proposal.affected_files:
        return {
            "status": "REFUSED",
            "reason": "ACTION_NOT_IN_PROPOSAL",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    protected = relative_path in authority["protected_files"]

    if protected and approval is None:
        return {
            "status": "APPROVAL_REQUIRED",
            "reason": "PROTECTED_REPAIR_REQUIRES_HUMAN_APPROVAL",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    backup = capture_backup(
        root=root,
        relative_path=relative_path,
    )

    apply_result = apply_repair(
        root=root,
        proposal=proposal,
        action=action,
        baseline=baseline,
        approval=approval,
        approval_ledger=approval_ledger,
    )

    if not apply_result.applied:
        return {
            "status": "REFUSED",
            "reason": apply_result.reason,
            "authority": authority,
            "apply": {
                "applied": False,
                "reason": apply_result.reason,
                "before_sha256": apply_result.before_sha256,
                "after_sha256": apply_result.after_sha256,
                "approval_verified": apply_result.approval_verified,
            },
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    verifier = reverifier or _transaction_reverification

    try:
        verification = verifier()
    except Exception as exc:
        verification = {
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    if not bool(verification.get("passed")):
        rollback = rollback_repair(
            root=root,
            backup=backup,
            expected_current_sha256=apply_result.after_sha256,
        )

        return {
            "status": (
                "ROLLED_BACK"
                if rollback.applied
                else "ROLLBACK_FAILED"
            ),
            "reason": (
                "REVERIFICATION_FAILED"
                if rollback.applied
                else "REVERIFICATION_FAILED_AND_ROLLBACK_FAILED"
            ),
            "authority": authority,
            "apply": {
                "applied": True,
                "reason": apply_result.reason,
                "before_sha256": apply_result.before_sha256,
                "after_sha256": apply_result.after_sha256,
                "approval_verified": apply_result.approval_verified,
            },
            "verification": verification,
            "rollback": {
                "applied": rollback.applied,
                "reason": rollback.reason,
                "after_sha256": rollback.after_sha256,
            },
            "applied": False,
            "rolled_back": rollback.applied,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    return {
        "status": "REPAIR_PENDING_HUMAN_REVIEW",
        "reason": "REPAIR_APPLIED_AND_REVERIFIED",
        "authority": authority,
        "apply": {
            "applied": True,
            "reason": apply_result.reason,
            "before_sha256": apply_result.before_sha256,
            "after_sha256": apply_result.after_sha256,
            "approval_verified": apply_result.approval_verified,
        },
        "verification": verification,
        "rollback": {
            "applied": False,
            "reason": "NOT_REQUIRED",
        },
        "applied": True,
        "rolled_back": False,
        "human_review_required": True,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "merge_allowed": False,
    }


__all__.extend(
    [
        "run_transactional_repair",
    ]
)
