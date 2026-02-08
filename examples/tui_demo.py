#!/usr/bin/env python3
"""TUI smoke test with mock data.

This test verifies the Textual TUI can launch with synthetic data without
requiring a full system scan. Useful for rapid TUI development and testing
UI components in isolation.

Note: This is a manual test script, not an automated unit test.
Run with: python3 examples/tui_demo.py
"""

from prose.tui.app import run_tui_sync


# Mock system report data for TUI testing
# Simulates a complete SystemReport structure with realistic values
mock_data = {
    "timestamp": 1738908295.123456,
    "system": {
        "model": "MacBook Pro",
        "model_identifier": "MacBookPro18,1",
        "macos_version": "macOS Sequoia 15.2",
        "architecture": "arm64",
        "board_id": "Mac-F42C89C8",
        "sip_enabled": True,
        "filevault_enabled": True,
        "gatekeeper_status": "Enabled",
    },
    "hardware": {
        "cpu": "Apple M1 Pro",
        "cpu_cores": 10,
        "memory_gb": 32,
        "gpu": ["Apple M1 Pro"],
        "thermal_pressure": [],
        "displays": [],
        "memory_pressure": {
            "level": "normal",
            "swap_used": "0 MB",
        },
    },
    "developer_tools": {
        "clouds": {"docker": "Docker version 25.0.0"},
        "languages": {
            "python3": "Python 3.11.5",
            "node": "v20.10.0",
        },
        "sdks": {
            "xcode": "Xcode 15.1",
        },
        "git_config": {
            "user.name": "Test User",
            "user.email": "test@example.com",
        },
    },
    "package_managers": {
        "homebrew": {
            "installed": True,
            "installed_formulae": [
                {"name": "git", "version": "2.43.0"},
                {"name": "python", "version": "3.11.5"},
            ],
            "installed_casks": [
                {"name": "visual-studio-code", "version": "1.85.0"},
            ],
        },
        "npm_global": {
            "installed": True,
            "packages": [
                {"name": "npm", "version": "10.2.5"},
                {"name": "yarn", "version": "1.22.19"},
            ],
        },
        "yarn_global": {
            "installed": True,
            "packages": [],
        },
    },
}

if __name__ == "__main__":
    print("🚀 Launching TUI with mock data...")
    print("Press 'q' to quit, 'r' to refresh")
    run_tui_sync(mock_data)
