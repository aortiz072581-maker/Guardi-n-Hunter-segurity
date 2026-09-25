import hashlib


def fingerprint_finding(
    target,
    category,
    title,
    evidence="",
):
    value = "|".join([
        str(target or "").strip().lower(),
        str(category or "").strip().lower(),
        str(title or "").strip().lower(),
        str(evidence or "").strip().lower(),
    ])

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def correlate_findings(
    target,
    findings=None,
    technologies=None,
    cves=None,
    kev=None,
):
    findings = findings or []
    technologies = technologies or []
    cves = cves or []
    kev = kev or []

    correlated = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        item = dict(finding)

        item["fingerprint"] = fingerprint_finding(
            target,
            item.get("category"),
            item.get("title"),
            item.get("evidence"),
        )

        related_technologies = []

        text = " ".join([
            str(item.get("title", "")),
            str(item.get("evidence", "")),
        ]).lower()

        for technology in technologies:
            if not isinstance(technology, dict):
                continue

            name = str(
                technology.get("name", "")
            ).strip()

            if name and name.lower() in text:
                related_technologies.append(
                    technology
                )

        related_cves = []

        for cve in cves:
            if not isinstance(cve, dict):
                continue

            description = str(
                cve.get("description", "")
            ).lower()

            if any(
                str(t.get("name", "")).lower()
                in description
                for t in related_technologies
            ):
                related_cves.append(cve)

        related_kev = []

        cve_ids = {
            str(cve.get("id", "")).upper()
            for cve in related_cves
        }

        for item_kev in kev:
            if not isinstance(item_kev, dict):
                continue

            if (
                str(
                    item_kev.get("cve", "")
                ).upper()
                in cve_ids
            ):
                related_kev.append(
                    item_kev
                )

        item["correlation"] = {
            "technologies": related_technologies,
            "cves": related_cves,
            "kev": related_kev,
        }

        correlated.append(item)

    return correlated
