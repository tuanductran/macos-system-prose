from prose.tui import run_tui, run_tui_enhanced, run_tui_enhanced_sync, run_tui_sync
from prose.tui.app import run_tui as legacy_run_tui
from prose.tui.app import run_tui_sync as legacy_run_tui_sync
from prose.tui.app_enhanced import (
    run_tui_enhanced as enhanced_run_tui,
    run_tui_enhanced_sync as enhanced_run_tui_sync,
)


def test_public_tui_api_uses_enhanced_implementation() -> None:
    assert run_tui is enhanced_run_tui
    assert run_tui_sync is enhanced_run_tui_sync
    assert run_tui_enhanced is enhanced_run_tui
    assert run_tui_enhanced_sync is enhanced_run_tui_sync


def test_legacy_module_is_compatibility_wrapper() -> None:
    assert legacy_run_tui is enhanced_run_tui
    assert legacy_run_tui_sync is enhanced_run_tui_sync
