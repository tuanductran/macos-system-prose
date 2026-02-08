"""Parsing utilities for system command outputs.

This module contains reusable functions for parsing various system command outputs,
reducing code duplication across collectors.
"""

from __future__ import annotations

import re


def parse_uptime(uptime_output: str) -> str:
    """Parse uptime command output to human-readable format.

    Args:
        uptime_output: Raw output from 'uptime' command

    Returns:
        Human-readable uptime string (e.g., "5 days, 3 hours")

    Examples:
        >>> parse_uptime("10:30  up 5 days,  3:45, 2 users")
        "5 days, 3 hours"
    """
    if not uptime_output:
        return "Unknown"

    # Match patterns like "5 days" or "3:45" (hours:minutes)
    days_match = re.search(r"(\d+)\s+day", uptime_output)
    time_match = re.search(r"up\s+(?:\d+\s+days?,\s*)?(\d+):(\d+)", uptime_output)

    parts = []
    if days_match:
        parts.append(f"{days_match.group(1)} days")
    if time_match:
        hours = int(time_match.group(1))
        if hours > 0:
            parts.append(f"{hours} hours")

    return ", ".join(parts) if parts else "Unknown"


def parse_boot_time(uptime_output: str) -> str:
    """Extract boot time from uptime output.

    Args:
        uptime_output: Raw output from 'uptime' command

    Returns:
        Boot time string or "Unknown"
    """
    if not uptime_output:
        return "Unknown"

    # Try to extract boot time if present
    match = re.search(r"boot time:\s*(.+)", uptime_output)
    if match:
        return match.group(1).strip()

    return "Unknown"


def parse_load_average(uptime_output: str) -> dict[str, float]:
    """Parse load average from uptime output.

    Args:
        uptime_output: Raw output from 'uptime' command

    Returns:
        Dictionary with keys: load_1m, load_5m, load_15m

    Examples:
        >>> parse_load_average("10:30  up 5 days, load averages: 2.15 1.80 1.65")
        {"load_1m": 2.15, "load_5m": 1.80, "load_15m": 1.65}
    """
    default = {"load_1m": 0.0, "load_5m": 0.0, "load_15m": 0.0}

    if not uptime_output:
        return default

    # Match load average pattern
    match = re.search(r"load averages?:\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)", uptime_output)
    if match:
        try:
            return {
                "load_1m": float(match.group(1)),
                "load_5m": float(match.group(2)),
                "load_15m": float(match.group(3)),
            }
        except ValueError:
            pass

    return default


def parse_version_line(output: str) -> str:
    """Extract version from first line of command output.

    Common pattern: many commands output "Name X.Y.Z" on first line.

    Args:
        output: Raw command output

    Returns:
        First non-empty line, stripped

    Examples:
        >>> parse_version_line("Python 3.11.5\\nAdditional info...")
        "Python 3.11.5"
    """
    if not output:
        return "Not installed"

    lines = output.strip().splitlines()
    return lines[0].strip() if lines else "Not installed"


def parse_int_from_string(text: str, default: int = 0) -> int:
    """Extract first integer from string using regex.

    Args:
        text: String containing integers
        default: Default value if no integer found

    Returns:
        First integer found or default

    Examples:
        >>> parse_int_from_string("Total: 42 items")
        42
        >>> parse_int_from_string("No numbers", default=0)
        0
    """
    match = re.search(r"\d+", text)
    if match:
        try:
            return int(match.group(0))
        except ValueError:
            pass
    return default


def parse_float_from_string(text: str, default: float = 0.0) -> float:
    """Extract first float from string using regex.

    Args:
        text: String containing floats
        default: Default value if no float found

    Returns:
        First float found or default

    Examples:
        >>> parse_float_from_string("Speed: 2.5 GHz")
        2.5
    """
    match = re.search(r"[\d.]+", text)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            pass
    return default


def parse_plist_value(
    plist_dict: dict[str, str | int | float | bool | list[str] | dict[str, str]],
    key: str,
    default: str | int | float | bool | None = None,
) -> str | int | float | bool | list[str] | dict[str, str] | None:
    """Safely extract value from plist dictionary with default.

    Args:
        plist_dict: Dictionary from plist parsing
        key: Key to extract
        default: Default value if key missing

    Returns:
        Value from dict or default
    """
    return plist_dict.get(key, default)


def parse_defaults_read(
    output: str, expected_type: type[str | int | float | bool] = str
) -> str | int | float | bool | None:
    """Parse output from 'defaults read' command.

    Args:
        output: Raw output from defaults read
        expected_type: Expected Python type (str, int, float, bool)

    Returns:
        Parsed value or None if parsing fails

    Examples:
        >>> parse_defaults_read("1.5", float)
        1.5
        >>> parse_defaults_read("42", int)
        42
    """
    if not output:
        return None

    output = output.strip()

    try:
        if expected_type is bool:
            return output.lower() in ("1", "true", "yes")
        elif expected_type is int:
            return int(output)
        elif expected_type is float:
            return float(output)
        else:
            return output
    except (ValueError, AttributeError):
        return None


def parse_key_value_line(line: str, separator: str = ":") -> tuple[str, str] | None:
    """Parse a "key: value" line into tuple.

    Args:
        line: Line in "key: value" format
        separator: Separator character (default: ":")

    Returns:
        Tuple of (key, value) or None if invalid format

    Examples:
        >>> parse_key_value_line("Name: John")
        ("Name", "John")
    """
    if separator not in line:
        return None

    parts = line.split(separator, 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()

    return None


def clean_null_bytes(text: str) -> str:
    """Remove null bytes from string (common in NVRAM data).

    Args:
        text: String potentially containing null bytes

    Returns:
        Cleaned string

    Examples:
        >>> clean_null_bytes("text%00with%00nulls")
        "textwwithnullss"
    """
    return text.replace("%00", "").replace("\x00", "")


def parse_size_to_gb(size_str: str) -> float:
    """Parse size string (with units) to GB.

    Args:
        size_str: Size with unit (e.g., "500 MB", "1.5 TB")

    Returns:
        Size in GB

    Examples:
        >>> parse_size_to_gb("500 MB")
        0.5
        >>> parse_size_to_gb("2 TB")
        2000.0
    """
    if not size_str:
        return 0.0

    size_str = size_str.upper().strip()

    # Extract number and unit
    match = re.match(r"([\d.]+)\s*([KMGT]?B)", size_str)
    if not match:
        return 0.0

    try:
        value = float(match.group(1))
        unit = match.group(2)

        # Convert to GB
        multipliers = {
            "B": 1 / (1024**3),
            "KB": 1 / (1024**2),
            "MB": 1 / 1024,
            "GB": 1,
            "TB": 1024,
        }

        return value * multipliers.get(unit, 1)
    except ValueError:
        return 0.0
