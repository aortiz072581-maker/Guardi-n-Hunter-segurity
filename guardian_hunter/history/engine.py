def finding_key(finding):
    return finding.get(
        "fingerprint"
    ) or "|".join([
        str(finding.get("category", "")),
        str(finding.get("title", "")),
        str(finding.get("evidence", "")),
    ])


def compare_findings(
    previous=None,
    current=None,
):
    previous = previous or []
    current = current or []

    previous_map = {
        finding_key(item): item
        for item in previous
        if isinstance(item, dict)
    }

    current_map = {
        finding_key(item): item
        for item in current
        if isinstance(item, dict)
    }

    added = []
    removed = []
    changed = []
    unchanged = []

    for key, item in current_map.items():
        if key not in previous_map:
            added.append(item)

        elif previous_map[key] != item:
            changed.append({
                "before": previous_map[key],
                "after": item,
            })

        else:
            unchanged.append(item)

    for key, item in previous_map.items():
        if key not in current_map:
            removed.append(item)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
    }
