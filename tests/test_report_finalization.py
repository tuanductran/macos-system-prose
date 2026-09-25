"""Tests for report finalization orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

from prose.report_finalization import finalize_report
from prose.schema import SystemReport


def test_finalize_report_saves_json_without_prompt(tmp_path: Path) -> None:
    report = cast(SystemReport, {"report_schema": "test"})
    output = tmp_path / "report.json"

    with patch(
        "prose.report_finalization.save_json_report",
        return_value=output,
    ) as save_json:
        result = finalize_report(report, output=str(output), no_prompt=True)

    assert result == 0
    save_json.assert_called_once_with(report, str(output))


def test_finalize_report_generates_prompt(tmp_path: Path) -> None:
    report = cast(SystemReport, {"report_schema": "test"})
    output = tmp_path / "report.json"
    prompt = "generated prompt"
    prompt_path = tmp_path / "report.txt"

    with (
        patch("prose.report_finalization.save_json_report", return_value=output),
        patch(
            "prose.report_finalization.generate_ai_prompt",
            return_value=prompt,
        ) as generate_prompt,
        patch(
            "prose.report_finalization.save_text",
            return_value=prompt_path,
        ) as save_prompt,
    ):
        result = finalize_report(report, output=str(output))

    assert result == 0
    generate_prompt.assert_called_once_with(report)
    save_prompt.assert_called_once_with(prompt, prompt_path)


def test_finalize_report_returns_error_when_json_save_fails(tmp_path: Path) -> None:
    report = cast(SystemReport, {"report_schema": "test"})
    output = tmp_path / "report.json"

    with patch(
        "prose.report_finalization.save_json_report",
        side_effect=OSError("disk full"),
    ):
        result = finalize_report(report, output=str(output), no_prompt=True)

    assert result == 1


def test_finalize_report_logs_existing_diff(tmp_path: Path) -> None:
    report = cast(SystemReport, {"report_schema": "test"})
    output = tmp_path / "report.json"
    diff_path = tmp_path / "old.json"
    diff_path.write_text('{"report_schema": "old"}', encoding="utf-8")

    with (
        patch("prose.report_finalization.save_json_report", return_value=output),
        patch(
            "prose.report_finalization.diff_reports",
            return_value=[("report_schema", "old", "test")],
        ),
        patch(
            "prose.report_finalization.format_diff",
            return_value=["report_schema: old -> test"],
        ),
        patch("prose.report_finalization.utils.log") as log,
    ):
        result = finalize_report(
            report,
            output=str(output),
            no_prompt=True,
            diff=str(diff_path),
        )

    assert result == 0
    log.assert_any_call("Comparing with: " + str(diff_path), "header")
    log.assert_any_call("report_schema: old -> test", "info")
