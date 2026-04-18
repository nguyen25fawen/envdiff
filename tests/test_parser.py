"""Tests for envdiff.parser."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, _strip_quotes


# ---------------------------------------------------------------------------
# _strip_quotes
# ---------------------------------------------------------------------------

def test_strip_double_quotes():
    assert _strip_quotes('"hello world"') == "hello world"


def test_strip_single_quotes():
    assert _strip_quotes("'hello'") == "hello"


def test_no_quotes_unchanged():
    assert _strip_quotes("plain") == "plain"


def test_mismatched_quotes_unchanged():
    assert _strip_quotes("'mixed\"") == "'mixed\""


# ---------------------------------------------------------------------------
# parse_env_file
# ---------------------------------------------------------------------------

def _write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return p


def test_basic_key_value(tmp_path):
    p = _write_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = parse_env_file(p)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_quoted_values(tmp_path):
    p = _write_env(tmp_path, 'KEY="spaced value"\nOTHER=\'single\'\n')
    result = parse_env_file(p)
    assert result["KEY"] == "spaced value"
    assert result["OTHER"] == "single"


def test_comments_and_blank_lines_ignored(tmp_path):
    content = "# comment\n\nFOO=1\n# another comment\nBAR=2\n"
    p = _write_env(tmp_path, content)
    result = parse_env_file(p)
    assert result == {"FOO": "1", "BAR": "2"}


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_invalid_line_raises(tmp_path):
    p = _write_env(tmp_path, "INVALID LINE\n")
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_file(p)


def test_empty_value(tmp_path):
    p = _write_env(tmp_path, "EMPTY=\n")
    result = parse_env_file(p)
    assert result["EMPTY"] == ""
