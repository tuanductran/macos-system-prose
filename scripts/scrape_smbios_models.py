#!/usr/bin/env python3
"""
SMBIOS Model Scraper — fetch Mac model database from EveryMac.com
and update data/smbios_models.json automatically.

Uses ONLY Python stdlib (no external dependencies).

Usage:
    python3 scripts/scrape_smbios_models.py           # Preview changes
    python3 scripts/scrape_smbios_models.py --write    # Write to data/smbios_models.json
    python3 scripts/scrape_smbios_models.py --verbose  # Debug output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

EVERYMAC_URL = (
    "https://everymac.com/systems/by_capability/mac-specs-by-machine-model-machine-id.html"
)
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "smbios_models.json"

# CPU generation mapping
CPU_GENERATIONS: dict[str, str] = {
    "Core Solo": "Yonah",
    "Core Duo": "Yonah",
    "Core 2 Duo": "Merom",
    "Core 2 Extreme": "Merom",
    "Xeon": "Harpertown",
    "Core i3": "Sandy Bridge",
    "Core i5": "Sandy Bridge",
    "Core i7": "Sandy Bridge",
    "Core i9": "Coffee Lake",
    "M1": "Apple M1",
    "M2": "Apple M2",
    "M3": "Apple M3",
    "M4": "Apple M4",
    "M5": "Apple M5",
}

# macOS version mapping
MACOS_VERSIONS: dict[str, str] = {
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


class _TableParser(HTMLParser):
    """Parse HTML tables from EveryMac.com."""

    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []
        self.cell_data: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_row:
            self.in_cell = True
            self.cell_data = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            self.in_table = False
        elif tag == "tr" and self.in_row:
            if self.current_row:
                self.rows.append(self.current_row)
            self.in_row = False
        elif tag in ("td", "th") and self.in_cell:
            self.current_row.append(" ".join(self.cell_data).strip())
            self.in_cell = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_data.append(data.strip())


def fetch_html(url: str, timeout: int = 30) -> str:
    """Fetch HTML content from URL using urllib (stdlib)."""
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )

    with urlopen(req, timeout=timeout) as response:
        content: bytes = response.read()
        return content.decode("utf-8", errors="ignore")


def parse_screen_size(name: str) -> int | None:
    """Extract screen size from marketing name."""
    match = re.search(r"(\d+)(?:\.\d+)?-inch", name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def infer_cpu_generation(cpu_info: str) -> str:
    """Infer CPU generation from CPU info string."""
    cpu_lower = cpu_info.lower()

    # Apple Silicon
    if "m5" in cpu_lower:
        return "Apple M5"
    if "m4" in cpu_lower:
        return "Apple M4"
    if "m3" in cpu_lower:
        return "Apple M3"
    if "m2" in cpu_lower:
        return "Apple M2"
    if "m1" in cpu_lower:
        return "Apple M1"

    # Intel generations
    if "ice lake" in cpu_lower:
        return "Ice Lake"
    if "comet lake" in cpu_lower:
        return "Comet Lake"
    if "coffee lake" in cpu_lower:
        return "Coffee Lake"
    if "kaby lake" in cpu_lower:
        return "Kaby Lake"
    if "skylake" in cpu_lower:
        return "Skylake"
    if "broadwell" in cpu_lower:
        return "Broadwell"
    if "haswell" in cpu_lower:
        return "Haswell"
    if "ivy bridge" in cpu_lower:
        return "Ivy Bridge"
    if "sandy bridge" in cpu_lower:
        return "Sandy Bridge"
    if "penryn" in cpu_lower:
        return "Penryn"
    if "merom" in cpu_lower:
        return "Merom"
    if "yonah" in cpu_lower:
        return "Yonah"

    # Fallback to CPU name
    for key, gen in CPU_GENERATIONS.items():
        if key.lower() in cpu_lower:
            return gen

    return "Unknown"


def infer_max_os(year: int, cpu_gen: str) -> str:
    """Infer maximum supported macOS version based on year and CPU generation."""
    # Apple Silicon
    if "Apple M" in cpu_gen:
        return "Tahoe"

    # Intel Macs by generation
    if cpu_gen in ("Ice Lake", "Comet Lake", "Coffee Lake"):
        return "Sequoia"
    if cpu_gen in ("Kaby Lake", "Skylake"):
        return "Ventura"
    if cpu_gen == "Broadwell":
        return "Monterey"
    if cpu_gen == "Haswell":
        return "Big Sur"
    if cpu_gen == "Ivy Bridge":
        return "Catalina"
    if cpu_gen == "Sandy Bridge":
        return "High Sierra"
    if cpu_gen == "Penryn":
        return "El Capitan"
    if cpu_gen in ("Merom", "Yonah"):
        return "Lion"

    # Fallback by year
    if year >= 2020:
        return "Sequoia"
    if year >= 2016:
        return "Monterey"
    if year >= 2013:
        return "Big Sur"
    if year >= 2012:
        return "Catalina"

    return "Unknown"


def extract_models_from_html(html: str, verbose: bool = False) -> dict[str, dict]:
    """Extract Mac models from EveryMac HTML table.

    Returns:
        Dict mapping model identifier to model data.
    """
    parser = _TableParser()
    parser.feed(html)

    if verbose:
        print(f"[DEBUG] Found {len(parser.rows)} table rows", file=sys.stderr)

    models: dict[str, dict] = {}

    for row in parser.rows:
        if len(row) < 3:
            continue

        # Skip header rows
        if "Model ID" in row[0] or "Machine Model" in row[0]:
            continue

        # Extract data (columns vary by source)
        model_id = row[0].strip()
        marketing_name = row[1].strip() if len(row) > 1 else ""

        # Skip invalid entries
        if not model_id or not marketing_name:
            continue
        if "discontinued" in marketing_name.lower():
            continue

        # Extract year from marketing name
        year_match = re.search(r"(Early|Mid|Late)?\s*(\d{4})", marketing_name)
        year = int(year_match.group(2)) if year_match else 2020

        # Infer CPU generation (placeholder - would need more data)
        cpu_gen = infer_cpu_generation(marketing_name)

        # Infer max OS
        max_os = infer_max_os(year, cpu_gen)

        # Extract screen size
        screen_size = parse_screen_size(marketing_name)

        # Placeholder board ID (would need to scrape from detailed pages)
        board_id = f"Mac-{model_id.replace(',', '').replace('.', '')[:16].upper()}"

        # Placeholder GPUs (would need more detailed scraping)
        stock_gpus = ["Integrated Graphics"]
        if "Pro" in marketing_name or "Max" in marketing_name:
            stock_gpus = [f"{cpu_gen} GPU"]

        models[model_id] = {
            "marketing_name": marketing_name,
            "board_id": board_id,
            "cpu_generation": cpu_gen,
            "max_os_supported": max_os,
            "screen_size": screen_size,
            "stock_gpus": stock_gpus,
        }

        if verbose:
            print(f"[DEBUG] {model_id}: {marketing_name}", file=sys.stderr)

    return models


def load_existing() -> dict | None:
    """Load existing data/smbios_models.json if it exists."""
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def merge_models(existing: dict | None, scraped: dict[str, dict]) -> dict[str, dict]:
    """Merge scraped data with existing data, preserving manual edits."""
    if not existing:
        return scraped

    merged = dict(existing)

    # Add new models from scraped data
    for model_id, data in scraped.items():
        if model_id not in merged:
            merged[model_id] = data

    return merged


def show_diff(old: dict | None, new: dict[str, dict]) -> None:
    """Show changes between old and new data."""
    if not old:
        print(f"  (no existing file — will create {len(new)} models)", file=sys.stderr)
        return

    added = set(new.keys()) - set(old.keys())
    removed = set(old.keys()) - set(new.keys())

    if added:
        print(f"  Added {len(added)} models:", file=sys.stderr)
        for model_id in sorted(added):
            print(f"    + {model_id}: {new[model_id]['marketing_name']}", file=sys.stderr)

    if removed:
        print(f"  Removed {len(removed)} models:", file=sys.stderr)
        for model_id in sorted(removed):
            print(f"    - {model_id}", file=sys.stderr)

    if not added and not removed:
        print("  (no changes)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Mac SMBIOS models from EveryMac.com")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--write",
        "-w",
        action="store_true",
        help="Write to data/smbios_models.json",
    )
    args = parser.parse_args()

    print(f"Fetching {EVERYMAC_URL} ...", file=sys.stderr)
    try:
        html = fetch_html(EVERYMAC_URL)
    except Exception as e:
        print(f"Error fetching EveryMac: {e}", file=sys.stderr)
        print("\nNote: This is a placeholder scraper.", file=sys.stderr)
        print("For production use, consider using the existing smbios_models.json", file=sys.stderr)
        print("or manually curating the database from multiple sources.", file=sys.stderr)
        sys.exit(1)

    print("Extracting models...", file=sys.stderr)
    scraped = extract_models_from_html(html, verbose=args.verbose)

    if not scraped:
        print("Warning: No models found from EveryMac page", file=sys.stderr)
        print("Using existing database instead.", file=sys.stderr)
        scraped = load_existing() or {}

    print(f"Scraped {len(scraped)} models from EveryMac", file=sys.stderr)

    old_data = load_existing()
    merged_data = merge_models(old_data, scraped)

    print("\nChanges:", file=sys.stderr)
    show_diff(old_data, merged_data)

    if args.write:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n✅ Updated {DATA_FILE}", file=sys.stderr)
    else:
        print(f"\nDry run — use --write to save to {DATA_FILE}", file=sys.stderr)
        print(f"Preview: {len(merged_data)} total models", file=sys.stderr)


if __name__ == "__main__":
    main()
