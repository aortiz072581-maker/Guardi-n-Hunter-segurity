"""Phase 126 — Email Security Core tests."""

from guardian_hunter.email.phase126 import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    inspect_email,
)


def test_safe_email():
    raw = (
        b"From: sender@example.com\n"
        b"To: user@example.com\n"
        b"Subject: Hello\n"
        b"Content-Type: text/plain; charset=utf-8\n"
        b"\n"
        b"Normal message.\n"
    )

    result = inspect_email(raw)

    assert result.parsed is True
    assert result.execution_allowed is False
    assert result.read_only is True
    assert result.dry_run is True
    assert result.human_review_required is True
    assert result.response_locked is True


def test_dangerous_attachment_is_blocked():
    raw = (
        b"From: attacker@example.com\n"
        b"To: user@example.com\n"
        b"Subject: Invoice\n"
        b"MIME-Version: 1.0\n"
        b'Content-Type: multipart/mixed; boundary="X"\n'
        b"\n"
        b"--X\n"
        b'Content-Type: application/octet-stream; name="invoice.exe"\n'
        b'Content-Disposition: attachment; filename="invoice.exe"\n'
        b"\n"
        b"NOT_EXECUTED\n"
        b"--X--\n"
    )

    result = inspect_email(raw)

    assert result.parsed is True
    assert result.blocked is True
    assert result.quarantine is True
    assert result.execution_allowed is False
    assert result.response_locked is True
    assert any(
        item.kind == "SUSPICIOUS_ATTACHMENT"
        for item in result.indicators
    )


def test_phishing_language_increases_risk():
    raw = (
        b"From: security@example.com\n"
        b"To: user@example.com\n"
        b"Subject: Urgent action\n"
        b"Content-Type: text/plain; charset=utf-8\n"
        b"\n"
        b"Verify your account immediately.\n"
    )

    result = inspect_email(raw)

    assert result.parsed is True
    assert result.phishing_score > 0
    assert result.risk_score > 0
    assert result.execution_allowed is False


def test_security_constants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True
