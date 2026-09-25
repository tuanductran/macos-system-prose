"""Report output helpers for macOS System Prose."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from prose.schema import SystemReport


def load_json_report(input_path: str | Path) -> dict[str, object]:
    """Read a JSON report from disk and return its decoded object."""
    path = Path(input_path)
    with path.open(encoding="utf-8") as file:
        return cast(dict[str, object], json.load(file))


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
