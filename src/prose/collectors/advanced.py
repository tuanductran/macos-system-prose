"""Advanced system data collectors for detailed analysis.

This module contains collectors for storage analysis, fonts, shell customizations,
OpenCore Patcher detection, system preferences, kernel parameters, and system logs.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from prose import utils
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

    def get_dir_size_gb(path: Path) -> float:
        """Get directory size in GB using du -sk for accuracy."""
        try:
            if not path.exists():
                return 0.0
            # Use -sk to get size in KB
            output = utils.run(
                ["bash", "-c", f"du -sk '{path}' 2>/dev/null"], timeout=30, log_errors=False
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

    documents = get_dir_size_gb(home / "Documents")
    downloads = get_dir_size_gb(home / "Downloads")
    desktop = get_dir_size_gb(home / "Desktop")
    library = get_dir_size_gb(home / "Library")
    caches = get_dir_size_gb(home / "Library" / "Caches")
    logs = get_dir_size_gb(home / "Library" / "Logs")

    return {
        "documents_gb": documents,
        "downloads_gb": downloads,
        "desktop_gb": desktop,
        "library_gb": library,
        "caches_gb": caches,
        "logs_gb": logs,
        "total_user_data_gb": documents + downloads + desktop,
    }


def collect_fonts() -> FontInfo:
    """Collect installed fonts information."""
    system_fonts = 0
    user_fonts = 0

    # System fonts
    system_font_dir = Path("/System/Library/Fonts")
    if system_font_dir.exists():
        system_fonts = len(list(system_font_dir.glob("*.ttf"))) + len(
            list(system_font_dir.glob("*.otf"))
        )

    # User fonts
    user_font_dir = Path.home() / "Library" / "Fonts"
    if user_font_dir.exists():
        user_fonts = len(list(user_font_dir.glob("*.ttf"))) + len(list(user_font_dir.glob("*.otf")))

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
            # Count functions
            functions_count = len(re.findall(r"^\s*function\s+", content, re.MULTILINE))
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


def collect_opencore_patcher() -> OpenCorePatcherInfo:
    """Detect OpenCore Patcher installation and configuration."""
    oclp_installed = False
    version = None
    root_patched = False
    patched_kexts: list[str] = []
    patched_frameworks: list[str] = []
    smbios_spoofed = False
    original_model = None

    # Check if OpenCore-Patcher.app exists
    oclp_app = Path("/Applications/OpenCore-Patcher.app")
    if oclp_app.exists():
        oclp_installed = True
        # Try to get version
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

    # Check for root patches (common OCLP indicator)
    root_patch_marker = Path("/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist")
    if root_patch_marker.exists():
        root_patched = True

    # Check for patched kexts in /Library/Extensions
    kext_dir = Path("/Library/Extensions")
    if kext_dir.exists():
        # Common OCLP kexts
        oclp_kext_patterns = [
            "AMFIPass",
            "RestrictEvents",
            "Lilu",
            "WhateverGreen",
            "FeatureUnlock",
            "AutoPkgInstaller",
            "RSRHelper",
            "AirportBrcmFixup",
        ]
        for pattern in oclp_kext_patterns:
            matching_kexts = list(kext_dir.glob(f"*{pattern}*.kext"))
            if matching_kexts:
                patched_kexts.extend([k.name for k in matching_kexts])

    # Check for SMBIOS spoofing (RestrictEvents indicates this)
    if any("RestrictEvents" in k for k in patched_kexts):
        smbios_spoofed = True
        # Try to detect original model from system_profiler
        model_info = utils.run(
            ["bash", "-c", "system_profiler SPHardwareDataType | grep 'Model Identifier'"],
            log_errors=False,
        )
        if model_info:
            original_model = model_info.split(":")[-1].strip()

    return {
        "installed": oclp_installed,
        "version": version,
        "root_patched": root_patched,
        "patched_kexts": patched_kexts,
        "patched_frameworks": patched_frameworks,
        "smbios_spoofed": smbios_spoofed,
        "original_model": original_model,
    }


def collect_system_preferences() -> SystemPreferences:
    """Collect key system preferences."""
    trackpad_speed = None
    key_repeat_rate = None
    mouse_speed = None
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
    """Collect critical system logs from last 24 hours."""
    critical_errors: list[str] = []
    warnings: list[str] = []

    # Get logs from last 24 hours using log command
    log_output = utils.run(
        [
            "bash",
            "-c",
            'log show --predicate \'messageType == "Error" OR messageType == "Fault"\' '
            "--style syslog --last 24h 2>/dev/null | tail -50",
        ],
        timeout=30,
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

    # Get warnings
    warning_output = utils.run(
        [
            "bash",
            "-c",
            "log show --predicate 'messageType == \"Default\"' "
            "--style syslog --last 24h 2>/dev/null | grep -i warning | tail -30",
        ],
        timeout=30,
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
        "log_period": "last 24 hours",
    }
