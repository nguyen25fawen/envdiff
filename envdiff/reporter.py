"""Generate summary reports from multiple env comparisons."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult, compare_envs
from envdiff.parser import parse_env_file


@dataclass
class ComparisonReport:
    """Aggregated report for a base env compared against multiple targets."""

    base_path: str
    results: Dict[str, DiffResult] = field(default_factory=dict)

    def add(self, target_path: str, result: DiffResult) -> None:
        self.results[target_path] = result

    @property
    def any_differences(self) -> bool:
        return any(r.has_differences for r in self.results.values())

    def summary_lines(self) -> List[str]:
        lines: List[str] = []
        lines.append(f"Base: {self.base_path}")
        for target, result in self.results.items():
            status = "DIFF" if result.has_differences else "OK"
            missing_b = len(result.missing_in_second)
            missing_a = len(result.missing_in_first)
            mismatched = len(result.mismatched)
            lines.append(
                f"  [{status}] {target} "
                f"(missing_in_target={missing_b}, "
                f"missing_in_base={missing_a}, "
                f"mismatched={mismatched})"
            )
        return lines


def build_report(
    base_path: str,
    target_paths: List[str],
    check_values: bool = False,
) -> ComparisonReport:
    """Parse and compare base env against each target, return a report."""
    report = ComparisonReport(base_path=base_path)
    base_env = parse_env_file(base_path)
    for target in target_paths:
        target_env = parse_env_file(target)
        result = compare_envs(base_env, target_env, check_values=check_values)
        report.add(target, result)
    return report
