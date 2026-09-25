from urllib.parse import urlparse


SECURITY_HEADERS = {
    "strict-transport-security": 15,
    "content-security-policy": 15,
    "x-content-type-options": 10,
    "x-frame-options": 10,
    "referrer-policy": 5,
    "permissions-policy": 5,
}


def assess_headers(headers):
    """
    Analiza headers que ya fueron obtenidos por una capa HTTP autorizada.

    No realiza conexiones de red por sí mismo.
    """
    normalized = {
        str(key).lower(): str(value)
        for key, value in (headers or {}).items()
    }

    findings = []

    for header, score in SECURITY_HEADERS.items():
        if header not in normalized:
            findings.append({
                "category": "headers",
                "title": f"Header ausente: {header}",
                "score": score,
                "evidence": "El header no apareció en la respuesta analizada.",
                "recommendation": f"Evaluar la configuración de {header}.",
            })

    return findings


def normalize_url(url):
    """Acepta únicamente URLs HTTP/HTTPS bien formadas."""
    if not isinstance(url, str):
        return ""

    value = url.strip()

    try:
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            return ""

        if not parsed.hostname:
            return ""

        return value

    except ValueError:
        return ""
