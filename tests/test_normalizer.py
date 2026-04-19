"""Tests for envdiff.normalizer."""
import pytest
from envdiff.normalizer import (
    normalize,
    normalize_keys,
    normalize_values,
    format_normalize_result,
)


def test_normalize_keys_strips_whitespace():
    env = {" KEY ": "value"}
    result = normalize_keys(env)
    assert "KEY" in result.normalized
    assert result.changes


def test_normalize_keys_no_change_when_clean():
    env = {"KEY": "value"}
    result = normalize_keys(env)
    assert result.normalized == {"KEY": "value"}
    assert result.changes == []


def test_normalize_keys_uppercase():
    env = {"key": "val"}
    result = normalize_keys(env, lowercase=True)
    assert "KEY" in result.normalized


def test_normalize_values_strips_whitespace():
    env = {"KEY": "  hello  "}
    result = normalize_values(env)
    assert result.normalized["KEY"] == "hello"
    assert result.changes


def test_normalize_values_no_change_when_clean():
    env = {"KEY": "hello"}
    result = normalize_values(env)
    assert result.normalized["KEY"] == "hello"
    assert result.changes == []


def test_normalize_values_skip_strip():
    env = {"KEY": "  spaced  "}
    result = normalize_values(env, strip_whitespace=False)
    assert result.normalized["KEY"] == "  spaced  "
    assert result.changes == []


def test_normalize_combines_both():
    env = {" key ": "  val  "}
    result = normalize(env, uppercase_keys=True, strip_values=True)
    assert "KEY" in result.normalized
    assert result.normalized["KEY"] == "val"
    assert len(result.changes) == 2


def test_normalize_original_unchanged():
    env = {" KEY ": "  val  "}
    result = normalize(env)
    assert result.original is env


def test_format_no_changes():
    env = {"KEY": "val"}
    result = normalize(env)
    out = format_normalize_result(result)
    assert "No normalization" in out


def test_format_with_changes():
    env = {" KEY ": "  val  "}
    result = normalize(env)
    out = format_normalize_result(result)
    assert "Normalization changes:" in out
    assert "•" in out
