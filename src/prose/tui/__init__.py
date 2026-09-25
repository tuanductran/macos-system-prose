"""Terminal User Interface for macOS System Prose.

The package exposes the enhanced Textual application as its public TUI API.
The legacy implementation remains available only through the compatibility
module prose.tui.app.
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
