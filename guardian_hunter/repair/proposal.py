"""Immutable repair proposals bound to their exact content."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re


FINDING_ID_RE = re.compile(r"^GH-[0-9]{3,}$")

PROTECTED_PREFIXES = (
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/evidence/",
    "guardian_hunter/gate/",
    "guardian_hunter/auditor/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
)

MAX_PATCH_BYTES = 512 * 1024


def _normalize_path(path: str) -> str:
    if not path or "\x00" in path:
        raise ValueError("INVALID_PATH")

    clean = path.replace("\\", "/")

    if clean.startswith("/"):
        raise ValueError("ABSOLUTE_PATH_FORBIDDEN")

    parts = clean.split("/")

    if ".." in parts:
        raise ValueError("PATH_TRAVERSAL_FORBIDDEN")

    normalized = "/".join(
        part for part in parts
        if part not in ("", ".")
    )

    if not normalized:
        raise ValueError("EMPTY_PATH")

    return normalized


def _protected(path: str) -> bool:
    clean = _normalize_path(path)

    return any(
        clean.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


@dataclass(frozen=True)
class RepairProposal:
    finding_id: str
    summary: str
    affected_files: tuple[str, ...]
    patch: str
    required_tests: tuple[str, ...]

    automatic_apply: bool = False
    execution_allowed: bool = False
    merge_allowed: bool = False
    human_approval_required: bool = True

    def validate(self) -> None:
        if not FINDING_ID_RE.fullmatch(self.finding_id):
            raise ValueError("INVALID_FINDING_ID")

        if not self.summary.strip():
            raise ValueError("EMPTY_SUMMARY")

        if not self.affected_files:
            raise ValueError("AFFECTED_FILES_REQUIRED")

        normalized = tuple(
            _normalize_path(path)
            for path in self.affected_files
        )

        if len(set(normalized)) != len(normalized):
            raise ValueError("DUPLICATE_AFFECTED_FILE")

        if not self.patch.strip():
            raise ValueError("EMPTY_PATCH")

        if len(self.patch.encode("utf-8")) > MAX_PATCH_BYTES:
            raise ValueError("PATCH_TOO_LARGE")

        if not self.required_tests:
            raise ValueError("REQUIRED_TESTS_MISSING")

        if self.automatic_apply:
            raise PermissionError("AUTOMATIC_APPLY_FORBIDDEN")

        if self.execution_allowed:
            raise PermissionError("EXECUTION_FORBIDDEN")

        if self.merge_allowed:
            raise PermissionError("MERGE_FORBIDDEN")

        if not self.human_approval_required:
            raise PermissionError("HUMAN_APPROVAL_REQUIRED")

    @property
    def touches_protected_boundary(self) -> bool:
        return any(
            _protected(path)
            for path in self.affected_files
        )

    def canonical_payload(self) -> bytes:
        self.validate()

        payload = {
            "finding_id": self.finding_id,
            "summary": self.summary,
            "affected_files": list(self.affected_files),
            "patch": self.patch,
            "required_tests": list(self.required_tests),
            "automatic_apply": self.automatic_apply,
            "execution_allowed": self.execution_allowed,
            "merge_allowed": self.merge_allowed,
            "human_approval_required":
                self.human_approval_required,
        }

        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    @property
    def proposal_hash(self) -> str:
        return hashlib.sha256(
            self.canonical_payload()
        ).hexdigest()
