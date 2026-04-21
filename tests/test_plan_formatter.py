"""Tests for envdiff.plan_formatter."""
import pytest

from envdiff.planner import Plan, PlanAction, build_plan
from envdiff.plan_formatter import format_plan, format_plan_summary


def _action(kind, key, current=None, desired=None):
    return PlanAction(kind=kind, key=key, current_value=current, desired_value=desired)


def test_empty_plan_shows_no_changes_message():
    plan = Plan(actions=[])
    output = format_plan(plan)
    assert "No changes" in output


def test_add_action_appears_in_output():
    plan = Plan(actions=[_action("add", "NEW_KEY", desired="value")])
    output = format_plan(plan)
    assert "NEW_KEY" in output
    assert "ADD" in output


def test_remove_action_appears_in_output():
    plan = Plan(actions=[_action("remove", "OLD_KEY", current="old")])
    output = format_plan(plan)
    assert "OLD_KEY" in output
    assert "REMOVE" in output


def test_update_action_appears_in_output():
    plan = Plan(actions=[_action("update", "PORT", current="3306", desired="5432")])
    output = format_plan(plan)
    assert "PORT" in output
    assert "UPDATE" in output


def test_values_masked_by_default():
    plan = Plan(actions=[_action("add", "SECRET", desired="supersecret")])
    output = format_plan(plan)
    assert "supersecret" not in output
    assert "***" in output


def test_values_shown_when_unmasked():
    plan = Plan(actions=[_action("add", "KEY", desired="plaintext")])
    output = format_plan(plan, mask_values=False)
    assert "plaintext" in output


def test_summary_empty_plan():
    plan = Plan(actions=[])
    summary = format_plan_summary(plan)
    assert "nothing" in summary.lower()


def test_summary_counts_actions():
    plan = Plan(actions=[
        _action("add", "A", desired="1"),
        _action("add", "B", desired="2"),
        _action("update", "C", current="x", desired="y"),
    ])
    summary = format_plan_summary(plan)
    assert "2 to add" in summary
    assert "1 to update" in summary


def test_summary_shows_removes():
    plan = Plan(actions=[_action("remove", "OLD", current="v")])
    summary = format_plan_summary(plan)
    assert "1 to remove" in summary
