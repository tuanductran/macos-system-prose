"""Module for comparing two SystemReport objects.

Provides functionality to identify differences between two system snapshots,
useful for tracking changes over time or across different systems.
"""

from __future__ import annotations

from typing import Any, Dict, List


def diff_reports(old: Dict[str, Any], new: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Recursively compare two dictionaries and return differences."""
    changes = {}

    # All keys from both
    all_keys = set(old.keys()) | set(new.keys())

    for key in all_keys:
        if key == "timestamp":
            continue

        full_key = f"{prefix}.{key}" if prefix else key

        if key not in old:
            changes[key] = {"status": "added", "new_value": new[key]}
        elif key not in new:
            changes[key] = {"status": "removed", "old_value": old[key]}
        else:
            old_val = old[key]
            new_val = new[key]

            if old_val == new_val:
                continue

            if isinstance(old_val, dict) and isinstance(new_val, dict):
                sub_changes = diff_reports(old_val, new_val, full_key)
                if sub_changes:
                    changes[key] = sub_changes
            elif isinstance(old_val, list) and isinstance(new_val, list):
                # Simple list compare for now (added/removed items)
                old_set = set(str(i) for i in old_val)
                new_set = set(str(i) for i in new_val)

                added = list(new_set - old_set)
                removed = list(old_set - new_set)

                if added or removed:
                    changes[key] = {"status": "changed", "added": added, "removed": removed}
            else:
                changes[key] = {"status": "changed", "old_value": old_val, "new_value": new_val}

    return changes


def format_diff(changes: Dict[str, Any], indent: int = 0) -> List[str]:
    """Format the diff dictionary into human-readable lines."""
    lines = []
    pad = "  " * indent

    for key, val in sorted(changes.items()):
        if "status" in val:
            status = val["status"]
            if status == "added":
                lines.append(f"{pad}+ {key}: {val['new_value']}")
            elif status == "removed":
                lines.append(f"{pad}- {key}: {val['old_value']}")
            elif status == "changed":
                if "added" in val or "removed" in val:
                    lines.append(f"{pad}* {key}:")
                    for item in val.get("removed", []):
                        lines.append(f"{pad}  - {item}")
                    for item in val.get("added", []):
                        lines.append(f"{pad}  + {item}")
                else:
                    lines.append(f"{pad}* {key}: {val['old_value']} -> {val['new_value']}")
        else:
            lines.append(f"{pad}{key}:")
            lines.extend(format_diff(val, indent + 1))

    return lines
