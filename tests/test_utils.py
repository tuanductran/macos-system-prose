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
