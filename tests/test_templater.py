"""Tests for envdiff.templater."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.templater import build_template, render_template, write_template


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_build_template_single_file(tmp_path):
    f = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    template, sources = build_template([f])
    assert list(template.keys()) == ["FOO", "BAZ"]
    assert all(v == "" for v in template.values())


def test_build_template_placeholder(tmp_path):
    f = _write(tmp_path, ".env", "KEY=value\n")
    template, _ = build_template([f], placeholder="CHANGE_ME")
    assert template["KEY"] == "CHANGE_ME"


def test_build_template_union_of_keys(tmp_path):
    a = _write(tmp_path, "a.env", "A=1\nB=2\n")
    b = _write(tmp_path, "b.env", "B=3\nC=4\n")
    template, sources = build_template([a, b])
    assert set(template.keys()) == {"A", "B", "C"}


def test_build_template_first_source_wins(tmp_path):
    a = _write(tmp_path, "a.env", "SHARED=1\n")
    b = _write(tmp_path, "b.env", "SHARED=2\n")
    _, sources = build_template([a, b])
    assert sources["SHARED"] == "a.env"


def test_render_template_contains_keys(tmp_path):
    f = _write(tmp_path, ".env", "FOO=bar\n")
    template, sources = build_template([f])
    text = render_template(template, sources)
    assert "FOO=" in text


def test_render_template_includes_source_comment(tmp_path):
    f = _write(tmp_path, "prod.env", "SECRET=x\n")
    template, sources = build_template([f])
    text = render_template(template, sources, include_source_comments=True)
    assert "# source: prod.env" in text


def test_render_template_no_source_comment(tmp_path):
    f = _write(tmp_path, "prod.env", "SECRET=x\n")
    template, sources = build_template([f])
    text = render_template(template, sources, include_source_comments=False)
    assert "# source" not in text


def test_write_template_creates_file(tmp_path):
    f = _write(tmp_path, ".env", "DB_URL=postgres\nPORT=5432\n")
    out = tmp_path / "output" / ".env.template"
    result = write_template([f], out)
    assert result == out
    assert out.exists()
    content = out.read_text()
    assert "DB_URL=" in content
    assert "PORT=" in content


def test_write_template_creates_parent_dirs(tmp_path):
    f = _write(tmp_path, ".env", "X=1\n")
    out = tmp_path / "deep" / "nested" / ".env.template"
    write_template([f], out)
    assert out.exists()
