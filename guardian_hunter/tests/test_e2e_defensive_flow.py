\
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guardian_hunter.assets import AssetManager
from guardian_hunter.authorization.contract import Role
from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.integration import e2e_defensive_flow as flow
from guardian_hunter.security.mode import Candidate
from guardian_hunter.security.trust_root import TrustResult


class FakePipeline:
    def __init__(self, assets):
        self.assets = assets
        self.called = False

    def assess(self, target):
        assert self.assets.is_authorized(target)
        self.called = True

        return {
            "report": {
                "target": target,
                "risk": {
                    "total": 1,
                    "max_score": 72,
                    "summary": {
                        "critical": 0,
                        "high": 1,
                        "medium": 0,
                        "low": 0,
                        "informational": 0,
                    },
                    "findings": [
                        {
                            "title": "defensive-test-finding",
                            "score": 72,
                            "severity": "high",
                        }
                    ],
                },
            },
            "reports": {},
            "alerts": [],
            "execution_id": 1,
        }


def build_assets(tmp_path: Path):
    return AssetManager(
        tmp_path / "assets.json"
    )


def test_complete_defensive_flow_is_locked(
    tmp_path,
    monkeypatch,
):
    assets = build_assets(tmp_path)
    assets.add_authorized("example.test")

    discovered = [
        "a.example.test",
        "b.example.test",
    ]

    def fake_hunter(domain, asset_manager=None):
        assert domain == "example.test"

        asset_manager.import_discovered(
            discovered,
            source="hunter",
        )

        return {
            "domain": domain,
            "source": "test",
            "status": "ok",
            "total": len(discovered),
            "subdomains": discovered,
            "known_assets": [],
            "review_assets": discovered,
            "shadow_subdomains": discovered,
            "shown_exposures": [],
            "errors": [],
        }

    monkeypatch.setattr(
        flow,
        "run_hunt",
        fake_hunter,
    )

    pipeline = FakePipeline(assets)


    trust = TrustResult(
        trusted=True,
        reason="TEST_TRUSTED",
        policy_id="E2E_TEST_POLICY",
        baseline_id="E2E_TEST_BASELINE",
        verification_time=datetime.now(timezone.utc).isoformat(),
    )

    now = datetime.now(timezone.utc)
    candidate = Candidate(
        candidate_id="e2e-candidate-1",
        evidence_id="e2e-e2e-auth-1",
        created_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(minutes=5),
    )

    result = flow.run_defensive_flow(
        target="example.test",
        asset_manager=assets,
        evidence_store=EvidenceStore(
            tmp_path / "evidence.jsonl"
        ),
        actor_id="e2e-operator",
        role=Role.OPERATOR,
        request_id="e2e-request-1",
        authorization_id="e2e-auth-1",
        nonce="e2e-nonce-1",
        pipeline=pipeline,
        trust_result=trust,
        candidate=candidate,
        approver="e2e-test-approver",
        approval_reason="controlled defensive E2E approval",
    )

    assert pipeline.called
    assert result["status"] == "review_required"
    assert result["authorized"] is True
    assert result["evidence_state"] == "EVIDENCE_INTEGRITY_OK"

    assert result["execution_allowed"] is False
    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True
    assert result["response_locked"] is True

    assert result["response"].execution_allowed is False
    assert result["response"].response_locked is True
    assert result["response"].human_review_required is True

    # Hunter discoveries are review/discovered only.
    for item in discovered:
        assert assets.is_authorized(item) is False


def test_unauthorized_target_never_reaches_hunter_or_pipeline(
    tmp_path,
    monkeypatch,
):
    assets = build_assets(tmp_path)

    called = {
        "hunter": False,
    }

    def forbidden_hunter(*args, **kwargs):
        called["hunter"] = True
        raise AssertionError(
            "Hunter must not run for unauthorized target"
        )

    monkeypatch.setattr(
        flow,
        "run_hunt",
        forbidden_hunter,
    )

    pipeline = FakePipeline(assets)

    result = flow.run_defensive_flow(
        target="unauthorized.test",
        asset_manager=assets,
        evidence_store=EvidenceStore(
            tmp_path / "evidence.jsonl"
        ),
        actor_id="e2e-operator",
        role=Role.OPERATOR,
        request_id="e2e-request-2",
        authorization_id="e2e-auth-2",
        nonce="e2e-nonce-2",
        pipeline=pipeline,
    )

    assert result["status"] == "blocked"
    assert result["stage"] == "asset_authorization"
    assert called["hunter"] is False
    assert pipeline.called is False
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True


def test_safety_invariant_failure_blocks_before_flow(
    tmp_path,
    monkeypatch,
):
    assets = build_assets(tmp_path)
    assets.add_authorized("example.test")

    monkeypatch.setattr(
        flow,
        "RESPONSE_LOCKED",
        False,
    )

    try:
        flow.run_defensive_flow(
            target="example.test",
            asset_manager=assets,
            evidence_store=EvidenceStore(
                tmp_path / "evidence.jsonl"
            ),
            actor_id="e2e-operator",
            role=Role.OPERATOR,
            request_id="e2e-request-3",
            authorization_id="e2e-auth-3",
            nonce="e2e-nonce-3",
            pipeline=FakePipeline(assets),
        )
    except RuntimeError as exc:
        assert str(exc) == "SAFETY_INVARIANTS_FAILED"
    else:
        raise AssertionError(
            "Safety drift must fail closed"
        )
