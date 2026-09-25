import shutil
import subprocess


def normalize_name(value):
    if not isinstance(value, str):
        return ""

    value = value.strip().lower()

    if value.endswith("."):
        value = value[:-1]

    return value


def find_subdomains(domain):
    domain = normalize_name(domain)

    if not domain:
        return {
            "status": "error",
            "subdomains": [],
            "errors": ["Dominio vacío o inválido."],
        }

    if not shutil.which("subfinder"):
        return {
            "status": "error",
            "subdomains": [],
            "errors": [
                "Subfinder no está instalado o no está disponible en PATH."
            ],
        }

    try:
        result = subprocess.run(
            [
                "subfinder",
                "-d",
                domain,
                "-silent",
                "-timeout",
                "15",
                "-max-time",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=75,
            check=False,
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "subdomains": [],
                "errors": [
                    result.stderr.strip()
                    or f"Subfinder terminó con código {result.returncode}."
                ],
            }

        found = []

        for line in result.stdout.splitlines():
            value = normalize_name(line)

            if value and value not in found:
                found.append(value)

        return {
            "status": "ok",
            "subdomains": found,
            "errors": [],
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "subdomains": [],
            "errors": ["Subfinder agotó el tiempo máximo permitido."],
        }

    except OSError as exc:
        return {
            "status": "error",
            "subdomains": [],
            "errors": [str(exc)],
        }

    except Exception as exc:
        return {
            "status": "error",
            "subdomains": [],
            "errors": [str(exc)],
        }


def run_hunt(domain, official_assets=None, asset_manager=None):
    """
    Hunter pasivo/autorizado.

    La ejecución de red solamente ocurre cuando esta función
    es llamada explícitamente por el operador.

    Asset Manager permite centralizar los assets autorizados.
    """

    domain = normalize_name(domain)

    if asset_manager is not None:
        authorized = asset_manager.get_authorized()
    else:
        authorized = official_assets or []

    authorized = {
        normalize_name(item)
        for item in authorized
        if normalize_name(item)
    }

    result = find_subdomains(domain)

    subdomains = result["subdomains"]

    known_assets = [
        item
        for item in subdomains
        if item in authorized
    ]

    review_assets = [
        item
        for item in subdomains
        if item not in authorized
    ]

    if asset_manager is not None:
        asset_manager.import_discovered(
            subdomains,
            source="hunter",
        )

    return {
        "domain": domain,
        "source": "subfinder",
        "status": result["status"],
        "total": len(subdomains),
        "subdomains": subdomains,
        "known_assets": known_assets,
        "review_assets": review_assets,
        "shadow_subdomains": review_assets,
        "shown_exposures": [],
        "errors": result["errors"],
    }
