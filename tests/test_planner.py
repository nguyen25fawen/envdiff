"""Tests for envdiff.planner."""
import pytest

from envdiff.planner import Plan, PlanAction, build_plan


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "localhost", "PORT": "3306"}


def test_missing_key_generates_add_action():
    plan = build_plan(BASE, TARGET)
    adds = plan.by_kind("add")
    assert any(a.key == "DEBUG" for a in adds)


def test_mismatched_value_generates_update_action():
    plan = build_plan(BASE, TARGET)
    updates = plan.by_kind("update")
    assert any(a.key == "PORT" for a in updates)
    update = next(a for a in updates if a.key == "PORT")
    assert update.current_value == "3306"
    assert update.desired_value == "5432"


def test_matching_key_generates_no_action():
    plan = build_plan(BASE, TARGET)
    all_keys = {a.key for a in plan.actions}
    assert "HOST" not in all_keys


def test_extra_key_ignored_when_remove_extra_false():
    target = {**TARGET, "EXTRA": "value"}
    plan = build_plan(BASE, target, remove_extra=False)
    removes = plan.by_kind("remove")
    assert removes == []


def test_extra_key_removed_when_remove_extra_true():
    target = {**TARGET, "EXTRA": "value"}
    plan = build_plan(BASE, target, remove_extra=True)
    removes = plan.by_kind("remove")
    assert any(a.key == "EXTRA" for a in removes)


def test_empty_base_and_target_is_empty_plan():
    plan = build_plan({}, {})
    assert plan.is_empty()


def test_identical_envs_produce_empty_plan():
    plan = build_plan(BASE, BASE)
    assert plan.is_empty()


def test_all_keys_missing_produces_only_add_actions():
    plan = build_plan(BASE, {})
    assert all(a.kind == "add" for a in plan.actions)
    assert len(plan.actions) == len(BASE)


def test_by_kind_filters_correctly():
    plan = build_plan(BASE, TARGET)
    assert all(a.kind == "add" for a in plan.by_kind("add"))
    assert all(a.kind == "update" for a in plan.by_kind("update"))
