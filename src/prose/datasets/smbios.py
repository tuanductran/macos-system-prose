"""
SMBIOS database for Mac model identification and enrichment.

Model data is loaded from data/smbios_models.json at runtime.
To update: run `python3 scripts/scrape_smbios_models.py --write`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class SMBIOSData(TypedDict):
    """SMBIOS metadata for a Mac model.

    All fields are required and populated from data/smbios_models.json.
    """

    marketing_name: str
    board_id: str
    cpu_generation: str
    max_os_supported: str
    screen_size: int | None
    stock_gpus: list[str]


def _load_smbios_database() -> dict[str, SMBIOSData]:
    """Load SMBIOS database from JSON file."""
    json_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "smbios_models.json"
    if not json_path.exists():
        return {}
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


SMBIOS_DATABASE: dict[str, SMBIOSData] = _load_smbios_database()


def get_smbios_data(model_identifier: str) -> SMBIOSData | None:
    """
    Get SMBIOS metadata for a Mac model identifier.

    Args:
        model_identifier: Model identifier (e.g., "MacBookAir6,2")

    Returns:
        SMBIOS metadata dictionary or None if not found

    Example:
        >>> data = get_smbios_data("MacBookAir6,2")
        >>> data["marketing_name"]
        'MacBook Air (13-inch, Mid 2013)'
    """
    return SMBIOS_DATABASE.get(model_identifier)


def _parse_version_tuple(version_str: str) -> tuple[int, ...]:
    """Parse a version string into a comparable tuple.

    Examples:
        "12" → (12, 0)
        "10.15" → (10, 15)
        "12.7.6" → (12, 7, 6)
    """
    parts = [int(p) for p in version_str.split(".") if p.isdigit()]
    while len(parts) < 2:
        parts.append(0)
    return tuple(parts)


def _build_os_version_map() -> dict[str, tuple[int, ...]]:
    """Build OS name → version tuple map from macos_versions.json."""
    json_path = (
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "macos_versions.json"
    )
    if not json_path.exists():
        return {}
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    result: dict[str, tuple[int, ...]] = {}
    for entry in data.get("versions", []):
        name = entry.get("name", "")
        version = entry.get("version")
        if name and version is not None:
            result[name] = _parse_version_tuple(str(version))
    return result


def is_legacy_mac(model_identifier: str, current_macos_version: str) -> bool:
    """
    Check if a Mac is running an unsupported macOS version (legacy/OCLP).

    Args:
        model_identifier: Model identifier (e.g., "MacBookAir6,2")
        current_macos_version: Current macOS version (e.g., "12.7.6")

    Returns:
        True if running unsupported OS, False otherwise

    Example:
        >>> is_legacy_mac("MacBookAir6,2", "12.7.6")  # Big Sur max, running Monterey
        True
    """
    data = get_smbios_data(model_identifier)
    if not data:
        return False

    os_version_map = _build_os_version_map()
    max_os = data.get("max_os_supported", "")
    max_version = os_version_map.get(max_os, (0, 0))

    # Parse current version major (e.g., "12.7.6" -> (12, 0), "10.15.7" -> (10, 15))
    try:
        parts = current_macos_version.split(".")
        major = int(parts[0])
        if major < 11 and len(parts) > 1:
            current_tuple = (major, int(parts[1]))
        else:
            current_tuple = (major, 0)
    except (ValueError, IndexError):
        return False

    return current_tuple > max_version


__all__ = ["SMBIOS_DATABASE", "SMBIOSData", "get_smbios_data", "is_legacy_mac"]
