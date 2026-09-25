"""Tests for report output helpers."""

from __future__ import annotations

import json
from typing import cast

from prose.output import save_json_report, save_text
from prose.schema import SystemReport


def test_save_json_report_writes_formatted_report(tmp_path):
    report = cast(SystemReport, {"report_schema": "test", "timestamp": 1.0})
    output = tmp_path / "report.json"

    result = save_json_report(report, output)

    assert result == output
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert output.read_text(encoding="utf-8").endswith("}")


def test_save_text_writes_content(tmp_path):
    output = tmp_path / "prompt.txt"

    result = save_text("hello\n", output)

    assert result == output
    assert output.read_text(encoding="utf-8") == "hello\n"
