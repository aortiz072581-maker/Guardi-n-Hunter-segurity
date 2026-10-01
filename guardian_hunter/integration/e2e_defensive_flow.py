\
"""Guardian Hunter — defensive end-to-end orchestration.

Connects existing defensive components without granting execution
and without automatically authorizing Hunter discoveries.
"""

from __future__ import annotations

from time import time
from typing import Any

from guardian_hunter.authorization.contract import Role
from guardian_hunter.authorization.decision_response_adapter import (
    AuthorizationDecisionResponseAdapter,
)
from guardian_hunter.decision.engine import make_decision
from guardian_hunter.evidence.persistence import (
    EvidenceStore,
    fail_closed as evidence_fail_closed,
    safety_invariants_hold as evidence_safety_invariants_hold,
)
from guardian_hunter.modules.hunter import run_hunt
from guardian_hunter.pipeline.engine import SecurityPipeline


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


def safety_invariants_hold() -> bool:
    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
        and evidence_safety_invariants_hold()
    )


def _risk_level(score: float) -> str:
    if score >= 90:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "INFORMATIONAL"


def run_defensive_flow(
    *,
    target: str,
    asset_manager: Any,
    evidence_store: EvidenceStore,
    actor_id: str,
    role: Role = Role.OPERATOR,
    request_id: str,
    authorization_id: str,
    nonce: str,
    pipeline: SecurityPipeline | None = None,
    adapter: AuthorizationDecisionResponseAdapter | None = None,
    run_hunter: bool = True,
) -> dict[str, Any]:
    """Run the existing defensive chain.

    Real response execution is never enabled.
    Hunter discoveries remain discovered/review assets.
    """

    if not safety_invariants_hold():
        raise RuntimeError("SAFETY_INVARIANTS_FAILED")

    if not asset_manager.is_authorized(target):
        return {
            "status": "blocked",
            "stage": "asset_authorization",
            "target": target,
            "authorized": False,
            "execution_allowed": False,
            "human_review_required": True,
            "response_locked": True,
            "reason": "TARGET_NOT_AUTHORIZED",
        }

    hunter_result = None

    local_target = target.lower().rstrip(".") in {
        "localhost",
        "127.0.0.1",
        "::1",
    }

    if run_hunter and not local_target:
        hunter_result = globals()["run_hunt"](
            target,
            asset_manager=asset_manager,
        )

        if hunter_result.get("status") == "blocked":
            return {
                "status": "blocked",
                "stage": "hunter",
                "target": target,
                "authorized": True,
                "hunter": hunter_result,
                "execution_allowed": False,
                "human_review_required": True,
                "response_locked": True,
                "reason": "HUNTER_BLOCKED",
            }

    pipeline = pipeline or SecurityPipeline(asset_manager)

    assessment = pipeline.assess(target)

    report = assessment.get("report", {})
    risk = report.get("risk", {})

    max_score = float(risk.get("max_score", 0) or 0)

    decision = make_decision(
        risk_score=max_score,
        confidence=1.0,
        context={
            "known_asset": True,
            "repeated_signal": False,
        },
        mode="DRY_RUN",
    )

    evidence_store.append(
        evidence_id=f"e2e-{authorization_id}",
        event_type="DEFENSIVE_ASSESSMENT",
        timestamp=time(),
        payload={
            "target": target,
            "risk": risk,
            "decision": decision,
            "hunter": hunter_result,
        },
    )

    evidence_verification = evidence_store.verify()

    if not evidence_fail_closed(evidence_verification):
        raise RuntimeError("EVIDENCE_FAIL_CLOSED_INVARIANT_FAILED")

    if evidence_verification.state != "EVIDENCE_INTEGRITY_OK":
        return {
            "status": "blocked",
            "stage": "evidence",
            "target": target,
            "authorized": True,
            "decision": decision,
            "execution_allowed": False,
            "human_review_required": True,
            "response_locked": True,
            "reason": "EVIDENCE_INTEGRITY_FAILED",
        }

    adapter = adapter or AuthorizationDecisionResponseAdapter()

    response = adapter.authorize_and_prepare_response(
        actor_id=actor_id,
        role=role,
        action="request_response",
        request_id=request_id,
        authorization_id=authorization_id,
        nonce=nonce,
        risk_level=_risk_level(max_score),
        reason=decision["decision"],
        target=target,
        risk_data=risk,
    )

    return {
        "status": (
            "review_required"
            if response.authorized
            else "blocked"
        ),
        "stage": "human_review",
        "target": target,
        "authorized": response.authorized,
        "hunter": hunter_result,
        "assessment": assessment,
        "risk": risk,
        "decision": decision,
        "evidence_state": evidence_verification.state,
        "response": response,
        "execution_allowed": False,
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "human_review_required": True,
        "response_locked": True,
    }


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "RESPONSE_LOCKED",
    "safety_invariants_hold",
    "run_defensive_flow",
]
