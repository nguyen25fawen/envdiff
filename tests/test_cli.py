"""Tests for the CLI entry point."""
import textwrap
from pathlib import Path

import pytest

from envdiff.cli import main


@pytest.fixture()
def tmp_env(tmp_path):
    """Return a helper that writes a .env file and returns its Path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return p

    return _write


def test_no_differences_exits_zero(tmp_env):
    f1 = tmp_env("a.env", "KEY=value\n")
    f2 = tmp_env("b.env", "KEY=value\n")
    assert main([str(f1), str(f2)]) == 0


def test_missing_key_exits_one(tmp_env):
    f1 = tmp_env("a.env", "KEY=value\nEXTRA=x\n")
    f2 = tmp_env("b.env", "KEY=value\n")
    assert main([str(f1), str(f2)]) == 1


def test_value_mismatch_exits_one_with_flag(tmp_env):
    f1 = tmp_env("a.env", "KEY=foo\n")
    f2 = tmp_env("b.env", "KEY=bar\n")
    assert main([str(f1), str(f2), "--check-values"]) == 1


def test_value_mismatch_ignored_without_flag(tmp_env):
    f1 = tmp_env("a.env", "KEY=foo\n")
    f2 = tmp_env("b.env", "KEY=bar\n")
    assert main([str(f1), str(f2)]) == 0


def test_missing_file_exits_two(tmp_env, tmp_path):
    f1 = tmp_env("a.env", "KEY=value\n")
    missing = tmp_path / "ghost.env"
    assert main([str(f1), str(missing)]) == 2


def test_no_color_flag_accepted(tmp_env, capsys):
    f1 = tmp_env("a.env", "KEY=value\n")
    f2 = tmp_env("b.env", "KEY=value\n")
    rc = main([str(f1), str(f2), "--no-color"])
    assert rc == 0


def test_show_values_flag_accepted(tmp_env, capsys):
    f1 = tmp_env("a.env", "KEY=foo\n")
    f2 = tmp_env("b.env", "KEY=foo\n")
    rc = main([str(f1), str(f2), "--show-values"])
    assert rc == 0


def test_missing_key_output_contains_key_name(tmp_env, capsys):
    """Verify that the key name missing from one file appears in the output."""
    f1 = tmp_env("a.env", "KEY=value\nMISSING_KEY=x\n")
    f2 = tmp_env("b.env", "KEY=value\n")
    main([str(f1), str(f2)])
    captured = capsys.readouterr()
    assert "MISSING_KEY" in captured.out or "MISSING_KEY" in captured.err
