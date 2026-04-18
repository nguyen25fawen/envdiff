"""Compare parsed .env file dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the comparison result between two environments."""

    missing_in_second: List[str] = field(default_factory=list)
    missing_in_first: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_second
            or self.missing_in_first
            or self.value_mismatches
        )


def compare_envs(
    first: Dict[str, Optional[str]],
    second: Dict[str, Optional[str]],
    check_values: bool = True,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        first: Parsed env dict for the first file.
        second: Parsed env dict for the second file.
        check_values: When True, also flag keys whose values differ.

    Returns:
        A DiffResult describing all detected differences.
    """
    result = DiffResult()

    keys_first = set(first.keys())
    keys_second = set(second.keys())

    result.missing_in_second = sorted(keys_first - keys_second)
    result.missing_in_first = sorted(keys_second - keys_first)

    if check_values:
        common_keys = keys_first & keys_second
        for key in sorted(common_keys):
            if first[key] != second[key]:
                result.value_mismatches[key] = (first[key], second[key])

    return result
