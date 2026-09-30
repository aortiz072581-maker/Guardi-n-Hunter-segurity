"""Adapt defensive hardware/network signals to Guardian Hunter findings.

This module only transforms already-collected defensive observations.
It performs no scanning, remediation, network modification or response.
"""

from __future__ import annotations

from typing import Any


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
RESPONSE_LOCKED = True


_SIGNAL_SCORES = {
    "HARDWARE_CHANGED": 55,
    "NEW_HARDWARE": 65,
    "NETWORK_INTERFACE_CHANGED": 55,
    "ROUTE_CHANGED": 70,
    "NEIGHBOR_TABLE_CHANGED": 45,
    "ADDRESS_CHANGED": 50,
}


def correlation_to_findings(
    correlation: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Convert correlation signals into risk-engine-compatible findings."""

    if not isinstance(correlation, dict):
        return []

    raw_signals = correlation.get("signals", [])
    if not isinstance(raw_signals, list):
        return []

    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    for raw_signal in raw_signals:
        signal = str(raw_signal).strip().upper()

        if not signal or signal in seen:
            continue

        seen.add(signal)

        score = _SIGNAL_SCORES.get(signal, 25)

        findings.append(
            {
                "category": "defensive_correlation",
                "title": signal,
                "score": score,
                "confidence": 1.0,
                "asset_criticality": 1.0,
                "exposure": 1.0,
                "evidence": (
                    "Observed by the local hardware/network "
                    "defensive correlation layer."
                ),
                "recommendation": "REVIEW_ONLY",
                "source": "hardware_network_correlation",
                "execution_allowed": False,
                "read_only": True,
                "dry_run": True,
            }
        )

    return findings


def build_defensive_risk_input(
    correlation: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a normalized, non-executing risk input."""

    correlation = correlation if isinstance(correlation, dict) else {}
    findings = correlation_to_findings(correlation)

    return {
        "findings": findings,
        "signal_count": len(findings),
        "correlator_risk_hint": correlation.get("risk_hint", "normal"),
        "execution_allowed": False,
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "response_locked": True,
    }


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "RESPONSE_LOCKED",
    "correlation_to_findings",
    "build_defensive_risk_input",
]
