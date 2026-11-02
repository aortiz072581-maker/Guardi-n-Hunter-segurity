"""Read-only C6 operational security correlation."""

from guardian_hunter.integration.c6_sensor_bridge import (
    correlate_sensor_report,
)

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False

def run_c6_operational(sensor_report):
    result = correlate_sensor_report(sensor_report)

    if result["execution_allowed"] is not False:
        raise RuntimeError("UNSAFE_C6_AUTHORITY")
    if result["automatic_repair"] is not False:
        raise RuntimeError("UNSAFE_C6_REPAIR")
    if result["merge_allowed"] is not False:
        raise RuntimeError("UNSAFE_C6_MERGE")

    return {
        "schema": "guardian-c6-operational-v1",
        "correlation": result,
        "finding_count": result["finding_count"],
        "classification_complete": result["classification_complete"],
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }
