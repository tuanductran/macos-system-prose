"""Tests for report output helpers."""

from __future__ import annotations

import json
from typing import cast

from prose.output import load_json_report, save_html_report, save_json_report, save_text
from prose.schema import SystemReport


def test_load_json_report_reads_report(tmp_path):
    output = tmp_path / "report.json"
    output.write_text('{"report_schema": "test", "timestamp": 1.0}', encoding="utf-8")

    result = load_json_report(output)

    assert result == {"report_schema": "test", "timestamp": 1.0}


def test_save_json_report_writes_formatted_report(tmp_path):
    report = cast(SystemReport, {"report_schema": "test", "timestamp": 1.0})
    output = tmp_path / "report.json"

    result = save_json_report(report, output)

    assert result == output
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert output.read_text(encoding="utf-8").endswith("}")


def test_save_json_report_creates_missing_parent_directories(tmp_path):
    report = cast(SystemReport, {"report_schema": "test", "timestamp": 1.0})
    output = tmp_path / "output" / "nested" / "report.json"

    result = save_json_report(report, output)

    assert result == output
    assert json.loads(output.read_text(encoding="utf-8")) == report


def test_save_text_creates_missing_parent_directories(tmp_path):
    output = tmp_path / "output" / "nested" / "prompt.txt"

    result = save_text("hello\n", output)

    assert result == output
    assert output.read_text(encoding="utf-8") == "hello\n"


def test_save_text_writes_content(tmp_path):
    output = tmp_path / "prompt.txt"

    result = save_text("hello\n", output)

    assert result == output
    assert output.read_text(encoding="utf-8") == "hello\n"


def test_save_html_report_writes_self_contained_html(tmp_path) -> None:
    report = cast(SystemReport, {"report_schema": "test", "report_schema_version": 1})
    output = tmp_path / "report.html"

    result = save_html_report(report, output)

    content = output.read_text(encoding="utf-8")
    assert result == output
    assert content.startswith("<!doctype html>")
    assert "<title>macOS System Prose Report</title>" in content
    assert "<summary>report_schema</summary>" in content
    assert '<pre>"test"</pre>' in content
