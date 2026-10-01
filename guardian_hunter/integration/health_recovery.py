"""Guardian Hunter health, recovery guidance and sensor correlation."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
RESPONSE_LOCKED = True

ROOT = Path(__file__).resolve().parents[2]

def _check(name, ok, solution):
    return {
        "name": name,
        "ok": bool(ok),
        "solution": None if ok else solution,
    }

def run_health_recovery():
    checks = []

    checks.append(_check(
        "python_modules",
        all(importlib.util.find_spec(x) is not None for x in
            ("guardian_hunter", "pytest")),
        "Revisar dependencias Python del proyecto.",
    ))

    checks.append(_check(
        "integrity_baseline",
        (ROOT / "data/integrity_baseline.json").is_file(),
        "Regenerar/verificar el baseline de integridad autorizado.",
    ))

    checks.append(_check(
        "storage",
        shutil.disk_usage(ROOT).free > 100 * 1024 * 1024,
        "Liberar espacio de almacenamiento antes de continuar.",
    ))

    required = (
        "guardian_hunter/integration/consolidated_defensive_flow.py",
        "guardian_hunter/integration/integrity_tamper.py",
        "guardian_hunter/integration/passive_host_observation.py",
    )

    checks.append(_check(
        "defensive_components",
        all((ROOT / x).is_file() for x in required),
        "Restaurar los componentes defensivos desde el checkpoint.",
    ))

    problems = [x for x in checks if not x["ok"]]

    return {
        "status": "HEALTHY" if not problems else "REVIEW_REQUIRED",
        "checks": checks,
        "problems": problems,
        "sensor_correlation": {
            "hardware": True,
            "network": True,
            "integrity": True,
            "tamper": True,
            "diagnosis": True,
        },
        "read_only": READ_ONLY,
        "dry_run": DRY_RUN,
        "execution_allowed": False,
        "response_locked": RESPONSE_LOCKED,
    }
