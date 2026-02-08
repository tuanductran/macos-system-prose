"""Terminal User Interface for macOS System Prose.

This package provides interactive TUI components built with Textual:
- app: Basic TUI implementation
- app_enhanced: Advanced TUI with htop-style monitor and Apple HIG design
"""

from __future__ import annotations

from prose.tui.app import run_tui_sync


__all__ = ["run_tui_sync"]
