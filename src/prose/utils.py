"""Utility functions for macOS System Prose.

This module provides helper functions for executing system commands,
parsing output, logging, and file operations.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union

VERBOSE = False
QUIET = False


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


def log(msg: str, level: str = "info") -> None:
    """Log a message with color coding based on severity level.

    Args:
        msg: The message to log.
        level: Severity level (info, success, warning, error, header).
    """
    if QUIET:
        return
    colors = {
        "info": Colors.CYAN,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "header": Colors.BOLD + Colors.BLUE,
    }
    print(f"{colors.get(level, '')}{msg}{Colors.ENDC}")


def verbose_log(msg: str) -> None:
    """Log a verbose/debug message (only shown with --verbose flag).

    Args:
        msg: The debug message to log.
    """
    if VERBOSE and not QUIET:
        print(f"{Colors.DIM}  -> {msg}{Colors.ENDC}")


def run(
    cmd: list[str],
    description: str = "",
    timeout: int = 15,
    log_errors: bool = True,
    capture_stderr: bool = False,
) -> str:
    """Execute a system command and return its output.

    Args:
        cmd: Command and arguments as a list.
        description: Optional description for verbose logging.
        timeout: Maximum time in seconds to wait for command completion.
        log_errors: Whether to log errors to console.
        capture_stderr: If True, return stderr instead of stdout (for tools like codesign).

    Returns:
        Command output as a string, or empty string on failure.

    Examples:
        >>> run(["sw_vers", "-productVersion"])
        '14.2.1'
        >>> run(["uname", "-m"])
        'arm64'
        >>> run(["codesign", "-dvv", "/Applications/Safari.app"], capture_stderr=True)
        'Identifier=com.apple.Safari...'
    """
    if description:
        verbose_log(description)
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            if log_errors:
                verbose_log(f"Command failed: {' '.join(cmd)}\nError: {result.stderr.strip()}")
            # For commands that write to stderr (like codesign), return stderr even on error
            if capture_stderr and result.stderr:
                return result.stderr.strip()
            return ""
        # Return stderr if requested (some tools write to stderr by design)
        if capture_stderr:
            return result.stderr.strip()
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        if log_errors:
            verbose_log(f"Command timed out: {' '.join(cmd)}")
        return ""
    except Exception as e:
        if log_errors:
            verbose_log(f"Command execution error: {e}")
        return ""


async def async_run_command(
    cmd: list[str],
    description: str = "",
    timeout: int = 15,
    log_errors: bool = True,
    capture_stderr: bool = False,
) -> str:
    """Execute a system command asynchronously and return its output.

    Args:
        cmd: Command and arguments as a list.
        description: Optional description for verbose logging.
        timeout: Maximum time in seconds to wait for command completion.
        log_errors: Whether to log errors to console.
        capture_stderr: If True, return stderr instead of stdout (for tools like codesign).

    Returns:
        Command output as a string, or empty string on failure.

    Examples:
        >>> await async_run_command(["sw_vers", "-productVersion"])
        '14.2.1'
        >>> await async_run_command(["uname", "-m"])
        'arm64'
    """
    if description:
        verbose_log(description)
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            if log_errors:
                verbose_log(f"Command timed out: {' '.join(cmd)}")
            return ""

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()

        if process.returncode != 0:
            if log_errors:
                verbose_log(f"Command failed: {' '.join(cmd)}\nError: {stderr_text}")
            # For commands that write to stderr (like codesign), return stderr even on error
            if capture_stderr and stderr_text:
                return stderr_text
            return ""

        # Return stderr if requested (some tools write to stderr by design)
        if capture_stderr:
            return stderr_text
        return stdout_text

    except Exception as e:
        if log_errors:
            verbose_log(f"Command execution error: {e}")
        return ""


async def async_get_json_output(cmd: list[str]) -> Optional[Union[dict, list]]:
    """Execute a command asynchronously and parse its JSON output.

    Args:
        cmd: Command that produces JSON output.

    Returns:
        Parsed JSON as dict or list, or None on failure.

    Examples:
        >>> await async_get_json_output(["npm", "list", "-g", "--json", "--depth=0"])
        {'dependencies': {'npm': {'version': '10.2.3'}}}
    """
    try:
        output = await async_run_command(cmd)
        if output:
            parsed = json.loads(output)
            return parsed  # type: ignore[no-any-return]
    except (json.JSONDecodeError, Exception):
        pass
    return None


def get_json_output(cmd: list[str]) -> Optional[Union[dict, list]]:
    """Execute a command and parse its JSON output.

    Args:
        cmd: Command that produces JSON output.

    Returns:
        Parsed JSON as dict or list, or None on failure.

    Examples:
        >>> get_json_output(["npm", "list", "-g", "--json", "--depth=0"])
        {'dependencies': {'npm': {'version': '10.2.3'}}}
    """
    try:
        output = run(cmd)
        if output:
            parsed = json.loads(output)
            return parsed  # type: ignore[no-any-return]
    except (json.JSONDecodeError, Exception):
        pass
    return None


def which(cmd: str) -> Optional[str]:
    """Find the full path of a command, resolving symlinks.

    Args:
        cmd: Command name to locate.

    Returns:
        Full path to the command, with symlink resolution if applicable.
        Returns None if command not found.

    Examples:
        >>> which("python3")
        '/usr/bin/python3 -> /Library/Developer/CommandLineTools/usr/bin/python3'
    """
    path = shutil.which(cmd)
    if not path:
        return None
    p = Path(path)
    if p.is_symlink():
        return f"{path} -> {p.resolve()}"
    return path


def get_version(cmd: list[str]) -> str:
    """Get the version string from a command.

    Args:
        cmd: Command with version flag (e.g., ["node", "--version"]).

    Returns:
        Version string or "Not Found" if command fails.

    Examples:
        >>> get_version(["node", "--version"])
        'v20.11.0'
    """
    try:
        # Version checks often fail if tool is not installed, so we suppress error logging
        out = run(cmd, timeout=3, log_errors=False)
        out = out.splitlines()[0] if out else ""
        return out.strip() if out.strip() else "Not Found"
    except Exception:
        return "Not Found"


def get_app_version(app_path: Path) -> str:
    """Extract version from a macOS .app bundle.

    Tries multiple common version keys in order of preference:
    1. CFBundleShortVersionString (most common, user-facing version)
    2. CFBundleVersion (build version)
    3. CFBundleGetInfoString (legacy version string)

    Args:
        app_path: Path to the .app bundle.

    Returns:
        Version string from Info.plist, or empty string on failure.

    Examples:
        >>> get_app_version(Path("/Applications/Safari.app"))
        '17.2.1'
    """
    try:
        plist_path = app_path / "Contents/Info.plist"
        if not plist_path.exists():
            return ""

        # Try multiple version keys in order of preference
        version_keys = [
            "CFBundleShortVersionString",  # Standard user-facing version
            "CFBundleVersion",  # Build version (fallback)
            "CFBundleGetInfoString",  # Legacy version info
        ]

        for key in version_keys:
            ver = run(
                ["defaults", "read", str(plist_path.absolute()), key],
                log_errors=False,
            )
            if ver.strip():
                return ver.strip()

        return ""
    except Exception:
        return ""


def safe_glob(path_str: str, pattern: str) -> list[str]:
    """Safely glob files with error handling.

    Args:
        path_str: Base path to search in (supports ~ expansion).
        pattern: Glob pattern (e.g., "*.app", "**/*.py").

    Returns:
        List of matching file paths, or empty list on error.

    Examples:
        >>> safe_glob("/Applications", "*.app")
        ['/Applications/Safari.app', '/Applications/Notes.app', ...]
    """
    try:
        path = Path(path_str).expanduser()
        if not path.exists():
            return []
        return [str(p) for p in path.glob(pattern)]
    except (PermissionError, OSError):
        return []


def parse_edid(edid_bytes: bytes) -> dict[str, Optional[str]]:
    """Parse EDID (Extended Display Identification Data) to extract display information.

    EDID structure (simplified):
    - Bytes 8-9: Manufacturer ID (3 chars encoded in 5-bit packed format)
    - Bytes 10-11: Product code (little-endian)
    - Bytes 12-15: Serial number (little-endian)
    - Byte 16: Manufacture week (0-53, 0xFF = unknown)
    - Byte 17: Manufacture year (offset from 1990)

    Args:
        edid_bytes: Raw EDID data (typically 128 or 256 bytes).

    Returns:
        Dictionary with keys: manufacturer_id, product_code, serial_number,
        manufacture_week, manufacture_year. Values are None if parsing fails.

    Examples:
        >>> edid = base64.b64decode("AP///////wAGECWT...")
        >>> parse_edid(edid)
        {'manufacturer_id': 'APP', 'product_code': '0x9227', ...}
    """
    result: dict[str, Optional[str]] = {
        "manufacturer_id": None,
        "product_code": None,
        "serial_number": None,
        "manufacture_week": None,
        "manufacture_year": None,
    }

    try:
        if len(edid_bytes) < 18:
            return result

        # Parse manufacturer ID (bytes 8-9)
        # Format: 5-bit packed ASCII (A=1, B=2, ..., Z=26)
        mfg_bytes = int.from_bytes(edid_bytes[8:10], "big")
        char1 = chr(((mfg_bytes >> 10) & 0x1F) + 64)
        char2 = chr(((mfg_bytes >> 5) & 0x1F) + 64)
        char3 = chr((mfg_bytes & 0x1F) + 64)
        result["manufacturer_id"] = f"{char1}{char2}{char3}"

        # Parse product code (bytes 10-11, little-endian)
        product_code = int.from_bytes(edid_bytes[10:12], "little")
        result["product_code"] = f"0x{product_code:04x}"

        # Parse serial number (bytes 12-15, little-endian)
        serial = int.from_bytes(edid_bytes[12:16], "little")
        if serial != 0:
            result["serial_number"] = str(serial)

        # Parse manufacture week (byte 16)
        week = edid_bytes[16]
        if week != 0xFF and week <= 53:
            result["manufacture_week"] = str(week)

        # Parse manufacture year (byte 17, offset from 1990)
        year_offset = edid_bytes[17]
        if year_offset > 0:
            result["manufacture_year"] = str(1990 + year_offset)

    except Exception as e:
        verbose_log(f"EDID parsing error: {e}")

    return result
