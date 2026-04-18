"""High-level diff driver: compare a base env against one or more targets."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.comparator import DiffResult, compare_envs
from envdiff.parser import parse_env_file


@dataclass
class EnvDiff:
    """Holds the base path, a target path, and their computed DiffResult."""

    base_path: Path
    target_path: Path
    result: DiffResult


@dataclass
class MultiDiff:
    """Collection of EnvDiff entries for one base vs many targets."""

    base_path: Path
    diffs: List[EnvDiff] = field(default_factory=list)

    def any_differences(self) -> bool:
        from envdiff.comparator import has_differences

        return any(has_differences(d.result) for d in self.diffs)


def diff_pair(
    base: Path,
    target: Path,
    check_values: bool = False,
) -> EnvDiff:
    """Parse and compare a single base/target pair."""
    base_env = parse_env_file(base)
    target_env = parse_env_file(target)
    result = compare_envs(base_env, target_env, check_values=check_values)
    return EnvDiff(base_path=base, target_path=target, result=result)


def diff_many(
    base: Path,
    targets: List[Path],
    check_values: bool = False,
) -> MultiDiff:
    """Compare a base env file against multiple target env files."""
    multi = MultiDiff(base_path=base)
    for target in targets:
        multi.diffs.append(diff_pair(base, target, check_values=check_values))
    return multi
