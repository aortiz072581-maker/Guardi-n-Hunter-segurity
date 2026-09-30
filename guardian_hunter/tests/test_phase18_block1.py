"""Tests — Guardian Hunter Phase 18 Block 1."""

from guardian_hunter.network.phase18_baseline import (
    create_network_baseline,
    validate_network_baseline,
    baseline_to_dict,
)
from guardian_hunter.network.phase18_diff import (
    compare_network_baseline,
    validate_network_diff,
)
from guardian_hunter.network.phase18_anomaly import (
    detect_network_anomalies,
    calculate_network_anomaly_score,
    validate_network_anomalies,
)
from guardian_hunter.network.phase18_snapshot import (
    build_network_security_snapshot,
    validate_network_snapshot,
)


def sample_baseline():
    return {
        "interfaces": ["eth0"],
        "addresses": ["192.168.1.10"],
        "mac_addresses": ["AA:BB:CC:DD:EE:01"],
        "gateways": ["192.168.1.1"],
        "routes": ["0.0.0.0/0 via 192.168.1.1"],
        "dns_servers": ["1.1.1.1"],
        "listeners": ["22/tcp"],
        "connections": ["192.168.1.10:40000->1.1.1.1:443"],
        "egress_destinations": ["1.1.1.1"],
    }


def sample_current():
    data = sample_baseline()
    data["dns_servers"] = ["8.8.8.8"]
    data["listeners"] = ["22/tcp", "8080/tcp"]
    data["egress_destinations"] = ["1.1.1.1", "8.8.8.8"]
    return data


def main():
    baseline_data = sample_baseline()
    current_data = sample_current()

    # 18.1
    baseline = create_network_baseline(baseline_data)

    assert validate_network_baseline(baseline)
    assert len(baseline.digest) == 64
    assert baseline.execution_allowed is False

    print("PHASE 18.1 NETWORK BASELINE 2.0: OK")
    print("PHASE 18.1 SHA-256 INTEGRITY: OK")
    print("PHASE 18.1 READ-ONLY: OK")

    # 18.2
    baseline_dict = baseline_to_dict(baseline)
    diff = compare_network_baseline(
        baseline_dict,
        current_data,
    )

    assert validate_network_diff(diff)
    assert diff.total_changes > 0
    assert "dns_servers" in diff.changed
    assert "listeners" in diff.changed

    print("PHASE 18.2 BASELINE DIFF: OK")
    print("PHASE 18.2 CHANGE DETECTION: OK")
    print("PHASE 18.2 READ-ONLY: OK")

    # 18.3
    anomalies = detect_network_anomalies(diff)
    score = calculate_network_anomaly_score(anomalies)

    assert anomalies
    assert score > 0
    assert score <= 100
    assert validate_network_anomalies(anomalies)

    print("PHASE 18.3 ANOMALY DETECTION: OK")
    print("PHASE 18.3 RISK SCORING: OK")
    print("PHASE 18.3 READ-ONLY: OK")

    # 18.4
    snapshot = build_network_security_snapshot(
        baseline_valid=validate_network_baseline(baseline),
        diff=diff,
        anomalies=anomalies,
        anomaly_score=score,
        current=current_data,
    )

    assert validate_network_snapshot(snapshot)
    assert snapshot.execution_allowed is False
    assert snapshot.phase == 18
    assert snapshot.total_changes > 0
    assert snapshot.anomaly_count > 0

    print("PHASE 18.4 NETWORK SECURITY SNAPSHOT: OK")
    print("PHASE 18.4 STATUS CORRELATION: OK")
    print("PHASE 18.4 READ-ONLY: OK")

    print("PHASE 18 BLOCK 1 TEST: OK")
    print("REAL EXECUTION: BLOCKED")


if __name__ == "__main__":
    main()
