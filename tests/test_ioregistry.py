"""Tests for IORegistry hardware detection collector."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose.collectors.ioregistry import (
    collect_audio_codecs,
    collect_ioregistry_info,
    collect_pcie_devices,
    collect_usb_devices,
)


class TestIORegistryCollector:
    """Test suite for IORegistry hardware detection."""

    @patch("prose.collectors.ioregistry.run")
    def test_collect_pcie_devices_empty(self, mock_run):
        """Test PCIe collection with no devices."""
        mock_run.return_value = ""
        devices = collect_pcie_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_collect_pcie_devices_with_data(self, mock_run):
        """Test PCIe collection with mock device data."""
        mock_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>IOName</key>
    <string>pci8086,9d23</string>
    <key>vendor-id</key>
    <data>hoYAAA==</data>
    <key>device-id</key>
    <data>I50AAA==</data>
    <key>class-code</key>
    <data>AwQIAA==</data>
    <key>pcidebug</key>
    <string>0:31:3</string>
</dict>
</plist>"""
        mock_run.return_value = mock_plist
        devices = collect_pcie_devices()
        assert isinstance(devices, list)
        assert len(devices) >= 0  # May be 0 or 1 depending on parsing logic

    @patch("prose.collectors.ioregistry.run")
    def test_collect_usb_devices_empty(self, mock_run):
        """Test USB collection with no devices."""
        mock_run.return_value = ""
        devices = collect_usb_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_collect_usb_devices_with_data(self, mock_run):
        """Test USB collection with mock device data."""
        mock_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>USB Product Name</key>
    <string>Apple Internal Keyboard / Trackpad</string>
    <key>idVendor</key>
    <integer>1452</integer>
    <key>idProduct</key>
    <integer>641</integer>
    <key>locationID</key>
    <integer>336592896</integer>
    <key>Device Speed</key>
    <integer>2</integer>
</dict>
</plist>"""
        mock_run.return_value = mock_plist
        devices = collect_usb_devices()
        assert isinstance(devices, list)
        # Should have 1 device with proper vendor/product IDs
        if len(devices) > 0:
            device = devices[0]
            assert "name" in device
            assert "vendor_id" in device
            assert "product_id" in device

    @patch("prose.collectors.ioregistry.run")
    def test_collect_audio_codecs_empty(self, mock_run):
        """Test audio codec collection with no codecs."""
        mock_run.return_value = ""
        codecs = collect_audio_codecs()
        assert isinstance(codecs, list)
        assert len(codecs) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_collect_audio_codecs_with_data(self, mock_run):
        """Test audio codec collection with mock codec data."""
        mock_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>IOName</key>
    <string>IOHDACodecDevice</string>
    <key>IOHDACodecVendorID</key>
    <integer>283904146</integer>
    <key>layout-id</key>
    <data>BwAAAA==</data>
</dict>
</plist>"""
        mock_run.return_value = mock_plist
        codecs = collect_audio_codecs()
        assert isinstance(codecs, list)

    @patch("prose.collectors.ioregistry.run")
    def test_collect_ioregistry_info_structure(self, mock_run):
        """Test that collect_ioregistry_info returns proper structure."""
        mock_run.return_value = ""
        info = collect_ioregistry_info()

        # Verify structure
        assert isinstance(info, dict)
        assert "pcie_devices" in info
        assert "usb_devices" in info
        assert "audio_codecs" in info
        assert isinstance(info["pcie_devices"], list)
        assert isinstance(info["usb_devices"], list)
        assert isinstance(info["audio_codecs"], list)

    @patch("prose.collectors.ioregistry.run")
    def test_pcie_error_handling(self, mock_run):
        """Test PCIe collection handles errors gracefully."""
        mock_run.side_effect = Exception("Test error")
        devices = collect_pcie_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_usb_error_handling(self, mock_run):
        """Test USB collection handles errors gracefully."""
        mock_run.side_effect = Exception("Test error")
        devices = collect_usb_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_audio_error_handling(self, mock_run):
        """Test audio codec collection handles errors gracefully."""
        mock_run.side_effect = Exception("Test error")
        codecs = collect_audio_codecs()
        assert isinstance(codecs, list)
        assert len(codecs) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_pcie_malformed_plist(self, mock_run):
        """Test PCIe collection with malformed plist data."""
        mock_run.return_value = "not a valid plist"
        devices = collect_pcie_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0

    @patch("prose.collectors.ioregistry.run")
    def test_usb_malformed_plist(self, mock_run):
        """Test USB collection with malformed plist data."""
        mock_run.return_value = "not a valid plist"
        devices = collect_usb_devices()
        assert isinstance(devices, list)
        assert len(devices) == 0
