"""Advanced system data collectors for detailed analysis.

This module contains collectors for storage analysis, fonts, shell customizations,
OpenCore Patcher detection, system preferences, kernel parameters, and system logs.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from prose import utils
from prose.datasets.smbios import is_legacy_mac
from prose.iokit import get_boot_args, get_oclp_nvram_version, parse_amfi_boot_arg
from prose.schema import (
    FontInfo,
    KernelParameters,
    OpenCorePatcherInfo,
    ShellCustomization,
    StorageAnalysis,
    SystemLogs,
    SystemPreferences,
)


def collect_storage_analysis() -> StorageAnalysis:
    """Analyze storage usage of key user directories."""
    home = Path.home()

    def get_dir_size_gb(path: Path, timeout: int = 30) -> float:
        """Get directory size in GB using du -sk for accuracy."""
        try:
            if not path.exists():
                return 0.0
            # Use -sk to get size in KB
            output = utils.run(
                ["bash", "-c", f"du -sk '{path}' 2>/dev/null"], timeout=timeout, log_errors=False
            )
            if output:
                try:
                    # du -sk output: "1234567\t/path/to/dir"
                    size_kb_str = output.split()[0]
                    size_kb = int(size_kb_str)
                    return round(size_kb / 1024 / 1024, 2)  # Convert KB to GB
                except (ValueError, IndexError):
                    return 0.0
            return 0.0
        except Exception:
            return 0.0

    documents = get_dir_size_gb(home / "Documents", timeout=30)
    downloads = get_dir_size_gb(home / "Downloads", timeout=30)
    desktop = get_dir_size_gb(home / "Desktop", timeout=10)
    library = get_dir_size_gb(home / "Library", timeout=120)  # Library can be huge
    caches = get_dir_size_gb(home / "Library" / "Caches", timeout=60)
    logs = get_dir_size_gb(home / "Library" / "Logs", timeout=10)

    return {
        "documents_gb": documents,
        "downloads_gb": downloads,
        "desktop_gb": desktop,
        "library_gb": library,
        "caches_gb": caches,
        "logs_gb": logs,
        "total_user_data_gb": documents + downloads + desktop + library,
    }


def collect_fonts() -> FontInfo:
    """Collect installed fonts information."""
    system_fonts = 0
    user_fonts = 0

    # System fonts
    system_font_dir = Path("/System/Library/Fonts")
    if system_font_dir.exists():
        for ext in ("*.ttf", "*.otf", "*.ttc", "*.dfont"):
            system_fonts += len(list(system_font_dir.glob(ext)))

    # User fonts
    user_font_dir = Path.home() / "Library" / "Fonts"
    if user_font_dir.exists():
        for ext in ("*.ttf", "*.otf", "*.ttc", "*.dfont"):
            user_fonts += len(list(user_font_dir.glob(ext)))

    return {
        "system_fonts": system_fonts,
        "user_fonts": user_fonts,
        "total_fonts": system_fonts + user_fonts,
    }


def collect_shell_customization() -> ShellCustomization:
    """Analyze shell customization (aliases, functions, rc files)."""
    home = Path.home()
    shell = os.environ.get("SHELL", "")

    # Determine RC file
    if "zsh" in shell:
        rc_file = home / ".zshrc"
    elif "bash" in shell:
        rc_file = home / ".bashrc"
    else:
        rc_file = home / ".profile"

    aliases_count = 0
    functions_count = 0
    rc_size_kb = 0.0

    if rc_file.exists():
        try:
            content = rc_file.read_text()
            # Count aliases
            aliases_count = len(re.findall(r"^\s*alias\s+", content, re.MULTILINE))
            # Count functions (both `function name` and `name()` syntax)
            functions_count = len(
                re.findall(r"^\s*(?:function\s+\w+|(\w+)\s*\(\)\s*\{)", content, re.MULTILINE)
            )
            # Get size
            rc_size_kb = rc_file.stat().st_size / 1024
        except Exception:
            pass

    return {
        "aliases_count": aliases_count,
        "functions_count": functions_count,
        "rc_file": str(rc_file),
        "rc_size_kb": round(rc_size_kb, 2),
    }


def collect_opencore_patcher(loaded_kexts: list[str] | None = None) -> OpenCorePatcherInfo:
    """Detect OpenCore Patcher installation and configuration.

    Enhanced detection with NVRAM, root patches, and AMFI configuration.

    Args:
        loaded_kexts: Optional list of currently loaded kexts from kextstat.
                      If None, will be collected internally.
    """
    detected = False
    version = None
    nvram_version = None
    patched_kexts: list[str] = []
    patched_frameworks: list[str] = []
    amfi_config = None
    boot_args = None

    # Get current macOS version and model
    current_os = utils.run(
        ["bash", "-c", "sw_vers -productVersion"],
        log_errors=False,
    ).strip()

    model_info = utils.run(
        ["bash", "-c", "system_profiler SPHardwareDataType | grep 'Model Identifier'"],
        log_errors=False,
    )
    current_model = ""
    if model_info:
        current_model = model_info.split(":")[-1].strip()

    # Method 1: Check NVRAM for OCLP-Version (most reliable)
    nvram_version = get_oclp_nvram_version()
    if nvram_version:
        detected = True
        # Clean null bytes (\x00 and %00)
        version = nvram_version.replace("\x00", "").replace("%00", "")
        utils.verbose_log(f"OCLP detected via NVRAM: {version}")

    # Method 2: Check if OpenCore-Patcher.app exists
    oclp_app = Path("/Applications/OpenCore-Patcher.app")
    if oclp_app.exists():
        detected = True
        if not version:
            # Try to get version from app bundle
            version_output = utils.run(
                [
                    "bash",
                    "-c",
                    "defaults read /Applications/OpenCore-Patcher.app/Contents/Info.plist "
                    "CFBundleShortVersionString",
                ],
                log_errors=False,
            )
            if version_output:
                version = version_output.strip()

    # Method 3: Check for root patches (OCLP indicator)
    root_patch_marker = Path("/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist")
    if root_patch_marker.exists():
        detected = True
        utils.verbose_log("OCLP root patch marker found")

    # Get loaded kexts (either passed or collect them)
    if loaded_kexts is None:
        kextstat_output = utils.run(["kextstat", "-l"], log_errors=False)
        loaded_kexts = []
        for line in kextstat_output.splitlines():
            if "com.apple" not in line and not line.startswith("Index"):
                match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+)\s\(([^)]+)\)", line)
                if match:
                    loaded_kexts.append(f"{match.group(1)} ({match.group(2)})")

    # Check for OCLP signature kexts in loaded kexts
    oclp_kext_patterns = [
        "AMFIPass",
        "RestrictEvents",
        "Lilu",
        "WhateverGreen",
        "FeatureUnlock",
        "AutoPkgInstaller",
        "RSRHelper",
        "AirportBrcmFixup",
        "DebugEnhancer",
        "CryptexFixup",
    ]

    for kext_info in loaded_kexts:
        for pattern in oclp_kext_patterns:
            if pattern in kext_info:
                patched_kexts.append(kext_info)
                break

    # Method 4: Detect patched frameworks
    patched_framework_paths = [
        "/System/Library/Extensions/AppleIntelHDGraphics.kext",  # Gen6 GPU
        "/System/Library/Extensions/AppleIntelHD3000Graphics.kext",  # Gen7 GPU
        "/System/Library/Extensions/AppleIntelSNBGraphicsFB.kext",  # Sandy Bridge
        "/System/Library/Extensions/IOBluetoothFamily.kext",  # Bluetooth patches
    ]

    for fw_path in patched_framework_paths:
        if Path(fw_path).exists():
            patched_frameworks.append(fw_path)
            utils.verbose_log(f"Patched framework found: {fw_path}")

    # Method 5: Check for unsupported OS (SMBIOS-based)
    unsupported_os_detected = False
    if current_os and current_model:
        unsupported_os_detected = is_legacy_mac(current_model, current_os)
        if unsupported_os_detected:
            utils.verbose_log(
                f"{current_model} running {current_os} (unsupported) - likely OCLP patched"
            )

    # Method 6: Get boot-args and parse AMFI configuration
    boot_args = get_boot_args()
    if boot_args:
        amfi_config = parse_amfi_boot_arg(boot_args)
        if amfi_config["amfi_value"]:
            utils.verbose_log(f"AMFI configuration: {amfi_config['amfi_value']}")

    # If unsupported OS + OCLP kexts present, highly likely OCLP is in use
    if unsupported_os_detected and patched_kexts and not detected:
        detected = True
        version = version or "Detected (version unknown)"

    clean_nvram_version = None
    if nvram_version:
        clean_nvram_version = nvram_version.replace("\x00", "").replace("%00", "")

    return {
        "detected": detected,
        "version": version,
        "nvram_version": clean_nvram_version,
        "unsupported_os_detected": unsupported_os_detected,
        "loaded_kexts": patched_kexts[:10],  # Limit to first 10 for brevity
        "patched_frameworks": patched_frameworks,
        "amfi_configuration": amfi_config if amfi_config and amfi_config["amfi_value"] else None,
        "boot_args": boot_args,
    }


def collect_system_preferences() -> SystemPreferences:
    """Collect key system preferences.

    When user hasn't explicitly changed a preference, macOS uses internal
    defaults that aren't stored in the user domain. We fall back to the
    documented macOS defaults in that case.
    """
    # macOS default values (used when user hasn't customized)
    default_trackpad = 1.0  # Medium tracking speed
    default_key_repeat = 6  # Normal repeat rate (unit: 15 ms tick)
    default_mouse = 1.0  # Medium tracking speed

    trackpad_speed: float | None = default_trackpad
    key_repeat_rate: int | None = default_key_repeat
    mouse_speed: float | None = default_mouse
    scroll_direction_natural = True

    # Trackpad tracking speed
    trackpad_output = utils.run(
        ["bash", "-c", "defaults read -g com.apple.trackpad.scaling 2>/dev/null"],
        log_errors=False,
    )
    if trackpad_output:
        try:
            trackpad_speed = float(trackpad_output.strip())
        except ValueError:
            pass

    # Key repeat rate
    key_repeat_output = utils.run(
        ["bash", "-c", "defaults read -g KeyRepeat 2>/dev/null"], log_errors=False
    )
    if key_repeat_output:
        try:
            key_repeat_rate = int(key_repeat_output.strip())
        except ValueError:
            pass

    # Mouse speed
    mouse_output = utils.run(
        ["bash", "-c", "defaults read -g com.apple.mouse.scaling 2>/dev/null"],
        log_errors=False,
    )
    if mouse_output:
        try:
            mouse_speed = float(mouse_output.strip())
        except ValueError:
            pass

    # Scroll direction
    scroll_output = utils.run(
        ["bash", "-c", "defaults read -g com.apple.swipescrolldirection 2>/dev/null"],
        log_errors=False,
    )
    if scroll_output and "0" in scroll_output:
        scroll_direction_natural = False

    return {
        "trackpad_speed": trackpad_speed,
        "key_repeat_rate": key_repeat_rate,
        "mouse_speed": mouse_speed,
        "scroll_direction_natural": scroll_direction_natural,
    }


def collect_kernel_parameters() -> KernelParameters:
    """Collect important kernel parameters via sysctl."""
    max_files = 0
    max_processes = 0
    max_vnodes = 0

    # Max files
    output = utils.run(["sysctl", "-n", "kern.maxfiles"], log_errors=False)
    if output:
        try:
            max_files = int(output.strip())
        except ValueError:
            pass

    # Max processes
    output = utils.run(["sysctl", "-n", "kern.maxproc"], log_errors=False)
    if output:
        try:
            max_processes = int(output.strip())
        except ValueError:
            pass

    # Max vnodes
    output = utils.run(["sysctl", "-n", "kern.maxvnodes"], log_errors=False)
    if output:
        try:
            max_vnodes = int(output.strip())
        except ValueError:
            pass

    return {"max_files": max_files, "max_processes": max_processes, "max_vnodes": max_vnodes}


def collect_system_logs() -> SystemLogs:
    """Collect critical system logs from last 1 hour."""
    critical_errors: list[str] = []
    warnings: list[str] = []

    # Get logs from last 1 hour using log command
    # Note: log show is VERY slow, so we use aggressive timeout and limit
    log_output = utils.run(
        [
            "bash",
            "-c",
            'log show --predicate \'messageType == "Error" OR messageType == "Fault"\' '
            "--style syslog --last 1h 2>/dev/null | tail -20",  # Reduced from 24h to 1h, 50 to 20
        ],
        timeout=15,  # Reduced from 30s to 15s
        log_errors=False,
    )

    if log_output:
        lines = log_output.strip().split("\n")
        for line in lines:
            if "Error" in line or "Fault" in line:
                # Extract meaningful part
                if len(line) > 100:
                    line = line[:97] + "..."
                critical_errors.append(line)

    # Get warnings (reduced scope for performance)
    warning_output = utils.run(
        [
            "bash",
            "-c",
            "log show --predicate 'messageType == \"Default\"' "
            "--style syslog --last 1h 2>/dev/null | grep -i warning | tail -10",
        ],
        timeout=15,  # Reduced from 30s to 15s
        log_errors=False,
    )

    if warning_output:
        lines = warning_output.strip().split("\n")
        for line in lines[:15]:  # Limit to 15 warnings
            if len(line) > 100:
                line = line[:97] + "..."
            warnings.append(line)

    return {
        "critical_errors": critical_errors[:20],
        "warnings": warnings[:15],
        "log_period": "last 1 hour",
    }
