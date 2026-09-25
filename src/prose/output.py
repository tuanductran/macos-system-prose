"""Report output helpers for macOS System Prose."""

from __future__ import annotations

import json
from pathlib import Path

from prose.schema import SystemReport


def save_json_report(report: SystemReport, output_path: str | Path) -> Path:
    """Write a system report as formatted JSON and return its resolved path."""
    path = Path(output_path)
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    return path


def save_text(content: str, output_path: str | Path) -> Path:
    """Write text content to disk and return its resolved path."""
    path = Path(output_path)
    with path.open("w", encoding="utf-8") as file:
        file.write(content)
    return path
