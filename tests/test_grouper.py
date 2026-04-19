import pytest
from envdiff.grouper import group_keys, format_groups, GroupedKeys


def test_single_prefix():
    result = group_keys(["DB_HOST", "DB_PORT", "DB_NAME"])
    assert "DB" in result.groups
    assert sorted(result.groups["DB"]) == ["DB_HOST", "DB_NAME", "DB_PORT"]
    assert result.ungrouped == []


def test_multiple_prefixes():
    result = group_keys(["AWS_KEY", "AWS_SECRET", "APP_DEBUG", "APP_PORT"])
    assert set(result.groups.keys()) == {"AWS", "APP"}


def test_ungrouped_keys():
    result = group_keys(["PORT", "DEBUG", "DB_HOST"])
    assert "ungrouped" not in result.groups
    assert sorted(result.ungrouped) == ["DEBUG", "PORT"]
    assert "DB" in result.groups


def test_empty_input():
    result = group_keys([])
    assert result.groups == {}
    assert result.ungrouped == []


def test_all_ungrouped():
    result = group_keys(["HOST", "PORT", "DEBUG"])
    assert result.groups == {}
    assert sorted(result.ungrouped) == ["DEBUG", "HOST", "PORT"]


def test_custom_separator():
    result = group_keys(["db.host", "db.port", "app.debug"], sep=".")
    assert "db" in result.groups
    assert "app" in result.groups


def test_format_groups_contains_prefix():
    grouped = group_keys(["DB_HOST", "DB_PORT", "TIMEOUT"])
    output = format_groups(grouped)
    assert "[DB]" in output
    assert "DB_HOST" in output
    assert "[ungrouped]" in output
    assert "TIMEOUT" in output


def test_format_groups_empty():
    grouped = GroupedKeys()
    output = format_groups(grouped)
    assert output == ""


def test_keys_sorted_within_group():
    result = group_keys(["DB_Z", "DB_A", "DB_M"])
    assert result.groups["DB"] == ["DB_A", "DB_M", "DB_Z"]
