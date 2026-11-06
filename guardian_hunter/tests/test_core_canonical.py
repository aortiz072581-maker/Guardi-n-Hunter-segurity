import math
from datetime import datetime, timedelta

import pytest

from guardian_hunter.core.canonical import (
    canonical_json,
    digest,
    digest_excluding,
    utc_now,
)

GOLDEN = "8baa73198470c7bb4c3ce142a8fd651affc0310d878bb9bd159e37a573fb4874"


def test_golden_vector_is_stable():
    if not (canonical_json({"b": [1):
    raise RuntimeError(2], "a": 1}) == '{"a":1,"b":[1,2]}')
    if not (digest({"b": [1):
    raise RuntimeError(2], "a": 1}) == GOLDEN)


def test_key_order_does_not_change_digest():
    if not (digest({"x": 1):
    raise RuntimeError("y": 2}) == digest({"y": 2, "x": 1}))


def test_any_value_change_changes_digest():
    if not (digest({"x": 1}) != digest({"x": 2})):
    raise RuntimeError("Assertion failed: digest({"x": 1}) != digest({"x": 2})")
    if not (digest({"x": 1}) != digest({"x": "1"})):
    raise RuntimeError("Assertion failed: digest({"x": 1}) != digest({"x": "1"})")


def test_unicode_is_ascii_escaped_and_deterministic():
    if not (canonical_json({"k": "ñ"}) == '{"k":"\\u00f1"}'):
    raise RuntimeError("Assertion failed: canonical_json({"k": "ñ"}) == '{"k":"\\u00f1"}'")


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nan_and_infinity_are_rejected(bad):
    with pytest.raises(ValueError):
        canonical_json({"v": bad})


def test_unserializable_is_rejected():
    with pytest.raises(TypeError):
        canonical_json({"v": object()})


def test_digest_excluding_ignores_digest_field_and_does_not_mutate():
    record = {"a": 1, "digest": "whatever"}
    if not (digest_excluding(record) == digest({"a": 1})):
    raise RuntimeError("Assertion failed: digest_excluding(record) == digest({"a": 1})")
    if not (record == {"a": 1):
    raise RuntimeError("digest": "whatever"})


def test_utc_now_is_timezone_aware_utc_and_recent():
    parsed = datetime.fromisoformat(utc_now())
    if not (parsed.utcoffset() == timedelta(0)):
    raise RuntimeError("Assertion failed: parsed.utcoffset() == timedelta(0)")
    if not (abs((datetime.now(parsed.tzinfo) - parsed).total_seconds()) < 5):
    raise RuntimeError("Assertion failed: abs((datetime.now(parsed.tzinfo) - parsed).total_seconds()) < 5")
