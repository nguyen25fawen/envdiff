"""Tests for envdiff.lint_formatter."""
from pathlib import Path
from envdiff.linter import LintResult, LintIssue
from envdiff.lint_formatter import format_lint_result, format_lint_summary


def _result(path: str = ".env", issues=None) -> LintResult:
    r = LintResult(path=Path(path))
    if issues:
        r.issues.extend(issues)
    return r


def _issue(lineno=1, key="KEY", msg="some issue", severity="error") -> LintIssue:
    return LintIssue(line_number=lineno, key=key, message=msg, severity=severity)


def test_clean_result_message():
    r = _result()
    lines = format_lint_result(r)
    assert len(lines) == 1
    assert "no issues found" in lines[0]


def test_error_appears_in_output():
    r = _result(issues=[_issue(msg="Duplicate key 'X'")])
    lines = format_lint_result(r)
    combined = "\n".join(lines)
    assert "Duplicate key 'X'" in combined


def test_warning_appears_in_output():
    r = _result(issues=[_issue(msg="empty value", severity="warning")])
    lines = format_lint_result(r)
    combined = "\n".join(lines)
    assert "empty value" in combined


def test_issue_count_in_header():
    r = _result(issues=[_issue(), _issue(lineno=2, msg="other")])
    lines = format_lint_result(r)
    assert "2 issue(s)" in lines[0]


def test_summary_all_clean():
    results = [_result("a.env"), _result("b.env")]
    lines = format_lint_summary(results)
    combined = "\n".join(lines)
    assert "All files passed" in combined


def test_summary_counts_errors_and_warnings():
    r1 = _result(issues=[_issue(severity="error")])
    r2 = _result(issues=[_issue(severity="warning")])
    lines = format_lint_summary([r1, r2])
    combined = "\n".join(lines)
    assert "1 error" in combined
    assert "1 warning" in combined


def test_line_number_shown():
    r = _result(issues=[_issue(lineno=42)])
    lines = format_lint_result(r)
    combined = "\n".join(lines)
    assert "line 42" in combined
