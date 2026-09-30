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

    assert diagnosis.problem_detected is True
    assert diagnosis.risk_level == "CRITICAL"
    assert diagnosis.execution_allowed is False
    assert diagnosis.dry_run is True
    assert diagnosis.requires_human_review is True

    assert (
        "NETWORK_STATE_OR_CONNECTIVITY_CHANGE"
        in diagnosis.probable_causes
    )

    assert (
        "HARDWARE_INVENTORY_OR_STATE_CHANGE"
        in diagnosis.probable_causes
    )

    assert "KEEP_RESPONSE_LOCKED" in diagnosis.recommendations
    assert validate_diagnosis(diagnosis)


def test_normal_diagnosis_remains_locked():
    diagnosis = diagnose_problem(
        {
            "categories": [],
            "correlated_score": 5.0,
        }
    )

    assert diagnosis.problem_detected is False
    assert diagnosis.risk_level == "NORMAL"
    assert diagnosis.execution_allowed is False
    assert diagnosis_to_dict(diagnosis)["mode"] == "READ_ONLY"
    assert validate_diagnosis(diagnosis)
