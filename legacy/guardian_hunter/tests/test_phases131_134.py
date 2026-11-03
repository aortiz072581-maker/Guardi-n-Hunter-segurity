from guardian_hunter.governance.phase131_master_handoff import (
    MasterStateHandoff,
)
from guardian_hunter.verification.phase132_handoff_integrity import (
    HandoffIntegrity,
)
from guardian_hunter.governance.phase133_continuity_lock import (
    ContinuityConsistencyLock,
)
from guardian_hunter.governance.phase134_master_gate import (
    ContinuityMasterGate,
)


def test_phase131():
    result = MasterStateHandoff().build()

    assert result.source_state == "DEFENSIVE_ATTESTATION_MASTER_READY"
    assert result.source_score == 100
    assert result.response_locked is True
    assert result.human_review_required is True
    assert result.read_only is True
    assert result.dry_run is True
    assert result.real_execution_blocked is True


def test_phase132():
    handoff = MasterStateHandoff().build()
    result = HandoffIntegrity().verify(handoff)

    assert result["valid"] is True
    assert result["state"] == "DEFENSIVE_HANDOFF_INTEGRITY_VALID"
    assert len(result["digest"]) == 64


def test_phase133():
    handoff = MasterStateHandoff().build()
    integrity = HandoffIntegrity().verify(handoff)
    result = ContinuityConsistencyLock().lock(integrity)

    assert result["locked"] is True
    assert result["score"] == 100
    assert result["state"] == (
        "DEFENSIVE_CONTINUITY_CONSISTENCY_LOCKED"
    )


def test_phase134():
    result = ContinuityMasterGate().evaluate()

    assert result["score"] == 100
    assert result["state"] == "DEFENSIVE_CONTINUITY_MASTER_READY"
    assert result["response_locked"] is True
    assert result["human_review_required"] is True
    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
