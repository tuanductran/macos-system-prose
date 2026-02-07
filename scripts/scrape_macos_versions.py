#!/usr/bin/env python3
"""
macOS Version Scraper - Fetch latest macOS versions from Apple Support.

This script uses ONLY Python stdlib (no external dependencies) to scrape
macOS version information from Apple's support website.

Usage:
    python3 scripts/scrape_macos_versions.py [--verbose]
    python3 scripts/scrape_macos_versions.py --output src/prose/macos_versions.py
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from urllib.request import Request, urlopen


class TextExtractor(HTMLParser):
    """Extract all text content from HTML (stdlib only)."""

    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []

    def handle_data(self, data: str) -> None:
        """Collect text data from HTML tags."""
        self.text.append(data)

    def get_text(self) -> str:
        """Return all collected text."""
        return " ".join(self.text)


# Known macOS versions to extract
KNOWN_VERSIONS = {
    "15": "Sequoia",
    "14": "Sonoma",
    "13": "Ventura",
    "12": "Monterey",
    "11": "Big Sur",
    "10.15": "Catalina",
    "10.14": "Mojave",
    "10.13": "High Sierra",
    "10.12": "Sierra",
    "10.11": "El Capitan",
    "10.10": "Yosemite",
    "10.9": "Mavericks",
}


def fetch_html(url: str, timeout: int = 30) -> str:
    """Fetch HTML content from URL using urllib (stdlib)."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as response:
        content: bytes = response.read()
        return content.decode("utf-8")


def extract_versions(html: str, verbose: bool = False) -> dict[str, str]:
    """Extract macOS versions from Apple Support HTML."""
    # Extract text from HTML
    parser = TextExtractor()
    parser.feed(html)
    text = parser.get_text()

    if verbose:
        print(f"[DEBUG] Extracted {len(text)} characters of text")

    # Pattern: "macOS Sequoia 15.3" or "macOS Big Sur 11.7.11"
    pattern = re.compile(r"macOS\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([\d.]+)")
    matches = pattern.findall(text)

    if verbose:
        print(f"[DEBUG] Found {len(matches)} version patterns")

    versions: dict[str, str] = {}
    for name, version in matches:
        # Determine major version key
        if version.startswith("10."):
            major = ".".join(version.split(".")[:2])  # "10.15"
        else:
            major = version.split(".")[0]  # "15"

        # Only track known versions
        if major in KNOWN_VERSIONS:
            # Keep highest version for each major
            if major not in versions or version > versions[major]:
                versions[major] = version
                if verbose:
                    print(f"[DEBUG] Found: {name} {version} (major: {major})")

    return versions


def generate_python_code(versions: dict[str, str]) -> str:
    """Generate Python code for macos_versions.py LATEST_VERSIONS dict."""
    lines = ["# Auto-generated macOS version data", f"# Updated: {datetime.now().isoformat()}", ""]
    lines.append("LATEST_VERSIONS = {")

    for major in sorted(versions.keys(), key=lambda x: float(x.replace(".", "0")), reverse=True):
        name = KNOWN_VERSIONS.get(major, "Unknown")
        lines.append(f'    "{major}": "{versions[major]}",  # {name}')

    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape latest macOS versions from Apple Support"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: print to stdout)",
    )
    args = parser.parse_args()

    url = "https://support.apple.com/en-us/109033"

    try:
        print(f"Fetching from {url}...", file=sys.stderr)
        html = fetch_html(url)

        print("Extracting versions...", file=sys.stderr)
        versions = extract_versions(html, verbose=args.verbose)

        if not versions:
            print("Error: No versions found", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(versions)} versions:", file=sys.stderr)
        for major in sorted(
            versions.keys(), key=lambda x: float(x.replace(".", "0")), reverse=True
        ):
            name = KNOWN_VERSIONS.get(major, "Unknown")
            print(f"  {name:<15} {versions[major]}", file=sys.stderr)

        # Generate output
        code = generate_python_code(versions)

        if args.output:
            with open(args.output, "w") as f:
                f.write(code + "\n")
            print(f"\nWrote to: {args.output}", file=sys.stderr)
        else:
            print("\n" + code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
