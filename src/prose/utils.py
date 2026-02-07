"""Utility functions for macOS System Prose.

This module provides helper functions for executing system commands,
parsing output, logging, and file operations.
"""

from __future__ import annotations

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


def run(cmd: list[str], description: str = "", timeout: int = 15, log_errors: bool = True) -> str:
    """Execute a system command and return its output.

    Args:
        cmd: Command and arguments as a list.
        description: Optional description for verbose logging.
        timeout: Maximum time in seconds to wait for command completion.
        log_errors: Whether to log errors to console.

    Returns:
        Command output as a string, or empty string on failure.

    Examples:
        >>> run(["sw_vers", "-productVersion"])
        '14.2.1'
        >>> run(["uname", "-m"])
        'arm64'
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
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        if log_errors:
            verbose_log(f"Command timed out: {' '.join(cmd)}")
        return ""
    except Exception as e:
        if log_errors:
            verbose_log(f"Command execution error: {e}")
        return ""


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
