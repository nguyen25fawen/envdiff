"""Tests for envdiff.linter."""
from pathlib import Path
import pytest
from envdiff.linter import lint_file, LintIssue


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_file(tmp_path):
    p = _write(tmp_path, ".env", "KEY=value\nOTHER=123\n")
    result = lint_file(p)
    assert result.is_clean


def test_duplicate_key_is_error(tmp_path):
    p = _write(tmp_path, ".env", "KEY=a\nKEY=b\n")
    result = lint_file(p)
    assert not result.is_clean
    assert len(result.errors) == 1
    assert "Duplicate" in result.errors[0].message
    assert result.errors[0].key == "KEY"


def test_empty_value_is_warning(tmp_path):
    p = _write(tmp_path, ".env", "KEY=\n")
    result = lint_file(p)
    assert result.is_clean is False
    assert len(result.warnings) == 1
    assert "empty value" in result.warnings[0].message


def test_invalid_line_no_equals(tmp_path):
    p = _write(tmp_path, ".env", "BADLINE\n")
    result = lint_file(p)
    errors = result.errors
    assert len(errors) == 1
    assert "no '='" in errors[0].message
    assert errors[0].key is None


def test_comments_and_blanks_ignored(tmp_path):
    p = _write(tmp_path, ".env", "# comment\n\nKEY=val\n")
    result = lint_file(p)
    assert result.is_clean


def test_empty_key_is_error(tmp_path):
    p = _write(tmp_path, ".env", "=value\n")
    result = lint_file(p)
    assert any(i.message == "Empty key name" for i in result.errors)


def test_duplicate_reports_first_line_number(tmp_path):
    p = _write(tmp_path, ".env", "A=1\nB=2\nA=3\n")
    result = lint_file(p)
    issue = result.errors[0]
    assert "line 1" in issue.message
    assert issue.line_number == 3


def test_multiple_issues_collected(tmp_path):
    p = _write(tmp_path, ".env", "KEY=\nKEY=\nBAD\n")
    result = lint_file(p)
    assert len(result.issues) >= 3
