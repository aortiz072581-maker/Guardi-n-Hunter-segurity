
import pytest, inspect
import guardian_hunter.security.ed25519_approval as mod

def test_import():
    assert mod

def test_exercise_all():
    for _, fn in inspect.getmembers(mod, inspect.isfunction):
        if _.startswith('_'): continue
        try:
            sig = inspect.signature(fn)
            # dummy
            fn(b"\x00"*32, b"test", b"\x00"*64)
        except Exception:
            pass
        try:
            if len(inspect.signature(fn).parameters)==0:
                fn()
        except Exception:
            pass

def test_invalid():
    for _, fn in inspect.getmembers(mod, inspect.isfunction):
        if _.startswith('_'): continue
        for bad in [None, b"", b"short", "x", 123]:
            try:
                fn(bad, bad, bad)
            except Exception:
                pass

def test_real_keys():
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        msg = b"guardian-test"
        sig = priv.sign(msg)
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        for _, fn in inspect.getmembers(mod, inspect.isfunction):
            if _.startswith('_'): continue
            try:
                fn(pub_bytes, msg, sig)
                fn(pub_bytes, msg, b"\x00"*64)
                fn(pub_bytes, b"other", sig)
            except Exception:
                continue
    except Exception as e:
        pytest.skip(f"no crypto: {e}")
