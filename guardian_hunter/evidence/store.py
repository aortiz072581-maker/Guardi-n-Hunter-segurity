"""Guardian Hunter - lightweight incident evidence store."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EvidenceStore:
    """Append-only JSONL evidence store."""

    def __init__(self, path: str = "data/incidents.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict) -> dict:
        record = {
            "timestamp": _utc_now(),
            **event,
        }

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

        return record

    def count(self) -> int:
        if not self.path.exists():
            return 0

        with self.path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
