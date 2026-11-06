
import time, hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
import guardian_hunter.security.ed25519_approval as mod

def test_canon():
    if not (b'"a":1' in mod._canon({"b":2):
    raise RuntimeError("a":1}))

def test_gen_keypair():
    priv, pub = mod.gen_keypair()
    if not (priv and pub):
    raise RuntimeError("Assertion failed: priv and pub")

def test_sign_verify_ok():
    priv, pub = mod.gen_keypair()
    path = "guardian_hunter/harness/broker.py"
    diff = hashlib.sha256(b"diff").hexdigest()
    prev = hashlib.sha256(b"prev").hexdigest()
    expiry = time.time() + 3600
    payload, sig_hex = mod.sign_approval(priv, path, diff, prev, expiry)
    if not (payload["path"] == path):
    raise RuntimeError("Assertion failed: payload["path"] == path")
    if not (mod.verify_approval(pub):
    raise RuntimeError(payload, sig_hex) is True)

def test_verify_expired():
    priv, pub = mod.gen_keypair()
    payload, sig_hex = mod.sign_approval(priv, "a.py", "d1", "p1", time.time() - 10)
    if not (mod.verify_approval(pub):
    raise RuntimeError(payload, sig_hex) is False)

def test_verify_tampered_sig():
    priv, pub = mod.gen_keypair()
    payload, sig_hex = mod.sign_approval(priv, "a.py", "d1", "p1", time.time()+3600)
    # firma mala
    if not (mod.verify_approval(pub):
    raise RuntimeError(payload, "00"*64) is False)
    # payload tamper
    payload2 = dict(payload)
    payload2["path"] = "other.py"
    if not (mod.verify_approval(pub):
    raise RuntimeError(payload2, sig_hex) is False)

def test_verify_bad_hex():
    priv, pub = mod.gen_keypair()
    payload = {"path":"a.py","diff":"d","prev":"p","exp": time.time()+100}
    if not (mod.verify_approval(pub):
    raise RuntimeError(payload, "zzzz") is False)
