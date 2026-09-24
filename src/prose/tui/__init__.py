"""Terminal User Interface for macOS System Prose.

This package provides interactive TUI components built with Textual:
- app: Basic TUI implementation
- app_enhanced: Live htop-style TUI implementation
"""

from __future__ import annotations

from prose.tui.app import run_tui_sync


__all__ = ["run_tui_sync"]
