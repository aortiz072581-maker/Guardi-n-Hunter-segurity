"""Phase 27 — Guardian Hunter health monitor."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_module(module_name: str) -> dict[str, Any]:
    result = {
        "module": module_name,
        "status": "OK",
        "error": None,
    }

    try:
        importlib.import_module(module_name)
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def check_project_modules(
    root: str = "guardian_hunter",
) -> list[dict[str, Any]]:
    base = Path(root)
    modules: list[str] = []

    for path in sorted(base.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue

        parts = list(path.with_suffix("").parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]

        if not parts:
            continue

        modules.append(".".join(parts))

    results = []

    for module in modules:
        results.append(check_module(module))

    return results


def summarize_health(
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(checks)
    errors = [
        item for item in checks
        if item.get("status") != "OK"
    ]

    if errors:
        status = "DEGRADED"
    else:
        status = "HEALTHY"

    return {
        "timestamp": _utc_now(),
        "status": status,
        "total_modules": total,
        "healthy_modules": total - len(errors),
        "error_modules": len(errors),
        "errors": errors,
    }


def health_check(
    modules: list[str] | None = None,
) -> dict[str, Any]:
    if modules is None:
        checks = check_project_modules()
    else:
        checks = [
            check_module(module)
            for module in modules
        ]

    return summarize_health(checks)
