"""Advanced system data collectors for detailed analysis.

This module contains collectors for storage analysis, fonts, shell customizations,
OpenCore Patcher detection, system preferences, kernel parameters, and system logs.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from prose import utils
from prose.constants import Timeouts
from prose.schema import (
    FontInfo,
    KernelParameters,
    ShellCustomization,
    StorageAnalysis,
    SystemLogs,
    SystemPreferences,
)
from prose.utils import verbose_log



def collect_storage_analysis() -> StorageAnalysis:
    """Analyze storage usage of key user directories."""
    home = Path.home()

    def get_dir_size_gb(path: Path, timeout: int = 30) -> float:
        """Get directory size in GB using du -sk for accuracy.

        SECURITY: Uses subprocess list arguments (no shell interpretation)
        to prevent command injection attacks.
        """
        try:
            if not path.exists():
                return 0.0
            # FIXED: Use list arguments directly - no shell interpretation
            # This prevents command injection even with malicious directory names
            output = utils.run(["du", "-sk", str(path)], timeout=timeout, log_errors=False)
            if output:
                try:
                    # du -sk output: "1234567\t/path/to/dir"
                    size_kb_str = output.split()[0]
                    size_kb = int(size_kb_str)
                    return round(size_kb / 1024 / 1024, 2)  # Convert KB to GB
                except (ValueError, IndexError):
                    return 0.0
            return 0.0
        except (OSError, TimeoutError):
            verbose_log("Failed to get directory size for user data path")
            return 0.0

    documents = get_dir_size_gb(home / "Documents", timeout=Timeouts.SLOW)
    downloads = get_dir_size_gb(home / "Downloads", timeout=Timeouts.SLOW)
    desktop = get_dir_size_gb(home / "Desktop", timeout=Timeouts.FAST)
    library = get_dir_size_gb(home / "Library", timeout=Timeouts.EXTREME)  # Library can be huge
    caches = get_dir_size_gb(home / "Library" / "Caches", timeout=Timeouts.VERY_SLOW)
    logs = get_dir_size_gb(home / "Library" / "Logs", timeout=Timeouts.FAST)

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
        except (OSError, ValueError):
            verbose_log("Failed to analyze shell customization")

    return {
        "aliases_count": aliases_count,
        "functions_count": functions_count,
        "rc_file": f"~/{rc_file.name}",
        "rc_size_kb": round(rc_size_kb, 2),
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
        ["defaults", "read", "-g", "com.apple.trackpad.scaling"],
        log_errors=False,
    )
    if trackpad_output:
        try:
            trackpad_speed = float(trackpad_output.strip())
        except ValueError:
            pass

    # Key repeat rate
    key_repeat_output = utils.run(["defaults", "read", "-g", "KeyRepeat"], log_errors=False)
    if key_repeat_output:
        try:
            key_repeat_rate = int(key_repeat_output.strip())
        except ValueError:
            pass

    # Mouse speed
    mouse_output = utils.run(
        ["defaults", "read", "-g", "com.apple.mouse.scaling"],
        log_errors=False,
    )
    if mouse_output:
        try:
            mouse_speed = float(mouse_output.strip())
        except ValueError:
            pass

    # Scroll direction
    scroll_output = utils.run(
        ["defaults", "read", "-g", "com.apple.swipescrolldirection"],
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
            "log",
            "show",
            "--predicate",
            'messageType == "Error" OR messageType == "Fault"',
            "--style",
            "syslog",
            "--last",
            "1h",
        ],
        timeout=Timeouts.STANDARD,
        log_errors=False,
    )

    if log_output:
        lines = log_output.strip().split("\n")[-20:]
        for line in lines:
            if "Error" in line or "Fault" in line:
                # Extract meaningful part
                if len(line) > 100:
                    line = line[:97] + "..."
                critical_errors.append(line)

    # Get warnings (reduced scope for performance)
    warning_output = utils.run(
        [
            "log",
            "show",
            "--predicate",
            'messageType == "Default"',
            "--style",
            "syslog",
            "--last",
            "1h",
        ],
        timeout=Timeouts.STANDARD,
        log_errors=False,
    )

    if warning_output:
        lines = [line for line in warning_output.strip().split("\n") if "warning" in line.lower()][
            -10:
        ]
        for line in lines:
            if len(line) > 100:
                line = line[:97] + "..."
            warnings.append(line)

    return {
        "critical_errors": critical_errors[:20],
        "warnings": warnings[:15],
        "log_period": "last 1 hour",
    }
