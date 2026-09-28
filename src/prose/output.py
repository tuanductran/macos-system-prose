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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    return path


def save_text(content: str, output_path: str | Path) -> Path:
    """Write text content to disk and return its resolved path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write(content)
    return path


def save_html_report(report: SystemReport, output_path: str | Path) -> Path:
    """Write a self-contained HTML report and return its path."""
    import html

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    title = "macOS System Prose Report"
    sections: list[str] = []
    for key, value in report.items():
        payload = json.dumps(value, indent=2, ensure_ascii=False)
        sections.append(
            f"<details open><summary>{html.escape(str(key))}</summary>"
            f"<pre>{html.escape(payload, quote=False)}</pre></details>"
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light dark; }}
body {{ font: 15px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;
  max-width: 1200px; margin: 0 auto; padding: 32px;
  background: Canvas; color: CanvasText; }}
h1 {{ font-size: 28px; margin: 0 0 8px; }}
.meta {{ opacity: .7; margin-bottom: 24px; }}
details {{ border: 1px solid color-mix(in srgb, CanvasText 15%, transparent);
  border-radius: 10px; margin: 10px 0; overflow: hidden; }}
summary {{ cursor: pointer; padding: 12px 16px; font-weight: 600; }}
pre {{ margin: 0; padding: 16px; overflow: auto;
  background: color-mix(in srgb, CanvasText 5%, Canvas); }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">Schema: {html.escape(str(report.get("report_schema", "")))} ·
Version: {report.get("report_schema_version", "")}</div>
{"".join(sections)}
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")
    return path
