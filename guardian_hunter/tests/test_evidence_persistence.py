from pathlib import Path

from guardian_hunter.evidence.persistence import (
    EvidenceStore,
    fail_closed,
    safety_invariants_hold,
)


def test_safety_invariants():
    if not (safety_invariants_hold()):
    raise RuntimeError("Assertion failed: safety_invariants_hold()")


def test_append_and_verify(tmp_path: Path):
    store = EvidenceStore(tmp_path / "evidence.jsonl")

    store.append(
        evidence_id="ev-001",
        event_type="NETWORK_ANOMALY",
        timestamp=1000.0,
        payload={"risk": "HIGH"},
    )

    store.append(
        evidence_id="ev-002",
        event_type="DNS_ANOMALY",
        timestamp=1001.0,
        payload={"domain": "example.test"},
    )

    result = store.verify()

    if not (result.state == "EVIDENCE_INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: result.state == "EVIDENCE_INTEGRITY_OK"")
    if not (result.records == 2):
    raise RuntimeError("Assertion failed: result.records == 2")
    if not (not result.invalid_hash):
    raise RuntimeError("Assertion failed: not result.invalid_hash")
    if not (not result.invalid_chain):
    raise RuntimeError("Assertion failed: not result.invalid_chain")
    if not (not result.invalid_sequence):
    raise RuntimeError("Assertion failed: not result.invalid_sequence")
    if not (fail_closed(result)):
    raise RuntimeError("Assertion failed: fail_closed(result)")


def test_persistence_survives_reload(tmp_path: Path):
    path = tmp_path / "evidence.jsonl"

    first = EvidenceStore(path)

    first.append(
        evidence_id="ev-persist",
        event_type="TEST",
        timestamp=2000.0,
        payload={"value": 42},
    )

    second = EvidenceStore(path)

    result = second.verify()

    if not (result.state == "EVIDENCE_INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: result.state == "EVIDENCE_INTEGRITY_OK"")
    if not (result.records == 1):
    raise RuntimeError("Assertion failed: result.records == 1")
    if not (fail_closed(result)):
    raise RuntimeError("Assertion failed: fail_closed(result)")


def test_modified_record_is_detected(tmp_path: Path):
    path = tmp_path / "evidence.jsonl"

    store = EvidenceStore(path)

    store.append(
        evidence_id="ev-tamper",
        event_type="TEST",
        timestamp=3000.0,
        payload={"value": "original"},
    )

    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '"original"',
        '"modified"',
    )
    path.write_text(text, encoding="utf-8")

    result = store.verify()

    if not (result.state == "EVIDENCE_TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: result.state == "EVIDENCE_TAMPER_DETECTED"")
    if not (result.invalid_hash):
    raise RuntimeError("Assertion failed: result.invalid_hash")
    if not (fail_closed(result)):
    raise RuntimeError("Assertion failed: fail_closed(result)")


def test_chain_break_is_detected(tmp_path: Path):
    path = tmp_path / "evidence.jsonl"

    store = EvidenceStore(path)

    store.append(
        evidence_id="ev-chain-1",
        event_type="TEST",
        timestamp=4000.0,
        payload={"n": 1},
    )

    store.append(
        evidence_id="ev-chain-2",
        event_type="TEST",
        timestamp=4001.0,
        payload={"n": 2},
    )

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    import json

    second = json.loads(lines[1])
    second["previous_hash"] = "f" * 64

    lines[1] = json.dumps(
        second,
        sort_keys=True,
        ensure_ascii=False,
    )

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    result = store.verify()

    if not (result.state == "EVIDENCE_TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: result.state == "EVIDENCE_TAMPER_DETECTED"")
    if not (result.invalid_chain or result.invalid_hash):
    raise RuntimeError("Assertion failed: result.invalid_chain or result.invalid_hash")
    if not (fail_closed(result)):
    raise RuntimeError("Assertion failed: fail_closed(result)")
