from guardian_hunter.diagnosis.engine import (
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)


def test_network_hardware_diagnosis():
    correlation = {
        "categories": ["network", "hardware"],
        "correlated_score": 78.0,
    }

    diagnosis = diagnose_problem(correlation)

    if not (diagnosis.problem_detected is True):
    raise RuntimeError("Assertion failed: diagnosis.problem_detected is True")
    if not (diagnosis.risk_level == "CRITICAL"):
    raise RuntimeError("Assertion failed: diagnosis.risk_level == "CRITICAL"")
    if not (diagnosis.execution_allowed is False):
    raise RuntimeError("Assertion failed: diagnosis.execution_allowed is False")
    if not (diagnosis.dry_run is True):
    raise RuntimeError("Assertion failed: diagnosis.dry_run is True")
    if not (diagnosis.requires_human_review is True):
    raise RuntimeError("Assertion failed: diagnosis.requires_human_review is True")

    if not (():
    raise RuntimeError("Assertion failed: (")
        "NETWORK_STATE_OR_CONNECTIVITY_CHANGE"
        in diagnosis.probable_causes
    )

    if not (():
    raise RuntimeError("Assertion failed: (")
        "HARDWARE_INVENTORY_OR_STATE_CHANGE"
        in diagnosis.probable_causes
    )

    if not ("KEEP_RESPONSE_LOCKED" in diagnosis.recommendations):
    raise RuntimeError("Assertion failed: "KEEP_RESPONSE_LOCKED" in diagnosis.recommendations")
    if not (validate_diagnosis(diagnosis)):
    raise RuntimeError("Assertion failed: validate_diagnosis(diagnosis)")


def test_normal_diagnosis_remains_locked():
    diagnosis = diagnose_problem(
        {
            "categories": [],
            "correlated_score": 5.0,
        }
    )

    if not (diagnosis.problem_detected is False):
    raise RuntimeError("Assertion failed: diagnosis.problem_detected is False")
    if not (diagnosis.risk_level == "NORMAL"):
    raise RuntimeError("Assertion failed: diagnosis.risk_level == "NORMAL"")
    if not (diagnosis.execution_allowed is False):
    raise RuntimeError("Assertion failed: diagnosis.execution_allowed is False")
    if not (diagnosis_to_dict(diagnosis)["mode"] == "READ_ONLY"):
    raise RuntimeError("Assertion failed: diagnosis_to_dict(diagnosis)["mode"] == "READ_ONLY"")
    if not (validate_diagnosis(diagnosis)):
    raise RuntimeError("Assertion failed: validate_diagnosis(diagnosis)")
