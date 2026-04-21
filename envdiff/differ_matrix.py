"""Build a comparison matrix across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envdiff.parser import parse_env_file


@dataclass
class MatrixCell:
    value: Optional[str]  # None means key is absent
    present: bool


@dataclass
class MatrixResult:
    files: List[str]
    keys: List[str]
    # rows[key][file_index] = MatrixCell
    rows: Dict[str, List[MatrixCell]] = field(default_factory=dict)


def build_matrix(file_paths: List[str]) -> MatrixResult:
    """Parse all files and build a key x file matrix."""
    parsed: List[Dict[str, str]] = [parse_env_file(p) for p in file_paths]

    all_keys: List[str] = sorted(
        {key for env in parsed for key in env}
    )

    rows: Dict[str, List[MatrixCell]] = {}
    for key in all_keys:
        cells: List[MatrixCell] = []
        for env in parsed:
            if key in env:
                cells.append(MatrixCell(value=env[key], present=True))
            else:
                cells.append(MatrixCell(value=None, present=False))
        rows[key] = cells

    return MatrixResult(files=list(file_paths), keys=all_keys, rows=rows)


def matrix_missing_pairs(result: MatrixResult) -> List[Tuple[str, str]]:
    """Return (key, file_path) pairs where the key is absent."""
    missing: List[Tuple[str, str]] = []
    for key in result.keys:
        for idx, cell in enumerate(result.rows[key]):
            if not cell.present:
                missing.append((key, result.files[idx]))
    return missing


def matrix_value_conflicts(result: MatrixResult) -> List[Tuple[str, List[str]]]:
    """Return (key, list_of_distinct_values) for keys with conflicting values."""
    conflicts: List[Tuple[str, List[str]]] = []
    for key in result.keys:
        values = [
            cell.value for cell in result.rows[key] if cell.present
        ]
        distinct = list(dict.fromkeys(values))  # preserve order, deduplicate
        if len(distinct) > 1:
            conflicts.append((key, distinct))
    return conflicts
