"""Tests for SMBIOS database and lookups."""

from __future__ import annotations

import pytest

from prose.datasets.smbios import is_legacy_mac


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
