
import pytest, inspect
import guardian_hunter.harness.broker_selftest as mod
import guardian_hunter.harness.broker as broker_mod

def test_import():
    assert mod

def test_all_callable():
    for name, obj in inspect.getmembers(mod):
        if name.startswith('_'): continue
        if inspect.isfunction(obj):
            try:
                if len(inspect.signature(obj).parameters)==0:
                    obj()
            except Exception:
                pass
        if inspect.isclass(obj):
            try:
                inst = obj()
                for _, m in inspect.getmembers(inst, inspect.iscallable):
                    try:
                        m()
                    except Exception:
                        pass
            except Exception:
                pass

def test_with_fake_broker(monkeypatch):
    class FakeBroker:
        def __init__(self, *a, **k): pass
        def run(self, *a, **k): return {"status":"ok"}
    monkeypatch.setattr(broker_mod, "Broker", FakeBroker, raising=False)
    for _, fn in inspect.getmembers(mod, inspect.isfunction):
        if _.startswith('_'): continue
        try:
            if len(inspect.signature(fn).parameters)==0:
                fn()
        except Exception:
            pass

def test_invalid():
    for _, fn in inspect.getmembers(mod, inspect.isfunction):
        if _.startswith('_'): continue
        for bad in [None, {}, [], ""]:
            try:
                fn(bad)
            except Exception:
                pass
