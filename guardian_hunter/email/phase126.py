"""
Guardian Hunter — Phase 126
Email Security Core

Safety model:
- READ_ONLY=True
- DRY_RUN=True
- REAL_EXECUTION_BLOCKED=True
- HUMAN_REVIEW_REQUIRED=True
- RESPONSE_LOCKED=True

This module performs static inspection only.
No message, attachment, URL, script or executable is executed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from email.message import Message
from hashlib import sha256
from typing import Any
import re


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass
class EmailIndicator:
    kind: str
    value: str
    severity: str = "INFO"


@dataclass
class AttachmentInspection:
    filename: str
    content_type: str
    size: int
    sha256: str
    suspicious: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass
class EmailSecurityResult:
    parsed: bool
    headers: dict[str, str]
    indicators: list[EmailIndicator]
    attachments: list[AttachmentInspection]
    phishing_score: int
    risk_score: int
    risk_level: str
    blocked: bool
    quarantine: bool
    human_review_required: bool
    response_locked: bool
    execution_allowed: bool
    dry_run: bool
    read_only: bool


DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".scr", ".com", ".bat", ".cmd", ".ps1",
    ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".msi",
    ".hta", ".jar", ".lnk", ".iso", ".img"
}

MACRO_EXTENSIONS = {
    ".docm", ".dotm", ".xlsm", ".xltm", ".pptm", ".ppsm"
}

ARCHIVE_EXTENSIONS = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
}

URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)


def _filename_extension(filename: str) -> str:
    filename = (filename or "").lower().strip()
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1]


def _risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _header_dict(message: Message) -> dict[str, str]:
    result: dict[str, str] = {}

    for key in (
        "From",
        "To",
        "Cc",
        "Reply-To",
        "Return-Path",
        "Subject",
        "Date",
        "Message-ID",
        "Authentication-Results",
        "Received",
    ):
        values = message.get_all(key, [])
        if values:
            result[key] = " | ".join(str(v) for v in values)

    return result


def _inspect_attachments(message: Message) -> list[AttachmentInspection]:
    results: list[AttachmentInspection] = []

    if not message.is_multipart():
        return results

    for part in message.walk():
        if part.get_content_disposition() != "attachment":
            continue

        filename = part.get_filename() or "unnamed"
        payload = part.get_payload(decode=True) or b""
        digest = sha256(payload).hexdigest()
        extension = _filename_extension(filename)

        reasons: list[str] = []
        suspicious = False

        if extension in DANGEROUS_EXTENSIONS:
            suspicious = True
            reasons.append("DANGEROUS_EXECUTABLE_OR_SCRIPT_EXTENSION")

        if extension in MACRO_EXTENSIONS:
            suspicious = True
            reasons.append("MACRO_ENABLED_DOCUMENT")

        if extension in ARCHIVE_EXTENSIONS:
            suspicious = True
            reasons.append("ARCHIVE_REQUIRES_DEEP_INSPECTION")

        results.append(
            AttachmentInspection(
                filename=filename,
                content_type=part.get_content_type(),
                size=len(payload),
                sha256=digest,
                suspicious=suspicious,
                reasons=reasons,
            )
        )

    return results


def inspect_email(raw_email: bytes) -> EmailSecurityResult:
    """
    Static email inspection.

    The input is treated strictly as untrusted data.
    No external process, URL, attachment, macro or script is executed.
    """

    indicators: list[EmailIndicator] = []

    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_email)
    except Exception as exc:
        indicators.append(
            EmailIndicator(
                kind="PARSER_ERROR",
                value=type(exc).__name__,
                severity="HIGH",
            )
        )

        return EmailSecurityResult(
            parsed=False,
            headers={},
            indicators=indicators,
            attachments=[],
            phishing_score=0,
            risk_score=90,
            risk_level="CRITICAL",
            blocked=True,
            quarantine=True,
            human_review_required=True,
            response_locked=True,
            execution_allowed=False,
            dry_run=DRY_RUN,
            read_only=READ_ONLY,
        )

    headers = _header_dict(message)

    subject = headers.get("Subject", "")
    body_parts: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body_parts.append(part.get_content())
                except Exception:
                    pass
    elif message.get_content_type() == "text/plain":
        try:
            body_parts.append(message.get_content())
        except Exception:
            pass

    body = "\n".join(body_parts)

    phishing_score = 0
    risk_score = 0

    urls = URL_RE.findall(subject + "\n" + body)

    if urls:
        indicators.append(
            EmailIndicator(
                kind="URL_PRESENT",
                value=str(len(urls)),
                severity="INFO",
            )
        )

    phishing_terms = (
        "verify your account",
        "verify account",
        "password expires",
        "urgent action",
        "confirm your identity",
        "suspended account",
        "payment required",
        "login immediately",
    )

    combined = (subject + "\n" + body).lower()

    for term in phishing_terms:
        if term in combined:
            phishing_score += 15
            indicators.append(
                EmailIndicator(
                    kind="PHISHING_LANGUAGE",
                    value=term,
                    severity="MEDIUM",
                )
            )

    if headers.get("Reply-To") and headers.get("From"):
        if headers["Reply-To"].lower() != headers["From"].lower():
            phishing_score += 20
            indicators.append(
                EmailIndicator(
                    kind="REPLY_TO_MISMATCH",
                    value="From and Reply-To differ",
                    severity="MEDIUM",
                )
            )

    authentication = headers.get("Authentication-Results", "").lower()

    for auth_failure in (
        "spf=fail",
        "dkim=fail",
        "dmarc=fail",
    ):
        if auth_failure in authentication:
            phishing_score += 20
            indicators.append(
                EmailIndicator(
                    kind="AUTHENTICATION_FAILURE",
                    value=auth_failure,
                    severity="HIGH",
                )
            )

    attachments = _inspect_attachments(message)

    for attachment in attachments:
        if attachment.suspicious:
            risk_score += 35

            for reason in attachment.reasons:
                indicators.append(
                    EmailIndicator(
                        kind="SUSPICIOUS_ATTACHMENT",
                        value=f"{attachment.filename}:{reason}",
                        severity="HIGH",
                    )
                )

    risk_score += phishing_score

    if not headers.get("From"):
        risk_score += 10
        indicators.append(
            EmailIndicator(
                kind="MISSING_FROM",
                value="From header absent",
                severity="MEDIUM",
            )
        )

    if risk_score > 100:
        risk_score = 100

    blocked = risk_score >= 60 or any(
        item.suspicious for item in attachments
    )

    quarantine = blocked

    return EmailSecurityResult(
        parsed=True,
        headers=headers,
        indicators=indicators,
        attachments=attachments,
        phishing_score=min(phishing_score, 100),
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        blocked=blocked,
        quarantine=quarantine,
        human_review_required=HUMAN_REVIEW_REQUIRED,
        response_locked=RESPONSE_LOCKED,
        execution_allowed=False,
        dry_run=DRY_RUN,
        read_only=READ_ONLY,
    )
