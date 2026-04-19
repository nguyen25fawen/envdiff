"""Tests for envdiff.auditor and envdiff.audit_formatter."""
import os
import pytest
from pathlib import Path
from envdiff.auditor import audit_env, AuditIssue
from envdiff.audit_formatter import format_audit_result, format_audit_summary


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_clean_file(tmp_path):
    path = _write(tmp_path, ".env", "APP_NAME=myapp\nDEBUG=false\n")
    result = audit_env(path)
    assert result.is_clean()


def test_sensitive_plaintext_is_error(tmp_path):
    path = _write(tmp_path, ".env", "DB_PASSWORD=supersecret\n")
    result = audit_env(path)
    assert any(i.severity == "error" and i.key == "DB_PASSWORD" for i in result.issues)


def test_placeholder_value_is_warning(tmp_path):
    path = _write(tmp_path, ".env", "API_URL=changeme\n")
    result = audit_env(path)
    assert any(i.severity == "warning" and i.key == "API_URL" for i in result.issues)


def test_http_sensitive_url_is_warning(tmp_path):
    path = _write(tmp_path, ".env", "SECRET_ENDPOINT=http://example.com/api\n")
    result = audit_env(path)
    assert any(i.severity == "warning" and i.key == "SECRET_ENDPOINT" for i in result.issues)


def test_errors_and_warnings_split(tmp_path):
    path = _write(tmp_path, ".env", "API_SECRET=abc123\nTOKEN=placeholder\n")
    result = audit_env(path)
    assert len(result.errors()) >= 1
    assert len(result.warnings()) >= 1


def test_format_clean_result(tmp_path):
    path = _write(tmp_path, ".env", "NAME=ok\n")
    result = audit_env(path)
    output = format_audit_result(result, no_color=True)
    assert "No audit issues found" in output


def test_format_error_appears(tmp_path):
    path = _write(tmp_path, ".env", "DB_PASSWORD=secret\n")
    result = audit_env(path)
    output = format_audit_result(result, no_color=True)
    assert "ERROR" in output
    assert "DB_PASSWORD" in output


def test_format_summary_no_issues(tmp_path):
    path = _write(tmp_path, ".env", "HOST=localhost\n")
    result = audit_env(path)
    summary = format_audit_summary([result], no_color=True)
    assert "passed" in summary


def test_format_summary_counts(tmp_path):
    path = _write(tmp_path, ".env", "API_KEY=real_key\nSECRET=todo\n")
    result = audit_env(path)
    summary = format_audit_summary([result], no_color=True)
    assert "error" in summary or "warning" in summary
