"""Tests for envdiff.differ_lens."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_lens import LensRule, apply_lens, load_lens_rules


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _diff(
    missing_second=None,
    missing_first=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_second=missing_second or [],
        missing_in_first=missing_first or [],
        mismatched=mismatched or {},
    )


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "lens.cfg"
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# load_lens_rules
# ---------------------------------------------------------------------------

def test_load_single_lens(tmp_path):
    p = _write(tmp_path, """
        [database]
        DB_*
        DATABASE_URL
    """)
    rules = load_lens_rules(str(p))
    assert len(rules) == 1
    assert rules[0].name == "database"
    assert "DB_*" in rules[0].patterns
    assert "DATABASE_URL" in rules[0].patterns


def test_load_multiple_lenses(tmp_path):
    p = _write(tmp_path, """
        [auth]
        SECRET_*
        TOKEN_*

        [infra]
        AWS_*
    """)
    rules = load_lens_rules(str(p))
    assert len(rules) == 2
    assert rules[0].name == "auth"
    assert rules[1].name == "infra"


def test_load_ignores_comments_and_blank_lines(tmp_path):
    p = _write(tmp_path, """
        # top comment
        [myapp]
        # inline comment
        APP_*

        ANOTHER_KEY
    """)
    rules = load_lens_rules(str(p))
    assert rules[0].patterns == ["APP_*", "ANOTHER_KEY"]


# ---------------------------------------------------------------------------
# apply_lens
# ---------------------------------------------------------------------------

def test_apply_lens_filters_missing_in_second():
    diff = _diff(missing_second=["DB_HOST", "APP_NAME"])
    lens = LensRule(name="db", patterns=["DB_*"])
    result = apply_lens(diff, lens)
    assert "DB_HOST" in result.focused.missing_in_second
    assert "APP_NAME" not in result.focused.missing_in_second


def test_apply_lens_filters_missing_in_first():
    diff = _diff(missing_first=["SECRET_KEY", "PORT"])
    lens = LensRule(name="secrets", patterns=["SECRET_*"])
    result = apply_lens(diff, lens)
    assert result.focused.missing_in_first == ["SECRET_KEY"]


def test_apply_lens_filters_mismatched():
    diff = _diff(mismatched={"DB_PASS": ("a", "b"), "LOG_LEVEL": ("info", "debug")})
    lens = LensRule(name="db", patterns=["DB_*"])
    result = apply_lens(diff, lens)
    assert "DB_PASS" in result.focused.mismatched
    assert "LOG_LEVEL" not in result.focused.mismatched


def test_apply_lens_matched_keys_count():
    diff = _diff(
        missing_second=["DB_HOST"],
        mismatched={"DB_PASS": ("x", "y")},
    )
    lens = LensRule(name="db", patterns=["DB_*"])
    result = apply_lens(diff, lens)
    assert result.matched_keys == 2


def test_apply_lens_total_keys_count():
    diff = _diff(
        missing_second=["DB_HOST", "APP_NAME"],
        mismatched={"LOG_LEVEL": ("a", "b")},
    )
    lens = LensRule(name="db", patterns=["DB_*"])
    result = apply_lens(diff, lens)
    assert result.total_keys == 3


def test_apply_lens_no_match_returns_empty_focused():
    diff = _diff(missing_second=["APP_NAME"])
    lens = LensRule(name="db", patterns=["DB_*"])
    result = apply_lens(diff, lens)
    assert result.matched_keys == 0
    assert result.focused.missing_in_second == []


def test_apply_lens_exact_key_pattern():
    diff = _diff(missing_second=["DATABASE_URL", "DATABASE_PORT"])
    lens = LensRule(name="url", patterns=["DATABASE_URL"])
    result = apply_lens(diff, lens)
    assert result.focused.missing_in_second == ["DATABASE_URL"]
