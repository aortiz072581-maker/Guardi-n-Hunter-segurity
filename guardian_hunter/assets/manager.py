import json
from datetime import datetime, timezone
from pathlib import Path

from guardian_hunter.config.settings import DATA_DIR


DEFAULT_FILE = DATA_DIR / "asset_registry.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _normalize(value):
    if not isinstance(value, str):
        return ""

    value = value.strip().lower()

    if value.endswith("."):
        value = value[:-1]

    return value


class AssetManager:
    """
    Registro central de assets de Guardian Hunter.

    Mantiene:
    - assets autorizados
    - assets descubiertos
    - historial de cambios

    No realiza conexiones de red.
    """

    def __init__(self, path=None):
        self.path = Path(path or DEFAULT_FILE)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.data = {
            "authorized": [],
            "discovered": [],
            "changes": [],
        }

        self.load()

    def load(self):
        if not self.path.exists():
            self.save()
            return self.data

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)

            if isinstance(loaded, dict):
                self.data["authorized"] = loaded.get(
                    "authorized", []
                )
                self.data["discovered"] = loaded.get(
                    "discovered", []
                )
                self.data["changes"] = loaded.get(
                    "changes", []
                )

        except (OSError, json.JSONDecodeError):
            self.data = {
                "authorized": [],
                "discovered": [],
                "changes": [],
            }

            self.save()

        return self.data

    def save(self):
        temporary = self.path.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(
                self.data,
                handle,
                indent=2,
                ensure_ascii=False,
            )

        temporary.replace(self.path)

    def add_authorized(self, asset):
        asset = _normalize(asset)

        if not asset:
            return False

        if asset in self.data["authorized"]:
            return False

        self.data["authorized"].append(asset)

        self.data["changes"].append({
            "timestamp": _now(),
            "type": "authorized_added",
            "asset": asset,
        })

        self.data["authorized"].sort()
        self.save()

        return True

    def remove_authorized(self, asset):
        asset = _normalize(asset)

        if asset not in self.data["authorized"]:
            return False

        self.data["authorized"].remove(asset)

        self.data["changes"].append({
            "timestamp": _now(),
            "type": "authorized_removed",
            "asset": asset,
        })

        self.save()

        return True

    def add_discovered(self, asset, source="hunter"):
        asset = _normalize(asset)

        if not asset:
            return False

        if asset in self.data["discovered"]:
            return False

        self.data["discovered"].append(asset)

        self.data["changes"].append({
            "timestamp": _now(),
            "type": "discovered_added",
            "asset": asset,
            "source": source,
        })

        self.data["discovered"].sort()
        self.save()

        return True

    def get_authorized(self):
        return list(self.data["authorized"])

    def get_discovered(self):
        return list(self.data["discovered"])

    def get_changes(self):
        return list(self.data["changes"])

    def is_authorized(self, asset):
        return _normalize(asset) in self.data["authorized"]

    def classify(self, asset):
        asset = _normalize(asset)

        if not asset:
            return "invalid"

        if asset in self.data["authorized"]:
            return "authorized"

        if asset in self.data["discovered"]:
            return "discovered"

        return "unknown"

    def import_discovered(self, assets, source="hunter"):
        added = 0

        for asset in assets or []:
            if self.add_discovered(asset, source=source):
                added += 1

        return added

    def snapshot(self):
        return {
            "authorized": len(self.data["authorized"]),
            "discovered": len(self.data["discovered"]),
            "changes": len(self.data["changes"]),
        }
