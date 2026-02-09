"""Dataset modules for macOS system information.

This package contains reference data used by collectors:
- smbios: Mac model database with marketing names, specs, and compatibility
"""

from __future__ import annotations

from prose.datasets import smbios


__all__ = ["smbios"]
