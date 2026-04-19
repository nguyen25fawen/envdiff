import pytest
from envdiff.renamer import detect_renames, RenameCandidate


def _base():
    return {"DB_HOST": "localhost", "DB_PASS": "secret", "OLD_KEY": "val"}


def _target():
    return {"DB_HOST": "localhost", "DB_PASSWORD": "secret", "NEW_KEY": "other"}


def test_confirmed_rename_detected():
    result = detect_renames(_base(), _target())
    assert any(c.old_key == "DB_PASS" and c.new_key == "DB_PASSWORD" for c in result.confirmed)


def test_unmatched_old_when_no_value_match():
    result = detect_renames(_base(), _target())
    assert "OLD_KEY" in result.unmatched_old


def test_unmatched_new_when_no_value_match():
    result = detect_renames(_base(), _target())
    assert "NEW_KEY" in result.unmatched_new


def test_no_renames_identical_dicts():
    d = {"A": "1", "B": "2"}
    result = detect_renames(d, d)
    assert result.confirmed == []
    assert result.unmatched_old == []
    assert result.unmatched_new == []


def test_ambiguous_value_not_confirmed():
    base = {"X": "same"}
    target = {"Y": "same", "Z": "same"}
    result = detect_renames(base, target)
    assert result.confirmed == []
    assert "X" in result.unmatched_old


def test_multiple_renames():
    base = {"A": "1", "B": "2"}
    target = {"AA": "1", "BB": "2"}
    result = detect_renames(base, target)
    assert len(result.confirmed) == 2
    keys = {(c.old_key, c.new_key) for c in result.confirmed}
    assert ("A", "AA") in keys
    assert ("B", "BB") in keys


def test_rename_candidate_value_preserved():
    base = {"OLD": "myvalue"}
    target = {"NEW": "myvalue"}
    result = detect_renames(base, target)
    assert result.confirmed[0].value == "myvalue"
