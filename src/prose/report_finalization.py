"""Final report output orchestration for macOS System Prose."""

from __future__ import annotations

from pathlib import Path

from prose import utils
from prose.diff import diff_reports, format_diff
from prose.output import load_json_report, save_json_report, save_text
from prose.prompt import generate_ai_prompt
from prose.schema import SystemReport


def finalize_report(
    report: SystemReport,
    *,
    output: str,
    no_prompt: bool = False,
    diff: str | None = None,
) -> int:
    """Save a report, optionally generate its AI prompt, and show a diff."""
    try:
        output_path = save_json_report(report, output)
        utils.log(f"Report saved to: {output_path.resolve()}", "success")
    except Exception as e:
        utils.log(f"Failed to save report: {e}", "error")
        return 1

    if not no_prompt:
        prompt_file = Path(output).with_suffix(".txt")
        try:
            prompt_content = generate_ai_prompt(report)
            prompt_path = save_text(prompt_content, prompt_file)
            utils.log(f"AI Prompt saved to: {prompt_path.resolve()}", "success")
        except Exception as e:
            utils.log(f"Failed to save AI prompt: {e}", "error")

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
