"""Supervised defensive flow with independent C6 assessment."""

from pathlib import Path
from shutil import which

from guardian_hunter.integration.consolidated_defensive_flow import (
    run_consolidated_defensive_flow,
)
from guardian_hunter.integration.security_sensor_adapter import (
    assess_security_sensors,
)
from guardian_hunter.integration.c6_operational import (
    run_c6_operational,
)

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False


def run_supervised_flow(
    *,
    root,
    baseline_file,
    previous_hardware=None,
    previous_network=None,
    hardware=None,
    network=None,
    sensor_report=None,
):
    root = Path(root).resolve()

    main = run_consolidated_defensive_flow(
        root=root,
        baseline_file=baseline_file,
        previous_hardware=previous_hardware,
        previous_network=previous_network,
        hardware=hardware,
        network=network,
    )

    if not isinstance(main, dict):
        raise ValueError("INVALID_MAIN_RESULT")

    if main.get("execution_allowed") is not False:
        raise ValueError("UNSAFE_MAIN_AUTHORITY")

    if main.get("response_locked") is not True:
        raise ValueError("MAIN_RESPONSE_UNLOCKED")

    if sensor_report is None:
        gitleaks = which("gitleaks")
        osv = which("osv-scanner")

        if not gitleaks or not osv:
            raise ValueError("C6_SCANNERS_MISSING")

        sensor_report = assess_security_sensors(
            root,
            gitleaks_binary=gitleaks,
            osv_binary=osv,
        )

    c6 = run_c6_operational(sensor_report)

    for key in (
        "execution_allowed",
        "automatic_repair",
        "merge_allowed",
    ):
        if c6.get(key) is not False:
            raise ValueError("UNSAFE_C6_AUTHORITY")

    if c6.get("human_approval_required") is not True:
        raise ValueError("C6_APPROVAL_MISSING")

    return {
        "schema": "guardian-supervised-flow-v1",
        "main": main,
        "c6_operational": c6,
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
        "response_locked": True,
    }
