"""Tests for SMBIOS database and lookups."""

from __future__ import annotations

import pytest

from prose.datasets.smbios import (
    SMBIOS_DATABASE,
    get_smbios_data,
    is_legacy_mac,
)


class TestSMBIOSDatabase:
    """Test SMBIOS database structure and content."""

    def test_database_not_empty(self):
        """Database should contain Mac models."""
        assert len(SMBIOS_DATABASE) > 50, "Expected 50+ Mac models in database"

    def test_database_structure(self):
        """Each entry should have required fields."""
        for model_id, data in SMBIOS_DATABASE.items():
            assert isinstance(model_id, str), f"Model ID {model_id} should be string"
            assert "marketing_name" in data, f"{model_id} missing marketing_name"
            assert "board_id" in data, f"{model_id} missing board_id"
            assert "cpu_generation" in data, f"{model_id} missing cpu_generation"
            assert "max_os_supported" in data, f"{model_id} missing max_os_supported"
            assert "stock_gpus" in data, f"{model_id} missing stock_gpus"

            # Validate types
            assert isinstance(data["marketing_name"], str)
            assert isinstance(data["board_id"], str)
            assert isinstance(data["cpu_generation"], str)
            assert isinstance(data["max_os_supported"], str)
            assert isinstance(data["stock_gpus"], list)

    def test_known_models_exist(self):
        """Test that common Mac models are in database."""
        known_models = [
            "MacBookAir6,2",  # MacBook Air 2013
            "MacBookPro14,1",  # MacBook Pro 2017
            "iMac19,1",  # iMac 2019
            "Macmini8,1",  # Mac Mini 2018
            "MacBookPro18,1",  # MacBook Pro M1 Pro 2021
        ]

        for model in known_models:
            assert model in SMBIOS_DATABASE, f"{model} should be in database"


class TestSMBIOSLookup:
    """Test SMBIOS data lookup functions."""

    def test_get_existing_model(self):
        """Should return data for known model."""
        data = get_smbios_data("MacBookAir6,2")
        assert data is not None
        assert data["marketing_name"] == "MacBook Air (13-inch, Mid 2013)"
        assert data["board_id"] == "Mac-7DF21CB3ED6977E5"
        assert data["cpu_generation"] == "Haswell"
        assert data["max_os_supported"] == "Big Sur"

    def test_get_nonexistent_model(self):
        """Should return None for unknown model."""
        data = get_smbios_data("NonExistentModel99,99")
        assert data is None

    def test_get_m1_model(self):
        """Should return data for Apple Silicon model."""
        data = get_smbios_data("MacBookPro18,1")
        assert data is not None
        assert "M1 Pro" in data["cpu_generation"]
        assert data["max_os_supported"] == "Tahoe"  # Updated from Apple Support Feb 2026

    def test_get_intel_model(self):
        """Should return data for Intel model."""
        data = get_smbios_data("iMac19,1")
        assert data is not None
        assert data["cpu_generation"] == "Coffee Lake"
        assert "AMD Radeon" in data["stock_gpus"][0]


class TestLegacyMacDetection:
    """Test legacy/unsupported Mac detection."""

    def test_legacy_mac_running_unsupported_os(self):
        """MacBookAir6,2 running Monterey (max: Big Sur) is legacy."""
        assert is_legacy_mac("MacBookAir6,2", "12.7.6") is True

    def test_modern_mac_running_supported_os(self):
        """MacBookPro14,1 running Monterey (max: Ventura) is not legacy."""
        assert is_legacy_mac("MacBookPro14,1", "12.7.6") is False  # Updated: max is Ventura

    def test_mac_at_max_supported_os(self):
        """MacBookAir6,2 running Big Sur (max: Big Sur) is not legacy."""
        assert is_legacy_mac("MacBookAir6,2", "11.7.10") is False

    def test_nonexistent_model(self):
        """Unknown model should return False."""
        assert is_legacy_mac("NonExistentModel99,99", "14.0") is False

    def test_m1_mac_running_sequoia(self):
        """M1 Mac running Sequoia (max: Sequoia) is not legacy."""
        assert is_legacy_mac("MacBookPro18,1", "15.1.0") is False

    def test_old_mac_running_old_os(self):
        """MacBook5,1 running Lion (max: Lion) is not legacy."""
        assert is_legacy_mac("MacBook5,1", "10.7.5") is False

    def test_version_parsing(self):
        """Should handle various version formats."""
        # Big Sur (11.x)
        assert is_legacy_mac("MacBookAir6,2", "11.0") is False
        assert is_legacy_mac("MacBookAir6,2", "11.7.10") is False
        assert is_legacy_mac("MacBookAir6,2", "12.0") is True

        # Catalina (10.15.x)
        assert is_legacy_mac("MacBookAir5,1", "10.15.7") is False  # max: Catalina
        assert is_legacy_mac("MacBookAir5,1", "11.0") is True  # Big Sur unsupported
        assert is_legacy_mac("MacBookAir5,1", "12.0") is True  # Monterey unsupported


class TestSMBIOSDataQuality:
    """Test data quality and consistency."""

    def test_marketing_names_are_descriptive(self):
        """Marketing names should be human-readable."""
        for model_id, data in SMBIOS_DATABASE.items():
            name = data["marketing_name"]
            assert len(name) > 5, f"{model_id} marketing name too short: {name}"
            assert any(
                keyword in name
                for keyword in ["MacBook", "Mac mini", "iMac", "Mac Pro", "Mac Studio"]
            ), f"{model_id} marketing name missing Mac product: {name}"

    def test_board_ids_format(self):
        """Board IDs should follow Mac-XXXXXXXX format (skip TBD for upcoming models)."""
        for model_id, data in SMBIOS_DATABASE.items():
            board_id = data["board_id"]
            assert board_id.startswith("Mac-"), f"{model_id} board ID invalid: {board_id}"
            # Skip validation for TBD (upcoming models not yet released)
            if board_id != "Mac-TBD":
                assert len(board_id) > 10, f"{model_id} board ID too short: {board_id}"

    def test_max_os_consistency(self):
        """Max OS should be from known macOS version list (updated Feb 2026)."""
        valid_os_versions = {
            "Snow Leopard",
            "Lion",
            "Mountain Lion",
            "Mavericks",
            "Yosemite",
            "El Capitan",
            "Sierra",
            "High Sierra",
            "Mojave",
            "Catalina",
            "Big Sur",
            "Monterey",
            "Ventura",
            "Sonoma",
            "Sequoia",
            "Tahoe",  # macOS Tahoe 26.x (2026)
        }

        for model_id, data in SMBIOS_DATABASE.items():
            max_os = data["max_os_supported"]
            assert max_os in valid_os_versions, f"{model_id} has invalid max OS: {max_os}"

    def test_gpus_not_empty(self):
        """Stock GPUs list should not be empty."""
        for model_id, data in SMBIOS_DATABASE.items():
            assert len(data["stock_gpus"]) > 0, f"{model_id} has no stock GPUs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
