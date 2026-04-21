"""Tests for envdiff.baseline."""
import pytest
from pathlib import Path

from envdiff.baseline import compare_against_base, BaselineResult


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_differences_when_identical(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\nBAZ=qux\n")
    target = _write(tmp_path, "target.env", "FOO=bar\nBAZ=qux\n")
    result = compare_against_base(base, [target])
    assert not result.any_differences()


def test_missing_in_target_detected(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\nMISSING=x\n")
    target = _write(tmp_path, "target.env", "FOO=bar\n")
    result = compare_against_base(base, [target])
    assert result.any_differences()
    diff = result.comparisons[target]
    assert "MISSING" in diff.missing_in_target


def test_missing_in_base_detected(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    target = _write(tmp_path, "target.env", "FOO=bar\nEXTRA=val\n")
    result = compare_against_base(base, [target])
    assert result.any_differences()
    diff = result.comparisons[target]
    assert "EXTRA" in diff.missing_in_base


def test_value_mismatch_with_check_values(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    target = _write(tmp_path, "target.env", "FOO=different\n")
    result = compare_against_base(base, [target], check_values=True)
    assert result.any_differences()
    diff = result.comparisons[target]
    assert "FOO" in diff.mismatched


def test_multiple_targets(tmp_path):
    base = _write(tmp_path, "base.env", "A=1\nB=2\n")
    ok = _write(tmp_path, "ok.env", "A=1\nB=2\n")
    bad = _write(tmp_path, "bad.env", "A=1\n")
    result = compare_against_base(base, [ok, bad])
    assert result.any_differences()
    assert ok in result.clean_targets()
    assert bad in result.targets_with_issues()


def test_targets_with_issues_and_clean_targets(tmp_path):
    base = _write(tmp_path, "base.env", "X=1\n")
    clean = _write(tmp_path, "clean.env", "X=1\n")
    broken = _write(tmp_path, "broken.env", "Y=2\n")
    result = compare_against_base(base, [clean, broken])
    assert clean in result.clean_targets()
    assert broken in result.targets_with_issues()


def test_empty_target_list(tmp_path):
    base = _write(tmp_path, "base.env", "FOO=bar\n")
    result = compare_against_base(base, [])
    assert isinstance(result, BaselineResult)
    assert not result.any_differences()
    assert result.comparisons == {}
