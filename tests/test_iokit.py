"""Tests for NVRAM privacy-safe access helpers."""

from __future__ import annotations

from unittest.mock import patch

from prose.iokit import read_nvram


def test_read_nvram_does_not_log_raw_value():
    with (
        patch("prose.iokit.run", return_value="boot-args\tsecret-value"),
        patch("prose.iokit.verbose_log") as verbose,
    ):
        assert read_nvram("boot-args") == "secret-value"

    messages = [call.args[0] for call in verbose.call_args_list]
    assert messages == ["NVRAM variable read: boot-args"]
    assert all("secret-value" not in message for message in messages)
