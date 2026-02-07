#!/usr/bin/env python3
"""
macOS Version Scraper — fetch latest macOS versions from Apple Support
and update data/macos_versions.json automatically.

Uses ONLY Python stdlib (no external dependencies).

Usage:
    python3 scripts/scrape_macos_versions.py           # Preview changes
    python3 scripts/scrape_macos_versions.py --write    # Write to data/macos_versions.json
    python3 scripts/scrape_macos_versions.py --verbose  # Debug output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

APPLE_SUPPORT_URL = "https://support.apple.com/en-us/109033"
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "macos_versions.json"

# Known macOS major version → marketing name (oldest to newest)
KNOWN_VERSIONS: dict[str, str] = {
    "10.0": "Cheetah",
    "10.1": "Puma",
    "10.2": "Jaguar",
    "10.3": "Panther",
    "10.4": "Tiger",
    "10.5": "Leopard",
    "10.6": "Snow Leopard",
    "10.7": "Lion",
    "10.8": "Mountain Lion",
    "10.9": "Mavericks",
    "10.10": "Yosemite",
    "10.11": "El Capitan",
    "10.12": "Sierra",
    "10.13": "High Sierra",
    "10.14": "Mojave",
    "10.15": "Catalina",
    "11": "Big Sur",
    "12": "Monterey",
    "13": "Ventura",
    "14": "Sonoma",
    "15": "Sequoia",
    "26": "Tahoe",
}

# Approximate release years
RELEASE_YEARS: dict[str, int] = {
    "10.0": 2001,
    "10.1": 2001,
    "10.2": 2002,
    "10.3": 2003,
    "10.4": 2005,
    "10.5": 2007,
    "10.6": 2009,
    "10.7": 2011,
    "10.8": 2012,
    "10.9": 2013,
    "10.10": 2014,
    "10.11": 2015,
    "10.12": 2016,
    "10.13": 2017,
    "10.14": 2018,
    "10.15": 2019,
    "11": 2020,
    "12": 2021,
    "13": 2022,
    "14": 2023,
    "15": 2024,
    "26": 2025,
}


class _TextExtractor(HTMLParser):
    """Extract all text content from HTML (stdlib only)."""

    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def get_text(self) -> str:
        return " ".join(self.text)


def fetch_html(url: str, timeout: int = 30) -> str:
    """Fetch HTML content from URL using urllib (stdlib)."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as response:
        content: bytes = response.read()
        return content.decode("utf-8")


def extract_latest_versions(html: str, verbose: bool = False) -> dict[str, str]:
    """Extract latest patch versions from Apple Support HTML.

    Returns:
        Dict mapping major version key (e.g., "15") to latest patch version (e.g., "15.3.1").
    """
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.get_text()

    if verbose:
        print(f"[DEBUG] Extracted {len(text)} characters of text", file=sys.stderr)

    # Pattern: "macOS Sequoia 15.3" or "macOS Big Sur 11.7.11"
    pattern = re.compile(r"macOS\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([\d.]+)")
    matches = pattern.findall(text)

    if verbose:
        print(f"[DEBUG] Found {len(matches)} version patterns", file=sys.stderr)

    latest: dict[str, str] = {}
    for _name, version in matches:
        if version.startswith("10."):
            major = ".".join(version.split(".")[:2])
        else:
            major = version.split(".")[0]

        if major in KNOWN_VERSIONS:
            if major not in latest or _compare_versions(version, latest[major]) > 0:
                latest[major] = version
                if verbose:
                    print(f"[DEBUG] {KNOWN_VERSIONS[major]}: {version}", file=sys.stderr)

    return latest


def _compare_versions(a: str, b: str) -> int:
    """Compare two version strings. Returns >0 if a > b."""
    pa = [int(x) for x in a.split(".")]
    pb = [int(x) for x in b.split(".")]
    for x, y in zip(pa, pb):
        if x != y:
            return x - y
    return len(pa) - len(pb)


def _version_sort_key(k: str) -> tuple[int, ...]:
    """Convert version string to tuple for sorting (e.g., '10.15' → (10, 15))."""
    return tuple(int(p) for p in k.split("."))


def build_json(scraped_latest: dict[str, str]) -> dict:
    """Build the full macos_versions.json structure.

    Merges scraped latest patch versions with the known version database.
    """
    # Build version_names (same as KNOWN_VERSIONS)
    version_names = dict(KNOWN_VERSIONS)

    # Build versions list (newest first)
    versions: list[dict[str, object]] = []
    sorted_keys = sorted(
        KNOWN_VERSIONS.keys(),
        key=_version_sort_key,
        reverse=True,
    )

    for major_key in sorted_keys:
        name = KNOWN_VERSIONS[major_key]
        release_year = RELEASE_YEARS.get(major_key, 0)
        major_int = int(major_key.split(".")[0])

        # Use scraped latest version, or fallback to existing data
        latest = scraped_latest.get(major_key, major_key + ".0")

        versions.append(
            {
                "major": major_int,
                "version": major_key,  # Store as string to preserve precision
                "name": name,
                "release_year": release_year,
                "latest": latest,
            }
        )

    return {
        "version_names": version_names,
        "versions": versions,
    }


def load_existing() -> dict | None:
    """Load existing data/macos_versions.json if it exists."""
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def show_diff(old: dict | None, new: dict) -> None:
    """Show changes between old and new data."""
    if not old:
        print("  (no existing file — will create new)", file=sys.stderr)
        return

    old_versions = {v["name"]: v.get("latest", "?") for v in old.get("versions", [])}
    new_versions = {v["name"]: v.get("latest", "?") for v in new.get("versions", [])}

    changed = False
    for name in new_versions:
        old_v = old_versions.get(name)
        new_v = new_versions[name]
        if old_v != new_v:
            print(f"  {name}: {old_v or '(new)'} → {new_v}", file=sys.stderr)
            changed = True

    if not changed:
        print("  (no changes)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape latest macOS versions from Apple Support")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--write",
        "-w",
        action="store_true",
        help="Write to data/macos_versions.json",
    )
    args = parser.parse_args()

    print(f"Fetching {APPLE_SUPPORT_URL} ...", file=sys.stderr)
    try:
        html = fetch_html(APPLE_SUPPORT_URL)
    except Exception as e:
        print(f"Error fetching Apple Support: {e}", file=sys.stderr)
        sys.exit(1)

    print("Extracting versions...", file=sys.stderr)
    scraped = extract_latest_versions(html, verbose=args.verbose)

    if not scraped:
        print("Error: No versions found from Apple Support page", file=sys.stderr)
        sys.exit(1)

    print(f"Scraped {len(scraped)} versions from Apple:", file=sys.stderr)
    for major in sorted(scraped, key=_version_sort_key, reverse=True):
        name = KNOWN_VERSIONS.get(major, "?")
        print(f"  {name:<15} {scraped[major]}", file=sys.stderr)

    new_data = build_json(scraped)

    print("\nChanges:", file=sys.stderr)
    old_data = load_existing()
    show_diff(old_data, new_data)

    if args.write:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n✅ Updated {DATA_FILE}", file=sys.stderr)
    else:
        print(f"\nDry run — use --write to save to {DATA_FILE}", file=sys.stderr)
        print(json.dumps(new_data, indent=2))


if __name__ == "__main__":
    main()
