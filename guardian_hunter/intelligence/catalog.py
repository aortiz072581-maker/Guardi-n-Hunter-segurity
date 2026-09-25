def technology_record(name, version=None, source="local"):
    """
    Registro normalizado de tecnología.
    No consulta servicios externos ni ejecuta código.
    """
    return {
        "name": str(name).strip(),
        "version": version,
        "source": source,
    }


def cve_record(cve_id, severity=None, description=""):
    return {
        "id": str(cve_id).strip().upper(),
        "severity": severity,
        "description": description,
    }


def kev_record(cve_id, known_exploited=False, source="local"):
    return {
        "cve": str(cve_id).strip().upper(),
        "known_exploited": bool(known_exploited),
        "source": source,
    }
