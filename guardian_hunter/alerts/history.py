import json
from datetime import datetime, timezone
from pathlib import Path

from guardian_hunter.config.settings import DATA_DIR


HISTORY_FILE = DATA_DIR / "alert_history.json"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class AlertHistory:
    """
    Historial local de alertas.

    No envía mensajes ni contacta servicios externos.
    """

    def __init__(self, path=None):
        self.path = Path(path or HISTORY_FILE)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.events = []
        self.load()

    def load(self):
        if not self.path.exists():
            self.save()
            return self.events

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)

            if isinstance(data, list):
                self.events = data
            else:
                self.events = []

        except (OSError, json.JSONDecodeError):
            self.events = []
            self.save()

        return self.events

    def save(self):
        temporary = self.path.with_suffix(".tmp")

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                self.events,
                handle,
                indent=2,
                ensure_ascii=False,
            )

        temporary.replace(self.path)

    def add(
        self,
        severity,
        title,
        message,
        source="guardian",
    ):
        event = {
            "timestamp": utc_now(),
            "severity": str(severity).lower(),
            "title": str(title),
            "message": str(message),
            "source": str(source),
        }

        self.events.append(event)
        self.save()

        return event

    def recent(self, limit=20):
        return self.events[-max(1, int(limit)):]

    def count(self):
        return len(self.events)
