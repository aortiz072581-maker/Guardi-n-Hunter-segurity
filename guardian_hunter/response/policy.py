"""Guardian Hunter - defensive response policy.

The policy decides what response class is appropriate.
It does not execute containment.
"""

from __future__ import annotations


LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def classify_response(risk_level: str, authorized: bool = False) -> str:
    level = LEVELS.get(str(risk_level).lower(), 1)

    if level <= 1:
        return "LOG"

    if level == 2:
        return "ALERT"

    if level == 3:
        return "CONTAINMENT_PENDING" if authorized else "CONTAINMENT_REVIEW"

    return "QUARANTINE_PENDING" if authorized else "QUARANTINE_REVIEW"


def build_policy_decision(
    risk_level: str,
    reason: str,
    authorized: bool = False,
) -> dict:
    return {
        "risk_level": str(risk_level).lower(),
        "reason": reason,
        "authorized": bool(authorized),
        "response": classify_response(risk_level, authorized),
        "execution_allowed": False,
    }
