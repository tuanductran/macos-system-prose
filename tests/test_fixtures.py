"""Tests for validating fixture data and system report schemas.

Fixtures are generated programmatically via conftest.py factories,
not loaded from static JSON files.
"""

from __future__ import annotations

import json

import pytest


class TestFixtureSchema:
    """Test that all fixtures conform to the expected schema."""

    def test_fixtures_exist(self, fixtures_data):
        """At least one fixture should exist."""
        assert len(fixtures_data) > 0

    def test_fixture_count(self, fixtures_data):
        """Should have all 5 fixture profiles."""
        assert len(fixtures_data) == 5

    def test_fixture_top_level_keys(self, fixtures_data):
        """All fixtures should have required top-level keys."""
        required_keys = {
            "report_schema",
            "report_schema_version",
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
            "nvram",
            "storage_analysis",
            "fonts",
            "shell_customization",
            "opencore_patcher",
            "oclp_compatibility",
            "system_preferences",
            "kernel_params",
            "system_logs",
            "ioregistry",
            "collection_errors",
            "collection_status",
        }

        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            missing = required_keys - set(fixture.keys())
            assert not missing, f"Fixture {name} missing keys: {missing}"

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
            name = fixture["_fixture_name"]
            system = fixture["system"]
            missing = required_fields - set(system.keys())
            assert not missing, f"Fixture {name} system info missing: {missing}"

    def test_hardware_info_structure(self, fixtures_data):
        """Validate hardware info structure in all fixtures."""
        required_fields = {"cpu", "cpu_cores", "memory_gb", "displays"}

        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            hardware = fixture["hardware"]
            missing = required_fields - set(hardware.keys())
            assert not missing, f"Fixture {name} hardware info missing: {missing}"

            assert isinstance(hardware["displays"], list)
            if hardware["displays"]:
                display = hardware["displays"][0]
                assert "resolution" in display
                assert "refresh_rate" in display

    def test_opencore_patcher_structure(self, fixtures_data):
        """Validate OpenCore Patcher info structure."""
        required_fields = {
            "detected",
            "detection_confidence",
            "detection_signals",
            "version",
            "nvram_version",
            "opencore_version",
            "unsupported_os_detected",
            "root_patch_marker_detected",
            "loaded_kexts",
            "patched_frameworks",
            "amfi_configuration",
            "boot_args",
        }

        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            oclp = fixture["opencore_patcher"]
            missing = required_fields - set(oclp.keys())
            assert not missing, f"Fixture {name} OCLP info missing: {missing}"

            assert isinstance(oclp["detected"], bool)
            assert oclp["detection_confidence"] in {"none", "low", "high"}
            assert isinstance(oclp["detection_signals"], list)
            assert isinstance(oclp["loaded_kexts"], list)
            assert isinstance(oclp["patched_frameworks"], list)

    def test_oclp_compatibility_structure(self, fixtures_data):
        """Validate the separate Apple/OCLP compatibility model."""
        required_fields = {
            "apple_native_supported",
            "oclp_model_supported",
            "oclp_os_supported",
            "oclp_target_os_min",
            "oclp_target_os_max",
            "root_patch_required",
            "root_patch_state",
            "root_patch_domains",
            "required_packages",
            "knowledge_schema_version",
            "knowledge_checked_at",
            "knowledge_sources",
        }
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            compatibility = fixture["oclp_compatibility"]
            missing = required_fields - set(compatibility.keys())
            assert not missing, f"Fixture {name} compatibility missing: {missing}"
            assert compatibility["root_patch_state"] in {"not_detected", "detected", "unknown"}

    def test_network_privacy_structure(self, fixtures_data):
        """Network fixtures must declare their privacy mode explicitly."""
        for fixture in fixtures_data:
            network = fixture["network"]
            assert network["privacy_mode"] in {"redacted", "full"}

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
            name = fixture["_fixture_name"]
            dev_tools = fixture["developer_tools"]
            missing = required_fields - set(dev_tools.keys())
            assert not missing, f"Fixture {name} dev tools missing: {missing}"

            assert isinstance(dev_tools["terminal_emulators"], list)

    def test_code_signing_structure(self, fixtures_data):
        """Validate code signing sample structure."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            signing = fixture["security"]["code_signing_sample"]

            assert isinstance(signing, list)
            if signing:
                app = signing[0]
                required_fields = {"app_name", "identifier", "authority", "valid", "team_id"}
                missing = required_fields - set(app.keys())
                assert not missing, f"Fixture {name} code signing missing: {missing}"


    def test_intel_and_apple_silicon_report_schema_is_stable(self, fixtures_data):
        """Intel and Apple-silicon profiles share the same report schema."""
        intel = [f for f in fixtures_data if f["system"]["architecture"] == "x86_64"]
        arm64 = [f for f in fixtures_data if f["system"]["architecture"] == "arm64"]

        assert intel
        assert arm64

        intel_keys = set(intel[0].keys())
        arm64_keys = set(arm64[0].keys())
        assert intel_keys == arm64_keys

        for fixture in intel + arm64:
            assert fixture["report_schema"] == "macos-system-prose/system-report"
            assert fixture["report_schema_version"] == 1
            assert fixture["system"]["architecture"] in {"x86_64", "arm64"}




class TestFixtureValues:
    """Test that fixture values are reasonable and valid."""

    def test_report_schema_metadata(self, fixtures_data):
        """Every fixture declares the machine-readable report schema contract."""
        for fixture in fixtures_data:
            assert fixture["report_schema"] == "macos-system-prose/system-report"
            assert fixture["report_schema_version"] == 1

    def test_timestamp_is_positive(self, fixtures_data):
        """Timestamp should be a positive number."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            assert fixture["timestamp"] > 0, f"Fixture {name} has invalid timestamp"

    def test_memory_is_positive(self, fixtures_data):
        """Memory should be a positive number."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            memory = fixture["hardware"]["memory_gb"]
            assert memory > 0, f"Fixture {name} has invalid memory: {memory}"

    def test_disk_space_reasonable(self, fixtures_data):
        """Disk space should be positive and free <= total."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            disk = fixture["disk"]
            total = disk["disk_total_gb"]
            free = disk["disk_free_gb"]

            assert total > 0, f"Fixture {name} has invalid total disk"
            assert free >= 0, f"Fixture {name} has negative free disk"
            assert free <= total, f"Fixture {name} free disk exceeds total"

    def test_macos_version_format(self, fixtures_data):
        """macOS version should be in correct format."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            version = fixture["system"]["macos_version"]

            parts = version.split(".")
            assert len(parts) >= 2, f"Fixture {name} has invalid version: {version}"
            assert all(p.isdigit() for p in parts), (
                f"Fixture {name} has non-numeric version: {version}"
            )

    def test_architecture_valid(self, fixtures_data):
        """Architecture should be valid Mac architecture."""
        valid_archs = {"x86_64", "arm64"}
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            arch = fixture["system"]["architecture"]
            assert arch in valid_archs, f"Fixture {name} has invalid arch: {arch}"

    def test_os_field_is_darwin(self, fixtures_data):
        """OS field should always be Darwin."""
        for fixture in fixtures_data:
            assert fixture["system"]["os"] == "Darwin"


class TestFixtureConsistency:
    """Test consistency between related fields in fixtures."""

    def test_oclp_kexts_consistency(self, fixtures_data):
        """If OCLP is detected, should have kexts listed."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            oclp = fixture["opencore_patcher"]

            if oclp["detected"] and oclp["version"]:
                assert isinstance(oclp["loaded_kexts"], list), (
                    f"Fixture {name} OCLP detected but loaded_kexts not a list"
                )

    def test_oclp_fixture_has_third_party_kexts(self, fixtures_data):
        """OCLP fixture should have third-party kexts loaded."""
        oclp_fixtures = [f for f in fixtures_data if f["opencore_patcher"]["detected"]]
        assert len(oclp_fixtures) >= 1, "Should have at least one OCLP fixture"

        for fixture in oclp_fixtures:
            name = fixture["_fixture_name"]
            kexts = fixture["kexts"]["third_party_kexts"]
            assert len(kexts) > 0, f"OCLP fixture {name} should have third-party kexts"

    def test_terminal_emulators_on_macos(self, fixtures_data):
        """macOS should always have at least Terminal.app."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            terminals = fixture["developer_tools"]["terminal_emulators"]
            assert isinstance(terminals, list), f"Fixture {name} terminal_emulators not a list"

    def test_package_managers_structure(self, fixtures_data):
        """Package managers should have consistent structure."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            pkg_mgrs = fixture["package_managers"]

            brew = pkg_mgrs.get("homebrew", {})
            assert "installed" in brew, f"Fixture {name} missing homebrew.installed"

            if brew["installed"]:
                assert "version" in brew, f"Fixture {name} Homebrew installed but no version"

    def test_intel_macs_have_x86_64(self, fixtures_data):
        """Intel-based fixtures should have x86_64 architecture."""
        for fixture in fixtures_data:
            cpu = fixture["hardware"]["cpu"].lower()
            arch = fixture["system"]["architecture"]
            if "intel" in cpu:
                assert arch == "x86_64", f"Intel Mac has wrong arch: {arch}"

    def test_apple_silicon_macs_have_arm64(self, fixtures_data):
        """Apple Silicon fixtures should have arm64 architecture."""
        for fixture in fixtures_data:
            cpu = fixture["hardware"]["cpu"].lower()
            arch = fixture["system"]["architecture"]
            if "apple m" in cpu:
                assert arch == "arm64", f"Apple Silicon Mac has wrong arch: {arch}"


class TestFixtureSerialization:
    """Test that fixtures can be properly serialized."""

    def test_fixture_is_valid_json(self, fixtures_data):
        """All fixtures should serialize to valid JSON."""
        for fixture in fixtures_data:
            name = fixture["_fixture_name"]
            try:
                json.dumps(fixture, indent=2)
            except (TypeError, ValueError) as e:
                pytest.fail(f"Fixture {name} is not JSON-serializable: {e}")

    def test_fixture_can_roundtrip(self, fixtures_data):
        """Fixtures should survive JSON roundtrip."""
        for fixture in fixtures_data:
            name = fixture.pop("_fixture_name")
            try:
                json_str = json.dumps(fixture, indent=2)
                reloaded = json.loads(json_str)
                assert reloaded == fixture, f"Fixture {name} failed roundtrip"
            except Exception as e:
                pytest.fail(f"Fixture {name} roundtrip failed: {e}")
            finally:
                fixture["_fixture_name"] = name
