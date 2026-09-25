"""Command-line argument parser for macOS System Prose."""

from __future__ import annotations

import argparse

from prose import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build and return the macOS System Prose CLI argument parser."""
    parser = argparse.ArgumentParser(description="macOS System Prose Collector")
    parser.add_argument(
        "--version",
        action="version",
        version=f"macos-system-prose {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all console output",
    )
    parser.add_argument(
        "--include-sensitive-network",
        action="store_true",
        help="Opt in to collecting network identity data and public IP (default: redacted)",
    )
    parser.add_argument(
        "--mode",
        choices=("fast", "deep"),
        default="deep",
        help=(
            "Collection depth: fast skips expensive filesystem/log collectors; "
            "deep collects all sections"
        ),
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip generating AI-optimized text prompt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="macos_system_report.json",
        help="Output JSON file path (default: %(default)s)",
    )
    parser.add_argument(
        "--diff",
        help="Compare current report with a previous JSON report",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch interactive terminal UI",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live refresh mode in TUI",
    )
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=30,
        help="Refresh interval in seconds for live TUI mode (default: %(default)s)",
    )
    return parser
