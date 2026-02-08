"""Module for generating a beautiful HTML report from a SystemReport using Bootstrap 5."""

from __future__ import annotations

from datetime import datetime

from prose.schema import SystemReport


def generate_html_report(data: SystemReport) -> str:
    """Generate a premium, dark-themed HTML report using Bootstrap 5.

    Args:
        data: System report with proper TypedDict structure

    Returns:
        HTML string with Bootstrap 5 dark theme
    """
    timestamp = datetime.fromtimestamp(data.get("timestamp", 0.0)).strftime("%Y-%m-%d %H:%M:%S")
    system = data.get("system") or {}
    hardware = data.get("hardware") or {}
    network = data.get("network") or {}
    disk = data.get("disk") or {}

    # Status checks
    pkg_mgrs = data.get("package_managers") or {}
    dev_tools = data.get("developer_tools") or {}

    # Type-safe nested extractions
    homebrew_info = pkg_mgrs.get("homebrew")
    has_homebrew = bool(
        homebrew_info.get("installed") if isinstance(homebrew_info, dict) else False
    )

    npm_info = pkg_mgrs.get("npm")
    has_npm = bool(npm_info.get("installed") if isinstance(npm_info, dict) else False)

    docker_info = dev_tools.get("docker")
    has_docker = bool(docker_info.get("installed") if isinstance(docker_info, dict) else False)

    sip_enabled = bool(system.get("sip_enabled"))
    gk_enabled = bool(system.get("gatekeeper_enabled"))
    fv_enabled = bool(system.get("filevault_enabled"))

    # Extract nested values with type checking
    time_machine = system.get("time_machine")
    tm_enabled = bool(
        time_machine.get("enabled", False) if isinstance(time_machine, dict) else False
    )

    fw_status = network.get("firewall_status", "Unknown")
    fw_enabled = fw_status.lower() == "enabled" if isinstance(fw_status, str) else False

    git_info = dev_tools.get("git")
    git_user = str(
        git_info.get("user_name", "Unknown") if isinstance(git_info, dict) else "Unknown"
    )

    mem_pressure_data = hardware.get("memory_pressure")
    mem_pressure_level = (
        mem_pressure_data.get("level", "normal")
        if isinstance(mem_pressure_data, dict)
        else "normal"
    )
    mem_pressure = str(mem_pressure_level).title()

    # Calculate disk usage from total and free space
    disk_total_gb = float(disk.get("disk_total_gb", 0))
    disk_free_gb = float(disk.get("disk_free_gb", 0))
    disk_used_gb = max(0.0, disk_total_gb - disk_free_gb)

    # Calculate percentage and clamp to 0-100 range
    if disk_total_gb > 0:
        disk_percent = min(100.0, max(0.0, (disk_used_gb / disk_total_gb) * 100))
    else:
        disk_percent = 0.0

    # Static resources
    bootstrap_css = (
        '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" '
        'rel="stylesheet">'
    )
    bootstrap_icons = (
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">'
    )

    header_class = (
        "d-flex justify-content-between align-items-end mb-5 border-bottom border-secondary pb-3"
    )

    # Format CPU cores info (no cpu_threads in schema, only cpu_cores)
    cpu_cores = hardware.get("cpu_cores")
    core_info = "Unknown" if cpu_cores is None else f"{cpu_cores} cores"

    # Format memory info
    memory_gb = hardware.get("memory_gb")
    memory_info = "Unknown" if memory_gb is None else f"{memory_gb} GB"

    def get_badge(status: bool) -> str:
        color = "success" if status else "danger"
        text = "Enabled" if status else "Disabled"
        return f'<span class="badge bg-{color}">{text}</span>'

    def get_check(status: bool) -> str:
        color = "success" if status else "secondary"
        icon = "✓" if status else "✗"
        return f'<span class="badge bg-{color} rounded-pill">{icon}</span>'

    def format_row(label: str, value: str | int | float | bool | None) -> str:
        return f"""
        <div class="d-flex justify-content-between mb-2 border-bottom border-secondary-subtle pb-1">
            <span class="text-secondary">{label}</span>
            <span class="fw-medium text-end">{value}</span>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>macOS System Report - {system.get("model_name", "Mac")}</title>
        {bootstrap_css}
        {bootstrap_icons}
        <style>
            body {{ background-color: #0d1117; }}
            .card {{ background-color: #161b22; border-color: #30363d; }}
            .card-header {{ background-color: #21262d; border-bottom-color: #30363d; }}
            .text-accent {{ color: #58a6ff; }}
        </style>
    </head>
    <body class="py-5">
        <div class="container">
            <!-- Header -->
            <header class="{header_class}">
                <div>
                    <h1 class="display-5 fw-bold text-accent mb-0">macOS System Prose</h1>
                    <div class="text-secondary">Generated on {timestamp}</div>
                </div>
                <div class="text-end">
                    <h2 class="h4 mb-0">{system.get("macos_name", "macOS")}</h2>
                    <div class="text-secondary">
                        {system.get("macos_version")} ({system.get("architecture")})
                    </div>
                </div>
            </header>

            <div class="row g-4">
                <!-- System Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-apple me-2"></i>System
                        </div>
                        <div class="card-body">
                            {format_row("Model", str(system.get("model_name", "Unknown")))}
                            {
        format_row(
            "Identifier",
            str(system.get("model_identifier", "Unknown")),
        )
    }
                            {format_row("Serial", str(system.get("serial_number", "redacted")))}
                            {format_row("Uptime", str(system.get("uptime", "Unknown")))}
                            {format_row("Time Machine", get_badge(tm_enabled))}
                        </div>
                    </div>
                </div>

                <!-- Hardware Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-cpu me-2"></i>Hardware
                        </div>
                        <div class="card-body">
                            {format_row("CPU", str(hardware.get("cpu", "Unknown")))}
                            {format_row("Cores", core_info)}
                            {format_row("Memory", memory_info)}
                            {format_row("GPU", ", ".join(hardware.get("gpu", ["Unknown"])))}
                            {format_row("Pressure", mem_pressure)}
                        </div>
                    </div>
                </div>

                <!-- Security Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-shield-lock me-2"></i>Security
                        </div>
                        <div class="card-body">
                            {format_row("SIP Integrity", get_badge(sip_enabled))}
                            {format_row("Gatekeeper", get_badge(gk_enabled))}
                            {format_row("FileVault", get_badge(fv_enabled))}
                            {format_row("Secure Boot", str(system.get("secure_boot", "Unknown")))}
                        </div>
                    </div>
                </div>

                <!-- Disk Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-hdd me-2"></i>Storage
                        </div>
                        <div class="card-body">
                            {format_row("Total Space", f"{disk_total_gb:.1f} GB")}
                            {format_row("Free Space", f"{disk_free_gb:.1f} GB")}
                            {format_row("Used Space", f"{disk_used_gb:.1f} GB")}
                            <div class="progress mt-3" style="height: 6px;">
                                <div class="progress-bar bg-info" role="progressbar"
                                     style="width: {disk_percent:.1f}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Network Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-wifi me-2"></i>Network
                        </div>
                        <div class="card-body">
                            {format_row("Public IP", str(network.get("public_ip", "Unknown")))}
                            {format_row("Local IP", str(network.get("ipv4_address", "Unknown")))}
                            {format_row("Gateway", str(network.get("gateway", "Unknown")))}
                            {format_row("Firewall", get_badge(fw_enabled))}
                        </div>
                    </div>
                </div>

                <!-- Dev Tools Card -->
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header fw-bold text-accent">
                            <i class="bi bi-code-slash me-2"></i>Developer
                        </div>
                        <div class="card-body">
                            {format_row("Homebrew", get_check(has_homebrew))}
                            {format_row("Node.js / NPM", get_check(has_npm))}
                            {format_row("Docker", get_check(has_docker))}
                            {format_row("Git User", git_user)}
                        </div>
                    </div>
                </div>
            </div>

            <footer class="text-center text-secondary mt-5 small">
                <p>Built with <strong>macOS System Prose</strong> &bull; Open Source MIT License</p>
            </footer>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return html.strip()
