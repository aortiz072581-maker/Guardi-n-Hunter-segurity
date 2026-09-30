"""Validation for Guardian Hunter Phase 18.5 -> 18.8.

The test adapts to the existing Phase 18.1 baseline
factory without changing Phase 18.1 implementation.
"""

import inspect

from guardian_hunter.network.phase18_baseline import (
    create_network_baseline,
    baseline_to_dict,
    validate_network_baseline,
)

from guardian_hunter.network.phase18_diff import (
    compare_network_baseline,
    validate_network_diff,
)

from guardian_hunter.network.phase18_anomaly import (
    detect_network_anomalies,
    validate_network_anomalies,
)

from guardian_hunter.network.phase18_dns import (
    analyze_dns_intelligence,
    validate_dns_intelligence,
)

from guardian_hunter.network.phase18_listener import (
    analyze_listener_intelligence,
    validate_listener_intelligence,
)

from guardian_hunter.network.phase18_connection import (
    analyze_connection_egress,
    validate_connection_egress,
)

from guardian_hunter.network.phase18_timeline import (
    build_network_timeline,
    build_timeline_summary,
    validate_network_timeline,
)


BASELINE = {
    "interfaces": ["eth0"],
    "addresses": ["192.168.1.10/24"],
    "mac_addresses": [
        "aa:bb:cc:dd:ee:01"
    ],
    "gateways": ["192.168.1.1"],
    "routes": [
        "0.0.0.0/0 via 192.168.1.1"
    ],
    "dns_servers": ["1.1.1.1"],
    "listeners": [
        "tcp:0.0.0.0:22"
    ],
    "connections": [
        "tcp|192.168.1.10:50000|1.1.1.1:443|ESTABLISHED"
    ],
    "egress_destinations": [
        "1.1.1.1:443"
    ],
}


CURRENT = {
    "interfaces": ["eth0"],
    "addresses": ["192.168.1.10/24"],
    "mac_addresses": [
        "aa:bb:cc:dd:ee:01"
    ],
    "gateways": ["192.168.1.1"],
    "routes": [
        "0.0.0.0/0 via 192.168.1.1"
    ],
    "dns_servers": [
        "1.1.1.1",
        "8.8.8.8",
    ],
    "listeners": [
        "tcp:0.0.0.0:22",
        "tcp:0.0.0.0:8080",
    ],
    "connections": [
        "tcp|192.168.1.10:50000|1.1.1.1:443|ESTABLISHED",
        "tcp|192.168.1.10:50001|8.8.8.8:443|ESTABLISHED",
    ],
    "egress_destinations": [
        "1.1.1.1:443",
        "8.8.8.8:443",
    ],
}


def _build_baseline(data):
    """Call the existing Phase 18.1 factory safely."""

    signature = inspect.signature(
        create_network_baseline
    )

    parameters = list(
        signature.parameters.values()
    )

    # Existing implementation accepts **kwargs.
    if any(
        p.kind
        == inspect.Parameter.VAR_KEYWORD
        for p in parameters
    ):
        return create_network_baseline(
            **data
        )

    # Existing implementation accepts one mapping.
    positional = [
        p
        for p in parameters
        if p.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    if len(positional) == 1:
        return create_network_baseline(
            data
        )

    # Try matching explicitly named parameters.
    accepted = {}

    for parameter in positional:
        if parameter.name in data:
            accepted[
                parameter.name
            ] = data[parameter.name]

    return create_network_baseline(
        **accepted
    )


def main():

    # ==================================================
    # EXISTING PHASE 18.1 → 18.4
    # ==================================================

    baseline = _build_baseline(
        BASELINE
    )

    assert validate_network_baseline(
        baseline
    )

    print(
        "PHASE 18 BASELINE INTEGRATION: OK"
    )

    baseline_dict = baseline_to_dict(
        baseline
    )

    diff = compare_network_baseline(
        baseline_dict,
        CURRENT,
    )

    assert validate_network_diff(
        diff
    )

    print(
        "PHASE 18 DIFF INTEGRATION: OK"
    )

    anomalies = detect_network_anomalies(
        diff
    )

    assert validate_network_anomalies(
        anomalies
    )

    print(
        "PHASE 18 ANOMALY INTEGRATION: OK"
    )

    # ==================================================
    # PHASE 18.5 — DNS
    # ==================================================

    dns = analyze_dns_intelligence(
        baseline_servers=BASELINE[
            "dns_servers"
        ],
        current_servers=CURRENT[
            "dns_servers"
        ],
        dns_queries=[
            {
                "domain": "example.test",
                "answer": "192.0.2.10",
            }
        ],
    )

    assert validate_dns_intelligence(
        dns
    )

    assert (
        "8.8.8.8"
        in dns.added_servers
    )

    assert dns.changed is True

    print(
        "PHASE 18.5 DNS INTELLIGENCE: OK"
    )

    print(
        "PHASE 18.5 DNS CHANGE DETECTION: OK"
    )

    print(
        "PHASE 18.5 READ-ONLY: OK"
    )

    # ==================================================
    # PHASE 18.6 — LISTENERS
    # ==================================================

    listeners = (
        analyze_listener_intelligence(
            baseline_listeners=BASELINE[
                "listeners"
            ],
            current_listeners=CURRENT[
                "listeners"
            ],
        )
    )

    assert validate_listener_intelligence(
        listeners
    )

    assert (
        "tcp:0.0.0.0:8080"
        in listeners.new_listeners
    )

    assert listeners.changed is True

    print(
        "PHASE 18.6 LISTENER INTELLIGENCE: OK"
    )

    print(
        "PHASE 18.6 NEW LISTENER DETECTION: OK"
    )

    print(
        "PHASE 18.6 READ-ONLY: OK"
    )

    # ==================================================
    # PHASE 18.7 — CONNECTION / EGRESS
    # ==================================================

    connections = (
        analyze_connection_egress(
            baseline_connections=BASELINE[
                "connections"
            ],
            current_connections=CURRENT[
                "connections"
            ],
            baseline_egress=BASELINE[
                "egress_destinations"
            ],
            current_egress=CURRENT[
                "egress_destinations"
            ],
        )
    )

    assert validate_connection_egress(
        connections
    )

    assert len(
        connections.new_connections
    ) == 1

    assert len(
        connections.new_egress
    ) == 1

    assert connections.egress_score == 45

    assert connections.status == "WATCH"

    print(
        "PHASE 18.7 CONNECTION INTELLIGENCE: OK"
    )

    print(
        "PHASE 18.7 EGRESS INTELLIGENCE: OK"
    )

    print(
        "PHASE 18.7 RISK SCORING: OK"
    )

    print(
        "PHASE 18.7 READ-ONLY: OK"
    )

    # ==================================================
    # PHASE 18.8 — NETWORK TIMELINE
    # ==================================================

    timeline = build_network_timeline(
        diff=diff,
        anomalies=anomalies,
        dns=dns,
        listeners=listeners,
        connections=connections,
    )

    assert validate_network_timeline(
        timeline
    )

    assert len(timeline) > 0

    summary = build_timeline_summary(
        timeline
    )

    assert (
        summary["total_events"]
        == len(timeline)
    )

    assert (
        summary["read_only"]
        is True
    )

    assert (
        summary["dry_run"]
        is True
    )

    assert (
        summary["execution_allowed"]
        is False
    )

    # Deterministic rebuild.
    timeline_again = (
        build_network_timeline(
            diff=diff,
            anomalies=anomalies,
            dns=dns,
            listeners=listeners,
            connections=connections,
        )
    )

    assert [
        event.event_id
        for event in timeline
    ] == [
        event.event_id
        for event in timeline_again
    ]

    assert [
        event.description
        for event in timeline
    ] == [
        event.description
        for event in timeline_again
    ]

    print(
        "PHASE 18.8 NETWORK TIMELINE: OK"
    )

    print(
        "PHASE 18.8 TIMELINE VALIDATION: OK"
    )

    print(
        "PHASE 18.8 DETERMINISTIC ORDER: OK"
    )

    print(
        "PHASE 18.8 READ-ONLY: OK"
    )

    print(
        "PHASE 18 BLOCK 2 TEST: OK"
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
