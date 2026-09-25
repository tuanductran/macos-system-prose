"""Tests for the CLI argument parser."""

from __future__ import annotations

from prose.cli import build_parser


def test_build_parser_defaults() -> None:
    args = build_parser().parse_args([])

    assert args.mode == "deep"
    assert args.output == "macos_system_report.json"
    assert args.refresh_interval == 30
    assert args.verbose is False
    assert args.quiet is False
    assert args.no_prompt is False
    assert args.tui is False
    assert args.live is False
    assert args.include_sensitive_network is False
    assert args.diff is None


def test_build_parser_accepts_collection_and_output_options() -> None:
    args = build_parser().parse_args(
        [
            "--verbose",
            "--include-sensitive-network",
            "--mode",
            "fast",
            "--no-prompt",
            "--output",
            "report.json",
            "--diff",
            "previous.json",
            "--tui",
            "--live",
            "--refresh-interval",
            "10",
        ]
    )

    assert args.verbose is True
    assert args.include_sensitive_network is True
    assert args.mode == "fast"
    assert args.no_prompt is True
    assert args.output == "report.json"
    assert args.diff == "previous.json"
    assert args.tui is True
    assert args.live is True
    assert args.refresh_interval == 10
