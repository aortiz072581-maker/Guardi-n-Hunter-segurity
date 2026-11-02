"""Utilidades canonicas unicas: JSON determinista, digest y reloj UTC."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping


def canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def digest(data: Any) -> str:
    return sha256(canonical_json(data).encode("utf-8")).hexdigest()


def digest_excluding(data: Mapping[str, Any], key: str = "digest") -> str:
    return digest({k: v for k, v in data.items() if k != key})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
