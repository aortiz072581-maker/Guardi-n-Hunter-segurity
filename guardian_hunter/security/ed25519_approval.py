
"""Firmas Ed25519 para aprobaciones: ruta + hash diff + hash previo + expiracion"""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import json, time, hashlib

def _canon(d): return json.dumps(d, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()

def sign_approval(private_key: ed25519.Ed25519PrivateKey, path: str, diff_hash: str, prev_hash: str, expiry: float):
    payload = {"path": path, "diff": diff_hash, "prev": prev_hash, "exp": expiry}
    sig = private_key.sign(_canon(payload))
    return payload, sig.hex()

def verify_approval(pub_key: ed25519.Ed25519PublicKey, payload: dict, sig_hex: str) -> bool:
    if payload.get("exp", 0) < time.time(): return False
    try:
        pub_key.verify(bytes.fromhex(sig_hex), _canon(payload))
        return True
    except Exception:
        return False

def gen_keypair():
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub
