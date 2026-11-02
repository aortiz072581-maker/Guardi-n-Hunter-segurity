"""
Guardian Hunter — Unified Defensive Orchestrator.

Single controlled entry point for:
state -> tools -> correlation -> audit -> diagnosis ->
repair decision -> verification -> evidence.

Critical security boundaries remain fail-closed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from guardian_hunter.integration.consolidated_defensive_flow import (
    run_consolidated_defensive_flow,
)
from guardian_hunter.auditor.engine import audit_extended_security


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TOOLS = (
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

CRITICAL_PREFIXES = (
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/evidence/",
    "guardian_hunter/gate/",
    "guardian_hunter/auditor/",
    "guardian_hunter/repair/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
    "guardian_hunter/runner/",
    ".guardian/",
    ".git/",
)


def tool_inventory() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for name in TOOLS:
        location = shutil.which(name)

        result[name] = {
            "available": location is not None,
            "path": location,
        }

    return result


def trusted_state() -> dict[str, Any]:
    baseline_path = PROJECT_ROOT / ".guardian" / "trusted-baseline"

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.strip()

    baseline = (
        baseline_path.read_text(encoding="utf-8").strip()
        if baseline_path.is_file()
        else None
    )

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.splitlines()

    # Tracked modifications affect the trusted repository state.
    # Untracked files are reported separately and are never silently
    # considered trusted, but they do not change committed HEAD.
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.splitlines()

    untracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.splitlines()

    return {
        "head": head,
        "baseline": baseline,
        "baseline_matches_head": baseline == head,
        "worktree_clean": not status,
        "trusted_tracked_state_clean": not tracked,
        "tracked_changes": tracked,
        "untracked_files": untracked,
        "changes": status,
    }


def run_internal_auditor() -> dict[str, Any]:
    report = audit_extended_security()

    findings = (
        report.findings
        if hasattr(report, "findings")
        else report
    )

    normalized = []

    for finding in findings:
        normalized.append(
            {
                "finding_id": getattr(
                    finding,
                    "finding_id",
                    "UNKNOWN",
                ),
                "severity": str(
                    getattr(finding, "severity", "UNKNOWN")
                ),
                "summary": getattr(
                    finding,
                    "summary",
                    repr(finding),
                ),
            }
        )

    return {
        "finding_count": len(normalized),
        "findings": normalized,
    }


def classify_repair_authority(
    affected_files: list[str],
) -> dict[str, Any]:
    protected = []

    for path in affected_files:
        clean = path.replace("\\", "/")

        if any(
            clean.startswith(prefix)
            for prefix in CRITICAL_PREFIXES
        ):
            protected.append(clean)

    if protected:
        return {
            "risk": "CRITICAL",
            "automatic_repair": False,
            "human_approval_required": True,
            "protected_files": protected,
        }

    return {
        "risk": "LOW",
        "automatic_repair": False,
        "human_approval_required": True,
        "protected_files": [],
    }


def run_verification() -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
        env={
            "HOME": str(Path.home()),
            "PATH": str(Path(sys.executable).resolve().parent),
            "PYTHONPATH": str(PROJECT_ROOT),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )

    return {
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "summary": (
            result.stdout.strip().splitlines()[-1]
            if result.stdout.strip()
            else ""
        ),
    }


def run_guardian_hunter() -> dict[str, Any]:
    state = trusted_state()

    if not state["baseline_matches_head"]:
        return {
            "status": "BLOCKED",
            "reason": "TRUSTED_BASELINE_MISMATCH",
            "trust": state,
            "execution_allowed": False,
        }

    if not state["trusted_tracked_state_clean"]:
        return {
            "status": "BLOCKED",
            "reason": "TRACKED_TRUST_STATE_CHANGED",
            "trust": state,
            "execution_allowed": False,
        }

    tools = tool_inventory()

    consolidated = run_consolidated_defensive_flow(
        root=PROJECT_ROOT,
        baseline_file=PROJECT_ROOT / "data" / "integrity_baseline.json",
    )

    auditor = run_internal_auditor()

    findings = auditor["findings"]

    diagnosis = {
        "problems_detected": len(findings),
        "repair_proposals_required": bool(findings),
        "ai_provider_available": any(
            tools[name]["available"]
            for name in ("claude", "aider", "codex")
        ),
        "external_ai_executed": False,
    }

    repair = {
        "automatic_repair": False,
        "human_approval_required": True,
        "proposals": [],
    }

    for finding in findings:
        affected = finding.get("affected_files", [])

        authority = classify_repair_authority(
            affected if isinstance(affected, list) else []
        )

        repair["proposals"].append(
            {
                "finding_id": finding["finding_id"],
                "authority": authority,
                "status": "PROPOSAL_REQUIRED",
            }
        )

    verification = run_verification()

    final_status = (
        "HEALTHY"
        if (
            not findings
            and verification["passed"]
        )
        else "REVIEW_REQUIRED"
    )

    return {
        "guardian_hunter": "UNIFIED_DEFENSIVE_FLOW",
        "status": final_status,
        "trust": state,
        "tools": tools,
        "correlation": consolidated,
        "audit": auditor,
        "diagnosis": diagnosis,
        "repair": repair,
        "verification": verification,
        "evidence": {
            "completed": True,
            "trusted_head": state["head"],
        },
        "automatic_commit": False,
        "automatic_baseline_update": False,
        "human_approval_required": True,
    }


def main() -> int:
    report = run_guardian_hunter()

    public_report = {
        "guardian_hunter": "UNIFIED_DEFENSIVE_FLOW",
        "status": report.get("status", "UNKNOWN"),
        "automatic_commit": False,
        "automatic_baseline_update": False,
        "human_approval_required": True,
        "sensitive_details_redacted": True,
    }

    print(
        json.dumps(
            public_report,
            indent=2,
            sort_keys=True,
        )
    )

    return 0 if report.get("status") == "HEALTHY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
