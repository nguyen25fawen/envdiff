"""Tests for envdiff.sorter."""

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiffs, group_diffs, sort_keys_by_severity


def _make_result(
    missing_in_second=None,
    missing_in_first=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_second=set(missing_in_second or []),
        missing_in_first=set(missing_in_first or []),
        mismatched=dict(mismatched or {}),
    )


def test_group_diffs_empty():
    result = _make_result()
    grouped = group_diffs(result)
    assert grouped.is_empty()
    assert grouped.all_keys() == []


def test_group_diffs_missing_in_second():
    result = _make_result(missing_in_second=["B", "A"])
    grouped = group_diffs(result)
    assert grouped.missing_in_second == ["A", "B"]
    assert grouped.missing_in_first == []
    assert grouped.mismatched == []


def test_group_diffs_missing_in_first():
    result = _make_result(missing_in_first=["Z", "M"])
    grouped = group_diffs(result)
    assert grouped.missing_in_first == ["M", "Z"]


def test_group_diffs_mismatched():
    result = _make_result(mismatched={"C": ("1", "2"), "A": ("x", "y")})
    grouped = group_diffs(result)
    assert grouped.mismatched == ["A", "C"]


def test_all_keys_deduplicates_and_sorts():
    grouped = GroupedDiffs(
        missing_in_second=["B", "A"],
        missing_in_first=["A", "C"],
        mismatched=["D"],
    )
    assert grouped.all_keys() == ["A", "B", "C", "D"]


def test_sort_keys_by_severity_ordering():
    result = _make_result(
        missing_in_second=["SEC"],
        missing_in_first=["FIRST"],
        mismatched={"MISMATCH": ("a", "b")},
    )
    ordered = sort_keys_by_severity(result)
    assert ordered.index("SEC") < ordered.index("FIRST")
    assert ordered.index("FIRST") < ordered.index("MISMATCH")


def test_sort_keys_by_severity_alpha_within_tier():
    result = _make_result(missing_in_second=["Z_KEY", "A_KEY", "M_KEY"])
    ordered = sort_keys_by_severity(result)
    assert ordered == ["A_KEY", "M_KEY", "Z_KEY"]


def test_sort_keys_by_severity_all_tiers_alpha_within_tier():
    """Keys within each severity tier should be sorted alphabetically."""
    result = _make_result(
        missing_in_second=["Z_SEC", "A_SEC"],
        missing_in_first=["Z_FIRST", "A_FIRST"],
        mismatched={"Z_MISMATCH": ("a", "b"), "A_MISMATCH": ("x", "y")},
    )
    ordered = sort_keys_by_severity(result)
    assert ordered == ["A_SEC", "Z_SEC", "A_FIRST", "Z_FIRST", "A_MISMATCH", "Z_MISMATCH"]


def test_is_empty_false_when_has_data():
    grouped = GroupedDiffs(mismatched=["KEY"])
    assert not grouped.is_empty()
