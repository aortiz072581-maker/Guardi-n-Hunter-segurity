"""Phase 132 — Defensive Master Handoff Integrity"""

import hashlib
import json


class HandoffIntegrity:
    EXPECTED_STATE = "DEFENSIVE_MASTER_HANDOFF_VALID"

    def verify(self, handoff):
        payload = {
            "source_state": handoff.source_state,
            "source_score": handoff.source_score,
            "response_locked": handoff.response_locked,
            "human_review_required": handoff.human_review_required,
            "read_only": handoff.read_only,
            "dry_run": handoff.dry_run,
            "real_execution_blocked": handoff.real_execution_blocked,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return {
            "valid": (
                handoff.state == self.EXPECTED_STATE
                and handoff.source_score == 100
                and handoff.response_locked
                and handoff.human_review_required
                and handoff.read_only
                and handoff.dry_run
                and handoff.real_execution_blocked
            ),
            "digest": digest,
            "state": "DEFENSIVE_HANDOFF_INTEGRITY_VALID",
        }
