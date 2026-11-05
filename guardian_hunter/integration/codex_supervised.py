"""Supervised read-only Codex repair candidate producer.

Flow:
auditor
 -> sanitized temporary context
 -> Codex read-only / ephemeral
 -> JSON Schema
 -> Guardian validation
 -> RepairAction bound to SHA-256

Codex is a proposal generator only. It has no repository mutation,
approval, commit, merge, or trusted-baseline authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from typing import Any

from guardian_hunter.integration.automatic_repair import (
    AutomaticRepairCandidate,
)
from guardian_hunter.repair.executor import RepairAction
from guardian_hunter.repair.proposal import RepairProposal


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_SOURCE_BYTES = 512 * 1024
MAX_REPLACEMENT_BYTES = 512 * 1024
CODEX_TIMEOUT_SECONDS = 180

PROTECTED_PREFIXES = (
    ".git/",
    ".guardian/",
    "guardian_hunter/gate/",
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/evidence/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
    "guardian_hunter/auditor/",
    "guardian_hunter/repair/",
    "guardian_hunter/runner/",
)

FINDING_RE = re.compile(r"^GH-[0-9]{3,}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class CodexCandidateResult:
    prepared: bool
    reason: str
    candidate: AutomaticRepairCandidate | None
    metadata: dict[str, Any]


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


from guardian_hunter.core.paths import normalize_relative


def _normalize_relative_path(value: str) -> str:
    return normalize_relative(value)


def _is_protected(value: str) -> bool:
    normalized = _normalize_relative_path(value)

    return any(
        normalized == prefix.rstrip("/")
        or normalized.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


def _safe_source_bytes(
    *,
    root: Path,
    relative_path: str,
) -> bytes:
    root = root.resolve()
    normalized = _normalize_relative_path(relative_path)

    if _is_protected(normalized):
        raise PermissionError("PROTECTED_PATH")

    _cur = root
    for _part in normalized.split("/"):
        _cur = _cur / _part
        if _cur.is_symlink():
            raise PermissionError("SOURCE_SYMLINK_FORBIDDEN")
    candidate = root / normalized

    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError:
        raise FileNotFoundError("SOURCE_NOT_FOUND")

    try:
        resolved.relative_to(root)
    except ValueError:
        raise PermissionError("SOURCE_ESCAPES_PROJECT")

    info = candidate.lstat()

    if stat.S_ISLNK(info.st_mode):
        raise PermissionError("SOURCE_SYMLINK_FORBIDDEN")

    if not stat.S_ISREG(info.st_mode):
        raise PermissionError("SOURCE_NOT_REGULAR_FILE")

    data = candidate.read_bytes()

    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError("SOURCE_TOO_LARGE")

    return data


def _output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "finding_id",
            "relative_path",
            "summary",
            "replacement_utf8",
            "required_tests",
        ],
        "properties": {
            "finding_id": {
                "type": "string",
                "pattern": "^GH-[0-9]{3,}$",
            },
            "relative_path": {
                "type": "string",
                "minLength": 1,
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
            "replacement_utf8": {
                "type": "string",
                "minLength": 1,
            },
            "required_tests": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "string",
                    "minLength": 1,
                },
            },
        },
    }


def _termux_environment() -> dict[str, str]:
    allowed = (
        "HOME",
        "PATH",
        "PREFIX",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "ANDROID_DATA",
        "ANDROID_ROOT",
        "LD_LIBRARY_PATH",
    )

    env = {
        key: os.environ[key]
        for key in allowed
        if key in os.environ
    }

    for key in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "GIT_ASKPASS",
        "SSH_AUTH_SOCK",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        env.pop(key, None)

    return env


def _failure(
    reason: str,
    **metadata: Any,
) -> CodexCandidateResult:
    metadata.setdefault("provider", "codex")
    metadata.setdefault("repository_write_access", False)
    metadata.setdefault("commit_allowed", False)
    metadata.setdefault("merge_allowed", False)
    metadata.setdefault("baseline_update_allowed", False)

    return CodexCandidateResult(
        prepared=False,
        reason=reason,
        candidate=None,
        metadata=metadata,
    )


def prepare_codex_candidate(
    *,
    finding: dict[str, Any],
    relative_path: str,
    root: Path = PROJECT_ROOT,
) -> CodexCandidateResult:

    # FIX5: return inalcanzable removido - dejaba muerto el try de abajo - return _failure("TRUSTED_EXECUTION_BROKER_NOT_CONFIGURED", provider_invoked=False)

    try:
        relative_path = _normalize_relative_path(
            relative_path
        )
    except Exception as exc:
        return _failure(
            f"INVALID_PATH:{type(exc).__name__}:{exc}"
        )

    # Protected content never reaches Codex.
    if _is_protected(relative_path):
        return _failure(
            "PROTECTED_REPAIR_REQUIRES_HUMAN_APPROVAL",
            relative_path=relative_path,
            provider_invoked=False,
            human_approval_required=True,
        )

    finding_id = str(
        finding.get("finding_id", "")
    )

    if FINDING_RE.fullmatch(finding_id) is None:
        return _failure(
            "FINDING_ID_NOT_EXECUTABLE"
        )

    affected = finding.get(
        "affected_files",
        (),
    )

    if isinstance(affected, str):
        affected_files = (affected,)
    else:
        affected_files = tuple(
            affected or ()
        )

    try:
        affected_files = tuple(
            _normalize_relative_path(item)
            for item in affected_files
        )
    except Exception:
        return _failure(
            "INVALID_AFFECTED_FILES"
        )

    if relative_path not in affected_files:
        return _failure(
            "PATH_NOT_IN_FINDING"
        )

    # Never split a mixed protected/non-protected finding.
    if any(
        _is_protected(item)
        for item in affected_files
    ):
        return _failure(
            "FINDING_TOUCHES_PROTECTED_BOUNDARY",
            provider_invoked=False,
            human_approval_required=True,
        )

    summary = str(
        finding.get(
            "title",
            finding.get("summary", ""),
        )
    ).strip()

    proposed_fix = str(
        finding.get("proposed_fix", "")
    ).strip()

    raw_tests = finding.get(
        "required_tests",
        (),
    )

    if isinstance(raw_tests, str):
        required_tests = (raw_tests,)
    else:
        required_tests = tuple(
            str(item)
            for item in (raw_tests or ())
        )

    if not summary:
        return _failure(
            "FINDING_TITLE_REQUIRED"
        )

    if not proposed_fix:
        return _failure(
            "PROPOSED_FIX_REQUIRED"
        )

    if not required_tests:
        return _failure(
            "REQUIRED_TESTS_REQUIRED"
        )

    try:
        source_bytes = _safe_source_bytes(
            root=root,
            relative_path=relative_path,
        )
    except Exception as exc:
        return _failure(
            "SOURCE_REJECTED:"
            f"{type(exc).__name__}:{exc}"
        )

    try:
        source_text = source_bytes.decode(
            "utf-8"
        )
    except UnicodeDecodeError:
        return _failure(
            "SOURCE_NOT_UTF8"
        )

    expected_sha256 = _digest(
        source_bytes
    )

    if SHA256_RE.fullmatch(
        expected_sha256
    ) is None:
        return _failure(
            "INTERNAL_SHA256_ERROR"
        )

    proot = shutil.which(
        "proot-distro"
    )

    if not proot:
        return _failure(
            "PROOT_DISTRO_UNAVAILABLE"
        )

    with tempfile.TemporaryDirectory(
        prefix="guardian-codex-",
    ) as temporary:

        workspace = Path(temporary)

        source_copy = (
            workspace / "source.txt"
        )

        schema_file = (
            workspace / "schema.json"
        )

        result_file = (
            workspace / "result.json"
        )

        source_copy.write_text(
            source_text,
            encoding="utf-8",
        )

        schema_file.write_text(
            json.dumps(
                _output_schema(),
                sort_keys=True,
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )

        prompt = f"""You are a supervised defensive repair proposal generator.

Analyze only source.txt in the temporary workspace.

Security requirements:
- Do not inspect the original Guardian Hunter repository.
- Do not use git.
- Do not access .git or .guardian.
- Do not access credentials or tokens.
- Do not use network access.
- Do not modify files.
- Return only the JSON required by the supplied schema.
- replacement_utf8 must contain the complete replacement file.
- Preserve unrelated behavior.
- Never weaken security controls.
- Never add autonomous approval, commit, merge, baseline update,
  sandbox bypass, shell bypass, or credential access.
- If no exact safe correction can be produced, return source.txt
  unchanged as replacement_utf8.

Finding ID:
{finding_id}

Original project-relative path:
{relative_path}

Finding:
{summary}

Defensive proposed fix:
{proposed_fix}

Required verification identifiers:
{json.dumps(required_tests)}

Return finding_id exactly as:
{finding_id}

Return relative_path exactly as:
{relative_path}
"""

        command = [
            proot,
            "login",
            "debian",
            "--",
            "/usr/local/bin/codex",
            "exec",
            "--sandbox",
            "read-only",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--color",
            "never",
            "-C",
            str(workspace),
            "--output-schema",
            str(schema_file),
            "--output-last-message",
            str(result_file),
            "-",
        ]

        try:
            completed = subprocess.run(
                command,
                input=prompt,
                cwd=workspace,
                env=_termux_environment(),
                capture_output=True,
                text=True,
                timeout=CODEX_TIMEOUT_SECONDS,
                check=False,
            )

        except subprocess.TimeoutExpired:
            return _failure(
                "CODEX_TIMEOUT"
            )

        except OSError as exc:
            return _failure(
                "CODEX_START_FAILED:"
                f"{type(exc).__name__}"
            )

        if completed.returncode != 0:
            return _failure(
                "CODEX_EXEC_FAILED",
                returncode=completed.returncode,
                stderr_tail=(
                    completed.stderr[-1000:]
                ),
            )

        if not result_file.is_file():
            return _failure(
                "CODEX_RESULT_MISSING"
            )

        try:
            payload = json.loads(
                result_file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as exc:
            return _failure(
                "CODEX_OUTPUT_INVALID:"
                f"{type(exc).__name__}"
            )

    # Provider output is untrusted.
    if not isinstance(payload, dict):
        return _failure(
            "CODEX_OUTPUT_NOT_OBJECT"
        )

    allowed_keys = {
        "finding_id",
        "relative_path",
        "summary",
        "replacement_utf8",
        "required_tests",
    }

    if set(payload) != allowed_keys:
        return _failure(
            "CODEX_OUTPUT_FIELDS_INVALID"
        )

    if payload["finding_id"] != finding_id:
        return _failure(
            "CODEX_FINDING_ID_MISMATCH"
        )

    try:
        returned_path = (
            _normalize_relative_path(
                payload["relative_path"]
            )
        )
    except Exception:
        return _failure(
            "CODEX_PATH_INVALID"
        )

    if returned_path != relative_path:
        return _failure(
            "CODEX_PATH_MISMATCH"
        )

    if _is_protected(returned_path):
        return _failure(
            "CODEX_RETURNED_PROTECTED_PATH"
        )

    returned_summary = payload["summary"]

    if (
        not isinstance(
            returned_summary,
            str,
        )
        or not returned_summary.strip()
    ):
        return _failure(
            "CODEX_SUMMARY_INVALID"
        )

    replacement_text = (
        payload["replacement_utf8"]
    )

    if not isinstance(
        replacement_text,
        str,
    ):
        return _failure(
            "CODEX_REPLACEMENT_INVALID"
        )

    if not replacement_text:
        return _failure(
            "CODEX_REPLACEMENT_EMPTY"
        )

    replacement = replacement_text.encode(
        "utf-8"
    )

    if (
        len(replacement)
        > MAX_REPLACEMENT_BYTES
    ):
        return _failure(
            "CODEX_REPLACEMENT_TOO_LARGE"
        )

    returned_tests = payload[
        "required_tests"
    ]

    if (
        not isinstance(
            returned_tests,
            list,
        )
        or not returned_tests
        or not all(
            isinstance(item, str)
            and bool(item)
            for item in returned_tests
        )
    ):
        return _failure(
            "CODEX_TESTS_INVALID"
        )

    # Codex cannot weaken auditor verification.
    if not set(required_tests).issubset(
        set(returned_tests)
    ):
        return _failure(
            "CODEX_DROPPED_REQUIRED_TESTS"
        )

    # Re-read real source after Codex returns.
    try:
        current_bytes = _safe_source_bytes(
            root=root,
            relative_path=relative_path,
        )
    except Exception as exc:
        return _failure(
            "SOURCE_REREAD_REJECTED:"
            f"{type(exc).__name__}:{exc}"
        )

    current_sha256 = _digest(
        current_bytes
    )

    if (
        current_sha256
        != expected_sha256
    ):
        return _failure(
            "SOURCE_CHANGED_DURING_CODEX_ANALYSIS",
            expected_sha256=expected_sha256,
            current_sha256=current_sha256,
        )

    if replacement == source_bytes:
        return _failure(
            "CODEX_PROPOSED_NO_CHANGE",
            relative_path=relative_path,
            expected_sha256=expected_sha256,
        )

    proposal = RepairProposal(
        finding_id=finding_id,
        summary=returned_summary.strip(),
        affected_files=(
            relative_path,
        ),
        patch=(
            "CODEX_STRUCTURED_REPLACEMENT:"
            + _digest(replacement)
        ),
        required_tests=required_tests,
    )

    action = RepairAction(
        relative_path=relative_path,
        expected_sha256=expected_sha256,
        replacement=replacement,
    )

    candidate = AutomaticRepairCandidate(
        proposal=proposal,
        action=action,
    )

    try:
        candidate.validate()
    except Exception as exc:
        return _failure(
            "CANDIDATE_VALIDATION_FAILED:"
            f"{type(exc).__name__}:{exc}"
        )

    return CodexCandidateResult(
        prepared=True,
        reason="CODEX_CANDIDATE_PREPARED",
        candidate=candidate,
        metadata={
            "provider": "codex",
            "provider_invoked": True,
            "sandbox": "read-only",
            "ephemeral": True,
            "repository_write_access": False,
            "relative_path": relative_path,
            "expected_sha256": (
                expected_sha256
            ),
            "replacement_sha256": (
                _digest(replacement)
            ),
            "human_approval_required_for_protected": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        },
    )


__all__ = [
    "CodexCandidateResult",
    "prepare_codex_candidate",
]