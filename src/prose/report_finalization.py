"""Final report output orchestration for macOS System Prose."""

from __future__ import annotations

from pathlib import Path

from prose import utils
from prose.diff import diff_reports, format_diff
from prose.output import load_json_report, save_html_report, save_json_report, save_text
from prose.prompt import generate_ai_prompt
from prose.schema import SystemReport


def finalize_report(
    report: SystemReport,
    *,
    output: str,
    report_format: str = "html",
    diff: str | None = None,
) -> int:
    """Save exactly one report format and optionally show a diff."""
    try:
        if report_format == "json":
            output_path = save_json_report(report, output)
        elif report_format == "txt":
            output_path = save_text(generate_ai_prompt(report), output)
        else:
            output_path = save_html_report(report, output)
        utils.log(f"Report saved to: {output_path.resolve()}", "success")
    except Exception as e:
        utils.log(f"Failed to save report: {e}", "error")
        return 1

    if diff:
        _log_report_diff(diff, report)

    utils.log("Collection complete.", "success")
    return 0


def _log_report_diff(diff_path: str, report: SystemReport) -> None:
    """Log differences between an existing report and the current report."""
    path = Path(diff_path)
    if not path.exists():
        utils.log(f"Diff target not found: {diff_path}", "error")
        return

    try:
        old_data = load_json_report(path)
        utils.log(f"Comparing with: {diff_path}", "header")
        changes = diff_reports(old_data, report)
        if changes:
            for line in format_diff(changes):
                utils.log(line, "info")
        else:
            utils.log("No differences found.", "success")
    except Exception as e:
        utils.log(f"Failed to compare reports: {e}", "error")
