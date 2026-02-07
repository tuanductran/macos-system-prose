"""Shared test fixtures generated programmatically.

Factory functions produce fixture data that mirrors real Mac configurations,
eliminating the need for static JSON fixture files.

All structures match the TypedDict definitions in src/prose/schema.py.
"""

from __future__ import annotations

import time
from typing import Any

import pytest


def _base_system(
    *,
    macos_version: str = "14.2.1",
    macos_name: str = "macOS Sonoma",
    model_name: str = "MacBook Pro",
    model_identifier: str = "Mac14,10",
    architecture: str = "arm64",
    marketing_name: str | None = None,
    board_id: str | None = None,
    cpu_generation: str | None = None,
    max_os_supported: str | None = None,
    filevault_enabled: bool = True,
) -> dict[str, Any]:
    """SystemInfo TypedDict."""
    return {
        "os": "Darwin",
        "macos_version": macos_version,
        "macos_name": macos_name,
        "model_name": model_name,
        "model_identifier": model_identifier,
        "marketing_name": marketing_name,
        "board_id": board_id,
        "cpu_generation": cpu_generation,
        "max_os_supported": max_os_supported,
        "kernel": "23.2.0",
        "architecture": architecture,
        "uptime": "5 days, 3:24",
        "uptime_seconds": 442440,
        "boot_time": "{ sec = 1735689600, usec = 0 }",
        "load_average": "{ 2.50 1.80 1.20 }",
        "sip_enabled": True,
        "gatekeeper_enabled": True,
        "filevault_enabled": filevault_enabled,
        "time_machine": {
            "enabled": True,
            "last_backup": None,
            "destination": None,
            "auto_backup": False,
        },
    }


def _base_display(
    *,
    resolution: str = "3456 x 2234",
    refresh_rate: str = "120 Hz",
    color_depth: str = "8-bit",
    external_displays: int = 0,
) -> dict[str, Any]:
    """DisplayInfo TypedDict."""
    return {
        "resolution": resolution,
        "refresh_rate": refresh_rate,
        "color_depth": color_depth,
        "external_displays": external_displays,
        "edid_manufacturer": None,
        "edid_product_code": None,
        "edid_serial": None,
        "connector_type": None,
    }


def _base_hardware(
    *,
    cpu: str = "Apple M3 Pro",
    cpu_cores: int = 12,
    memory_gb: float = 36.0,
    gpu: list[str] | None = None,
    displays: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """HardwareInfo TypedDict."""
    return {
        "cpu": cpu,
        "cpu_cores": cpu_cores,
        "gpu": gpu or ["Apple M3 Pro"],
        "memory_gb": memory_gb,
        "thermal_pressure": ["Nominal"],
        "displays": displays or [_base_display()],
        "memory_pressure": {
            "level": "normal",
            "pages_free": 100000,
            "pages_active": 200000,
            "pages_inactive": 150000,
            "pages_wired": 300000,
            "swap_used": 0,
            "swap_free": 2048,
        },
    }


def _base_disk(*, total_gb: float = 994.66, free_gb: float = 487.23) -> dict[str, Any]:
    """DiskInfo TypedDict."""
    return {
        "disk_total_gb": total_gb,
        "disk_free_gb": free_gb,
        "apfs_info": [
            {
                "reference": "disk1",
                "physical_store": "disk0s2",
                "capacity_gb": total_gb,
                "free_gb": free_gb,
                "used_percent": round((total_gb - free_gb) / total_gb * 100, 1) if total_gb else 0,
                "fusion": False,
                "volumes": [
                    {
                        "name": "Macintosh - Data",
                        "device": "disk1s1",
                        "role": "Data",
                        "capacity_used_gb": round(total_gb - free_gb, 2),
                        "encrypted": False,
                        "filevault": False,
                    }
                ],
            }
        ],
        "disk_health": [
            {
                "disk_name": "disk0",
                "disk_type": "SSD",
                "smart_status": "Verified",
                "health_percentage": None,
            }
        ],
    }


def _base_network(*, vpn: bool = False) -> dict[str, Any]:
    """NetworkInfo TypedDict."""
    return {
        "hostname": "Mac.local",
        "primary_interface": "en0",
        "ipv4_address": "192.168.1.100",
        "public_ip": "203.0.113.42",
        "gateway": "192.168.1.1",
        "subnet_mask": "255.255.255.0",
        "mac_address": "a4:83:e7:00:00:00",
        "dns_servers": ["1.1.1.1", "8.8.8.8"],
        "wifi_ssid": "TestNetwork",
        "firewall_status": "enabled",
        "local_interfaces": [{"name": "en0", "type": "Wi-Fi", "status": "active"}],
        "vpn_status": vpn,
        "vpn_connections": [],
        "vpn_apps": [],
    }


def _base_processes() -> list[dict[str, Any]]:
    """list[ProcessInfo] TypedDict."""
    return [
        {"pid": 123, "cpu_percent": 5.2, "mem_percent": 2.8, "command": "WindowServer"},
        {"pid": 0, "cpu_percent": 3.1, "mem_percent": 12.0, "command": "kernel_task"},
    ]


def _base_startup() -> dict[str, Any]:
    """LaunchItems TypedDict."""
    return {
        "user_agents": ["~/Library/LaunchAgents/com.example.plist"],
        "system_agents": ["/Library/LaunchAgents/com.example.plist"],
        "system_daemons": ["/Library/LaunchDaemons/com.example.plist"],
    }


def _not_installed() -> dict[str, Any]:
    """NotInstalled TypedDict."""
    return {"installed": False}


def _base_package_managers(*, homebrew: bool = True) -> dict[str, Any]:
    """PackageManagers TypedDict."""
    brew: dict[str, Any] = (
        {
            "installed": True,
            "version": "4.2.5",
            "bin_path": "/opt/homebrew/bin/brew",
            "globals": None,
            "prefix": "/opt/homebrew",
            "formula": ["git", "node", "python@3.12"],
            "casks": ["visual-studio-code"],
            "active_ports": None,
            "packages": None,
        }
        if homebrew
        else _not_installed()
    )
    return {
        "homebrew": brew,
        "macports": _not_installed(),
        "pipx": _not_installed(),
        "npm": {
            "installed": True,
            "version": "10.2.4",
            "bin_path": "/opt/homebrew/bin/npm",
            "globals": ["typescript"],
            "prefix": None,
            "formula": None,
            "casks": None,
            "active_ports": None,
            "packages": None,
        },
        "yarn": _not_installed(),
        "pnpm": _not_installed(),
        "bun": _not_installed(),
        "homebrew_services": [],
    }


def _base_developer_tools(*, docker: bool = False) -> dict[str, Any]:
    """DeveloperToolsInfo TypedDict."""
    docker_info: dict[str, Any] = {
        "installed": docker,
        "version": "24.0.7" if docker else "",
        "running": docker,
        "containers_total": 2 if docker else 0,
        "containers_running": 1 if docker else 0,
        "images_count": 5 if docker else 0,
        "containers": [],
        "images": [],
    }
    return {
        "languages": {"node": "v20.11.0", "python3": "Python 3.12.1"},
        "sdks": {"xcode": "Xcode 15.2"},
        "cloud_devops": {},
        "databases": {},
        "version_managers": {},
        "infra": {},
        "extensions": {"vscode": ["ms-python.python"]},
        "editors": ["Visual Studio Code"],
        "docker": docker_info,
        "browsers": [
            {
                "name": "Safari",
                "installed": True,
                "version": "17.2",
                "path": "/Applications/Safari.app",
            }
        ],
        "git_config": {
            "user_name": "Test User",
            "user_email": "test@example.com",
            "core_editor": None,
            "credential_helper": None,
            "aliases": {},
            "other_settings": {},
        },
        "terminal_emulators": ["Terminal"],
        "shell_frameworks": {},
    }


def _base_kexts(*, third_party_kexts: list[str] | None = None) -> dict[str, Any]:
    """KernelExtensionsInfo TypedDict."""
    return {
        "third_party_kexts": third_party_kexts or [],
        "system_extensions": [],
    }


def _base_opencore_patcher(*, detected: bool = False, **kwargs: Any) -> dict[str, Any]:
    """OpenCorePatcherInfo TypedDict."""
    return {
        "detected": detected,
        "version": kwargs.get("version"),
        "nvram_version": kwargs.get("nvram_version"),
        "unsupported_os_detected": kwargs.get("unsupported_os_detected", False),
        "loaded_kexts": kwargs.get("loaded_kexts", []),
        "patched_frameworks": kwargs.get("patched_frameworks", []),
        "amfi_configuration": kwargs.get("amfi_configuration"),
        "boot_args": kwargs.get("boot_args"),
    }


def _base_security() -> dict[str, Any]:
    """SecurityInfo TypedDict."""
    return {
        "security_tools": [],
        "antivirus": [],
        "tcc_permissions": [],
        "code_signing_sample": [
            {
                "app_name": "Safari",
                "identifier": "com.apple.Safari",
                "authority": "Apple",
                "valid": True,
                "team_id": "apple",
            }
        ],
    }


def _base_environment() -> dict[str, Any]:
    """EnvironmentInfo TypedDict."""
    return {
        "shell": "/bin/zsh",
        "python_executable": "/usr/bin/python3",
        "python_version": "3.12.1",
        "path_entries": ["/usr/local/bin", "/usr/bin", "/bin"],
        "path_duplicates": [],
        "listening_ports": [],
        "launchd_services": [],
    }


def _base_battery(
    *,
    present: bool = True,
    percentage: str | None = "67%",
    cycle_count: int | None = 124,
    condition: str | None = "Normal",
    power_source: str | None = "Battery Power",
) -> dict[str, Any]:
    """BatteryInfo TypedDict."""
    return {
        "present": present,
        "percentage": percentage,
        "cycle_count": cycle_count,
        "condition": condition,
        "power_source": power_source,
    }


def _base_nvram() -> dict[str, Any]:
    """NVRAMInfo TypedDict."""
    return {
        "boot_args": "",
        "csr_active_config": "0x0",
        "sip_disabled": False,
        "oclp_version": None,
        "oclp_settings": None,
        "secure_boot_model": None,
        "hardware_model": None,
        "nvram_variables_count": 0,
    }


def _base_ioregistry() -> dict[str, Any]:
    """IORegistryInfo TypedDict."""
    return {
        "pcie_devices": [],
        "usb_devices": [],
        "audio_codecs": [],
    }


def _make_fixture(fixture_name: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a complete fixture matching SystemReport TypedDict."""
    o = overrides or {}
    data: dict[str, Any] = {
        "timestamp": o.get("timestamp", time.time()),
        "system": o.get("system", _base_system()),
        "hardware": o.get("hardware", _base_hardware()),
        "disk": o.get("disk", _base_disk()),
        "top_processes": o.get("top_processes", _base_processes()),
        "startup": o.get("startup", _base_startup()),
        "login_items": o.get("login_items", []),
        "package_managers": o.get("package_managers", _base_package_managers()),
        "developer_tools": o.get("developer_tools", _base_developer_tools()),
        "kexts": o.get("kexts", _base_kexts()),
        "applications": o.get("applications", {"electron_apps": [], "all_apps": []}),
        "environment": o.get("environment", _base_environment()),
        "network": o.get("network", _base_network()),
        "battery": o.get("battery", _base_battery()),
        "cron": o.get("cron", {"user_crontab": []}),
        "diagnostics": o.get("diagnostics", {"recent_crashes": []}),
        "security": o.get("security", _base_security()),
        "cloud": o.get(
            "cloud",
            {
                "sync_status": {
                    "icloud_enabled": False,
                    "icloud_status": "unknown",
                    "drive_enabled": False,
                    "storage_used": None,
                }
            },
        ),
        "nvram": o.get("nvram", _base_nvram()),
        "storage_analysis": o.get(
            "storage_analysis",
            {
                "documents_gb": 0.0,
                "downloads_gb": 0.0,
                "desktop_gb": 0.0,
                "library_gb": 0.0,
                "caches_gb": 0.0,
                "logs_gb": 0.0,
                "total_user_data_gb": 0.0,
            },
        ),
        "fonts": o.get(
            "fonts",
            {
                "system_fonts": 300,
                "user_fonts": 0,
                "total_fonts": 300,
            },
        ),
        "shell_customization": o.get(
            "shell_customization",
            {
                "aliases_count": 0,
                "functions_count": 0,
                "rc_file": ".zshrc",
                "rc_size_kb": 0.0,
            },
        ),
        "opencore_patcher": o.get("opencore_patcher", _base_opencore_patcher()),
        "system_preferences": o.get(
            "system_preferences",
            {
                "trackpad_speed": None,
                "key_repeat_rate": None,
                "mouse_speed": None,
                "scroll_direction_natural": True,
            },
        ),
        "kernel_params": o.get(
            "kernel_params",
            {
                "max_files": 12288,
                "max_processes": 2048,
                "max_vnodes": 132096,
            },
        ),
        "system_logs": o.get(
            "system_logs",
            {
                "critical_errors": [],
                "warnings": [],
                "log_period": "last 1 hour",
            },
        ),
        "ioregistry": o.get("ioregistry", _base_ioregistry()),
        "_fixture_name": fixture_name,
    }
    return data


# ---------------------------------------------------------------------------
# 5 fixture profiles matching the old JSON files
# ---------------------------------------------------------------------------


def make_macbookair_monterey_oclp() -> dict[str, Any]:
    """MacBook Air 2013, Intel Haswell, Monterey via OCLP."""
    return _make_fixture(
        "macbookair6-2_monterey_oclp",
        {
            "timestamp": 1770452643.148194,
            "system": _base_system(
                macos_version="12.7.6",
                macos_name="macOS Monterey",
                model_name="MacBook Air",
                model_identifier="MacBookAir6,2",
                architecture="x86_64",
                filevault_enabled=False,
            ),
            "hardware": _base_hardware(
                cpu="Intel(R) Core(TM) i5-4260U CPU @ 1.40GHz",
                cpu_cores=4,
                memory_gb=4.0,
                gpu=["Intel HD Graphics 5000 (1536 MB)"],
                displays=[
                    _base_display(
                        resolution="1440 x 900",
                        refresh_rate="60 Hz",
                        color_depth="CGSThirtytwoBitColor",
                        external_displays=1,
                    )
                ],
            ),
            "disk": _base_disk(total_gb=233.57, free_gb=167.01),
            "package_managers": _base_package_managers(homebrew=False),
            "opencore_patcher": _base_opencore_patcher(
                detected=True,
                version="2.2.0",
                loaded_kexts=["AMFIPass", "RestrictEvents", "Lilu", "WhateverGreen"],
                patched_frameworks=["CoreDisplay", "SkyLight"],
            ),
            "battery": _base_battery(
                percentage="92%",
                cycle_count=847,
                condition="Service Recommended",
            ),
            "kexts": _base_kexts(
                third_party_kexts=["AMFIPass", "RestrictEvents", "Lilu", "WhateverGreen"]
            ),
        },
    )


def make_macbookpro_sequoia_m1pro() -> dict[str, Any]:
    """MacBook Pro 2021, Apple M1 Pro, Sequoia."""
    return _make_fixture(
        "macbookpro18-1_sequoia_m1pro",
        {
            "timestamp": 1735689600.0,
            "system": _base_system(
                macos_version="15.2",
                macos_name="macOS Sequoia",
                model_name="MacBook Pro",
                model_identifier="MacBookPro18,1",
            ),
            "hardware": _base_hardware(
                cpu="Apple M1 Pro",
                cpu_cores=10,
                memory_gb=16.0,
                gpu=["Apple M1 Pro"],
            ),
            "disk": _base_disk(total_gb=494.38, free_gb=178.92),
            "developer_tools": _base_developer_tools(docker=True),
            "battery": _base_battery(
                percentage="67%",
                cycle_count=124,
                condition="Normal",
            ),
        },
    )


def make_macbookpro_ventura_m1() -> dict[str, Any]:
    """MacBook Pro 2021, Apple M1, Ventura."""
    return _make_fixture(
        "macbookpro18-1_ventura_m1",
        {
            "timestamp": 1735689600.0,
            "system": _base_system(
                macos_version="13.6.3",
                macos_name="macOS Ventura",
                model_name="MacBook Pro",
                model_identifier="MacBookPro18,1",
            ),
            "hardware": _base_hardware(
                cpu="Apple M1",
                cpu_cores=8,
                memory_gb=16.0,
                gpu=["Apple M1"],
            ),
            "disk": _base_disk(total_gb=494.38, free_gb=245.67),
        },
    )


def make_imac_bigsur_intel() -> dict[str, Any]:
    """iMac 2019, Intel Coffee Lake, Big Sur."""
    return _make_fixture(
        "imac19-1_bigsur_intel",
        {
            "timestamp": 1735689600.0,
            "system": _base_system(
                macos_version="11.7.10",
                macos_name="macOS Big Sur",
                model_name="iMac",
                model_identifier="iMac19,1",
                architecture="x86_64",
                marketing_name="iMac (Retina 5K, 27-inch, 2019)",
                board_id="Mac-AA95B1DDAB278B95",
                cpu_generation="Coffee Lake",
                max_os_supported="Ventura",
            ),
            "hardware": _base_hardware(
                cpu="Intel Core i9-9900K",
                cpu_cores=8,
                memory_gb=64.0,
                gpu=["Radeon Pro Vega 48 (8 GB)"],
                displays=[
                    _base_display(
                        resolution="5120 x 2880",
                        refresh_rate="60 Hz",
                        color_depth="CGSThirtytwoBitColor",
                    )
                ],
            ),
            "disk": _base_disk(total_gb=1000.17, free_gb=423.89),
            "developer_tools": _base_developer_tools(docker=True),
        },
    )


def make_macmini_sonoma_server() -> dict[str, Any]:
    """Mac mini 2018, Intel Coffee Lake, Sonoma (server workload)."""
    return _make_fixture(
        "macmini8-1_sonoma_server",
        {
            "timestamp": 1735689600.0,
            "system": _base_system(
                macos_version="14.2.1",
                macos_name="macOS Sonoma",
                model_name="Mac mini",
                model_identifier="Macmini8,1",
                architecture="x86_64",
                marketing_name="Mac mini (2018)",
                board_id="Mac-7BA5B2DFE22DDD8C",
                cpu_generation="Coffee Lake",
                max_os_supported="Sonoma",
            ),
            "hardware": _base_hardware(
                cpu="Intel Core i7-8700B",
                cpu_cores=6,
                memory_gb=16.0,
                gpu=["Intel UHD Graphics 630"],
                displays=[],
            ),
            "disk": _base_disk(total_gb=476.94, free_gb=189.23),
            "battery": _base_battery(
                present=False, percentage=None, cycle_count=None, condition=None, power_source=None
            ),
            "developer_tools": _base_developer_tools(docker=True),
        },
    )


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

ALL_FIXTURE_FACTORIES = [
    make_macbookair_monterey_oclp,
    make_macbookpro_sequoia_m1pro,
    make_macbookpro_ventura_m1,
    make_imac_bigsur_intel,
    make_macmini_sonoma_server,
]


@pytest.fixture
def fixtures_data() -> list[dict[str, Any]]:
    """Generate all fixture profiles in-memory."""
    return [factory() for factory in ALL_FIXTURE_FACTORIES]
