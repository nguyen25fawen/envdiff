"""planner.py – generate an action plan to reconcile two .env files.

Given a base env and a target env, produce a list of recommended actions
(add, remove, update) that would make the target match the base.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

ActionKind = Literal["add", "remove", "update"]


@dataclass(frozen=True)
class PlanAction:
    kind: ActionKind
    key: str
    current_value: str | None  # value in target (None if missing)
    desired_value: str | None  # value in base  (None if key should be removed)


@dataclass
class Plan:
    actions: List[PlanAction] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.actions) == 0

    def by_kind(self, kind: ActionKind) -> List[PlanAction]:
        return [a for a in self.actions if a.kind == kind]


def build_plan(
    base: Dict[str, str],
    target: Dict[str, str],
    *,
    remove_extra: bool = False,
) -> Plan:
    """Return actions needed to make *target* match *base*.

    Args:
        base: The authoritative environment (e.g. .env.example).
        target: The environment to reconcile (e.g. .env).
        remove_extra: When True, also emit ``remove`` actions for keys that
            exist in *target* but not in *base*.
    """
    actions: List[PlanAction] = []

    for key, desired in sorted(base.items()):
        if key not in target:
            actions.append(PlanAction("add", key, None, desired))
        elif target[key] != desired:
            actions.append(PlanAction("update", key, target[key], desired))

    if remove_extra:
        for key in sorted(target):
            if key not in base:
                actions.append(PlanAction("remove", key, target[key], None))

    return Plan(actions=actions)
