import socket


def assess_dns(hostname):
    findings = []

    if not isinstance(hostname, str) or not hostname.strip():
        return {
            "target": hostname,
            "addresses": [],
            "findings": [],
            "error": "Hostname inválido.",
        }

    hostname = hostname.strip().lower()

    try:
        results = socket.getaddrinfo(hostname, None)
        addresses = sorted({
            result[4][0]
            for result in results
            if result and result[4]
        })

        return {
            "target": hostname,
            "addresses": addresses,
            "findings": findings,
            "error": None,
        }

    except socket.gaierror as exc:
        return {
            "target": hostname,
            "addresses": [],
            "findings": [],
            "error": str(exc),
        }

    except OSError as exc:
        return {
            "target": hostname,
            "addresses": [],
            "findings": [],
            "error": str(exc),
        }
