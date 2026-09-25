from datetime import datetime, timezone
import hashlib


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def fingerprint_item(item):
    if not isinstance(item, dict):
        return None

    base = "|".join([
        str(item.get("category", "")),
        str(item.get("title", "")),
        str(item.get("evidence", "")),
    ])

    return hashlib.sha256(base.encode()).hexdigest()


def build_baseline(findings):
    baseline = []

    for finding in findings or []:
        if not isinstance(finding, dict):
            continue

        item = dict(finding)
        item["fingerprint"] = (
            item.get("fingerprint")
            or fingerprint_item(item)
        )
        baseline.append(item)

    return {
        "timestamp": utc_now(),
        "count": len(baseline),
        "findings": baseline,
    }


def compare_baseline(previous, current):
    previous = previous or {}
    current = current or {}

    old = {
        item.get("fingerprint")
        for item in previous.get("findings", [])
        if isinstance(item, dict)
    }

    new = {
        item.get("fingerprint")
        for item in current.get("findings", [])
        if isinstance(item, dict)
    }

    return {
        "new": sorted(new - old),
        "resolved": sorted(old - new),
        "unchanged": sorted(old & new),
        "timestamp": utc_now(),
    }
