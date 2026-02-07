"""Tests for utility functions."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose import utils


class TestUtilityFunctions:
    """Test suite for utility functions."""

    def test_which_existing_command(self):
        """Test which() with existing command."""
        result = utils.which("python3")
        assert result is not None
        assert "python3" in result

    def test_which_nonexistent_command(self):
        """Test which() with non-existent command."""
        result = utils.which("nonexistent_command_12345")
        assert result is None

    def test_get_version_success(self):
        """Test get_version() with working command."""
        version = utils.get_version(["python3", "--version"])
        assert "Python" in version or version != "Not Found"

    def test_get_version_failure(self):
        """Test get_version() with failing command."""
        version = utils.get_version(["nonexistent_cmd_xyz", "--version"])
        assert version == "Not Found"

    @patch("prose.utils.run")
    def test_get_json_output_valid(self, mock_run):
        """Test get_json_output() with valid JSON."""
        mock_run.return_value = '{"key": "value"}'
        result = utils.get_json_output(["echo", "test"])
        assert result == {"key": "value"}

    @patch("prose.utils.run")
    def test_get_json_output_invalid(self, mock_run):
        """Test get_json_output() with invalid JSON."""
        mock_run.return_value = "not json"
        result = utils.get_json_output(["echo", "test"])
        assert result is None

    def test_parse_edid_basic(self):
        """Test parse_edid() with basic valid data."""
        # Create minimal valid EDID (128 bytes)
        edid = bytearray(128)
        # Set manufacturer ID to "APP" (Apple) at bytes 8-9
        edid[8] = 0x06  # First part of packed manufacturer ID
        edid[9] = 0x10  # Second part
        # Set product code at bytes 10-11
        edid[10] = 0x26
        edid[11] = 0x92
        # Set serial at bytes 12-15
        edid[12] = 0x01
        edid[13] = 0x00
        edid[14] = 0x00
        edid[15] = 0x00
        # Set manufacture week/year at bytes 16-17
        edid[16] = 26  # Week 26
        edid[17] = 24  # Year 2014 (1990+24)

        result = utils.parse_edid(bytes(edid))

        assert isinstance(result, dict)
        assert "manufacturer_id" in result
        assert "product_code" in result
        assert result["product_code"] == "0x9226"

    def test_parse_edid_empty(self):
        """Test parse_edid() with empty data."""
        result = utils.parse_edid(b"")
        assert isinstance(result, dict)
        assert result["manufacturer_id"] is None

    def test_safe_glob_existing_dir(self):
        """Test safe_glob() with existing directory."""
        result = utils.safe_glob("/Applications", "*.app")
        assert isinstance(result, list)

    def test_safe_glob_nonexistent_dir(self):
        """Test safe_glob() with non-existent directory."""
        result = utils.safe_glob("/nonexistent_path_xyz", "*.app")
        assert result == []

    def test_log_levels(self, capsys):
        """Test log() with different levels."""
        utils.QUIET = False
        utils.log("Test info", "info")
        captured = capsys.readouterr()
        assert "Test info" in captured.out

        utils.log("Test error", "error")
        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_verbose_log(self, capsys):
        """Test verbose_log() with VERBOSE flag."""
        utils.VERBOSE = True
        utils.QUIET = False
        utils.verbose_log("Debug message")
        captured = capsys.readouterr()
        assert "Debug message" in captured.out

        utils.VERBOSE = False
        utils.verbose_log("Should not appear")
        captured = capsys.readouterr()
        assert "Should not appear" not in captured.out

    def test_run_command_success(self):
        """Test run() with successful command."""
        result = utils.run(["echo", "test"])
        assert result == "test"

    def test_run_command_timeout(self):
        """Test run() with command timeout."""
        result = utils.run(["sleep", "10"], timeout=1)
        assert result == ""

    def test_run_command_failure(self):
        """Test run() with failing command."""
        result = utils.run(["false"])
        assert result == ""

    @patch("prose.utils.run")
    def test_get_app_version_short_version(self, mock_run):
        """Test get_app_version() with CFBundleShortVersionString."""
        mock_run.return_value = "1.2.3"
        fake_app = Path("/Applications/Test.app")
        with patch.object(Path, "exists", return_value=True):
            version = utils.get_app_version(fake_app)
            assert version == "1.2.3"

    @patch("prose.utils.run")
    def test_get_app_version_fallback_keys(self, mock_run):
        """Test get_app_version() falls back to CFBundleVersion and CFBundleGetInfoString."""
        # Simulate CFBundleShortVersionString missing, CFBundleVersion found
        mock_run.side_effect = ["", "1.0.0", ""]
        fake_app = Path("/Applications/Test.app")
        with patch.object(Path, "exists", return_value=True):
            version = utils.get_app_version(fake_app)
            assert version == "1.0.0"

    @patch("prose.utils.run")
    def test_get_app_version_legacy_key(self, mock_run):
        """Test get_app_version() uses CFBundleGetInfoString as last resort."""
        # Simulate only CFBundleGetInfoString available
        mock_run.side_effect = ["", "", "20250001"]
        fake_app = Path("/Applications/Test.app")
        with patch.object(Path, "exists", return_value=True):
            version = utils.get_app_version(fake_app)
            assert version == "20250001"

    @patch("prose.utils.run")
    def test_get_app_version_no_version(self, mock_run):
        """Test get_app_version() returns empty string when no version found."""
        mock_run.return_value = ""
        fake_app = Path("/Applications/Test.app")
        with patch.object(Path, "exists", return_value=True):
            version = utils.get_app_version(fake_app)
            assert version == ""

    def test_get_app_version_no_plist(self):
        """Test get_app_version() with missing Info.plist."""
        fake_app = Path("/nonexistent/Test.app")
        version = utils.get_app_version(fake_app)
        assert version == ""


class TestAsyncUtilityFunctions:
    """Test suite for async utility functions."""

    async def async_test_async_run_command_success(self):
        """Test async_run_command() with successful command."""
        result = await utils.async_run_command(["echo", "test"])
        assert result == "test"

    async def async_test_async_run_command_timeout(self):
        """Test async_run_command() with command timeout."""
        result = await utils.async_run_command(["sleep", "10"], timeout=1)
        assert result == ""

    async def async_test_async_run_command_failure(self):
        """Test async_run_command() with failing command."""
        result = await utils.async_run_command(["false"])
        assert result == ""

    async def async_test_async_get_json_output_valid(self):
        """Test async_get_json_output() with valid JSON."""
        result = await utils.async_get_json_output(["echo", '{"key": "value"}'])
        assert result == {"key": "value"}

    async def async_test_async_get_json_output_invalid(self):
        """Test async_get_json_output() with invalid JSON."""
        result = await utils.async_get_json_output(["echo", "not json"])
        assert result is None

    def test_async_run_command_success(self):
        """Wrapper to run async test."""
        import asyncio

        asyncio.run(self.async_test_async_run_command_success())

    def test_async_run_command_timeout(self):
        """Wrapper to run async test."""
        import asyncio

        asyncio.run(self.async_test_async_run_command_timeout())

    def test_async_run_command_failure(self):
        """Wrapper to run async test."""
        import asyncio

        asyncio.run(self.async_test_async_run_command_failure())

    def test_async_get_json_output_valid(self):
        """Wrapper to run async test."""
        import asyncio

        asyncio.run(self.async_test_async_get_json_output_valid())

    def test_async_get_json_output_invalid(self):
        """Wrapper to run async test."""
        import asyncio

        asyncio.run(self.async_test_async_get_json_output_invalid())
