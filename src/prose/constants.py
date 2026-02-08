"""Centralized constants for macOS System Prose.

This module contains all hardcoded values, magic numbers, and configuration
constants used throughout the project to improve maintainability.
"""

from __future__ import annotations


# Default values for missing/unknown data
DEFAULT_UNKNOWN = "Unknown"
DEFAULT_NOT_INSTALLED = "Not installed"
DEFAULT_NOT_CONFIGURED = "Not configured"

# Display constants
DEFAULT_INTERNAL_DISPLAY_REFRESH = "60 Hz"

# Color depth mapping (from CGS constants to human-readable)
COLOR_DEPTH_MAP = {
    "CGSThirtytwoBitColor": "32-bit Color",
    "CGSSixteenBitColor": "16-bit Color",
    "CGSEightBitColor": "8-bit Color",
    "kIO30BitDirectPixels": "30-bit Color (HDR)",
    "kIO24BitDirectPixels": "24-bit Color",
    "kIO16BitDirectPixels": "16-bit Color",
}

# Display connector type mapping
CONNECTOR_TYPE_MAP = {
    "DisplayPort": "DisplayPort",
    "HDMI": "HDMI",
    "DVI": "DVI",
    "VGA": "VGA",
    "Thunderbolt": "Thunderbolt",
    "USB-C": "USB-C",
    "Built-in": "Built-in",
}

# OpenCore Legacy Patcher detection patterns
OCLP_KEXT_PATTERNS = [
    "AMFIPass.kext",
    "RestrictEvents.kext",
    "Lilu.kext",
    "WhateverGreen.kext",
    "FeatureUnlock.kext",
    "AppleALC.kext",
    "CPUFriend.kext",
    "BrightnessKeys.kext",
    "IOSkywalkFamily.kext",
    "IO80211FamilyLegacy.kext",
]

# Patched framework paths for OCLP detection
OCLP_PATCHED_FRAMEWORKS = [
    "/System/Library/Frameworks/OpenCL.framework",
    "/System/Library/Frameworks/IOSurface.framework",
    "/System/Library/PrivateFrameworks/SkyLight.framework",
    "/System/Library/PrivateFrameworks/GPUSupport.framework",
]

# OCLP application and marker file paths
OCLP_APP_PATH = "/Applications/OpenCore-Patcher.app"
OCLP_MARKER_PLIST = "/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist"

# VPN application paths for detection
VPN_APPS = {
    "Tailscale": "/Applications/Tailscale.app",
    "NordVPN": "/Applications/NordVPN.app",
    "ExpressVPN": "/Applications/ExpressVPN.app",
    "ProtonVPN": "/Applications/Proton VPN.app",
    "Mullvad": "/Applications/Mullvad VPN.app",
    "Private Internet Access": "/Applications/Private Internet Access.app",
}

# System preference default values
DEFAULT_TRACKPAD_SPEED = 1.0
DEFAULT_KEY_REPEAT_RATE = 6
DEFAULT_MOUSE_SPEED = 1.0
DEFAULT_SCROLL_SPEED = 1.0


# Command timeout defaults (in seconds)
class Timeouts:
    """Command execution timeout constants."""

    FAST = 5  # Quick commands (version checks)
    STANDARD = 15  # Normal commands (system_profiler)
    SLOW = 30  # Slow commands (package managers)
    VERY_SLOW = 60  # Very slow commands (Homebrew list)
    EXTREME = 120  # Extremely slow commands (full system scan)


# IORegistry class codes
IOREGISTRY_CLASS_CODES = {
    "0x020000": "Ethernet Controller",
    "0x030000": "VGA Controller",
    "0x038000": "Audio Device",
    "0x060400": "PCI Bridge",
    "0x0c0330": "USB Controller (xHCI)",
}

# Security tool detection paths
SECURITY_TOOLS = {
    "Little Snitch": "/Applications/Little Snitch.app",
    "Lulu": "/Applications/LuLu.app",
    "BlockBlock": "/Applications/BlockBlock Helper.app",
    "OverSight": "/Applications/OverSight.app",
    "RansomWhere": "/Applications/RansomWhere.app",
    "KnockKnock": "/Applications/KnockKnock.app",
}

# Antivirus detection paths
ANTIVIRUS_TOOLS = {
    "ClamXav": "/Applications/ClamXav.app",
    "Avast": "/Applications/Avast.app",
    "AVG": "/Applications/AVG AntiVirus.app",
    "Bitdefender": "/Applications/Bitdefender.app",
    "Kaspersky": "/Applications/Kaspersky Internet Security.app",
    "Norton": "/Applications/Norton Security.app",
    "Sophos": "/Applications/Sophos/Sophos Anti-Virus.app",
    "ESET": "/Applications/ESET Cyber Security.app",
}

# App version fallback keys (in order of preference)
APP_VERSION_KEYS = [
    "CFBundleShortVersionString",
    "CFBundleVersion",
    "CFBundleGetInfoString",
]

# Maximum number of apps to sample for code signing verification
MAX_CODE_SIGNING_SAMPLES = 5

# Maximum number of diagnostic logs to collect
MAX_DIAGNOSTIC_LOGS = 10

# Process limits for top_processes
MAX_PROCESSES_BY_CPU = 20
MAX_PROCESSES_BY_MEMORY = 20

# Launch items limits
MAX_LAUNCH_AGENTS = 100
MAX_LAUNCH_DAEMONS = 100

# Browser extensions display limit
MAX_BROWSER_EXTENSIONS = 50
