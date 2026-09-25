EXPECTED_HEADERS = {
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
}


def analyze_headers(headers):
    normalized = {
        str(k).lower(): str(v)
        for k, v in (headers or {}).items()
    }

    missing = sorted(
        EXPECTED_HEADERS - set(normalized)
    )

    return {
        "checked": len(EXPECTED_HEADERS),
        "missing": missing,
        "present": sorted(
            EXPECTED_HEADERS & set(normalized)
        ),
    }
