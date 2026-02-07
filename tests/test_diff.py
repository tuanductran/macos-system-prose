"""Tests for the diff module."""

from __future__ import annotations

from prose.diff import diff_reports, format_diff


def test_diff_reports_basic():
    old = {"a": 1, "b": 2, "c": [1, 2]}
    new = {"a": 1, "b": 3, "c": [2, 3], "d": 4}

    changes = diff_reports(old, new)

    assert "a" not in changes
    assert changes["b"] == {"status": "changed", "old_value": 2, "new_value": 3}
    assert changes["c"]["status"] == "changed"
    assert "3" in changes["c"]["added"]
    assert "1" in changes["c"]["removed"]
    assert changes["d"] == {"status": "added", "new_value": 4}


def test_diff_reports_nested():
    old = {"nested": {"key": "val1"}}
    new = {"nested": {"key": "val2"}}

    changes = diff_reports(old, new)
    assert "nested" in changes
    assert changes["nested"]["key"] == {
        "status": "changed",
        "old_value": "val1",
        "new_value": "val2",
    }


def test_format_diff():
    changes = {
        "b": {"status": "changed", "old_value": 2, "new_value": 3},
        "c": {"status": "changed", "added": ["3"], "removed": ["1"]},
        "d": {"status": "added", "new_value": 4},
        "nested": {"key": {"status": "changed", "old_value": "val1", "new_value": "val2"}},
    }

    lines = format_diff(changes)
    joined = "\n".join(lines)

    assert "b: 2 -> 3" in joined
    assert "+ d: 4" in joined
    assert "nested:" in joined
    assert "  * key: val1 -> val2" in joined
    assert "  + 3" in joined
    assert "  - 1" in joined
