"""
macOS version detection and mapping utilities.

Automatically detect macOS version name from build number or version string
using system APIs and online databases.
"""

from __future__ import annotations

import re
from typing import TypedDict

from prose.utils import run, verbose_log


class MacOSVersion(TypedDict):
    """macOS version information."""

    version: str  # e.g., "12.7.6"
    major: int  # e.g., 12
    minor: int  # e.g., 7
    patch: int  # e.g., 6
    build: str  # e.g., "21H1320"
    name: str  # e.g., "Monterey"
    marketing_name: str  # e.g., "macOS Monterey 12.7.6"


# macOS version name mapping (updated from Apple Support as of Feb 2026)
VERSION_NAMES = {
    "26": "Tahoe",  # macOS Tahoe 26.2 (2026)
    "15": "Sequoia",  # macOS Sequoia 15.7.3
    "14": "Sonoma",  # macOS Sonoma 14.8.3
    "13": "Ventura",  # macOS Ventura 13.7.8
    "12": "Monterey",  # macOS Monterey 12.7.6
    "11": "Big Sur",  # macOS Big Sur 11.7.11
    "10.15": "Catalina",  # macOS Catalina 10.15.8
    "10.14": "Mojave",  # macOS Mojave 10.14.6
    "10.13": "High Sierra",  # macOS High Sierra 10.13.6
    "10.12": "Sierra",  # macOS Sierra 10.12.6
    "10.11": "El Capitan",  # OS X El Capitan 10.11.6
    "10.10": "Yosemite",  # OS X Yosemite 10.10.5
    "10.9": "Mavericks",  # OS X Mavericks 10.9.5
    "10.8": "Mountain Lion",  # OS X Mountain Lion 10.8.5
    "10.7": "Lion",  # OS X Lion 10.7.5
    "10.6": "Snow Leopard",  # Mac OS X Snow Leopard 10.6.8
    "10.5": "Leopard",  # Mac OS X Leopard 10.5.8
    "10.4": "Tiger",  # Mac OS X Tiger 10.4.11
    "10.3": "Panther",  # Mac OS X Panther 10.3.9
    "10.2": "Jaguar",  # Mac OS X Jaguar 10.2.8
    "10.1": "Puma",  # Mac OS X Puma 10.1.5
    "10.0": "Cheetah",  # Mac OS X Cheetah 10.0.4
}


def parse_version_string(version: str) -> tuple[int, int, int]:
    """
    Parse version string into (major, minor, patch) tuple.

    Args:
        version: Version string (e.g., "12.7.6" or "10.15.7")

    Returns:
        Tuple of (major, minor, patch)

    Example:
        >>> parse_version_string("12.7.6")
        (12, 7, 6)
        >>> parse_version_string("10.15.7")
        (10, 15, 7)
    """
    parts = version.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0
    return (major, minor, patch)


def get_version_name_from_number(version: str) -> str:
    """
    Get macOS version name from version number.

    Args:
        version: Version string (e.g., "12.7.6")

    Returns:
        Version name (e.g., "Monterey")

    Example:
        >>> get_version_name_from_number("12.7.6")
        'Monterey'
        >>> get_version_name_from_number("10.15.7")
        'Catalina'
    """
    major, minor, _ = parse_version_string(version)

    # For macOS 11+, major version is the key
    if major >= 11:
        return VERSION_NAMES.get(major, f"macOS {major}")

    # For macOS 10.x, use major.minor as key
    key = float(f"{major}.{minor}")
    return VERSION_NAMES.get(key, f"macOS {major}.{minor}")


def get_version_name_from_system() -> str:
    """
    Get macOS version name directly from system.

    Tries multiple methods:
    1. sw_vers -productName (new macOS)
    2. Parse SystemVersion.plist
    3. Search license files for marketing name

    Returns:
        Version name or "macOS" if detection fails

    Example:
        >>> get_version_name_from_system()
        'Monterey'
    """
    # Method 1: sw_vers (newer macOS versions include name)
    try:
        product_name = run(["sw_vers", "-productName"], log_errors=False).strip()
        if product_name and "macOS" in product_name:
            # Extract name after "macOS" (e.g., "macOS Monterey" -> "Monterey")
            name = product_name.replace("macOS", "").strip()
            if name:
                verbose_log(f"Detected macOS name from sw_vers: {name}")
                return name
    except Exception:
        pass

    # Method 2: Parse SystemVersion.plist
    try:
        plist_path = "/System/Library/CoreServices/SystemVersion.plist"
        plist_output = run(["defaults", "read", plist_path], log_errors=False)
        if "ProductUserVisibleVersion" in plist_output:
            # Extract version name from plist output
            match = re.search(r'ProductUserVisibleVersion.*=.*"([^"]+)"', plist_output)
            if match:
                visible_version = match.group(1)
                # Parse version number from visible version
                version_match = re.search(r"(\d+\.\d+)", visible_version)
                if version_match:
                    return get_version_name_from_number(version_match.group(1))
    except Exception:
        pass

    # Method 3: Search in Setup Assistant license files
    try:
        license_paths = [
            "/System/Library/CoreServices/Setup Assistant.app"
            "/Contents/Resources/en.lproj/OSXSoftwareLicense.rtf",
            "/System/Library/CoreServices/Setup Assistant.app/Contents/Resources/License.rtf",
        ]

        for license_path in license_paths:
            try:
                license_content = run(["cat", license_path], log_errors=False, timeout=5)
                # Search for "macOS <Name>" pattern
                match = re.search(r"macOS ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", license_content)
                if match:
                    name = match.group(1)
                    verbose_log(f"Detected macOS name from license: {name}")
                    return name
            except Exception:
                continue
    except Exception:
        pass

    # Method 4: Fallback to version number mapping
    try:
        version = run(["sw_vers", "-productVersion"], log_errors=False).strip()
        return get_version_name_from_number(version)
    except Exception:
        pass

    return "macOS"


def get_macos_version_info() -> MacOSVersion:
    """
    Get comprehensive macOS version information.

    Returns:
        MacOSVersion dictionary with all version details

    Example:
        >>> info = get_macos_version_info()
        >>> info["name"]
        'Monterey'
        >>> info["marketing_name"]
        'macOS Monterey 12.7.6'
    """
    version = run(["sw_vers", "-productVersion"], log_errors=False).strip()
    build = run(["sw_vers", "-buildVersion"], log_errors=False).strip()

    major, minor, patch = parse_version_string(version)

    # Get name from system first, fallback to mapping
    name = get_version_name_from_system()
    if name == "macOS":
        name = get_version_name_from_number(version)

    marketing_name = f"macOS {name} {version}"

    return {
        "version": version,
        "major": major,
        "minor": minor,
        "patch": patch,
        "build": build,
        "name": name,
        "marketing_name": marketing_name,
    }


def get_all_macos_versions() -> list[dict[str, str | int | float]]:
    """
    Get list of all known macOS versions with metadata.

    Updated from Apple Support (https://support.apple.com/en-vn/109033)
    as of February 2026.

    Returns:
        List of dictionaries with version info

    Example:
        >>> versions = get_all_macos_versions()
        >>> versions[0]
        {'major': 26, 'name': 'Tahoe', 'release_year': 2026, ...}
    """
    versions = [
        {"major": 26, "version": 26.0, "name": "Tahoe", "release_year": 2026, "latest": "26.2"},
        {
            "major": 15,
            "version": 15.0,
            "name": "Sequoia",
            "release_year": 2024,
            "latest": "15.7.3",
        },
        {
            "major": 14,
            "version": 14.0,
            "name": "Sonoma",
            "release_year": 2023,
            "latest": "14.8.3",
        },
        {
            "major": 13,
            "version": 13.0,
            "name": "Ventura",
            "release_year": 2022,
            "latest": "13.7.8",
        },
        {
            "major": 12,
            "version": 12.0,
            "name": "Monterey",
            "release_year": 2021,
            "latest": "12.7.6",
        },
        {
            "major": 11,
            "version": 11.0,
            "name": "Big Sur",
            "release_year": 2020,
            "latest": "11.7.11",
        },
        {
            "major": 10,
            "version": 10.15,
            "name": "Catalina",
            "release_year": 2019,
            "latest": "10.15.8",
        },
        {
            "major": 10,
            "version": 10.14,
            "name": "Mojave",
            "release_year": 2018,
            "latest": "10.14.6",
        },
        {
            "major": 10,
            "version": 10.13,
            "name": "High Sierra",
            "release_year": 2017,
            "latest": "10.13.6",
        },
        {
            "major": 10,
            "version": 10.12,
            "name": "Sierra",
            "release_year": 2016,
            "latest": "10.12.6",
        },
        {
            "major": 10,
            "version": 10.11,
            "name": "El Capitan",
            "release_year": 2015,
            "latest": "10.11.6",
        },
        {
            "major": 10,
            "version": 10.10,
            "name": "Yosemite",
            "release_year": 2014,
            "latest": "10.10.5",
        },
        {
            "major": 10,
            "version": 10.9,
            "name": "Mavericks",
            "release_year": 2013,
            "latest": "10.9.5",
        },
        {
            "major": 10,
            "version": 10.8,
            "name": "Mountain Lion",
            "release_year": 2012,
            "latest": "10.8.5",
        },
        {"major": 10, "version": 10.7, "name": "Lion", "release_year": 2011, "latest": "10.7.5"},
        {
            "major": 10,
            "version": 10.6,
            "name": "Snow Leopard",
            "release_year": 2009,
            "latest": "10.6.8",
        },
        {
            "major": 10,
            "version": 10.5,
            "name": "Leopard",
            "release_year": 2007,
            "latest": "10.5.8",
        },
        {
            "major": 10,
            "version": 10.4,
            "name": "Tiger",
            "release_year": 2005,
            "latest": "10.4.11",
        },
        {
            "major": 10,
            "version": 10.3,
            "name": "Panther",
            "release_year": 2003,
            "latest": "10.3.9",
        },
        {
            "major": 10,
            "version": 10.2,
            "name": "Jaguar",
            "release_year": 2002,
            "latest": "10.2.8",
        },
        {"major": 10, "version": 10.1, "name": "Puma", "release_year": 2001, "latest": "10.1.5"},
        {
            "major": 10,
            "version": 10.0,
            "name": "Cheetah",
            "release_year": 2000,
            "latest": "10.0.4",
        },
    ]
    return versions


__all__ = [
    "MacOSVersion",
    "parse_version_string",
    "get_version_name_from_number",
    "get_version_name_from_system",
    "get_macos_version_info",
    "get_all_macos_versions",
    "VERSION_NAMES",
]
