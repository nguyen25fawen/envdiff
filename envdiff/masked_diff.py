"""masked_diff.py — produce a diff view with sensitive values redacted."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult, compare_envs
from envdiff.redactor import is_sensitive, redact


@dataclass
class MaskedDiffEntry:
    key: str
    base_value: str | None      # None means key absent in base
    target_value: str | None    # None means key absent in target
    is_sensitive: bool = False
    kind: str = ""              # 'missing_in_target', 'missing_in_base', 'mismatch', 'equal'


@dataclass
class MaskedDiffResult:
    base_label: str
    target_label: str
    entries: List[MaskedDiffEntry] = field(default_factory=list)

    def has_differences(self) -> bool:
        return any(e.kind != "equal" for e in self.entries)

    def by_kind(self, kind: str) -> List[MaskedDiffEntry]:
        return [e for e in self.entries if e.kind == kind]


def _mask(value: str | None, sensitive: bool) -> str | None:
    if value is None:
        return None
    return redact({"_k": value})["_k"] if sensitive else value


def build_masked_diff(
    base: Dict[str, str],
    target: Dict[str, str],
    base_label: str = "base",
    target_label: str = "target",
    check_values: bool = True,
) -> MaskedDiffResult:
    """Compare two env dicts and return a MaskedDiffResult with sensitive values hidden."""
    diff: DiffResult = compare_envs(base, target, check_values=check_values)
    result = MaskedDiffResult(base_label=base_label, target_label=target_label)

    all_keys = sorted(
        set(base) | set(target)
        | set(diff.missing_in_target)
        | set(diff.missing_in_base)
        | set(diff.mismatched.keys())
    )

    for key in all_keys:
        sensitive = is_sensitive(key)
        b_val = base.get(key)
        t_val = target.get(key)

        if key in diff.missing_in_target:
            kind = "missing_in_target"
        elif key in diff.missing_in_base:
            kind = "missing_in_base"
        elif key in diff.mismatched:
            kind = "mismatch"
        else:
            kind = "equal"

        entry = MaskedDiffEntry(
            key=key,
            base_value=_mask(b_val, sensitive),
            target_value=_mask(t_val, sensitive),
            is_sensitive=sensitive,
            kind=kind,
        )
        result.entries.append(entry)

    return result
