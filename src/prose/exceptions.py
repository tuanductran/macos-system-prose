"""Custom exception classes for macOS System Prose."""

from __future__ import annotations


class ProseError(Exception):
    """Base exception for all macOS System Prose errors."""

    pass


class CollectorError(ProseError):
    """Raised when a data collector encounters an error."""

    def __init__(self, collector_name: str, message: str) -> None:
        """Initialize collector error.

        Args:
            collector_name: Name of the collector that failed.
            message: Error message describing what went wrong.
        """
        self.collector_name = collector_name
        super().__init__(f"[{collector_name}] {message}")


class SystemCommandError(ProseError):
    """Raised when a system command fails to execute."""

    def __init__(self, command: list[str], error: str) -> None:
        """Initialize system command error.

        Args:
            command: The command that failed.
            error: Error message from the command.
        """
        self.command = command
        super().__init__(f"Command failed: {' '.join(command)}\n{error}")


class UnsupportedPlatformError(ProseError):
    """Raised when running on non-macOS platform."""

    def __init__(self, platform: str) -> None:
        """Initialize unsupported platform error.

        Args:
            platform: The detected platform name.
        """
        super().__init__(f"This tool only supports macOS, detected: {platform}")
