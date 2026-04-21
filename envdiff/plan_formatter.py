"""plan_formatter.py – human-readable rendering of a reconciliation Plan."""
from __future__ import annotations

from typing import List

from .planner import Plan, PlanAction


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code* (reset afterwards)."""
    return f"\033[{code}m{text}\033[0m"


_ICONS: dict[str, str] = {
    "add": "+",
    "remove": "-",
    "update": "~",
}

_COLOURS: dict[str, str] = {
    "add": "32",     # green
    "remove": "31",  # red
    "update": "33",  # yellow
}


def _fmt_action(action: PlanAction, *, mask_values: bool = True) -> str:
    icon = _ICONS[action.kind]
    colour = _COLOURS[action.kind]
    label = _c(f"[{icon}] {action.kind.upper():6s}", colour)
    key_part = _c(action.key, "1")  # bold

    if action.kind == "add":
        val = "***" if mask_values else action.desired_value
        return f"  {label} {key_part}  →  {val}"
    if action.kind == "remove":
        val = "***" if mask_values else action.current_value
        return f"  {label} {key_part}  (was {val})"
    # update
    cur = "***" if mask_values else action.current_value
    des = "***" if mask_values else action.desired_value
    return f"  {label} {key_part}  {cur}  →  {des}"


def format_plan(plan: Plan, *, mask_values: bool = True) -> str:
    if plan.is_empty():
        return _c("✔ No changes required.", "32")

    lines: List[str] = [_c("Reconciliation plan:", "1")]
    for action in plan.actions:
        lines.append(_fmt_action(action, mask_values=mask_values))
    return "\n".join(lines)


def format_plan_summary(plan: Plan) -> str:
    adds = len(plan.by_kind("add"))
    removes = len(plan.by_kind("remove"))
    updates = len(plan.by_kind("update"))
    total = adds + removes + updates
    if total == 0:
        return _c("Plan: nothing to do.", "32")
    parts = []
    if adds:
        parts.append(_c(f"{adds} to add", "32"))
    if updates:
        parts.append(_c(f"{updates} to update", "33"))
    if removes:
        parts.append(_c(f"{removes} to remove", "31"))
    return "Plan: " + ", ".join(parts) + "."
