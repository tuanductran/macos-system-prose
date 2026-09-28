"""Tests for the command-line parser."""

from __future__ import annotations

from prose.cli import build_parser


def test_build_parser_defaults() -> None:
    args = build_parser("1.2.3").parse_args([])

    assert args.verbose is False
    assert args.quiet is False
    assert args.include_sensitive_network is False
    assert args.mode == "deep"
    assert args.json is False
    assert args.txt is False
    assert args.output is None
    assert args.diff is None
    assert args.tui is False
    assert args.live is False
    assert args.refresh_interval == 30


def test_build_parser_accepts_all_options() -> None:
    args = build_parser("1.2.3").parse_args(
        [
            "--verbose",
            "--quiet",
            "--include-sensitive-network",
            "--mode",
            "fast",
            "--json",
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
    assert args.quiet is True
    assert args.include_sensitive_network is True
    assert args.mode == "fast"
    assert args.json is True
    assert args.txt is False
    assert args.output == "report.json"
    assert args.diff == "previous.json"
    assert args.tui is True
    assert args.live is True
    assert args.refresh_interval == 10


def test_build_parser_accepts_txt_format() -> None:
    args = build_parser("1.2.3").parse_args(["--txt"])

    assert args.txt is True
    assert args.json is False


def test_build_parser_rejects_json_and_txt_together() -> None:
    import pytest

    with pytest.raises(SystemExit):
        build_parser("1.2.3").parse_args(["--json", "--txt"])
