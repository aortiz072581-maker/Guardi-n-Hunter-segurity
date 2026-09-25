def match_technology(technology, catalog):
    if not isinstance(technology, str):
        return []

    name = technology.strip().lower()

    return [
        item
        for item in catalog or []
        if isinstance(item, dict)
        and str(item.get("name", "")).strip().lower()
        == name
    ]


def match_cves(technologies, cve_catalog):
    names = {
        str(item).strip().lower()
        for item in technologies or []
        if str(item).strip()
    }

    matches = []

    for cve in cve_catalog or []:
        if not isinstance(cve, dict):
            continue

        text = " ".join([
            str(cve.get("id", "")),
            str(cve.get("description", "")),
        ]).lower()

        if any(name in text for name in names):
            matches.append(cve)

    return matches


def correlate(
    technologies=None,
    technology_catalog=None,
    cve_catalog=None,
):
    technologies = technologies or []

    technology_matches = []

    for technology in technologies:
        technology_matches.extend(
            match_technology(
                technology,
                technology_catalog or [],
            )
        )

    cve_matches = match_cves(
        technologies,
        cve_catalog or [],
    )

    return {
        "technologies": technologies,
        "technology_matches": technology_matches,
        "cve_matches": cve_matches,
        "total_cves": len(cve_matches),
    }
