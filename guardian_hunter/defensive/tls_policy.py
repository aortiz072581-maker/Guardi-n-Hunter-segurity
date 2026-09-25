SAFE_TLS_MINIMUM = "TLSv1.2"


def evaluate_tls(version):
    if not version:
        return {
            "version": None,
            "status": "unknown",
        }

    if version in {"TLSv1.3", "TLSv1.2"}:
        status = "acceptable"
    else:
        status = "review"

    return {
        "version": version,
        "minimum": SAFE_TLS_MINIMUM,
        "status": status,
    }
