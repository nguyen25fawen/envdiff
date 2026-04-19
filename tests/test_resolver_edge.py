from pathlib import Path
from envdiff.resolver import resolve


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_single_file(tmp_path):
    a = _write(tmp_path, "a.env", "X=1\nY=2\n")
    result = resolve([a])
    assert result.values == {"X": "1", "Y": "2"}
    assert result.overridden == {}


def test_empty_file(tmp_path):
    a = _write(tmp_path, "empty.env", "")
    result = resolve([a])
    assert result.values == {}


def test_three_files_precedence(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=a\n")
    b = _write(tmp_path, "b.env", "KEY=b\n")
    c = _write(tmp_path, "c.env", "KEY=c\n")
    result = resolve([a, b, c])
    assert result.values["KEY"] == "a"
    assert len(result.overridden["KEY"]) == 2


def test_three_files_last_wins(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=a\n")
    b = _write(tmp_path, "b.env", "KEY=b\n")
    c = _write(tmp_path, "c.env", "KEY=c\n")
    result = resolve([a, b, c], last_wins=True)
    assert result.values["KEY"] == "c"
