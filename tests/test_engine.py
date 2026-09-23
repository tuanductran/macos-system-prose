"""Tests for the engine module."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock, patch

from prose.engine import collect_all, generate_ai_prompt


async def async_test_collect_all_structure():
    """Test that collect_all returns the expected structure with async execution."""
    patches = {
        "collect_system_info": AsyncMock(return_value={}),  # Now async
        "collect_hardware_info": AsyncMock(return_value={}),  # Now async
        "collect_disk_info": MagicMock(return_value={}),
        "collect_processes": MagicMock(return_value=[]),
        "collect_launch_items": MagicMock(return_value={}),
        "collect_login_items": MagicMock(return_value=[]),
        "collect_package_managers": MagicMock(return_value={}),
        "collect_dev_tools": AsyncMock(return_value={}),  # Now async
        "collect_kexts": MagicMock(return_value={"third_party_kexts": []}),
        "collect_electron_apps": MagicMock(return_value={}),
        "collect_environment_info": MagicMock(return_value={}),
        "collect_network_info": MagicMock(return_value={}),
        "collect_battery_info": MagicMock(return_value={}),
        "collect_cron_jobs": MagicMock(return_value={}),
        "collect_diagnostics": MagicMock(return_value={}),
        "collect_security_tools": MagicMock(return_value={}),
        "collect_cloud_sync": MagicMock(return_value={}),
        "collect_nvram_variables": MagicMock(return_value={}),
        "collect_storage_analysis": MagicMock(return_value={}),
        "collect_fonts": MagicMock(return_value={}),
        "collect_shell_customization": MagicMock(return_value={}),
        "collect_opencore_patcher": MagicMock(
            return_value={
                "detected": False,
                "detection_confidence": "none",
                "detection_signals": [],
                "version": None,
                "nvram_version": None,
                "opencore_version": None,
                "unsupported_os_detected": False,
                "root_patch_marker_detected": False,
                "loaded_kexts": [],
                "patched_frameworks": [],
                "amfi_configuration": None,
                "boot_args": None,
            }
        ),
        "collect_system_preferences": MagicMock(return_value={}),
        "collect_kernel_parameters": MagicMock(return_value={}),
        "collect_system_logs": MagicMock(return_value={}),
        "collect_ioregistry_info": MagicMock(
            return_value={
                "wifi": {"present": None, "components": []},
                "bluetooth": {"present": None, "controllers": []},
                "t1": {"present": None, "components": []},
                "usb_1_1": {"present": None, "controllers": []},
                "camera": {"present": None, "components": []},
            }
        ),
    }

    with patch.multiple("prose.engine", **patches):
        report = await collect_all()

        assert "timestamp" in report
        assert "system" in report
        assert "hardware" in report
        assert "disk" in report
        assert "top_processes" in report
        assert "package_managers" in report
        assert "opencore_patcher" in report
        assert "collection_status" in report
        assert report["collection_status"]["system_info"]["status"] == "ok"


def test_collect_all_structure():
    """Wrapper to run async test."""
    asyncio.run(async_test_collect_all_structure())


def test_collect_all_structure_old():
    """Test that collect_all returns the expected structure (old test - now async)."""
    patches = {
        "collect_system_info": AsyncMock(return_value={}),  # Now async
        "collect_hardware_info": AsyncMock(return_value={}),  # Now async
        "collect_disk_info": MagicMock(return_value={}),
        "collect_processes": MagicMock(return_value=[]),
        "collect_launch_items": MagicMock(return_value={}),
        "collect_login_items": MagicMock(return_value=[]),
        "collect_package_managers": MagicMock(return_value={}),
        "collect_dev_tools": AsyncMock(return_value={}),  # Now async
        "collect_kexts": MagicMock(return_value={"third_party_kexts": []}),
        "collect_electron_apps": MagicMock(return_value={}),
        "collect_environment_info": MagicMock(return_value={}),
        "collect_network_info": MagicMock(return_value={}),
        "collect_battery_info": MagicMock(return_value={}),
        "collect_cron_jobs": MagicMock(return_value={}),
        "collect_diagnostics": MagicMock(return_value={}),
        "collect_security_tools": MagicMock(return_value={}),
        "collect_cloud_sync": MagicMock(return_value={}),
        "collect_nvram_variables": MagicMock(return_value={}),
        "collect_storage_analysis": MagicMock(return_value={}),
        "collect_fonts": MagicMock(return_value={}),
        "collect_shell_customization": MagicMock(return_value={}),
        "collect_opencore_patcher": MagicMock(return_value={"detected": False}),
        "collect_system_preferences": MagicMock(return_value={}),
        "collect_kernel_parameters": MagicMock(return_value={}),
        "collect_system_logs": MagicMock(return_value={}),
        "collect_ioregistry_info": MagicMock(
            return_value={
                "wifi": {"present": None, "components": []},
                "bluetooth": {"present": None, "controllers": []},
                "t1": {"present": None, "components": []},
                "usb_1_1": {"present": None, "controllers": []},
                "camera": {"present": None, "components": []},
            }
        ),
    }

    async def run_test():
        with patch.multiple("prose.engine", **patches):
            report = await collect_all()

            assert "timestamp" in report
            assert "system" in report
            assert "hardware" in report
            assert "disk" in report
            assert "top_processes" in report
            assert "package_managers" in report
            assert "opencore_patcher" in report

    asyncio.run(run_test())


def test_generate_ai_prompt_without_oclp():
    """Test AI prompt generation for standard macOS."""
    from typing import cast

    from prose.schema import SystemReport

    data = cast(
        SystemReport,
        {
            "timestamp": 1738908295.123,
            "system": {"sip_enabled": True},
            "opencore_patcher": {"detected": False},
            "oclp_compatibility": {
                "apple_native_supported": True,
                "oclp_model_supported": False,
                "oclp_os_supported": False,
                "oclp_target_os_min": 11,
                "oclp_target_os_max": 15,
                "root_patch_required": None,
                "root_patch_state": "unknown",
                "root_patch_domains": [],
                "required_packages": [],
                "hardware_evidence": {},
                "knowledge_schema_version": 1,
                "knowledge_checked_at": "2026-09-22",
                "knowledge_sources": [],
            },
        },
    )

    prompt = generate_ai_prompt(data)

    assert "macOS System Analysis Assistant" in prompt
    assert "Standard macOS Configuration" in prompt
    assert "OCLP" not in prompt or "without OpenCore" in prompt


def test_generate_ai_prompt_with_oclp():
    """Test AI prompt generation for OCLP-patched macOS."""
    from typing import cast

    from prose.schema import SystemReport

    data = cast(
        SystemReport,
        {
            "timestamp": 1738908295.123,
            "system": {"sip_enabled": False},
            "opencore_patcher": {
                "detected": True,
                "detection_confidence": "high",
                "detection_signals": ["oclp_nvram_version"],
                "version": "2.2.0",
                "nvram_version": "2.2.0",
                "opencore_version": "0.9.9",
                "unsupported_os_detected": True,
                "root_patch_marker_detected": True,
                "loaded_kexts": ["Lilu", "WhateverGreen"],
                "patched_frameworks": [],
                "amfi_configuration": {"amfi_value": "0x80"},
                "boot_args": "amfi=0x80",
            },
            "oclp_compatibility": {
                "apple_native_supported": False,
                "oclp_model_supported": True,
                "oclp_os_supported": True,
                "oclp_target_os_min": 11,
                "oclp_target_os_max": 15,
                "root_patch_required": True,
                "root_patch_state": "detected",
                "root_patch_domains": ["graphics"],
                "required_packages": ["metallib_support_pkg"],
                "hardware_evidence": {
                    "wifi": None,
                    "bluetooth": None,
                    "t1": None,
                    "usb": None,
                    "camera": None,
                },
                "hardware_patch_requirements": {
                    "wifi": None,
                    "bluetooth": None,
                    "t1": None,
                    "usb": True,
                    "camera": None,
                },
                "knowledge_schema_version": 1,
                "knowledge_checked_at": "2026-09-22",
                "knowledge_sources": [],
            },
        },
    )

    prompt = generate_ai_prompt(data)

    assert "OpenCore Legacy Patcher Detected" in prompt
    assert "2.2.0" in prompt
    assert "Do not assume SIP must be fully disabled" in prompt
    assert "Root patch required" in prompt
    assert "Root patch domains" in prompt
    assert "Hardware evidence" in prompt
    assert '"usb": null' in prompt
    assert "Hardware patch requirements" in prompt


def test_collect_all_exception_handling():
    """Test that exceptions are replaced with type-appropriate defaults."""
    patches = {
        "collect_system_info": AsyncMock(side_effect=ValueError("System error")),
        "collect_hardware_info": AsyncMock(return_value={}),
        "collect_disk_info": MagicMock(return_value={}),
        "collect_processes": MagicMock(side_effect=OSError("Process error")),
        "collect_launch_items": MagicMock(return_value={}),
        "collect_login_items": MagicMock(side_effect=RuntimeError("Login error")),
        "collect_package_managers": MagicMock(return_value={}),
        "collect_dev_tools": AsyncMock(return_value={}),
        "collect_kexts": MagicMock(side_effect=Exception("Kext error")),
        "collect_electron_apps": MagicMock(return_value={}),
        "collect_environment_info": MagicMock(return_value={}),
        "collect_network_info": MagicMock(return_value={}),
        "collect_battery_info": MagicMock(return_value={}),
        "collect_cron_jobs": MagicMock(return_value={}),
        "collect_diagnostics": MagicMock(return_value={}),
        "collect_security_tools": MagicMock(return_value={}),
        "collect_cloud_sync": MagicMock(return_value={}),
        "collect_nvram_variables": MagicMock(return_value={}),
        "collect_storage_analysis": MagicMock(return_value={}),
        "collect_fonts": MagicMock(return_value={}),
        "collect_shell_customization": MagicMock(return_value={}),
        "collect_opencore_patcher": MagicMock(return_value={"detected": False}),
        "collect_system_preferences": MagicMock(return_value={}),
        "collect_kernel_parameters": MagicMock(return_value={}),
        "collect_system_logs": MagicMock(return_value={}),
        "collect_ioregistry_info": MagicMock(
            return_value={
                "wifi": {"present": None, "components": []},
                "bluetooth": {"present": None, "controllers": []},
                "t1": {"present": None, "components": []},
                "usb_1_1": {"present": None, "controllers": []},
                "camera": {"present": None, "components": []},
            }
        ),
    }

    async def run_test():
        with patch.multiple("prose.engine", **patches):
            report = await collect_all()

            # Verify collection_errors contains the failed collectors
            assert "collection_errors" in report
            errors = report["collection_errors"]
            expected_failed = ["system_info", "top_processes", "login_items", "kext_info"]
            assert len(errors) == len(expected_failed)
            assert any("system_info" in err for err in errors)
            assert any("top_processes" in err for err in errors)
            assert any("login_items" in err for err in errors)
            assert any("kext_info" in err for err in errors)

            # Verify type-appropriate defaults were used
            # system_info should be a dict (empty dict)
            assert isinstance(report["system"], dict)
            assert report["system"] == {}
            assert not isinstance(report["system"], Exception)

            # top_processes should be a list (empty list)
            assert isinstance(report["top_processes"], list)
            assert report["top_processes"] == []
            assert not isinstance(report["top_processes"], Exception)

            # login_items should be a list (empty list)
            assert isinstance(report["login_items"], list)
            assert report["login_items"] == []
            assert not isinstance(report["login_items"], Exception)

            # kext_info should be a dict with required fields
            assert isinstance(report["kexts"], dict)
            assert "third_party_kexts" in report["kexts"]
            assert "system_extensions" in report["kexts"]
            assert report["kexts"]["third_party_kexts"] == []
            assert report["kexts"]["system_extensions"] == []
            assert not isinstance(report["kexts"], Exception)

            status = report["collection_status"]
            assert status["system_info"]["status"] == "error"
            assert status["top_processes"]["status"] == "error"
            assert status["login_items"]["status"] == "error"
            assert status["kext_info"]["status"] == "error"
            assert status["package_managers"]["status"] == "ok"

    asyncio.run(run_test())


async def _failing_collector() -> object:
    raise RuntimeError("injected collector failure")


def test_failure_injection_covers_every_registered_collector():
    """Every registry entry must degrade to its default and expose failure metadata."""
    from prose.engine import CollectorSpec, _build_collector_registry

    def _valid_result(spec: CollectorSpec) -> object:
        if spec.name == "kext_info":
            return {"third_party_kexts": [], "system_extensions": []}
        return spec.default

    def _default_collector_factory(default: object) -> Callable[[], Awaitable[object]]:
        async def run_default() -> object:
            return default

        return run_default

    report_keys = {
        "system_info": "system",
        "hardware_info": "hardware",
        "disk_info": "disk",
        "kext_info": "kexts",
    }

    async def run_case(spec: CollectorSpec) -> None:
        registry = tuple(
            CollectorSpec(
                candidate.name,
                _failing_collector
                if candidate.name == spec.name
                else _default_collector_factory(_valid_result(candidate)),
                candidate.default,
                candidate.timeout_seconds,
            )
            for candidate in _build_collector_registry(include_sensitive_network=False)
        )
        deterministic_opencore = {
            "detected": False,
            "detection_confidence": "none",
            "detection_signals": [],
            "version": None,
            "nvram_version": None,
            "opencore_version": None,
            "unsupported_os_detected": False,
            "root_patch_marker_detected": False,
            "loaded_kexts": [],
            "patched_frameworks": [],
            "amfi_configuration": None,
            "boot_args": None,
        }
        with (
            patch(
                "prose.engine._build_collector_registry",
                return_value=registry,
            ),
            patch(
                "prose.engine.collect_opencore_patcher",
                return_value=deterministic_opencore,
            ),
        ):
            report = await collect_all()
        assert report[report_keys.get(spec.name, spec.name)] == spec.default
        assert report["collection_status"][spec.name]["status"] == "error"
        assert report["collection_status"][spec.name]["error"] == (
            "RuntimeError: injected collector failure"
        )
        assert report["collection_errors"] == [
            f"{spec.name}: RuntimeError: injected collector failure"
        ]

    async def run_all() -> None:
        for spec in _build_collector_registry(include_sensitive_network=False):
            await run_case(spec)

    asyncio.run(run_all())


async def _slow_collector() -> object:
    await asyncio.sleep(0.05)
    return {}


def test_collector_timeout_and_execution_metadata():
    """A timed-out collector must use its default and expose measured metadata."""
    from prose.engine import CollectorSpec, _build_collector_registry

    def _default_collector_factory(default: object):
        async def run_default() -> object:
            return default

        return run_default

    target_name = "system_logs"
    registry = tuple(
        CollectorSpec(
            candidate.name,
            _slow_collector
            if candidate.name == target_name
            else _default_collector_factory(candidate.default),
            candidate.default,
            0.01 if candidate.name == target_name else candidate.timeout_seconds,
        )
        for candidate in _build_collector_registry(include_sensitive_network=False)
    )
    deterministic_opencore = {
        "detected": False,
        "detection_confidence": "none",
        "detection_signals": [],
        "version": None,
        "nvram_version": None,
        "opencore_version": None,
        "unsupported_os_detected": False,
        "root_patch_marker_detected": False,
        "loaded_kexts": [],
        "patched_frameworks": [],
        "amfi_configuration": None,
        "boot_args": None,
    }

    async def run_test() -> None:
        with (
            patch("prose.engine._build_collector_registry", return_value=registry),
            patch("prose.engine.collect_opencore_patcher", return_value=deterministic_opencore),
        ):
            report = await collect_all()

        status = report["collection_status"][target_name]
        assert status["status"] == "timeout"
        assert status["error"] == "CollectorTimeoutError: collector exceeded 0.01s timeout"
        assert status["timeout_seconds"] == 0.01
        assert isinstance(status["duration_ms"], float)
        assert status["duration_ms"] >= 0
        assert report["system_logs"] == {}

        ok_status = report["collection_status"]["system_info"]
        assert ok_status["status"] == "ok"
        assert isinstance(ok_status["duration_ms"], float)
        assert ok_status["duration_ms"] >= 0
        assert ok_status["error"] is None

    asyncio.run(run_test())


def test_fast_mode_skips_expensive_collectors():
    """Fast mode must skip filesystem/log collectors while deep mode keeps them."""
    from prose.engine import _build_collector_registry

    fast = _build_collector_registry(include_sensitive_network=False, mode="fast")
    deep = _build_collector_registry(include_sensitive_network=False, mode="deep")

    fast_names = {spec.name for spec in fast}
    deep_names = {spec.name for spec in deep}

    assert {"storage_analysis", "fonts", "system_logs"} <= deep_names
    assert {"storage_analysis", "fonts", "system_logs"}.isdisjoint(fast_names)
    assert fast_names < deep_names


def test_fast_mode_reports_skipped_collectors():
    """Fast mode must retain typed defaults and explicit skipped metadata."""
    from prose.engine import CollectorSpec, _build_collector_registry

    deep = _build_collector_registry(include_sensitive_network=False, mode="deep")

    def _default_collector_factory(default: object):
        async def run_default() -> object:
            return default

        return run_default

    active = tuple(
        CollectorSpec(
            spec.name,
            _default_collector_factory(spec.default),
            spec.default,
            spec.timeout_seconds,
        )
        for spec in deep
        if spec.name not in {"storage_analysis", "fonts", "system_logs"}
    )

    deterministic_opencore = {
        "detected": False,
        "detection_confidence": "none",
        "detection_signals": [],
        "version": None,
        "nvram_version": None,
        "opencore_version": None,
        "unsupported_os_detected": False,
        "root_patch_marker_detected": False,
        "loaded_kexts": [],
        "patched_frameworks": [],
        "amfi_configuration": None,
        "boot_args": None,
    }

    async def run_test() -> None:
        with (
            patch(
                "prose.engine._build_collector_registry",
                side_effect=[active, deep],
            ),
            patch(
                "prose.engine.collect_opencore_patcher",
                return_value=deterministic_opencore,
            ),
        ):
            report = await collect_all(mode="fast")

        for name in ("storage_analysis", "fonts", "system_logs"):
            status = report["collection_status"][name]
            assert status["status"] == "skipped"
            assert status["error"] is None
            assert status["duration_ms"] is None
            assert isinstance(status["timeout_seconds"], (int, float))

    asyncio.run(run_test())
