"""Terminal UI dispatch helpers for macOS System Prose."""

from __future__ import annotations

from prose import utils
from prose.schema import SystemReport


async def run_tui_mode(
    report: SystemReport,
    *,
    live_mode: bool = False,
    refresh_interval: int = 30,
) -> int:
    """Launch the enhanced terminal UI for an already-collected report."""
    try:
        from prose.tui.app_enhanced import run_tui_enhanced
    except ImportError:
        utils.log(
            "TUI mode requires textual. Install with: uv sync --extra tui",
            "error",
        )
        return 1

    if live_mode:
        utils.log(f"Live mode enabled (refresh every {refresh_interval}s)", "info")
    utils.log("✓ Data collected. Starting TUI...", "success")

    try:
        await run_tui_enhanced(
            report,
            live_mode=live_mode,
            refresh_interval=refresh_interval,
        )
        return 0
    except Exception as e:
        utils.log(f"TUI failed: {e}", "error")
        return 1
