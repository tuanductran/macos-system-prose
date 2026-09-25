"""Compatibility wrapper for the consolidated Textual TUI.

The original basic TUI implementation has been retired. Public imports from
prose.tui.app continue to resolve to the enhanced application.
"""

from __future__ import annotations

from prose.tui.app_enhanced import run_tui_enhanced, run_tui_enhanced_sync


run_tui = run_tui_enhanced
run_tui_sync = run_tui_enhanced_sync

__all__ = [
    "run_tui",
    "run_tui_enhanced",
    "run_tui_enhanced_sync",
    "run_tui_sync",
]
