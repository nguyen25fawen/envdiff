"""Tests for envdiff.annotator."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.annotator import annotate_lines, annotate_file, write_annotated
from envdiff.comparator import DiffResult


def _diff(
    missing_in_second=None,
    missing_in_first=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_second=missing_in_second or {},
        missing_in_first=missing_in_first or {},
        mismatched=mismatched or {},
    )


LINES = [
    "# comment",
    "KEY_A=hello",
    "KEY_B=world",
    "KEY_C=foo",
    "",
]


def test_missing_in_second_annotated():
    diff = _diff(missing_in_second={"KEY_A": "hello"})
    result = annotate_lines(LINES, diff)
    assert any("missing in target" in l for l in result)


def test_missing_in_first_annotated():
    diff = _diff(missing_in_first={"KEY_B": "world"})
    result = annotate_lines(LINES, diff)
    assert any("missing in base" in l for l in result)


def test_mismatch_annotated():
    diff = _diff(mismatched={"KEY_C": ("foo", "bar")})
    result = annotate_lines(LINES, diff)
    assert any("value mismatch" in l for l in result)


def test_clean_key_no_annotation_by_default():
    diff = _diff()
    result = annotate_lines(LINES, diff)
    assert not any("envdiff" in l for l in result)


def test_annotate_ok_flag():
    diff = _diff()
    result = annotate_lines(LINES, diff, annotate_ok=True)
    assert any("ok" in l for l in result)


def test_comments_and_blanks_unchanged():
    diff = _diff()
    result = annotate_lines(LINES, diff)
    assert result[0] == "# comment"
    assert result[4] == ""


def test_annotate_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("KEY_A=hello\nKEY_B=world\n")
    diff = _diff(missing_in_second={"KEY_A": "hello"})
    text = annotate_file(env, diff)
    assert "missing in target" in text
    assert "KEY_B=world" in text


def test_write_annotated_creates_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("KEY_A=val\n")
    out = tmp_path / "out" / "annotated.env"
    diff = _diff(mismatched={"KEY_A": ("val", "other")})
    write_annotated(env, diff, out)
    assert out.exists()
    assert "value mismatch" in out.read_text()
