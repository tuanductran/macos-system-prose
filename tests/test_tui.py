from prose.tui import run_tui, run_tui_enhanced, run_tui_enhanced_sync, run_tui_sync
from prose.tui.app import run_tui as legacy_run_tui
from prose.tui.app import run_tui_sync as legacy_run_tui_sync
from prose.tui.app_enhanced import run_tui_enhanced, run_tui_enhanced_sync


def test_public_tui_api_uses_enhanced_implementation() -> None:
    assert run_tui is run_tui_enhanced
    assert run_tui_sync is run_tui_enhanced_sync
    assert run_tui_enhanced is not None
    assert run_tui_enhanced_sync is not None


def test_legacy_module_is_compatibility_wrapper() -> None:
    assert legacy_run_tui is run_tui_enhanced
    assert legacy_run_tui_sync is run_tui_enhanced_sync
