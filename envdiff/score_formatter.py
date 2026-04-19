"""Rich colour formatting for EnvScore output."""
from envdiff.scorer import EnvScore

try:
    import sys
    _USE_COLOR = sys.stdout.isatty()
except Exception:
    _USE_COLOR = False

_COLORS = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _c(text: str, *codes: str) -> str:
    if not _USE_COLOR:
        return text
    prefix = "".join(_COLORS.get(c, "") for c in codes)
    return f"{prefix}{text}{_COLORS['reset']}"


def _grade_color(grade: str) -> str:
    return {"A": "green", "B": "green", "C": "yellow", "D": "yellow"}.get(grade, "red")


def format_score_rich(env_score: EnvScore) -> str:
    grade_col = _grade_color(env_score.grade)
    header = _c(
        f"Health Score: {env_score.score:.1f} / 100  [{env_score.grade}]",
        "bold",
        grade_col,
    )
    missing_line = _c(
        f"  Missing keys  : {env_score.missing_count}",
        "red" if env_score.missing_count else "green",
    )
    mismatch_line = _c(
        f"  Mismatches    : {env_score.mismatch_count}",
        "yellow" if env_score.mismatch_count else "green",
    )
    total_line = f"  Total keys    : {env_score.total_keys}"
    return "\n".join([header, total_line, missing_line, mismatch_line])
