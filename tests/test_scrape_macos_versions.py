"""Tests for the macOS version maintenance scraper."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_SCRIPT = Path(__file__).parents[1] / "scripts" / "scrape_macos_versions.py"
_SPEC = importlib.util.spec_from_file_location("scrape_macos_versions", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_scraper_knows_current_major_versions() -> None:
    assert _MODULE.KNOWN_VERSIONS["26"] == "Tahoe"
    assert _MODULE.KNOWN_VERSIONS["27"] == "Golden Gate"
    assert _MODULE.RELEASE_YEARS["27"] == 2026


def test_extract_latest_versions_supports_current_multiword_names() -> None:
    html = """
    <html><body>
      macOS Golden Gate 27.0
      macOS Tahoe 26.7
      macOS Sequoia 15.8
      macOS Sonoma 14.8.9
    </body></html>
    """
    assert _MODULE.extract_latest_versions(html) == {
        "27": "27.0",
        "26": "26.7",
        "15": "15.8",
        "14": "14.8.9",
    }


def test_build_json_preserves_current_major_versions() -> None:
    data = _MODULE.build_json({"27": "27.0", "26": "26.7", "15": "15.8"})
    versions = {item["version"]: item["latest"] for item in data["versions"]}
    assert versions["27"] == "27.0"
    assert versions["26"] == "26.7"
    assert versions["15"] == "15.8"
