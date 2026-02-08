"""Module for comparing two SystemReport objects.

Provides functionality to identify differences between two system snapshots,
useful for tracking changes over time or across different systems.
"""

from __future__ import annotations

from typing import Any, cast

# NOTE: Any is acceptable here for recursive dictionary comparison.
# The diff function needs to handle arbitrary nested structures at runtime,
# making static typing impractical. This is ONE OF ONLY TWO places in the
# codebase where Any is used (the other is conftest.py for test fixtures).
from prose.schema import SystemReport


def diff_reports(
    old: SystemReport,
    new: SystemReport,
    prefix: str = "",
) -> dict[str, Any]:
    """Recursively compare two dictionaries and return differences.

    Args:
        old: Old report to compare
        new: New report to compare
        prefix: Internal prefix for nested keys (default: "")

    Returns:
        Dictionary containing changes with status and values
    """
    changes: dict[str, Any] = {}

    # Cast TypedDict to regular dict for dynamic key access
    old_dict = cast(dict[str, Any], old)
    new_dict = cast(dict[str, Any], new)

    # All keys from both
    all_keys = set(old_dict.keys()) | set(new_dict.keys())

    for key in all_keys:
        if key == "timestamp":
            continue

        full_key = f"{prefix}.{key}" if prefix else key

        if key not in old_dict:
            changes[key] = {"status": "added", "new_value": new_dict[key]}
        elif key not in new_dict:
            changes[key] = {"status": "removed", "old_value": old_dict[key]}
        else:
            old_val = old_dict[key]
            new_val = new_dict[key]

            if old_val == new_val:
                continue

            if isinstance(old_val, dict) and isinstance(new_val, dict):
                sub_changes = diff_reports(
                    cast(SystemReport, old_val), cast(SystemReport, new_val), full_key
                )
                if sub_changes:
                    changes[key] = sub_changes
            elif isinstance(old_val, list) and isinstance(new_val, list):
                # Simple list compare for now (added/removed items)
                old_set = {str(i) for i in old_val}
                new_set = {str(i) for i in new_val}

                added = list(new_set - old_set)
                removed = list(old_set - new_set)

                if added or removed:
                    changes[key] = {"status": "changed", "added": added, "removed": removed}
            else:
                changes[key] = {"status": "changed", "old_value": old_val, "new_value": new_val}

    return changes


def format_diff(changes: dict[str, Any], indent: int = 0) -> list[str]:
    """Format the diff dictionary into human-readable lines."""
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
            # Recursive call
            lines.extend(format_diff(val, indent + 1))

    return lines
