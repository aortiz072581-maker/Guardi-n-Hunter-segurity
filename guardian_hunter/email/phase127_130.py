"""
Guardian Hunter — Phases 127 → 130
Malware & Vulnerability Defense

STATIC / READ-ONLY ONLY.

No attachment is executed.
No macro is executed.
No script is executed.
No URL is contacted.
No external scanner is invoked.

Security invariants:
READ_ONLY=True
DRY_RUN=True
REAL_EXECUTION_BLOCKED=True
HUMAN_REVIEW_REQUIRED=True
RESPONSE_LOCKED=True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import hashlib
import re


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".scr", ".com", ".bat", ".cmd",
    ".ps1", ".vbs", ".vbe", ".js", ".jse", ".wsf",
    ".wsh", ".hta", ".msi", ".jar", ".lnk"
}

MACRO_EXTENSIONS = {
    ".docm", ".dotm", ".xlsm", ".xltm",
    ".pptm", ".ppsm"
}

ARCHIVE_EXTENSIONS = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
    ".xz"
}

SCRIPT_EXTENSIONS = {
    ".ps1", ".psm1", ".bat", ".cmd", ".vbs",
    ".vbe", ".js", ".jse", ".wsf", ".wsh",
    ".hta", ".sh"
}

DOCUMENT_EXTENSIONS = {
    ".doc", ".docx", ".docm", ".dot", ".dotm",
    ".xls", ".xlsx", ".xlsm", ".xltm",
    ".ppt", ".pptx", ".pptm", ".ppsm"
}


@dataclass
class SecurityFinding:
    category: str
    severity: str
    value: str
    evidence: str


@dataclass
class AttachmentSecurityResult:
    filename: str
    declared_content_type: str
    detected_type: str
    size: int
    sha256: str
    extension: str
    findings: list[SecurityFinding] = field(default_factory=list)
    blocked: bool = False
    quarantined: bool = False


@dataclass
class MalwareDefenseResult:
    analyzed: bool
    attachments: list[AttachmentSecurityResult]
    findings: list[SecurityFinding]
    cve_matches: list[str]
    ioc_matches: list[str]
    risk_score: int
    risk_level: str
    blocked: bool
    quarantine: bool
    human_review_required: bool
    response_locked: bool
    execution_allowed: bool
    read_only: bool
    dry_run: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extension(filename: str) -> str:
    name = PurePosixPath(filename or "").name.lower()

    if "." not in name:
        return ""

    return "." + name.rsplit(".", 1)[1]


def normalize_cve(value: str) -> str | None:
    match = re.fullmatch(
        r"CVE-\d{4}-\d{4,7}",
        value.strip().upper()
    )

    return match.group(0) if match else None


def detect_file_type(data: bytes) -> str:
    """
    Minimal magic-byte detection.

    Unknown data remains UNKNOWN.
    No external library is required.
    """

    if data.startswith(b"MZ"):
        return "PE_EXECUTABLE"

    if data.startswith(b"\x7fELF"):
        return "ELF_EXECUTABLE"

    if data.startswith(b"PK\x03\x04"):
        return "ZIP_CONTAINER"

    if data.startswith(b"%PDF"):
        return "PDF"

    if data.startswith(b"\xD0\xCF\x11\xE0"):
        return "OLE_CONTAINER"

    if data.startswith(b"\x89PNG"):
        return "PNG"

    if data.startswith(b"\xFF\xD8\xFF"):
        return "JPEG"

    return "UNKNOWN"


def _severity_score(severity: str) -> int:
    return {
        "INFO": 0,
        "LOW": 5,
        "MEDIUM": 15,
        "HIGH": 30,
        "CRITICAL": 50,
    }.get(severity, 0)


def _risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"


def inspect_attachment(
    filename: str,
    content_type: str,
    data: bytes,
    known_iocs: set[str] | None = None,
    known_cves: set[str] | None = None,
) -> AttachmentSecurityResult:

    known_iocs = known_iocs or set()
    known_cves = known_cves or set()

    ext = extension(filename)
    detected = detect_file_type(data)
    digest = sha256_bytes(data)

    findings: list[SecurityFinding] = []

    if ext in DANGEROUS_EXTENSIONS:
        findings.append(
            SecurityFinding(
                category="DANGEROUS_EXTENSION",
                severity="HIGH",
                value=ext,
                evidence=filename,
            )
        )

    if ext in SCRIPT_EXTENSIONS:
        findings.append(
            SecurityFinding(
                category="SCRIPT_ATTACHMENT",
                severity="HIGH",
                value=ext,
                evidence=filename,
            )
        )

    if ext in MACRO_EXTENSIONS:
        findings.append(
            SecurityFinding(
                category="MACRO_ENABLED_DOCUMENT",
                severity="HIGH",
                value=ext,
                evidence=filename,
            )
        )

    if ext in ARCHIVE_EXTENSIONS:
        findings.append(
            SecurityFinding(
                category="ARCHIVE_ATTACHMENT",
                severity="MEDIUM",
                value=ext,
                evidence=filename,
            )
        )

    # Extension/content mismatch.
    if ext in DANGEROUS_EXTENSIONS and detected not in {
        "PE_EXECUTABLE",
        "UNKNOWN",
    }:
        findings.append(
            SecurityFinding(
                category="TYPE_MISMATCH",
                severity="HIGH",
                value=detected,
                evidence=f"{filename}:{content_type}",
            )
        )

    if detected in {"PE_EXECUTABLE", "ELF_EXECUTABLE"}:
        findings.append(
            SecurityFinding(
                category="EXECUTABLE_CONTENT",
                severity="CRITICAL",
                value=detected,
                evidence=digest,
            )
        )

    if digest.lower() in {x.lower() for x in known_iocs}:
        findings.append(
            SecurityFinding(
                category="KNOWN_IOC",
                severity="CRITICAL",
                value=digest,
                evidence="SHA256 IOC match",
            )
        )

    # CVE matching is intentionally data-driven.
    # The engine never invents CVEs.
    cve_matches: list[str] = []

    for item in known_cves:
        normalized = normalize_cve(item)

        if normalized:
            cve_matches.append(normalized)

    if cve_matches:
        findings.append(
            SecurityFinding(
                category="CVE_MATCH",
                severity="HIGH",
                value=",".join(sorted(set(cve_matches))),
                evidence="Locally supplied vulnerability intelligence",
            )
        )

    score = min(
        100,
        sum(_severity_score(item.severity) for item in findings),
    )

    blocked = any(
        item.severity in {"CRITICAL", "HIGH"}
        for item in findings
    )

    return AttachmentSecurityResult(
        filename=filename,
        declared_content_type=content_type,
        detected_type=detected,
        size=len(data),
        sha256=digest,
        extension=ext,
        findings=findings,
        blocked=blocked,
        quarantined=blocked,
    )


def analyze_email_attachments(
    attachments: list[dict],
    known_iocs: set[str] | None = None,
    known_cves: set[str] | None = None,
) -> MalwareDefenseResult:

    results: list[AttachmentSecurityResult] = []
    findings: list[SecurityFinding] = []
    cve_matches: list[str] = []
    ioc_matches: list[str] = []

    for item in attachments:
        result = inspect_attachment(
            filename=str(item.get("filename", "unnamed")),
            content_type=str(
                item.get("content_type", "application/octet-stream")
            ),
            data=bytes(item.get("data", b"")),
            known_iocs=known_iocs,
            known_cves=known_cves,
        )

        results.append(result)
        findings.extend(result.findings)

        for finding in result.findings:
            if finding.category == "CVE_MATCH":
                cve_matches.extend(
                    finding.value.split(",")
                )

            if finding.category == "KNOWN_IOC":
                ioc_matches.append(finding.value)

    risk_score = min(
        100,
        sum(_severity_score(item.severity) for item in findings),
    )

    blocked = any(
        item.severity in {"CRITICAL", "HIGH"}
        for item in findings
    )

    return MalwareDefenseResult(
        analyzed=True,
        attachments=results,
        findings=findings,
        cve_matches=sorted(set(cve_matches)),
        ioc_matches=sorted(set(ioc_matches)),
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        blocked=blocked,
        quarantine=blocked,
        human_review_required=HUMAN_REVIEW_REQUIRED,
        response_locked=RESPONSE_LOCKED,
        execution_allowed=False,
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
    )
