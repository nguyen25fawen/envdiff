"""Tests for envdiff.trimmer."""
from pathlib import Path

import pytest

from envdiff.trimmer import TrimResult, trim_env, trim_files, render_trimmed, write_trimmed


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_trim_env_keeps_matching_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    ref = {"A": "x", "C": "y"}
    result = trim_env(env, ref)
    assert result.kept == {"A": "1", "C": "3"}


def test_trim_env_removes_extra_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    ref = {"A": "x"}
    result = trim_env(env, ref)
    assert sorted(result.removed) == ["B", "C"]


def test_trim_env_removed_sorted():
    env = {"Z": "1", "M": "2", "A": "3"}
    ref = {}
    result = trim_env(env, ref)
    assert result.removed == ["A", "M", "Z"]


def test_any_removed_true_when_keys_dropped():
    result = trim_env({"A": "1", "B": "2"}, {"A": "x"})
    assert result.any_removed is True


def test_any_removed_false_when_nothing_dropped():
    result = trim_env({"A": "1"}, {"A": "x", "B": "y"})
    assert result.any_removed is False


def test_trim_env_empty_target():
    result = trim_env({}, {"A": "1"})
    assert result.kept == {}
    assert result.removed == []


def test_trim_files(tmp_path):
    target = _write(tmp_path, ".env.target", "A=1\nB=2\nC=3\n")
    ref = _write(tmp_path, ".env.ref", "A=x\nC=y\n")
    result = trim_files(target, ref)
    assert "A" in result.kept
    assert "C" in result.kept
    assert "B" in result.removed


def test_trim_files_missing_target(tmp_path):
    """trim_files should raise FileNotFoundError when the target file does not exist."""
    target = tmp_path / ".env.missing"
    ref = _write(tmp_path, ".env.ref", "A=x\n")
    with pytest.raises(FileNotFoundError):
        trim_files(target, ref)


def test_trim_files_missing_ref(tmp_path):
    """trim_files should raise FileNotFoundError when the reference file does not exist."""
    target = _write(tmp_path, ".env.target", "A=1\n")
    ref = tmp_path / ".env.missing"
    with pytest.raises(FileNotFoundError):
        trim_files(target, ref)


def test_render_trimmed_format():
    result = TrimResult(kept={"FOO": "bar", "BAZ": "qux"})
    text = render_trimmed(result)
    assert "FOO=bar" in text
    assert "BAZ=qux" in text


def test_render_trimmed_empty():
    result = TrimResult(kept={})
    assert render_trimmed(result) == ""


def test_write_trimmed_creates_file(tmp_path):
    dest = tmp_path / "out" / ".env"
    result = TrimResult(kept={"X": "1"})
    write_trimmed(result, dest)
    assert dest.exists()
    assert "X=1" in dest.read_text()


def test_write_trimmed_creates_parents(tmp_path):
    dest = tmp_path / "deep" / "nested" / ".env"
    write_trimmed(TrimResult(kept={"K": "v"}), dest)
    assert dest.exists()
