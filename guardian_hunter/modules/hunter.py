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

    El descubrimiento solamente puede ejecutarse cuando:
    - run_hunt() es llamado explícitamente;
    - el dominio es válido;
    - el dominio está expresamente autorizado.

    Los activos descubiertos quedan como discovered/review.
    Nunca se convierten automáticamente en autorizados.
    """

    domain = normalize_name(domain)

    base_result = {
        "domain": domain,
        "source": "subfinder",
        "status": "blocked",
        "total": 0,
        "subdomains": [],
        "known_assets": [],
        "review_assets": [],
        "shadow_subdomains": [],
        "shown_exposures": [],
        "errors": [],
    }

    # Fail closed ante entrada inválida.
    if not domain:
        base_result["errors"] = [
            "Dominio vacío o inválido."
        ]
        return base_result

    # AssetManager es la fuente preferida de autorización.
    if asset_manager is not None:
        authorized_source = asset_manager.get_authorized()
    else:
        authorized_source = official_assets or []

    authorized = {
        normalize_name(item)
        for item in authorized_source
        if normalize_name(item)
    }

    # IMPORTANTE:
    # La autorización se verifica ANTES de find_subdomains().
    # Un argumento proporcionado por el operador no equivale
    # automáticamente a autorización.
    if domain not in authorized:
        base_result["errors"] = [
            f"Dominio no autorizado para Hunter: {domain}"
        ]
        return base_result

    # Solo llegamos aquí si el dominio está autorizado.
    result = find_subdomains(domain)

    subdomains = [
        normalize_name(item)
        for item in result.get("subdomains", [])
        if normalize_name(item)
    ]

    # Eliminar duplicados conservando orden.
    subdomains = list(dict.fromkeys(subdomains))

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

    # Los descubrimientos se registran como discovered.
    # NO se promueven automáticamente a authorized.
    if asset_manager is not None and subdomains:
        asset_manager.import_discovered(
            subdomains,
            source="hunter",
        )

    return {
        "domain": domain,
        "source": "subfinder",
        "status": result.get("status", "error"),
        "total": len(subdomains),
        "subdomains": subdomains,
        "known_assets": known_assets,
        "review_assets": review_assets,
        "shadow_subdomains": review_assets,
        "shown_exposures": [],
        "errors": result.get("errors", []),
    }
