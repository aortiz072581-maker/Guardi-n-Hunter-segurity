"""Unica validacion de rutas relativas propuestas por un agente o un humano."""
from __future__ import annotations

MAX_PATH_LENGTH = 1024


def normalize_relative(value: str) -> str:
    """Devuelve la ruta canonica (separador '/') o lanza un error con codigo.

    Estricta: rechaza absolutas, '..', componentes vacios o '.', caracteres de
    control, unidades tipo 'C:' y rutas demasiado largas. No toca el disco.
    """
    if not isinstance(value, str):
        raise TypeError("PATH_MUST_BE_STRING")
    if not value or len(value) > MAX_PATH_LENGTH:
        raise ValueError("INVALID_PATH")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("INVALID_PATH")
    raw = value.replace("\\", "/")
    if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
        raise ValueError("ABSOLUTE_PATH_FORBIDDEN")
    parts = raw.split("/")
    if ".." in parts:
        raise ValueError("PATH_TRAVERSAL_FORBIDDEN")
    if any(part in ("", ".") for part in parts):
        raise ValueError("INVALID_PATH")
    return "/".join(parts)
