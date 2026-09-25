import socket
import ssl
from datetime import datetime, timezone


def assess_tls(hostname, port=443, timeout=8):
    findings = []

    context = ssl.create_default_context()

    try:
        with socket.create_connection(
            (hostname, port),
            timeout=timeout,
        ) as sock:
            with context.wrap_socket(
                sock,
                server_hostname=hostname,
            ) as secure_socket:

                certificate = secure_socket.getpeercert()
                cipher = secure_socket.cipher()

                expires = certificate.get("notAfter")

                if expires:
                    try:
                        expiry = datetime.strptime(
                            expires,
                            "%b %d %H:%M:%S %Y %Z",
                        ).replace(tzinfo=timezone.utc)

                        if expiry < datetime.now(timezone.utc):
                            findings.append({
                                "category": "tls",
                                "title": "Certificado TLS expirado",
                                "score": 70,
                                "evidence": expires,
                                "recommendation": (
                                    "Renovar el certificado TLS."
                                ),
                            })
                    except ValueError:
                        pass

                return {
                    "hostname": hostname,
                    "port": port,
                    "certificate": certificate,
                    "cipher": cipher,
                    "findings": findings,
                    "error": None,
                }

    except Exception as exc:
        return {
            "hostname": hostname,
            "port": port,
            "certificate": {},
            "cipher": None,
            "findings": [],
            "error": str(exc),
        }
