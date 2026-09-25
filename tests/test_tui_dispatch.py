"""Tests for terminal UI dispatch helpers."""

from __future__ import annotations

import asyncio
import sys
from types import ModuleType
from unittest.mock import AsyncMock

from prose.tui_dispatch import run_tui_mode


def test_run_tui_mode_delegates_to_enhanced_tui(monkeypatch) -> None:
    tui_module = ModuleType("prose.tui.app_enhanced")
    run_tui = AsyncMock()
    setattr(tui_module, "run_tui_enhanced", run_tui)
    monkeypatch.setitem(sys.modules, "prose.tui.app_enhanced", tui_module)

    report = {"report_schema": "test"}

    result = asyncio.run(run_tui_mode(report, live_mode=True, refresh_interval=10))

    assert result == 0
    run_tui.assert_awaited_once_with(report, live_mode=True, refresh_interval=10)


def test_run_tui_mode_returns_error_when_tui_fails(monkeypatch) -> None:
    tui_module = ModuleType("prose.tui.app_enhanced")

    async def fail(*args, **kwargs):
        raise RuntimeError("boom")

    setattr(tui_module, "run_tui_enhanced", fail)
    monkeypatch.setitem(sys.modules, "prose.tui.app_enhanced", tui_module)

    result = asyncio.run(run_tui_mode({"report_schema": "test"}))

    assert result == 1
