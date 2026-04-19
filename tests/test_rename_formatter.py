import pytest
from envdiff.renamer import RenameResult, RenameCandidate
from envdiff.rename_formatter import format_rename_result


def _empty():
    return RenameResult()


def _with_rename():
    return RenameResult(
        confirmed=[RenameCandidate("OLD", "NEW", "val")],
        unmatched_old=[],
        unmatched_new=[],
    )


def _full():
    return RenameResult(
        confirmed=[RenameCandidate("A", "AA", "1")],
        unmatched_old=["GONE"],
        unmatched_new=["FRESH"],
    )


def test_empty_result_message():
    out = format_rename_result(_empty(), color=False)
    assert "No rename candidates" in out


def test_confirmed_rename_shown():
    out = format_rename_result(_with_rename(), color=False)
    assert "OLD" in out
    assert "NEW" in out


def test_unmatched_old_shown():
    out = format_rename_result(_full(), color=False)
    assert "GONE" in out


def test_unmatched_new_shown():
    out = format_rename_result(_full(), color=False)
    assert "FRESH" in out


def test_color_output_contains_escape():
    out = format_rename_result(_with_rename(), color=True)
    assert "\033[" in out


def test_no_color_no_escape():
    out = format_rename_result(_full(), color=False)
    assert "\033[" not in out
