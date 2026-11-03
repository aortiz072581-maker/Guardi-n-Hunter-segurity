"""Validation tests for Phase 18.9 → 18.12."""

from guardian_hunter.network.phase18_correlation import (
    READ_ONLY as CORR_READ_ONLY,
    DRY_RUN as CORR_DRY_RUN,
    EXECUTION_ALLOWED as CORR_EXECUTION_ALLOWED,
    correlate_hardware_network,
    validate_hardware_network_correlation,
)

from guardian_hunter.network.phase18_risk import (
    READ_ONLY as RISK_READ_ONLY,
    DRY_RUN as RISK_DRY_RUN,
    EXECUTION_ALLOWED as RISK_EXECUTION_ALLOWED,
    calculate_network_risk,
    validate_network_risk,
)

from guardian_hunter.network.phase18_evidence import (
    READ_ONLY as EVIDENCE_READ_ONLY,
    DRY_RUN as EVIDENCE_DRY_RUN,
    EXECUTION_ALLOWED as EVIDENCE_EXECUTION_ALLOWED,
    build_network_evidence,
    validate_network_evidence,
)

from guardian_hunter.network.phase18_integration import (
    READ_ONLY as INTEGRATION_READ_ONLY,
    DRY_RUN as INTEGRATION_DRY_RUN,
    EXECUTION_ALLOWED as INTEGRATION_EXECUTION_ALLOWED,
    build_network_defense_integration,
    validate_network_defense_integration,
)


HARDWARE = [
    {
        "interface": "eth0",
        "mac": "AA:BB:CC:DD:EE:01",
        "name": "adapter0",
    },
    {
        "interface": "wlan0",
        "mac": "AA:BB:CC:DD:EE:02",
        "name": "adapter1",
    },
]

NETWORK = [
    {
        "interface": "eth0",
        "mac": "AA:BB:CC:DD:EE:01",
        "address": "192.168.1.10",
    },
    {
        "interface": "wlan1",
        "mac": "AA:BB:CC:DD:EE:03",
        "address": "192.168.1.20",
    },
]


def main():
    # --------------------------------------------------
    # 18.9
    # --------------------------------------------------

    correlation = correlate_hardware_network(
        HARDWARE,
        NETWORK,
    )

    assert validate_hardware_network_correlation(
        correlation
    )

    assert correlation.correlation_count == 1
    assert len(correlation.unmatched_hardware) == 1
    assert len(correlation.unmatched_network) == 1

    print(
        "PHASE 18.9 HARDWARE/NETWORK CORRELATION: OK"
    )
    print(
        "PHASE 18.9 MATCH/UNMATCHED ANALYSIS: OK"
    )
    print(
        "PHASE 18.9 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.10
    # --------------------------------------------------

    risk = calculate_network_risk(
        baseline_anomaly_score=30,
        dns_score=20,
        listener_score=40,
        connection_score=35,
        correlation_score=25,
    )

    assert validate_network_risk(risk)
    assert 0 <= risk.total_score <= 100
    assert risk.risk_level in {
        "NORMAL",
        "WATCH",
        "HIGH",
        "CRITICAL",
    }

    print(
        "PHASE 18.10 NETWORK RISK SCORING: OK"
    )
    print(
        "PHASE 18.10 RISK LEVEL: OK"
    )
    print(
        "PHASE 18.10 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.11
    # --------------------------------------------------

    evidence = build_network_evidence(
        {
            "correlation": {
                "matched": correlation.correlation_count
            },
            "risk": {
                "score": risk.total_score
            },
        },
        evidence_type="NETWORK_SECURITY",
        source_phase="18",
    )

    assert validate_network_evidence(evidence)
    assert evidence.evidence_count == 1
    assert len(evidence.digest) == 64
    assert evidence.evidence_id.startswith(
        "NET-EVIDENCE-"
    )

    print(
        "PHASE 18.11 NETWORK EVIDENCE: OK"
    )
    print(
        "PHASE 18.11 SHA-256 INTEGRITY: OK"
    )
    print(
        "PHASE 18.11 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # 18.12
    # --------------------------------------------------

    integration = build_network_defense_integration(
        baseline={"phase": "18.1"},
        diff={"phase": "18.2"},
        anomalies={"phase": "18.3"},
        dns={"phase": "18.5"},
        listeners={"phase": "18.6"},
        connections={"phase": "18.7"},
        timeline={"phase": "18.8"},
        correlation=correlation,
        risk=risk,
        evidence=evidence,
    )

    assert validate_network_defense_integration(
        integration
    )

    assert (
        integration.integration_status
        == "INTEGRATED_READ_ONLY"
    )

    assert len(integration.integrity_digest) == 64

    print(
        "PHASE 18.12 NETWORK DEFENSE INTEGRATION: OK"
    )
    print(
        "PHASE 18.12 INTEGRITY GATE: OK"
    )
    print(
        "PHASE 18.12 READ-ONLY: OK"
    )

    # --------------------------------------------------
    # GLOBAL SAFETY
    # --------------------------------------------------

    assert all(
        (
            CORR_READ_ONLY,
            RISK_READ_ONLY,
            EVIDENCE_READ_ONLY,
            INTEGRATION_READ_ONLY,
        )
    )

    assert all(
        (
            CORR_DRY_RUN,
            RISK_DRY_RUN,
            EVIDENCE_DRY_RUN,
            INTEGRATION_DRY_RUN,
        )
    )

    assert all(
        value is False
        for value in (
            CORR_EXECUTION_ALLOWED,
            RISK_EXECUTION_ALLOWED,
            EVIDENCE_EXECUTION_ALLOWED,
            INTEGRATION_EXECUTION_ALLOWED,
        )
    )

    print(
        "PHASE 18 BLOCK 3 TEST: OK"
    )
    print(
        "READ_ONLY: TRUE"
    )
    print(
        "DRY_RUN: TRUE"
    )
    print(
        "REAL EXECUTION: BLOCKED"
    )


if __name__ == "__main__":
    main()
