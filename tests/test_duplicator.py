import pytest
from pathlib import Path
from envdiff.duplicator import find_duplicates, has_duplicates, format_duplicate_result


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_duplicates(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "BAZ=3\n")
    result = find_duplicates([a, b])
    assert not has_duplicates(result)
    assert result.duplicates == {}


def test_single_duplicate(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=99\nBAZ=3\n")
    result = find_duplicates([a, b])
    assert has_duplicates(result)
    assert "FOO" in result.duplicates
    assert len(result.duplicates["FOO"]) == 2


def test_multiple_duplicates(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_path, "b.env", "FOO=9\nBAR=8\n")
    result = find_duplicates([a, b])
    assert "FOO" in result.duplicates
    assert "BAR" in result.duplicates


def test_duplicate_across_three_files(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")
    c = _write(tmp_path, "c.env", "KEY=3\n")
    result = find_duplicates([a, b, c])
    assert len(result.duplicates["KEY"]) == 3


def test_all_files_recorded(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\n")
    b = _write(tmp_path, "b.env", "Y=2\n")
    result = find_duplicates([a, b])
    assert len(result.all_files) == 2


def test_format_no_duplicates(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\n")
    result = find_duplicates([a])
    out = format_duplicate_result(result, color=False)
    assert "No duplicate" in out


def test_format_shows_duplicate_key(tmp_path):
    a = _write(tmp_path, "a.env", "FOO=1\n")
    b = _write(tmp_path, "b.env", "FOO=2\n")
    result = find_duplicates([a, b])
    out = format_duplicate_result(result, color=False)
    assert "FOO" in out
    assert "defined in" in out
