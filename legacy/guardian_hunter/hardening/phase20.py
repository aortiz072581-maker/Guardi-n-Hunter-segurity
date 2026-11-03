from pathlib import Path
import hashlib
import json
import os
import platform


def _network_interfaces():
    """
    Obtiene las interfaces de red disponibles.

    En Termux/Android /sys/class/net puede estar restringido.
    Un problema de permisos no debe detener el baseline.
    """
    base = Path("/sys/class/net")

    try:
        return sorted(
            item.name
            for item in base.iterdir()
            if item.is_dir()
        )
    except (PermissionError, FileNotFoundError, OSError):
        return []


def _platform_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


def _environment_info():
    prefix = os.environ.get("PREFIX", "")

    return {
        "termux": bool(
            os.environ.get("TERMUX_VERSION")
            or prefix.startswith("/data/data/com.termux")
        )
    }


def system_baseline():
    """
    Captura un baseline defensivo y no intrusivo del sistema.
    """
    return {
        "platform": _platform_info(),
        "network_interfaces": _network_interfaces(),
        "environment": _environment_info(),
    }


def baseline_fingerprint(baseline):
    """
    Genera una huella SHA-256 determinista del baseline.
    """
    payload = json.dumps(
        baseline,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def compare_baseline(reference, current):
    """
    Compara dos baselines sin modificar ninguno.
    """
    reference_fingerprint = baseline_fingerprint(reference)
    current_fingerprint = baseline_fingerprint(current)

    changed = reference_fingerprint != current_fingerprint

    return {
        "changed": changed,
        "status": "CHANGED" if changed else "UNCHANGED",
        "reference_fingerprint": reference_fingerprint,
        "current_fingerprint": current_fingerprint,
    }


def integrity_manifest(paths):
    """
    Genera un manifiesto SHA-256 de los archivos indicados.

    Devuelve una entrada por archivo.
    Si un archivo no puede leerse, devuelve False para ese archivo.
    """
    manifest = {}

    for raw_path in paths:
        path = Path(raw_path)

        try:
            digest = hashlib.sha256()

            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    digest.update(chunk)

            manifest[str(path)] = digest.hexdigest()

        except (OSError, IOError):
            manifest[str(path)] = False

    return manifest
