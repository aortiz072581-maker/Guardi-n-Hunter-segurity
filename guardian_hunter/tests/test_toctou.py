
"""TOCTOU: cambiar archivo entre verify y write debe fallar"""
import tempfile, pathlib, os
from guardian_hunter.evidence.persistence import EvidenceStore
def test_toctou_detection(tmp_path):
    store = EvidenceStore(tmp_path/"evidence.jsonl")
    rec = store.append(evidence_id="a", event_type="TEST", timestamp=1.0, payload={"x":1})
    # Simular cambio externo entre lectura y escritura - debe detectarse por cadena
    # Corromper archivo manualmente
    with open(store.path, "a") as f:
        f.write("{corrupted}\n")
    v = store.verify()
    assert v.state != "EVIDENCE_INTEGRITY_OK"
