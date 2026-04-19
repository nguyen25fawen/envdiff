"""Tests for envdiff.interpolator."""
import pytest
from envdiff.interpolator import interpolate, _refs, InterpolationResult


def test_refs_dollar_brace():
    assert _refs("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_refs_plain_dollar():
    assert _refs("$USER") == ["USER"]


def test_refs_no_interpolation():
    assert _refs("plain_value") == []


def test_simple():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = interpolate(env)
    assert result.resolved["URL"] == "http://localhost/api"


def test_chained_resolution():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate(env)
    assert result.resolved["B"] == "hello_world"
    assert result.resolved["C"] == "hello_world!"


def test_missing_ref_unresolved():
    env = {"URL": "http://${MISSING_HOST}/path"}
    result = interpolate(env)
    assert "URL" in result.unresolved
    assert "MISSING_HOST" in result.unresolved["URL"]


def test_no_interpolation_key_still_resolved():
    env = {"PLAIN": "value"}
    result = interpolate(env)
    assert result.resolved["PLAIN"] == "value"
    assert "PLAIN" not in result.references


def test_references_tracked():
    env = {"BASE": "x", "DERIVED": "${BASE}_y"}
    result = interpolate(env)
    assert "DERIVED" in result.references
    assert "BASE" in result.references["DERIVED"]


def test_multiple_missing_refs():
    env = {"CONN": "${USER}:${PASS}@${HOST}"}
    result = interpolate(env)
    assert set(result.unresolved["CONN"]) == {"USER", "PASS", "HOST"}


def test_self_reference_is_unresolved():
    env = {"A": "${A}"}
    result = interpolate(env)
    assert "A" in result.unresolved
