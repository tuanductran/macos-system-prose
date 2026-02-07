"""
macOS version detection and mapping utilities.

Version names and metadata are loaded from data/macos_versions.json at runtime.
To update: run ``python3 scripts/scrape_macos_versions.py``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
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


def _load_versions_json() -> dict:
    """Load macOS version data from JSON file."""
    json_path = Path(__file__).resolve().parent.parent.parent / "data" / "macos_versions.json"
    if not json_path.exists():
        return {"version_names": {}, "versions": []}
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


_VERSIONS_DATA = _load_versions_json()
VERSION_NAMES: dict[str, str] = _VERSIONS_DATA.get("version_names", {})


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
        return VERSION_NAMES.get(str(major), f"macOS {major}")

    # For macOS 10.x, use major.minor as key
    key = f"{major}.{minor}"
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


def get_all_macos_versions() -> list[dict[str, object]]:
    """
    Get list of all known macOS versions with metadata.

    Data is loaded from data/macos_versions.json. To update, run:
        python3 scripts/scrape_macos_versions.py

    Returns:
        List of dictionaries with version info
    """
    return _VERSIONS_DATA.get("versions", [])  # type: ignore[no-any-return]


__all__ = [
    "MacOSVersion",
    "parse_version_string",
    "get_version_name_from_number",
    "get_version_name_from_system",
    "get_macos_version_info",
    "get_all_macos_versions",
    "VERSION_NAMES",
]
