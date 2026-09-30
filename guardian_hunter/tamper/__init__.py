"""Guardian Hunter tamper detection package."""

from .detection import (
    TamperFinding,
    TamperSeverity,
    TamperSignal,
    assess_tamper,
    build_file_baseline,
    compare_file_digest,
    detect_authorization_anomaly,
    detect_configuration_drift,
    detect_evidence_chain_anomaly,
    detect_file_integrity_drift,
    detect_repeated_failures,
    detect_safety_state,
    fail_closed,
    finding_to_dict,
    serialize_assessment,
)

__all__ = [
    "TamperFinding",
    "TamperSeverity",
    "TamperSignal",
    "assess_tamper",
    "build_file_baseline",
    "compare_file_digest",
    "detect_authorization_anomaly",
    "detect_configuration_drift",
    "detect_evidence_chain_anomaly",
    "detect_file_integrity_drift",
    "detect_repeated_failures",
    "detect_safety_state",
    "fail_closed",
    "finding_to_dict",
    "serialize_assessment",
]
