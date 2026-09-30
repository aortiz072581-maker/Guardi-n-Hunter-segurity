from pathlib import Path

from guardian_hunter.evidence.persistence import (
    EvidenceStore,
    fail_closed,
    safety_invariants_hold,
)


def test_safety_invariants():
    assert safety_invariants_hold()


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

    assert result.state == "EVIDENCE_INTEGRITY_OK"
    assert result.records == 2
    assert not result.invalid_hash
    assert not result.invalid_chain
    assert not result.invalid_sequence
    assert fail_closed(result)


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

    assert result.state == "EVIDENCE_INTEGRITY_OK"
    assert result.records == 1
    assert fail_closed(result)


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

    assert result.state == "EVIDENCE_TAMPER_DETECTED"
    assert result.invalid_hash
    assert fail_closed(result)


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

    assert result.state == "EVIDENCE_TAMPER_DETECTED"
    assert result.invalid_chain or result.invalid_hash
    assert fail_closed(result)
