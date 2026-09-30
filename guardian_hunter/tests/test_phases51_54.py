from guardian_hunter.governance.phase51_control_snapshot import (
    build_control_snapshot,
    validate_control_snapshot,
)

from guardian_hunter.verification.phase52_integrity_chain import (
    build_integrity_chain,
    validate_integrity_chain,
)

from guardian_hunter.governance.phase53_state_gate import (
    build_state_gate,
    validate_state_gate,
)

from guardian_hunter.governance.phase54_continuity import (
    build_continuity,
    validate_continuity,
)


def test_phase51():
    snapshot = build_control_snapshot()
    assert snapshot.controls_valid is True
    assert validate_control_snapshot(snapshot) is True


def test_phase52():
    chain = build_integrity_chain("control-digest")
    assert chain.chain_valid is True
    assert chain.execution_blocked is True
    assert validate_integrity_chain(chain) is True


def test_phase53():
    gate = build_state_gate(
        "MONITORING",
        "ENHANCED_MONITORING",
    )
    assert gate.transition_allowed is True
    assert gate.execution_blocked is True
    assert validate_state_gate(gate) is True


def test_phase54():
    continuity = build_continuity(
        True,
        True,
        True,
        True,
    )
    assert continuity.continuity_score == 100
    assert continuity.release_state == "CONTINUITY_READY"
    assert continuity.execution_blocked is True
    assert validate_continuity(continuity) is True


if __name__ == "__main__":
    test_phase51()
    test_phase52()
    test_phase53()
    test_phase54()

    print("PHASE 51: OK")
    print("PHASE 52: OK")
    print("PHASE 53: OK")
    print("PHASE 54: OK")
    print("51 → 54 TEST: OK")
