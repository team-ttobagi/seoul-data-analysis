import math

from backend.app.domain.analytics.service import _optional_float
from backend.app.external.gemini.client import _numeric_tokens


class FloatValue:
    def __float__(self) -> float:
        return 1.25


def test_optional_float_preserves_missing_nonfinite_and_unconvertible_values():
    assert _optional_float(None) is None
    assert _optional_float(float("nan")) is None
    assert _optional_float(float("inf")) is None
    assert _optional_float("NaN") is None
    assert _optional_float("-Infinity") is None
    assert _optional_float(10**10_000) is None
    assert _optional_float("not a number") is None
    assert _optional_float(object()) is None
    assert _optional_float(True) is None


def test_optional_float_narrows_supported_float_inputs():
    assert _optional_float("202.5") == 202.5
    assert _optional_float(b"202.5") == 202.5
    assert _optional_float(bytearray(b"202.5")) == 202.5
    assert _optional_float(FloatValue()) == 1.25


def test_numeric_tokens_preserves_empty_whitelist_for_invalid_values():
    assert _numeric_tokens(None) == set()
    assert _numeric_tokens(float("nan")) == set()
    assert _numeric_tokens(float("-inf")) == set()
    assert _numeric_tokens("NaN") == set()
    assert _numeric_tokens("Infinity") == set()
    assert _numeric_tokens(10**10_000) == set()
    assert _numeric_tokens("not a number") == set()
    assert _numeric_tokens(object()) == set()
    assert _numeric_tokens(False) == set()


def test_numeric_tokens_accepts_supported_float_inputs():
    tokens = _numeric_tokens("-12.5")

    assert "-12.5" in tokens
    assert "12.5" in tokens
    assert all(math.isfinite(float(token)) for token in tokens)
