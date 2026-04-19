"""Key renaming: detect renamed keys between env files and suggest mappings."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envdiff.parser import parse_env_file


@dataclass
class RenameCandidate:
    old_key: str
    new_key: str
    value: str


@dataclass
class RenameResult:
    confirmed: List[RenameCandidate] = field(default_factory=list)
    unmatched_old: List[str] = field(default_factory=list)
    unmatched_new: List[str] = field(default_factory=list)


def _missing_keys(base: Dict[str, str], target: Dict[str, str]) -> List[str]:
    return [k for k in base if k not in target]


def detect_renames(
    base: Dict[str, str],
    target: Dict[str, str],
) -> RenameResult:
    """Match keys missing in target to keys missing in base by value."""
    result = RenameResult()
    only_in_base = _missing_keys(base, target)
    only_in_target = _missing_keys(target, base)

    value_to_new: Dict[str, List[str]] = {}
    for k in only_in_target:
        v = target[k]
        value_to_new.setdefault(v, []).append(k)

    unmatched_old: List[str] = []
    for old_key in only_in_base:
        v = base[old_key]
        candidates = value_to_new.get(v, [])
        if len(candidates) == 1:
            result.confirmed.append(RenameCandidate(old_key, candidates[0], v))
            value_to_new.pop(v)
        else:
            unmatched_old.append(old_key)

    result.unmatched_old = unmatched_old
    result.unmatched_new = [k for keys in value_to_new.values() for k in keys]
    return result


def detect_renames_from_files(base_path: str, target_path: str) -> RenameResult:
    base = parse_env_file(base_path)
    target = parse_env_file(target_path)
    return detect_renames(base, target)
