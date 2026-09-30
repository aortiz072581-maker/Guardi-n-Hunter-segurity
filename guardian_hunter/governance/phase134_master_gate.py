"""Phase 134 — Defensive Continuity Master Gate"""

from guardian_hunter.governance.phase131_master_handoff import (
    MasterStateHandoff,
)
from guardian_hunter.verification.phase132_handoff_integrity import (
    HandoffIntegrity,
)
from guardian_hunter.governance.phase133_continuity_lock import (
    ContinuityConsistencyLock,
)


class ContinuityMasterGate:

    def evaluate(self):
        handoff = MasterStateHandoff().build()
        integrity = HandoffIntegrity().verify(handoff)
        lock = ContinuityConsistencyLock().lock(integrity)

        ready = (
            lock["locked"] is True
            and lock["score"] == 100
            and lock["response_locked"] is True
            and lock["human_review_required"] is True
            and lock["read_only"] is True
            and lock["dry_run"] is True
            and lock["real_execution_blocked"] is True
        )

        return {
            "score": 100 if ready else 0,
            "state": (
                "DEFENSIVE_CONTINUITY_MASTER_READY"
                if ready
                else "DEFENSIVE_CONTINUITY_MASTER_FAILED"
            ),
            "response_locked": True,
            "human_review_required": True,
            "read_only": True,
            "dry_run": True,
            "real_execution_blocked": True,
            "handoff": handoff,
            "integrity": integrity,
            "lock": lock,
        }
