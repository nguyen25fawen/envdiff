import os
import pytest
from pathlib import Path
from envdiff.resolver import resolve, format_resolved


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_first_file_wins_by_default(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=from_a\nONLY_A=1\n")
    b = _write(tmp_path, "b.env", "KEY=from_b\nONLY_B=2\n")
    result = resolve([a, b])
    assert result.values["KEY"] == "from_a"


def test_last_wins_flag(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=from_a\n")
    b = _write(tmp_path, "b.env", "KEY=from_b\n")
    result = resolve([a, b], last_wins=True)
    assert result.values["KEY"] == "from_b"


def test_union_of_keys(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    b = _write(tmp_path, "b.env", "B=2\n")
    result = resolve([a, b])
    assert "A" in result.values
    assert "B" in result.values


def test_sources_tracked(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=val\n")
    b = _write(tmp_path, "b.env", "OTHER=x\n")
    result = resolve([a, b])
    assert result.sources["KEY"] == a
    assert result.sources["OTHER"] == b


def test_overridden_recorded(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=first\n")
    b = _write(tmp_path, "b.env", "KEY=second\n")
    result = resolve([a, b])
    assert "KEY" in result.overridden
    shadowed = result.overridden["KEY"]
    assert any(v == "second" for _, v in shadowed)


def test_format_resolved_basic(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    result = resolve([a])
    output = format_resolved(result)
    assert "FOO=bar" in output


def test_format_resolved_show_sources(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=bar\n")
    result = resolve([a])
    output = format_resolved(result, show_sources=True)
    assert "# from" in output


def test_format_resolved_shows_shadowed(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=first\n")
    b = _write(tmp_path, "b.env", "KEY=second\n")
    result = resolve([a, b])
    output = format_resolved(result, show_sources=True)
    assert "shadowed" in output
