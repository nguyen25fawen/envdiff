"""Tests for envdiff.stacker and envdiff.stack_formatter."""
import os
import pytest
from pathlib import Path
from envdiff.stacker import stack_envs, format_stack
from envdiff.stack_formatter import format_stack_rich, format_stack_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_stack_single_file(tmp_path):
    f = _write(tmp_path, "a.env", "KEY=hello\nOTHER=world\n")
    result = stack_envs([f])
    assert result.winning_value("KEY") == "hello"
    assert result.winning_value("OTHER") == "world"


def test_first_wins_by_default(tmp_path):
    f1 = _write(tmp_path, "base.env", "KEY=base\n")
    f2 = _write(tmp_path, "override.env", "KEY=override\n")
    result = stack_envs([f1, f2])
    assert result.winning_value("KEY") == "base"


def test_last_wins_flag(tmp_path):
    f1 = _write(tmp_path, "base.env", "KEY=base\n")
    f2 = _write(tmp_path, "override.env", "KEY=override\n")
    result = stack_envs([f1, f2], last_wins=True)
    assert result.winning_value("KEY") == "override"


def test_union_of_keys(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\n")
    f2 = _write(tmp_path, "b.env", "B=2\n")
    result = stack_envs([f1, f2])
    assert set(result.all_keys()) == {"A", "B"}


def test_override_tracked(tmp_path):
    f1 = _write(tmp_path, "base.env", "KEY=base\n")
    f2 = _write(tmp_path, "prod.env", "KEY=prod\n")
    result = stack_envs([f1, f2])
    assert result.was_overridden("KEY")
    sources = [src for src, _ in result.entries["KEY"].overridden_by]
    assert any("prod.env" in s for s in sources)


def test_no_override_when_unique(tmp_path):
    f1 = _write(tmp_path, "a.env", "ONLY=here\n")
    f2 = _write(tmp_path, "b.env", "OTHER=there\n")
    result = stack_envs([f1, f2])
    assert not result.was_overridden("ONLY")


def test_format_stack_plain(tmp_path):
    f1 = _write(tmp_path, "a.env", "X=1\n")
    result = stack_envs([f1])
    out = format_stack(result)
    assert "X=1" in out


def test_format_stack_rich_contains_key(tmp_path):
    f1 = _write(tmp_path, "a.env", "FOO=bar\n")
    result = stack_envs([f1])
    out = format_stack_rich(result)
    assert "FOO" in out
    assert "bar" in out


def test_format_stack_summary_counts(tmp_path):
    f1 = _write(tmp_path, "a.env", "A=1\nB=2\n")
    f2 = _write(tmp_path, "b.env", "A=99\n")
    result = stack_envs([f1, f2])
    summary = format_stack_summary(result)
    assert "2 layers" in summary
    assert "2 keys" in summary
    assert "1 overridden" in summary


def test_empty_stack_message(tmp_path):
    f = _write(tmp_path, "empty.env", "")
    result = stack_envs([f])
    out = format_stack_rich(result)
    assert "No keys" in out
