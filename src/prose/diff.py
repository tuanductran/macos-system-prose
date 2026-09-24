"""Module for comparing two JSON-compatible macOS system reports.

The diff operates on arbitrary nested JSON objects while keeping the recursive
value domain explicit through the shared JSONValue type.
"""

from __future__ import annotations

from collections.abc import Mapping

from prose.schema import JSONValue


def _json_value(value: object) -> JSONValue:
    """Validate and return a value as the project's JSON-compatible value type."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        result: dict[str, JSONValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"JSON object key must be str, got {type(key).__name__}")
            result[key] = _json_value(item)
        return result
    raise TypeError(f"Unsupported JSON value type: {type(value).__name__}")


def diff_reports(
    old: Mapping[str, object],
    new: Mapping[str, object],
    prefix: str = "",
) -> dict[str, JSONValue]:
    """Recursively compare two JSON-compatible mappings and return differences."""
    changes: dict[str, JSONValue] = {}
    all_keys = set(old) | set(new)

    for key in all_keys:
        if key == "timestamp":
            continue

        full_key = f"{prefix}.{key}" if prefix else key

        if key not in old:
            changes[key] = {"status": "added", "new_value": _json_value(new[key])}
            continue

        if key not in new:
            changes[key] = {"status": "removed", "old_value": _json_value(old[key])}
            continue

        old_val = old[key]
        new_val = new[key]

        if old_val == new_val:
            continue

        if isinstance(old_val, dict) and isinstance(new_val, dict):
            sub_changes = diff_reports(old_val, new_val, full_key)
            if sub_changes:
                changes[key] = sub_changes
        elif isinstance(old_val, list) and isinstance(new_val, list):
            old_set = {str(item) for item in old_val}
            new_set = {str(item) for item in new_val}

            added = sorted(new_set - old_set)
            removed = sorted(old_set - new_set)

            if added or removed:
                changes[key] = {
                    "status": "changed",
                    "added": _json_value(added),
                    "removed": _json_value(removed),
                }
        else:
            changes[key] = {
                "status": "changed",
                "old_value": _json_value(old_val),
                "new_value": _json_value(new_val),
            }

    return changes


def format_diff(changes: Mapping[str, JSONValue], indent: int = 0) -> list[str]:
    """Format a JSON-compatible diff dictionary into human-readable lines."""
    lines: list[str] = []
    pad = "  " * indent

    for key, val in sorted(changes.items()):
        if isinstance(val, dict) and "status" in val:
            status = val.get("status")
            if status == "added":
                lines.append(f"{pad}+ {key}: {val.get('new_value')}")
            elif status == "removed":
                lines.append(f"{pad}- {key}: {val.get('old_value')}")
            elif status == "changed":
                if "added" in val or "removed" in val:
                    lines.append(f"{pad}* {key}:")
                    removed_items = val.get("removed", [])
                    added_items = val.get("added", [])

                    if isinstance(removed_items, list):
                        for item in removed_items:
                            lines.append(f"{pad}  - {item}")
                    if isinstance(added_items, list):
                        for item in added_items:
                            lines.append(f"{pad}  + {item}")
                else:
                    lines.append(f"{pad}* {key}: {val.get('old_value')} -> {val.get('new_value')}")
        elif isinstance(val, dict):
            lines.append(f"{pad}{key}:")
            lines.extend(format_diff(val, indent + 1))

    return lines
