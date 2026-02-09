"""Data collectors for macOS system information.

This package contains 7 specialized collector modules that gather system data:
- system: OS, hardware, displays, disk information
- network: Network interfaces, DNS, firewall, VPN
- packages: Package managers (Homebrew, MacPorts, npm, etc.)
- developer: Languages, SDKs, Docker, Git, browsers
- environment: Processes, security, TCC permissions, apps
- advanced: Storage, fonts, OCLP, shell customization
- ioregistry: IORegistry data (PCIe, USB, audio)
"""

from __future__ import annotations

from prose.collectors import (
    advanced,
    developer,
    environment,
    ioregistry,
    network,
    packages,
    system,
)


__all__ = [
    "advanced",
    "developer",
    "environment",
    "ioregistry",
    "network",
    "packages",
    "system",
]
