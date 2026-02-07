"""Tests for exception classes."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose.exceptions import (
    CollectorError,
    ProseError,
    SystemCommandError,
    UnsupportedPlatformError,
)


class TestExceptions:
    """Test suite for custom exceptions."""

    def test_prose_error(self):
        """Test base ProseError exception."""
        error = ProseError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_collector_error(self):
        """Test CollectorError with collector name."""
        error = CollectorError("system", "Failed to collect data")
        assert "system" in str(error)
        assert "Failed to collect data" in str(error)
        assert error.collector_name == "system"

    def test_system_command_error(self):
        """Test SystemCommandError with command."""
        cmd = ["sw_vers", "-productVersion"]
        error = SystemCommandError(cmd, "Command not found")
        assert "sw_vers" in str(error)
        assert "Command not found" in str(error)
        assert error.command == cmd

    def test_unsupported_platform_error(self):
        """Test UnsupportedPlatformError with platform name."""
        error = UnsupportedPlatformError("linux")
        assert "linux" in str(error)
        assert "macOS" in str(error)
