"""Tests for envdiff.validator."""
import pytest

from envdiff.validator import ValidationResult, load_required_keys, validate


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------

def test_all_required_present():
    env = {"A": "1", "B": "2", "C": "3"}
    result = validate(env, required=["A", "B"])
    assert result.is_valid
    assert result.missing_required == []


def test_missing_required_key():
    env = {"A": "1"}
    result = validate(env, required=["A", "B"])
    assert not result.is_valid
    assert "B" in result.missing_required


def test_missing_keys_sorted():
    env = {}
    result = validate(env, required=["Z", "A", "M"])
    assert result.missing_required == ["A", "M", "Z"]


def test_strict_flags_unknown_keys():
    env = {"A": "1", "EXTRA": "x"}
    result = validate(env, required=["A"], strict=True)
    assert result.is_valid
    assert "EXTRA" in result.unknown_keys


def test_non_strict_ignores_unknown_keys():
    env = {"A": "1", "EXTRA": "x"}
    result = validate(env, required=["A"], strict=False)
    assert result.unknown_keys == []


def test_empty_env_all_missing():
    result = validate({}, required=["A", "B"])
    assert result.missing_required == ["A", "B"]


def test_empty_required_always_valid():
    result = validate({"A": "1"}, required=[])
    assert result.is_valid


# ---------------------------------------------------------------------------
# load_required_keys()
# ---------------------------------------------------------------------------

def _write_schema(tmp_path, content: str) -> str:
    p = tmp_path / "required.txt"
    p.write_text(content)
    return str(p)


def test_load_required_keys_basic(tmp_path):
    path = _write_schema(tmp_path, "DB_URL\nSECRET_KEY\nDEBUG\n")
    keys = load_required_keys(path)
    assert keys == ["DB_URL", "SECRET_KEY", "DEBUG"]


def test_load_skips_comments(tmp_path):
    path = _write_schema(tmp_path, "# comment\nDB_URL\n# another\nSECRET_KEY\n")
    keys = load_required_keys(path)
    assert keys == ["DB_URL", "SECRET_KEY"]


def test_load_skips_blank_lines(tmp_path):
    path = _write_schema(tmp_path, "DB_URL\n\nSECRET_KEY\n")
    keys = load_required_keys(path)
    assert keys == ["DB_URL", "SECRET_KEY"]


def test_load_empty_file(tmp_path):
    path = _write_schema(tmp_path, "")
    assert load_required_keys(path) == []
