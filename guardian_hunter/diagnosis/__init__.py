"""Defensive problem diagnosis and remediation recommendations."""

from .engine import (
    ProblemDiagnosis,
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)

__all__ = [
    "ProblemDiagnosis",
    "diagnose_problem",
    "diagnosis_to_dict",
    "validate_diagnosis",
]
