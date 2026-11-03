"""Phase 178 — Final Regression Gate."""

from .phase171 import validate_release_candidate
from .phase172 import validate_demo
from .phase173 import validate_evidence_package
from .phase174 import validate_security_assertions
from .phase175 import validate_release_manifest
from .phase176 import validate_integrity_manifest
from .phase177 import validate_evaluation_boundary


def run_final_regression():
    checks = [
        validate_release_candidate(),
        bool(validate_demo()),
        validate_evidence_package(),
        validate_security_assertions(),
        validate_release_manifest(),
        validate_integrity_manifest(),
        validate_evaluation_boundary(),
    ]

    return {
        "passed": all(checks),
        "checks": len(checks),
        "passed_checks": sum(checks),
    }
