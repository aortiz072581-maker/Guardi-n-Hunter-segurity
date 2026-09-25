from datetime import datetime, timezone

from guardian_hunter.config.settings import APP_NAME


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def system_state(asset_manager=None):
    assets = asset_manager

    if assets is None:
        authorized = 0
        discovered = 0
        changes = 0
    else:
        authorized = len(assets.get_authorized())
        discovered = len(assets.get_discovered())
        changes = len(assets.get_changes())

    return {
        "application": APP_NAME,
        "status": "ready",
        "mode": "authorized_defensive",
        "network_activity": False,
        "timestamp": utc_now(),
        "assets": {
            "authorized": authorized,
            "discovered": discovered,
            "changes": changes,
        },
        "modules": {
            "system": "ready",
            "assets": "ready",
            "hunter": "ready",
            "assessment": "ready",
            "risk": "ready",
            "intelligence": "ready",
            "reports": "ready",
            "alerts": "ready",
        },
    }
