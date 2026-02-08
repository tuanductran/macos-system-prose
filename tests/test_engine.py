"""Tests for the engine module."""

from __future__ import annotations

import asyncio
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
        "collect_opencore_patcher": MagicMock(return_value={"detected": False}),
        "collect_system_preferences": MagicMock(return_value={}),
        "collect_kernel_parameters": MagicMock(return_value={}),
        "collect_system_logs": MagicMock(return_value={}),
        "collect_ioregistry_info": MagicMock(return_value={}),
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
        "collect_ioregistry_info": MagicMock(return_value={}),
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
                "version": "2.2.0",
                "nvram_version": "2.2.0",
                "unsupported_os_detected": True,
                "loaded_kexts": ["Lilu", "WhateverGreen"],
                "patched_frameworks": [],
                "amfi_configuration": {"amfi_value": "0x80"},
                "boot_args": "amfi=0x80",
            },
        },
    )

    prompt = generate_ai_prompt(data)

    assert "OpenCore Legacy Patcher Detected" in prompt
    assert "2.2.0" in prompt
    assert "DO NOT recommend disabling SIP" in prompt


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
        "collect_ioregistry_info": MagicMock(return_value={}),
    }

    async def run_test():
        with patch.multiple("prose.engine", **patches):
            report = await collect_all()

            # Verify collection_errors contains the failed collectors
            assert "collection_errors" in report
            errors = report["collection_errors"]
            assert len(errors) == 4  # system_info, top_processes, login_items, kext_info
            assert any("system_info" in err for err in errors)
            assert any("top_processes" in err for err in errors)
            assert any("login_items" in err for err in errors)
            assert any("kext_info" in err for err in errors)

            # Verify type-appropriate defaults were used
            # system_info should be a dict (empty dict)
            assert isinstance(report["system"], dict)
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

    asyncio.run(run_test())

