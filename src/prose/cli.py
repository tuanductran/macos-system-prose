"""Command-line parser for macOS System Prose."""

from __future__ import annotations

import argparse


def build_parser(version: str) -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="macOS System Prose Collector")
    parser.add_argument(
        "--version",
        action="version",
        version=f"macos-system-prose {version}",
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
    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "--json",
        action="store_true",
        help="Write only the JSON report",
    )
    output_format.add_argument(
        "--txt",
        action="store_true",
        help="Write only the AI-optimized text report",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output/macos_system_report.html",
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
