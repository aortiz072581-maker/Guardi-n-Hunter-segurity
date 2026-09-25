from guardian_hunter.intelligence.enhanced import (
    build_baseline,
    compare_baseline,
)


class Monitor:
    def __init__(self, baseline=None):
        self.baseline = baseline or {}

    def evaluate(self, findings):
        current = build_baseline(findings)

        changes = compare_baseline(
            self.baseline,
            current,
        )

        self.baseline = current

        return {
            "baseline": current,
            "changes": changes,
            "changed": bool(
                changes["new"] or changes["resolved"]
            ),
        }
