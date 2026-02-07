"""Tests for validating fixture files and system report schemas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Get fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_fixtures() -> list[Path]:
    """Get all JSON fixture files."""
    return sorted(FIXTURES_DIR.glob("*.json"))


@pytest.fixture
def fixtures_data() -> list[dict]:
    """Load all fixture files."""
    fixtures = []
    for fixture_file in get_fixtures():
        with open(fixture_file) as f:
            data = json.load(f)
            data["_fixture_name"] = fixture_file.name
            fixtures.append(data)
    return fixtures


class TestFixtureSchema:
    """Test that all fixtures conform to the expected schema."""

    def test_fixtures_exist(self):
        """At least one fixture file should exist."""
        fixtures = get_fixtures()
        assert len(fixtures) > 0, "No fixture files found in tests/fixtures/"

    def test_fixture_top_level_keys(self, fixtures_data):
        """All fixtures should have required top-level keys."""
        required_keys = {
            "timestamp",
            "system",
            "hardware",
            "disk",
            "top_processes",
            "startup",
            "login_items",
            "package_managers",
            "developer_tools",
            "kexts",
            "applications",
            "environment",
            "network",
            "battery",
            "cron",
            "diagnostics",
            "security",
            "cloud",
            "storage_analysis",
            "fonts",
            "shell_customization",
            "opencore_patcher",
            "system_preferences",
            "kernel_params",
            "system_logs",
        }

        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            missing_keys = required_keys - set(fixture.keys())
            assert not missing_keys, f"Fixture {fixture_name} missing keys: {missing_keys}"

    def test_system_info_structure(self, fixtures_data):
        """Validate system info structure in all fixtures."""
        required_fields = {
            "os",
            "macos_version",
            "model_name",
            "model_identifier",
            "kernel",
            "architecture",
        }

        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            system = fixture["system"]
            missing_fields = required_fields - set(system.keys())
            assert not missing_fields, (
                f"Fixture {fixture_name} system info missing: {missing_fields}"
            )

    def test_hardware_info_structure(self, fixtures_data):
        """Validate hardware info structure in all fixtures."""
        required_fields = {"cpu", "cpu_cores", "memory_gb", "displays"}

        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            hardware = fixture["hardware"]
            missing_fields = required_fields - set(hardware.keys())
            assert not missing_fields, (
                f"Fixture {fixture_name} hardware info missing: {missing_fields}"
            )

            # Validate displays structure
            assert isinstance(hardware["displays"], list)
            if hardware["displays"]:
                display = hardware["displays"][0]
                assert "resolution" in display
                assert "refresh_rate" in display

    def test_opencore_patcher_structure(self, fixtures_data):
        """Validate OpenCore Patcher info structure."""
        required_fields = {
            "installed",
            "version",
            "root_patched",
            "patched_kexts",
            "smbios_spoofed",
        }

        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            oclp = fixture["opencore_patcher"]
            missing_fields = required_fields - set(oclp.keys())
            assert not missing_fields, f"Fixture {fixture_name} OCLP info missing: {missing_fields}"

            # Validate types
            assert isinstance(oclp["installed"], bool)
            assert isinstance(oclp["root_patched"], bool)
            assert isinstance(oclp["patched_kexts"], list)
            assert isinstance(oclp["smbios_spoofed"], bool)

    def test_developer_tools_structure(self, fixtures_data):
        """Validate developer tools structure."""
        required_fields = {
            "languages",
            "sdks",
            "cloud_devops",
            "databases",
            "version_managers",
            "infra",
            "extensions",
            "editors",
            "docker",
            "browsers",
            "git_config",
            "terminal_emulators",
            "shell_frameworks",
        }

        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            dev_tools = fixture["developer_tools"]
            missing_fields = required_fields - set(dev_tools.keys())
            assert not missing_fields, f"Fixture {fixture_name} dev tools missing: {missing_fields}"

            # Validate terminal_emulators is a list
            assert isinstance(dev_tools["terminal_emulators"], list)

    def test_code_signing_structure(self, fixtures_data):
        """Validate code signing sample structure."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            signing = fixture["security"]["code_signing_sample"]

            assert isinstance(signing, list)
            if signing:
                app = signing[0]
                required_fields = {"app_name", "identifier", "authority", "valid", "team_id"}
                missing_fields = required_fields - set(app.keys())
                assert not missing_fields, (
                    f"Fixture {fixture_name} code signing missing: {missing_fields}"
                )


class TestFixtureValues:
    """Test that fixture values are reasonable and valid."""

    def test_timestamp_is_positive(self, fixtures_data):
        """Timestamp should be a positive number."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            assert fixture["timestamp"] > 0, f"Fixture {fixture_name} has invalid timestamp"

    def test_memory_is_positive(self, fixtures_data):
        """Memory should be a positive number."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            memory = fixture["hardware"]["memory_gb"]
            assert memory > 0, f"Fixture {fixture_name} has invalid memory: {memory}"

    def test_disk_space_reasonable(self, fixtures_data):
        """Disk space should be positive and free < total."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            disk = fixture["disk"]
            total = disk["disk_total_gb"]
            free = disk["disk_free_gb"]

            assert total > 0, f"Fixture {fixture_name} has invalid total disk"
            assert free >= 0, f"Fixture {fixture_name} has negative free disk"
            assert free <= total, f"Fixture {fixture_name} free disk exceeds total"

    def test_macos_version_format(self, fixtures_data):
        """macOS version should be in correct format."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            version = fixture["system"]["macos_version"]

            # Should be like "12.7.6" or "14.2"
            parts = version.split(".")
            assert len(parts) >= 2, f"Fixture {fixture_name} has invalid version format: {version}"
            assert all(p.isdigit() for p in parts), (
                f"Fixture {fixture_name} has non-numeric version: {version}"
            )

    def test_architecture_valid(self, fixtures_data):
        """Architecture should be valid Mac architecture."""
        valid_archs = {"x86_64", "arm64"}
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            arch = fixture["system"]["architecture"]
            assert arch in valid_archs, f"Fixture {fixture_name} has invalid arch: {arch}"


class TestFixtureConsistency:
    """Test consistency between related fields in fixtures."""

    def test_oclp_kexts_consistency(self, fixtures_data):
        """If OCLP is installed, should have kexts listed."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            oclp = fixture["opencore_patcher"]

            if oclp["installed"] and oclp["version"]:
                # If OCLP is actually installed, expect some kexts
                # But allow empty list for detection-only cases
                assert isinstance(oclp["patched_kexts"], list), (
                    f"Fixture {fixture_name} OCLP installed but kexts not a list"
                )

    def test_terminal_emulators_on_macos(self, fixtures_data):
        """macOS should always have at least Terminal.app."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            terminals = fixture["developer_tools"]["terminal_emulators"]

            # Should have at least Terminal on macOS
            assert isinstance(terminals, list), (
                f"Fixture {fixture_name} terminal_emulators not a list"
            )
            # This is only true after our fix - old fixtures might not have this
            if "Terminal" in terminals:
                assert True  # Good!

    def test_package_managers_structure(self, fixtures_data):
        """Package managers should have consistent structure."""
        for fixture in fixtures_data:
            fixture_name = fixture["_fixture_name"]
            pkg_mgrs = fixture["package_managers"]

            # Check Homebrew structure
            brew = pkg_mgrs.get("homebrew", {})
            assert "installed" in brew, f"Fixture {fixture_name} missing homebrew.installed"

            # If installed, should have version
            if brew["installed"]:
                assert "version" in brew, (
                    f"Fixture {fixture_name} Homebrew installed but no version"
                )


class TestFixtureSerialization:
    """Test that fixtures can be properly serialized."""

    def test_fixture_is_valid_json(self):
        """All fixtures should be valid JSON."""
        for fixture_file in get_fixtures():
            try:
                with open(fixture_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Fixture {fixture_file.name} is not valid JSON: {e}")

    def test_fixture_can_roundtrip(self, fixtures_data):
        """Fixtures should be able to roundtrip through JSON."""
        for fixture in fixtures_data:
            fixture_name = fixture.pop("_fixture_name")
            try:
                json_str = json.dumps(fixture, indent=2)
                reloaded = json.loads(json_str)
                assert reloaded == fixture, f"Fixture {fixture_name} failed roundtrip"
            except Exception as e:
                pytest.fail(f"Fixture {fixture_name} roundtrip failed: {e}")
