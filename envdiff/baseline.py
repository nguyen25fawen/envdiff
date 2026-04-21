"""Baseline comparison: compare multiple env files against a designated base."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import EnvDiff, diff_pair
from envdiff.parser import parse_env_file


@dataclass
class BaselineResult:
    base_path: str
    comparisons: Dict[str, EnvDiff] = field(default_factory=dict)

    def any_differences(self) -> bool:
        return any(d.missing_in_target or d.missing_in_base or d.mismatched for d in self.comparisons.values())

    def targets_with_issues(self) -> List[str]:
        return [
            path
            for path, diff in self.comparisons.items()
            if diff.missing_in_target or diff.missing_in_base or diff.mismatched
        ]

    def clean_targets(self) -> List[str]:
        return [
            path
            for path, diff in self.comparisons.items()
            if not diff.missing_in_target and not diff.missing_in_base and not diff.mismatched
        ]


def compare_against_base(
    base_path: str,
    target_paths: List[str],
    check_values: bool = False,
) -> BaselineResult:
    """Compare each target file against the base env file."""
    base_env = parse_env_file(base_path)
    result = BaselineResult(base_path=base_path)
    for target_path in target_paths:
        target_env = parse_env_file(target_path)
        result.comparisons[target_path] = diff_pair(
            base_env, target_env, check_values=check_values
        )
    return result
