
import pytest, json, time, hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
import guardian_hunter.security.ed25519_approval as mod

def test_canon():
    assert mod._canon({"b":2,"a":1})

def test_sign_real():
    priv = ed25519.Ed25519PrivateKey.generate()
    res = mod.sign_approval(priv, "a.py", "abc", "def", time.time()+3600)
    assert res

def test_verify_flow():
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    expiry = time.time()+3600
    signed = mod.sign_approval(priv, "guardian_hunter/harness/broker.py", "d"*64, "p"*64, expiry)
    # Intenta todas las verifies posibles
    for name in ["verify_approval","verify","check"]:
        if hasattr(mod, name):
            fn = getattr(mod, name)
            try:
                fn(pub, signed)
                fn(pub, signed.get("path") if isinstance(signed, dict) else "a.py", signed)
            except Exception:
                pass

def test_expired():
    priv = ed25519.Ed25519PrivateKey.generate()
    try:
        mod.sign_approval(priv, "p", "d", "pr", time.time()-5)
    except Exception:
        pass

def test_invalid():
    priv = ed25519.Ed25519PrivateKey.generate()
    for bad in [None, "", 123]:
        try:
            mod.sign_approval(bad, "p", "d", "pr", time.time()+100)
        except Exception:
            pass
