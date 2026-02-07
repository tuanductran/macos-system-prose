"""Module for generating a beautiful HTML report from a SystemReport."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate a premium, dark-themed HTML report for the system data."""
    timestamp = datetime.fromtimestamp(data.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
    system = data.get("system", {})
    hardware = data.get("hardware", {})

    # Status checks for cleaner template
    pkg_mgrs = data.get("package_managers", {})
    dev_tools = data.get("developer_tools", {})

    has_homebrew = pkg_mgrs.get("homebrew", {}).get("installed")
    has_npm = pkg_mgrs.get("npm", {}).get("installed")
    has_docker = dev_tools.get("docker", {}).get("installed")

    sip_status = "Enabled" if system.get("sip_enabled") else "Disabled"
    gatekeeper_status = "Enabled" if system.get("gatekeeper_enabled") else "Disabled"
    filevault_status = "Enabled" if system.get("filevault_enabled") else "Disabled"

    # Modern CSS with glassmorphism and animated gradients
    css = """
    :root {
        --bg: #0a0a0c;
        --card-bg: rgba(30, 30, 35, 0.7);
        --accent: #4a9eff;
        --text: #e0e0e0;
        --text-dim: #a0a0a0;
        --success: #43d39e;
        --warning: #ffbe0b;
        --error: #ff5f5f;
    }

    body {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0;
        padding: 40px;
        line-height: 1.6;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
    }

    header {
        margin-bottom: 40px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #4a9eff 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .timestamp { color: var(--text-dim); font-size: 0.9rem; }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 20px;
    }

    .card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 24px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .card:hover {
        transform: translateY(-4px);
        border-color: rgba(74, 158, 255, 0.3);
    }

    h2 {
        margin-top: 0;
        font-size: 1.2rem;
        color: var(--accent);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }

    .label { color: var(--text-dim); }
    .value { font-weight: 500; text-align: right; }

    .footer {
        margin-top: 60px;
        text-align: center;
        color: var(--text-dim);
        font-size: 0.8rem;
    }

    .badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        background: rgba(255,255,255,0.1);
    }

    .badge-success { background: rgba(67, 211, 158, 0.15); color: var(--success); }
    .badge-warning { background: rgba(255, 190, 11, 0.15); color: var(--warning); }
    .badge-error { background: rgba(255, 95, 95, 0.15); color: var(--error); }
    """

    def format_dict(d: Dict[str, Any]) -> str:
        rows = ""
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                continue
            label = k.replace("_", " ").title()
            val = str(v)
            if v is True:
                val = '<span class="badge badge-success">Enabled</span>'
            elif v is False:
                val = '<span class="badge badge-error">Disabled</span>'
            rows += f'<div class="info-row"><span class="label">{label}</span><span class="value">{val}</span></div>'  # noqa: E501
        return rows

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>macOS System Report - {system.get("model_name", "Mac")}</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>macOS System Prose</h1>
                    <div class="timestamp">Generated on {timestamp}</div>
                </div>
                <div style="text-align: right">
                    <div style="font-weight: bold">{system.get("macos_name")}</div>
                    <div class="label">
                        {system.get("macos_version")} ({system.get("architecture")})
                    </div>
                </div>
            </header>

            <div class="grid">
                <div class="card">
                    <h2> System</h2>
                    {format_dict(system)}
                </div>

                <div class="card">
                    <h2>⚙️ Hardware</h2>
                    {format_dict(hardware)}
                    <div class="info-row">
                        <span class="label">Memory Pressure</span>
                        <span class="value">
                            {hardware.get("memory_pressure", {}).get("level", "Unknown").title()}
                        </span>
                    </div>
                </div>

                <div class="card">
                    <h2>💾 Disk</h2>
                    <div class="info-row">
                        <span class="label">Total</span>
                        <span class="value">{data.get("disk", {}).get("disk_total_gb")} GB</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Free</span>
                        <span class="value">{data.get("disk", {}).get("disk_free_gb")} GB</span>
                    </div>
                </div>

                <div class="card">
                    <h2>🌐 Network</h2>
                    {format_dict(data.get("network", {}))}
                </div>


                <div class="card">
                    <h2>📦 Management</h2>
                    <div class="info-row">
                        <span class="label">Homebrew</span>
                        <span class="value">{"✓" if has_homebrew else "✗"}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">NPM</span>
                        <span class="value">{"✓" if has_npm else "✗"}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Docker</span>
                        <span class="value">{"✓" if has_docker else "✗"}</span>
                    </div>
                </div>


                <div class="card">
                    <h2>🛡️ Security</h2>
                    <div class="info-row">
                        <span class="label">SIP</span>
                        <span class="value">{sip_status}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Gatekeeper</span>
                        <span class="value">{gatekeeper_status}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">FileVault</span>
                        <span class="value">{filevault_status}</span>
                    </div>
                </div>
            </div>

            <div class="footer">
                Built with <strong>macOS System Prose</strong> &bull; Open Source MIT License
            </div>
        </div>
    </body>
    </html>
    """
    return html.strip()
