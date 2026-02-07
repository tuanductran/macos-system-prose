#!/usr/bin/env python3
"""
macOS Version Scraper - Fetch latest macOS versions from Apple Support.

Usage: python3 scripts/scrape_macos_versions.py [--verbose]
"""

import argparse
import re
import sys
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

APPLE_URL = "https://support.apple.com/en-us/109033"
KNOWN = {
    "15": "Sequoia",
    "14": "Sonoma",
    "13": "Ventura",
    "12": "Monterey",
    "11": "Big Sur",
    "10.15": "Catalina",
    "10.14": "Mojave",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")
    _args = parser.parse_args()

    print(f"Fetching from {APPLE_URL}...")
    resp = requests.get(APPLE_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    pattern = re.compile(r"macOS\s+(\w+)\s+([\d.]+)")
    matches = pattern.findall(soup.get_text())

    versions = {}
    for _name, ver in matches:
        major = ver.split(".")[0] if not ver.startswith("10.") else ".".join(ver.split(".")[:2])
        if major in KNOWN:
            versions[major] = ver

    print(f"\nFound {len(versions)} versions:\n")
    for m in sorted(versions.keys(), reverse=True):
        print(f"  {KNOWN.get(m, m):<15} {versions[m]}")

    print("\nPython dict:")
    print("LATEST_VERSIONS = {")
    for m in sorted(versions.keys(), reverse=True):
        print(f'    "{m}": "{versions[m]}",  # {KNOWN.get(m, m)}')
    print("}")
    print(f"\nUpdated: {datetime.now().strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    main()
