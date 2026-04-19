"""Assigns a health score to an env file comparison."""
from dataclasses import dataclass
from typing import List
from envdiff.reporter import ComparisonReport


@dataclass
class EnvScore:
    total_keys: int
    missing_count: int
    mismatch_count: int
    score: float  # 0.0 – 100.0
    grade: str


def _grade(score: float) -> str:
    if score >= 95:
        return "A"
    if score >= 80:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_report(report: ComparisonReport, base_keys: List[str]) -> EnvScore:
    """Score a comparison report relative to the set of base keys."""
    total = len(base_keys)
    if total == 0:
        return EnvScore(0, 0, 0, 100.0, "A")

    missing = 0
    mismatches = 0
    for diff in report.diffs.values():
        missing += len(diff.missing_in_second) + len(diff.missing_in_first)
        mismatches += len(diff.mismatched_values)

    penalty = (missing * 2 + mismatches) / (total * len(report.diffs) or 1)
    raw = max(0.0, 100.0 - penalty * 100.0)
    score = round(raw, 1)
    return EnvScore(
        total_keys=total,
        missing_count=missing,
        mismatch_count=mismatches,
        score=score,
        grade=_grade(score),
    )


def format_score(env_score: EnvScore) -> str:
    lines = [
        f"Health Score : {env_score.score:.1f} / 100  [{env_score.grade}]",
        f"Total Keys   : {env_score.total_keys}",
        f"Missing      : {env_score.missing_count}",
        f"Mismatches   : {env_score.mismatch_count}",
    ]
    return "\n".join(lines)
