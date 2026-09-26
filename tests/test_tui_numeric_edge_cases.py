"""Regression tests for numeric edge cases in the enhanced Textual TUI."""

from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult

from prose.tui.app_enhanced import MonitorHeader


def _make_app(data: dict) -> App:
    class _HarnessApp(App[None]):
        def compose(self) -> ComposeResult:
            yield MonitorHeader(data)  # type: ignore[arg-type]

    return _HarnessApp()


def test_monitor_header_handles_zero_cpu_cores() -> None:
    """cpu_cores can be present but 0 (e.g. `sysctl hw.ncpu` failed), which
    must not raise ZeroDivisionError while computing the CPU percentage."""
    data = {
        "system": {"load_average": "1.0 0.5 0.2", "uptime": "up 1 day", "model_name": "Mac"},
        "hardware": {"cpu_cores": 0, "memory_pressure": {"level": "normal"}},
        "disk": {"disk_total_gb": 100.0, "disk_free_gb": 50.0},
        "top_processes": [],
    }

    async def _mount_and_check() -> None:
        app = _make_app(data)
        async with app.run_test():
            header = app.query_one(MonitorHeader)
            assert header.cpu_pct == 0.0

    asyncio.run(_mount_and_check())


def test_monitor_header_handles_zero_disk_total() -> None:
    """disk_total_gb can be present but 0 (e.g. an unusual statvfs result),
    which must not raise ZeroDivisionError while computing disk percentage."""
    data = {
        "system": {"load_average": "1.0 0.5 0.2", "uptime": "up 1 day", "model_name": "Mac"},
        "hardware": {"cpu_cores": 4, "memory_pressure": {"level": "normal"}},
        "disk": {"disk_total_gb": 0, "disk_free_gb": 0},
        "top_processes": [],
    }

    async def _mount_and_check() -> None:
        app = _make_app(data)
        async with app.run_test():
            header = app.query_one(MonitorHeader)
            assert header.disk_pct == 0.0

    asyncio.run(_mount_and_check())
