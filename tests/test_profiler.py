"""Tests for envdiff.profiler."""
import textwrap
from pathlib import Path

import pytest

from envdiff.profiler import EnvProfile, format_profile, profile_env


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return p


def test_total_keys(tmp_path):
    f = _write(tmp_path, """
        FOO=bar
        BAZ=qux
    """)
    result = profile_env(f)
    assert result.total_keys == 2


def test_empty_value_detected(tmp_path):
    f = _write(tmp_path, """
        EMPTY=
        PRESENT=hello
    """)
    result = profile_env(f)
    assert "EMPTY" in result.empty_values
    assert "PRESENT" not in result.empty_values


def test_no_empty_values(tmp_path):
    f = _write(tmp_path, "KEY=value\n")
    result = profile_env(f)
    assert result.empty_values == []


def test_duplicate_key_detected(tmp_path):
    f = _write(tmp_path, """
        DUP=first
        DUP=second
        UNIQUE=only
    """)
    result = profile_env(f)
    assert "DUP" in result.duplicate_keys
    assert "UNIQUE" not in result.duplicate_keys


def test_no_duplicates(tmp_path):
    f = _write(tmp_path, "A=1\nB=2\n")
    result = profile_env(f)
    assert result.duplicate_keys == []


def test_longest_key(tmp_path):
    f = _write(tmp_path, """
        SHORT=x
        VERY_LONG_KEY_NAME=y
    """)
    result = profile_env(f)
    assert result.longest_key == "VERY_LONG_KEY_NAME"


def test_longest_value_key(tmp_path):
    f = _write(tmp_path, """
        A=short
        B=this_is_a_much_longer_value
    """)
    result = profile_env(f)
    assert result.longest_value_key == "B"


def test_format_profile_contains_path(tmp_path):
    f = _write(tmp_path, "X=1\n")
    profile = profile_env(f)
    output = format_profile(profile)
    assert str(f) in output


def test_format_profile_shows_key_count(tmp_path):
    f = _write(tmp_path, "A=1\nB=2\nC=3\n")
    profile = profile_env(f)
    output = format_profile(profile)
    assert "3" in output


def test_empty_file(tmp_path):
    f = _write(tmp_path, "")
    result = profile_env(f)
    assert result.total_keys == 0
    assert result.longest_key == ""
