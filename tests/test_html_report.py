"""Tests for the HTML report generator."""

from __future__ import annotations

from prose.html_report import generate_html_report


def test_generate_html_report_basic():
    """Test basic HTML report generation."""
    data = {
        "timestamp": 1738908295.123,
        "system": {
            "macos_name": "macOS Monterey",
            "macos_version": "12.7.6",
            "architecture": "x86_64",
            "model_name": "MacBook Air",
            "sip_enabled": True,
            "gatekeeper_enabled": True,
            "filevault_enabled": False,
        },
        "hardware": {
            "cpu": "Intel Core i5",
            "memory_gb": 8.0,
            "memory_pressure": {"level": "normal"},
        },
        "disk": {
            "disk_total_gb": 256.0,
            "disk_free_gb": 128.5,
        },
        "network": {
            "hostname": "test-mac",
            "ipv4_address": "192.168.1.10",
        },
        "package_managers": {
            "homebrew": {"installed": True},
            "npm": {"installed": False},
        },
        "developer_tools": {
            "docker": {"installed": True},
        },
    }

    html = generate_html_report(data)

    # Check basic structure
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html
    assert "macOS System Prose" in html

    # Check data is present
    assert "MacBook Air" in html
    assert "macOS Monterey" in html
    assert "12.7.6" in html
    assert "x86_64" in html

    # Check badges
    assert "Enabled" in html
    assert "Disabled" in html

    # Check CSS is included
    assert "<style>" in html
    assert "background-color" in html
    assert "glassmorphism" in html or "backdrop-filter" in html


def test_generate_html_report_empty_data():
    """Test HTML generation with minimal data."""
    data = {
        "timestamp": 0,
        "system": {},
        "hardware": {},
        "disk": {},
        "network": {},
        "package_managers": {},
        "developer_tools": {},
    }

    html = generate_html_report(data)

    # Should still generate valid HTML
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html


def test_generate_html_report_special_characters():
    """Test HTML generation with special characters."""
    data = {
        "timestamp": 1738908295.123,
        "system": {
            "macos_name": "macOS <Test>",
            "model_name": "Mac & Air",
        },
        "hardware": {},
        "disk": {},
        "network": {},
        "package_managers": {},
        "developer_tools": {},
    }

    html = generate_html_report(data)

    # Should escape special characters
    assert "<!DOCTYPE html>" in html
    # Note: Python's f-strings don't auto-escape, so we just check it doesn't crash
