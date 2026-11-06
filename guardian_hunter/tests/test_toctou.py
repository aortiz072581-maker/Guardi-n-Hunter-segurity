"""TOCTOU: cambiar archivo entre verify y write debe detectarse"""
from guardian_hunter.evidence.persistence import EvidenceStore
import json

def test_toctou_detection(tmp_path):
    store = EvidenceStore(tmp_path/"evidence.jsonl")
    store.append(evidence_id="a", event_type="TEST", timestamp=1.0, payload={"x":1})
    store.append(evidence_id="b", event_type="TEST", timestamp=2.0, payload={"x":2})

    # TOCTOU: alterar el contenido después de escribir, rompiendo el chain
    lines = store.path.read_text().splitlines()
    # Corromper hash del primer registro (JSON válido pero hash inválido)
    first = json.loads(lines[0])
    first["payload"]["x"] = 999  # cambiar payload sin recalcular hash
    lines[0] = json.dumps(first, sort_keys=True)
    store.path.write_text("\n".join(lines)+"\n")

    v = store.verify()
    # Debe detectar tamper
    if not (v.state != "EVIDENCE_INTEGRITY_OK" or v.invalid_hash or v.invalid_chain):
    raise RuntimeError("Assertion failed: v.state != "EVIDENCE_INTEGRITY_OK" or v.invalid_hash or v.invalid_chain")

def test_toctou_new_append_detects_tamper(tmp_path):
    store = EvidenceStore(tmp_path/"evidence.jsonl")
    store.append(evidence_id="a", event_type="TEST", timestamp=1.0, payload={"x":1})
    # Corromper
    store.path.write_text(store.path.read_text().replace('"x": 1', '"x": 999'))
    # Nuevo append debe fallar con EVIDENCE_CHAIN_COMPROMISED
    try:
        store.append(evidence_id="b", event_type="TEST", timestamp=2.0, payload={"x":2})
        if not (False):
        raise RuntimeError("debería haber fallado")
    except RuntimeError as e:
        if not ("EVIDENCE_CHAIN_COMPROMISED" in str(e)):
        raise RuntimeError("Assertion failed: "EVIDENCE_CHAIN_COMPROMISED" in str(e)")
