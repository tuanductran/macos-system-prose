from __future__ import annotations

from prose.macos_versions import parse_version_string


def test_parse_version_string_normal():
    assert parse_version_string("12.7.6") == (12, 7, 6)
    assert parse_version_string("10.15.7") == (10, 15, 7)


def test_parse_version_string_partial_components_default_to_zero():
    assert parse_version_string("14") == (14, 0, 0)
    assert parse_version_string("14.5") == (14, 5, 0)


def test_parse_version_string_empty_does_not_raise():
    """``sw_vers -productVersion`` can return an empty string if the command
    fails or times out (e.g. under heavy load); this must not crash the
    system-info collector with a ValueError."""
    assert parse_version_string("") == (0, 0, 0)


def test_parse_version_string_non_numeric_components_default_to_zero():
    """A malformed or unexpected version string (e.g. a beta suffix) should
    degrade gracefully instead of raising."""
    assert parse_version_string("12.7.6-beta") == (12, 7, 0)
    assert parse_version_string("not-a-version") == (0, 0, 0)
