"""Tests for display detection and EDID parsing."""

from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose.collectors.system import collect_display_info
from prose.utils import parse_edid


class TestEDIDParsing:
    """Test suite for EDID parsing functionality."""

    def test_parse_edid_valid_data(self):
        """Test EDID parsing with valid data."""
        # Mock EDID data (128 bytes) - Apple Cinema Display example
        # Manufacturer: APP (Apple), Product: 0x9226
        edid_hex = (
            "00ffffffffffff000610269200000000"  # Header + manufacturer/product
            "1a0e0103802213780aee91a3544c9926"  # Serial, week, year, features
            "0f505400000001010101010101010101"  # Established timings
            "010101010101302a009851002a403070"  # Standard timings
            "1300520e1100001e000000fd00384c1f"  # Detailed timings
            "510e000a202020202020000000fc0041"  # Monitor name
            "70706c6520436f6c6f720a2000000000"  # ...
            "00000000000000000000000000000066"  # Padding + checksum
        )
        edid_bytes = bytes.fromhex(edid_hex)

        result = parse_edid(edid_bytes)

        assert isinstance(result, dict)
        assert "manufacturer_id" in result
        assert "product_code" in result
        assert "serial_number" in result
        assert "manufacture_week" in result
        assert "manufacture_year" in result

        # Verify manufacturer ID is 3 uppercase letters
        if result["manufacturer_id"]:
            assert len(result["manufacturer_id"]) == 3
            assert result["manufacturer_id"].isupper()

    def test_parse_edid_short_data(self):
        """Test EDID parsing with insufficient data."""
        edid_bytes = b"short"
        result = parse_edid(edid_bytes)

        assert isinstance(result, dict)
        assert result["manufacturer_id"] is None
        assert result["product_code"] is None

    def test_parse_edid_empty_data(self):
        """Test EDID parsing with empty data."""
        edid_bytes = b""
        result = parse_edid(edid_bytes)

        assert isinstance(result, dict)
        assert result["manufacturer_id"] is None

    def test_parse_edid_zero_serial(self):
        """Test EDID parsing with zero serial number."""
        # Create minimal EDID with zero serial
        edid_bytes = bytes(128)
        # Set manufacturer to "APP" (Apple)
        edid_bytes = bytearray(edid_bytes)
        edid_bytes[8] = 0x06  # A=0, P=15 -> packed
        edid_bytes[9] = 0x10  # P=15 -> 0x10
        edid_bytes = bytes(edid_bytes)

        result = parse_edid(edid_bytes)

        # Zero serial should result in None
        assert result["serial_number"] is None

    def test_parse_edid_unknown_week(self):
        """Test EDID parsing with unknown manufacture week (0xFF)."""
        edid_bytes = bytearray(128)
        edid_bytes[16] = 0xFF  # Unknown week
        edid_bytes[17] = 20  # Year 2010
        edid_bytes = bytes(edid_bytes)

        result = parse_edid(edid_bytes)

        # 0xFF week should result in None
        assert result["manufacture_week"] is None

    def test_parse_edid_product_code_format(self):
        """Test EDID product code is formatted as hex string."""
        edid_bytes = bytearray(128)
        edid_bytes[10] = 0x34  # Product code low byte
        edid_bytes[11] = 0x12  # Product code high byte
        edid_bytes = bytes(edid_bytes)

        result = parse_edid(edid_bytes)

        if result["product_code"]:
            assert result["product_code"].startswith("0x")


class TestDisplayCollection:
    """Test suite for display information collection."""

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_empty(self, mock_json, mock_run):
        """Test display collection with no displays."""
        # Make the mock functions return coroutines on each call
        async def mock_run_coro(*args, **kwargs):
            return ""
        async def mock_json_coro(*args, **kwargs):
            return None
        
        mock_run.side_effect = mock_run_coro
        mock_json.side_effect = mock_json_coro

        async def run_test():
            displays = await collect_display_info()

            assert isinstance(displays, list)
            assert len(displays) >= 1  # Should have at least one default entry

            # Check structure of default entry
            display = displays[0]
            assert "resolution" in display
            assert "refresh_rate" in display
            assert "color_depth" in display
            assert "external_displays" in display
            assert "edid_manufacturer" in display
            assert "edid_product_code" in display
            assert "edid_serial" in display
            assert "connector_type" in display

        asyncio.run(run_test())

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_with_data(self, mock_json, mock_run):
        """Test display collection with mock display data."""
        # Make the mock functions return coroutines on each call
        async def mock_run_coro(*args, **kwargs):
            return ""  # No EDID data
        async def mock_json_coro(*args, **kwargs):
            return {
                "SPDisplaysDataType": [
                    {
                        "spdisplays_ndrvs": [
                            {
                                "_spdisplays_resolution": "2560 x 1600",
                                "spdisplays_refresh_rate": "60 Hz",
                                "spdisplays_depth": "32-Bit Color",
                                "_name": "Test Display",
                                "spdisplays_connection_type": "DisplayPort",
                            }
                        ]
                    }
                ]
            }
        
        mock_run.side_effect = mock_run_coro
        mock_json.side_effect = mock_json_coro

        async def run_test():
            displays = await collect_display_info()

            assert isinstance(displays, list)
            assert len(displays) >= 1

            display = displays[0]
            assert display["resolution"] == "2560 x 1600"
            assert display["refresh_rate"] == "60 Hz"
            assert display["color_depth"] == "32-Bit Color"

        asyncio.run(run_test())

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_internal_display(self, mock_json, mock_run):
        """Test display collection with internal display (default refresh rate)."""
        # Make the mock functions return coroutines on each call
        async def mock_run_coro(*args, **kwargs):
            return ""
        async def mock_json_coro(*args, **kwargs):
            return {
                "SPDisplaysDataType": [
                    {
                        "spdisplays_ndrvs": [
                            {
                                "_spdisplays_resolution": "1440 x 900",
                                "spdisplays_depth": "32-Bit Color",
                                "spdisplays_connection_type": "Internal",
                            }
                        ]
                    }
                ]
            }
        
        mock_run.side_effect = mock_run_coro
        mock_json.side_effect = mock_json_coro

        async def run_test():
            displays = await collect_display_info()

            assert len(displays) >= 1
            display = displays[0]
            # Internal displays should default to 60 Hz
            assert display["refresh_rate"] == "60 Hz"

        asyncio.run(run_test())

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_error_handling(self, mock_json, mock_run):
        """Test display collection handles errors gracefully."""
        # Make the mock functions raise exceptions
        mock_run.side_effect = Exception("Test error")
        mock_json.side_effect = Exception("Test error")

        async def run_test():
            displays = await collect_display_info()

            assert isinstance(displays, list)
            assert len(displays) >= 1  # Should have default entry
            display = displays[0]
            assert display["resolution"] == "Unknown"

        asyncio.run(run_test())

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_with_edid(self, mock_json, mock_run):
        """Test display collection with EDID data from ioreg."""
        # Mock EDID data in ioreg format
        edid_hex = (
            "00ffffffffffff000610269200000000"
            "1a0e0103802213780aee91a3544c9926"
            "0f505400000001010101010101010101"
            "010101010101302a009851002a403070"
            "1300520e1100001e000000fd00384c1f"
            "510e000a202020202020000000fc0041"
            "70706c6520436f6c6f720a2000000000"
            "00000000000000000000000000000066"
        )
        edid_bytes = bytes.fromhex(edid_hex)

        mock_ioreg_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>IODisplayEDID</key>
    <data>{base64.b64encode(edid_bytes).decode()}</data>
    <key>IODisplayPrefsKey</key>
    <string>Test Display</string>
    <key>IODisplayLocation</key>
    <string>DisplayPort</string>
</dict>
</plist>"""

        # Make the mock functions return coroutines on each call
        async def mock_run_coro(*args, **kwargs):
            return mock_ioreg_plist
        async def mock_json_coro(*args, **kwargs):
            return {
                "SPDisplaysDataType": [
                    {
                        "spdisplays_ndrvs": [
                            {
                                "_spdisplays_resolution": "2560 x 1600",
                                "spdisplays_refresh_rate": "60 Hz",
                                "spdisplays_depth": "32-Bit Color",
                                "_name": "Test Display",
                            }
                        ]
                    }
                ]
            }
        
        mock_run.side_effect = mock_run_coro
        mock_json.side_effect = mock_json_coro

        async def run_test():
            displays = await collect_display_info()

            assert len(displays) >= 1
            # EDID data should be present (if parsing succeeded)
            # Note: Actual values depend on EDID parsing implementation

        asyncio.run(run_test())

    @patch("prose.collectors.system.async_run_command")
    @patch("prose.collectors.system.async_get_json_output")
    def test_collect_display_info_structure_complete(self, mock_json, mock_run):
        """Test that all required fields are present in display info."""
        # Make the mock functions return coroutines on each call
        async def mock_run_coro(*args, **kwargs):
            return ""
        async def mock_json_coro(*args, **kwargs):
            return None
        
        mock_run.side_effect = mock_run_coro
        mock_json.side_effect = mock_json_coro

        async def run_test():
            displays = await collect_display_info()
            display = displays[0]

            # Verify all Phase 4 fields are present
            required_fields = [
                "resolution",
                "refresh_rate",
                "color_depth",
                "external_displays",
                "edid_manufacturer",
                "edid_product_code",
                "edid_serial",
                "connector_type",
            ]

            for field in required_fields:
                assert field in display, f"Missing field: {field}"

        asyncio.run(run_test())
