"""Tests for envdiff.digest_formatter."""
from __future__ import annotations

from envdiff.digester import DigestEntry, DigestResult
from envdiff.digest_formatter import format_digest_rich, format_digest_summary


def _entry(path: str, checksum: str = "abc123", key_count: int = 3) -> DigestEntry:
    return DigestEntry(path=path, checksum=checksum, key_count=key_count)


def _result(*entries: DigestEntry, conflicts=None) -> DigestResult:
    return DigestResult(
        entries=list(entries),
        conflicts=conflicts if conflicts is not None else [],
    )


def test_rich_contains_header():
    r = _result(_entry("a.env"))
    out = format_digest_rich(r, color=False)
    assert "Digest" in out


def test_rich_shows_path():
    r = _result(_entry("production.env"))
    out = format_digest_rich(r, color=False)
    assert "production.env" in out


def test_rich_shows_key_count():
    r = _result(_entry("a.env", key_count=7))
    out = format_digest_rich(r, color=False)
    assert "7" in out


def test_rich_shows_short_checksum():
    r = _result(_entry("a.env", checksum="deadbeef1234567890"))
    out = format_digest_rich(r, color=False)
    assert "deadbeef1234" in out


def test_rich_no_files_message():
    r = _result()
    out = format_digest_rich(r, color=False)
    assert "No files" in out


def test_summary_all_match():
    e = _entry("a.env", checksum="same")
    f = _entry("b.env", checksum="same")
    r = _result(e, f)
    out = format_digest_summary(r, color=False)
    assert "same" in out.lower() or "share" in out.lower()


def test_summary_conflict_count():
    e = _entry("a.env", checksum="aaa")
    f = _entry("b.env", checksum="bbb")
    r = DigestResult(entries=[e, f], conflicts=["b.env"])
    out = format_digest_summary(r, color=False)
    assert "1" in out
    assert "2" in out


def test_summary_no_color_no_escape():
    r = _result(_entry("x.env"))
    out = format_digest_summary(r, color=False)
    assert "\033[" not in out
