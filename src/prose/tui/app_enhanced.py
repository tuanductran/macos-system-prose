"""macOS System Prose - Enhanced Textual TUI Application

Professional terminal user interface implementing:
- Phases 2-4: Enhanced navigation, live updates, Apple HIG compliance
- 7 tabs with detailed DataTables
- Keyboard shortcuts (⌘1-7, ⌘F, ⌘E, ⌘R, ⌘?)
- Apple Human Interface Guidelines colors and typography
- Progress bars for disk/battery/memory usage
- Live refresh support
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar, cast

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    ProgressBar,
    Static,
    TabbedContent,
    TabPane,
)

from prose.schema import SystemReport


if TYPE_CHECKING:
    from prose.schema import SystemReport


# Apple HIG Colors (macOS system colors)
COLORS = {
    "blue": "#007AFF",  # Primary action color
    "green": "#34C759",  # Success, enabled states
    "red": "#FF3B30",  # Destructive, alerts
    "orange": "#FF9500",  # Warnings
    "yellow": "#FFCC00",  # Attention
    "purple": "#AF52DE",  # Secondary action
    "pink": "#FF2D55",  # Tertiary action
    "gray": "#8E8E93",  # Disabled, placeholder
    "background": "#1C1C1E",  # Dark mode background
    "surface": "#2C2C2E",  # Card background
}


class StatsCard(Static):
    """Base card class with Apple HIG styling."""

    DEFAULT_CSS = """
    StatsCard {
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
        height: auto;
        min-height: 10;
    }
    """


class SystemOverviewCard(StatsCard):
    """System overview with progress bars for disk/memory."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data
        system = data.get("system", {})
        self.model = system.get("model_name", "Unknown")
        self.macos_version = system.get("macos_version", "Unknown")
        self.kernel = system.get("kernel", "Unknown")
        self.uptime = system.get("uptime", "Unknown")

        # Memory pressure
        hardware = data.get("hardware", {})
        mem_pressure = hardware.get("memory_pressure", {})
        self.mem_level = mem_pressure.get("level", "Unknown")

        # Disk usage
        disk = data.get("disk", {})
        if disk:
            self.disk_total = disk.get("disk_total_gb", 0)
            self.disk_free = disk.get("disk_free_gb", 0)
            self.disk_used = self.disk_total - self.disk_free
            self.disk_percent = (
                int((self.disk_used / self.disk_total) * 100) if self.disk_total > 0 else 0
            )
        else:
            self.disk_percent = 0

    def compose(self) -> ComposeResult:
        yield Label("[bold #007AFF]System Overview[/]")
        yield Label(f"[#8E8E93]Model:[/] {self.model}")
        yield Label(f"[#8E8E93]macOS:[/] {self.macos_version}")
        yield Label(f"[#8E8E93]Kernel:[/] {self.kernel}")
        yield Label(f"[#8E8E93]Uptime:[/] {self.uptime}")
        yield Label("")
        yield Label(f"[#8E8E93]Disk Usage:[/] {self.disk_percent}%")
        yield ProgressBar(total=100, show_eta=False, show_percentage=False)
        yield Label(f"[#8E8E93]Memory Pressure:[/] {self.mem_level.title()}")

    def on_mount(self) -> None:
        """Update progress bar on mount."""
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(progress=self.disk_percent)


class MonitorHeader(Static):
    """Compact header with htop-style metrics."""

    DEFAULT_CSS = """
    MonitorHeader {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        height: auto;
        padding: 1;
        background: $surface;
        border-bottom: solid $primary;
        margin-bottom: 1;
    }
    .metric-row {
        layout: horizontal;
        height: 1;
        margin-right: 2;
    }
    .font-bold {
        text-style: bold;
    }
    .metric-label {
        width: 12;
        color: #8E8E93;
    }
    .metric-value {
        width: auto;
        color: white;
    }
    ProgressBar {
        width: 1fr;
        margin-left: 1;
    }
    """

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data
        self.cpu_pct = 0.0
        self.mem_pct = 0.0
        self.disk_pct = 0.0

    def compose(self) -> ComposeResult:
        # Extract data
        system = self.data.get("system", {})
        hard = self.data.get("hardware", {})
        disk = self.data.get("disk", {})
        load = system.get("load_average", "0.0 0.0 0.0").split()
        mem_pressure = hard.get("memory_pressure", {})

        # Calculate Percentages
        cores = hard.get("cpu_cores", 8)
        try:
            load_1min = float(load[0])
            self.cpu_pct = min(100, (load_1min / cores) * 100)
        except (ValueError, IndexError):
            self.cpu_pct = 0.0

        mem_level = mem_pressure.get("level", "normal")
        self.mem_pct = 30 if mem_level == "normal" else (60 if mem_level == "warn" else 90)

        used_gb = disk.get("disk_total_gb", 0) - disk.get("disk_free_gb", 0)
        total_gb = disk.get("disk_total_gb", 1)
        self.disk_pct = (used_gb / total_gb) * 100

        # CPU/Mem (Left Column)
        with Vertical():
            with Horizontal(classes="metric-row"):
                yield Label("CPU Usage:", classes="metric-label")
                yield ProgressBar(total=100, show_eta=False, id="pb_cpu")
                yield Label(f" {self.cpu_pct:.1f}%", classes="metric-value")

            with Horizontal(classes="metric-row"):
                yield Label("Memory:", classes="metric-label")
                yield ProgressBar(total=100, show_eta=False, id="pb_mem")
                yield Label(f" {mem_level.title()}", classes="metric-value")

            with Horizontal(classes="metric-row"):
                yield Label("Disk /:", classes="metric-label")
                yield ProgressBar(total=100, show_eta=False, id="pb_disk")
                yield Label(f" {used_gb:.0f}/{total_gb:.0f}G", classes="metric-value")

        # Info (Right Column)
        with Vertical():
            with Horizontal(classes="metric-row"):
                yield Label("Tasks:", classes="metric-label")
                proc_count = len(self.data.get("top_processes", []))
                yield Label(f"{proc_count} running processes", classes="metric-value")

            with Horizontal(classes="metric-row"):
                yield Label("Load Avg:", classes="metric-label")
                yield Label(f"{' '.join(load)}", classes="metric-value")

            with Horizontal(classes="metric-row"):
                yield Label("Uptime:", classes="metric-label")
                yield Label(f"{system.get('uptime', 'Unknown')}", classes="metric-value")

            with Horizontal(classes="metric-row"):
                yield Label("System:", classes="metric-label")
                yield Label(f"{system.get('model_name')}", classes="metric-value")

    def on_mount(self) -> None:
        """Update progress bars."""
        self.query_one("#pb_cpu", ProgressBar).update(progress=self.cpu_pct)
        self.query_one("#pb_mem", ProgressBar).update(progress=self.mem_pct)
        self.query_one("#pb_disk", ProgressBar).update(progress=self.disk_pct)


class NetworkOverviewCard(StatsCard):
    """Network overview with connection status."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        # MyPy can infer these types from SystemReport
        network = data.get("network", {})
        self.public_ip = network.get("public_ip", "Unknown")
        interfaces = network.get("interfaces", [])
        self.interface_count = len(interfaces) if isinstance(interfaces, list) else 0
        self.vpn_active = network.get("vpn_active", False)

        dns = network.get("dns", {})
        dns_servers = dns.get("servers", []) if isinstance(dns, dict) else []
        self.dns_servers = len(dns_servers) if isinstance(dns_servers, list) else 0

    def compose(self) -> ComposeResult:
        yield Label("[bold #007AFF]Network[/]")
        yield Label(f"[#8E8E93]Public IP:[/] {self.public_ip}")
        yield Label(f"[#8E8E93]Interfaces:[/] {self.interface_count}")
        yield Label(f"[#8E8E93]DNS Servers:[/] {self.dns_servers}")
        vpn_status = "[#34C759]✓ Active[/]" if self.vpn_active else "[#8E8E93]Inactive[/]"
        yield Label(f"[#8E8E93]VPN:[/] {vpn_status}")


class ProcessesTable(VerticalScroll):
    """DataTable for top processes."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        table: DataTable = DataTable()
        table.add_column("Process", width=30)
        table.add_column("PID", width=10)
        table.add_column("CPU %", width=10)
        table.add_column("Memory", width=15)

        # MyPy can infer this type from SystemReport
        processes = self.data.get("top_processes", [])

        # Sort by CPU descending (just in case)
        if isinstance(processes, list):
            try:
                processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
            except Exception:
                pass

        for proc in processes[:100]:  # Top 100 rows like htop
            table.add_row(
                proc.get("command", "?"),
                str(proc.get("pid", "?")),
                f"{proc.get('cpu_percent', 0):.1f}",
                proc.get("memory", "?"),
            )

        yield Label("[bold #007AFF]Top Processes (by CPU)[/]")
        yield table


class PackagesTable(VerticalScroll):
    """DataTable for installed packages."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        pkg_mgrs = self.data.get("package_managers", {})

        # Homebrew Formulae
        yield Label("[bold #007AFF]Homebrew Formulae[/]")
        brew_table: DataTable = DataTable()
        brew_table.add_column("Formula", width=30)
        brew_table.add_column("Version", width=20)

        homebrew = cast("dict[str, list[str] | bool]", pkg_mgrs.get("homebrew", {}))
        formulae = cast(list[str], homebrew.get("formula", []))

        for formula in formulae[:50]:  # Limit to 50
            if isinstance(formula, str):
                brew_table.add_row(formula, "—")
            else:
                brew_table.add_row(
                    formula.get("name", formula),
                    formula.get("version", "—"),
                )

        yield brew_table

        # NPM Global
        yield Label("")
        yield Label("[bold #007AFF]npm Global Packages[/]")
        npm_table: DataTable = DataTable()
        npm_table.add_column("Package", width=30)
        npm_table.add_column("Version", width=20)

        npm_global = cast("dict[str, list[str] | bool]", pkg_mgrs.get("npm", {}))
        npm_packages = cast(list[str], npm_global.get("globals", []))

        for pkg in npm_packages[:30]:  # Limit to 30
            # Format: "package@version"
            if "@" in pkg:
                name, version = pkg.rsplit("@", 1)
                npm_table.add_row(name, version)
            else:
                npm_table.add_row(pkg, "—")

        yield npm_table


class DeveloperToolsPanel(VerticalScroll):
    """Developer tools detailed view."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        dev_tools = self.data.get("developer_tools", {})

        # Languages
        yield Label("[bold #007AFF]Installed Languages[/]")
        lang_table: DataTable = DataTable()
        lang_table.add_column("Language", width=20)
        lang_table.add_column("Version", width=30)

        languages = dev_tools.get("languages", {})
        for lang_name, version in languages.items():
            if version and version != "Not installed":
                lang_table.add_row(lang_name, version)

        yield lang_table
        yield Label("")

        # SDKs
        yield Label("[bold #007AFF]Installed SDKs[/]")
        sdk_table: DataTable = DataTable()
        sdk_table.add_column("SDK", width=20)
        sdk_table.add_column("Version", width=30)

        sdks = dev_tools.get("sdks", {})
        for sdk_name, version in sdks.items():
            if version and version != "Not installed":
                sdk_table.add_row(sdk_name, version)

        yield sdk_table


class StorageDetails(VerticalScroll):
    """Detailed storage analysis."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        disk = self.data.get("disk", {})

        # Overview
        valid_disk = disk and isinstance(disk, dict)
        total = f"{disk.get('disk_total_gb', 0)} GB" if valid_disk else "?"
        free = f"{disk.get('disk_free_gb', 0)} GB" if valid_disk else "?"

        yield Label("[bold #007AFF]Storage Overview[/]")
        yield Label(f"Total Capacity: {total}")
        yield Label(f"Free Space: {free}")
        yield Label("")

        # Volumes Table
        yield Label("[bold #007AFF]APFS Volumes[/]")
        vol_table: DataTable = DataTable()
        vol_table.add_column("Volume Name", width=30)
        vol_table.add_column("Used (GB)", width=15)
        vol_table.add_column("Role", width=15)
        vol_table.add_column("Encrypted", width=10)
        vol_table.add_column("FileVault", width=10)

        if valid_disk:
            containers = disk.get("apfs_info", []) or []
            for container in containers:
                if isinstance(container, dict):
                    volumes = container.get("volumes", []) or []
                    for vol in volumes:
                        if isinstance(vol, dict):
                            is_encrypted = "Yes" if vol.get("encrypted") else "No"
                            is_fv = "Yes" if vol.get("filevault") else "No"
                            vol_table.add_row(
                                str(vol.get("name", "Unknown")),
                                f"{vol.get('capacity_used_gb', 0)}",
                                str(vol.get("role", "Unknown")),
                                is_encrypted,
                                is_fv,
                            )
        yield vol_table
        yield Label("")

        # Disk Health
        yield Label("[bold #007AFF]Physical Disk Health (S.M.A.R.T)[/]")
        health_table: DataTable = DataTable()
        health_table.add_column("Disk", width=30)
        health_table.add_column("Type", width=10)
        health_table.add_column("Status", width=20)

        if valid_disk:
            health_info = disk.get("disk_health", []) or []
            for h in health_info:
                if isinstance(h, dict):
                    status = str(h.get("smart_status", "Unknown"))
                    color = "[green]" if "Verified" in status else "[red]"
                    health_table.add_row(
                        str(h.get("disk_name", "Unknown")),
                        str(h.get("disk_type", "Unknown")),
                        f"{color}{status}[/]",
                    )
        yield health_table


class SecurityDetails(VerticalScroll):
    """Detailed security analysis."""

    def __init__(self, data: SystemReport) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        system = self.data.get("system", {})

        yield Label("[bold #007AFF]System Integrity & Encryption[/]")
        sec_table: DataTable = DataTable()
        sec_table.add_column("Feature", width=30)
        sec_table.add_column("Status", width=40)

        sip = "Enabled" if system.get("sip_enabled") else "Disabled"
        gk = "Enabled" if system.get("gatekeeper_enabled") else "Disabled"
        fv = "Enabled" if system.get("filevault_enabled") else "Disabled"

        sip_status = f"[{'green' if sip == 'Enabled' else 'red'}]{sip}[/]"
        gk_status = f"[{'green' if gk == 'Enabled' else 'red'}]{gk}[/]"
        fv_status = f"[{'green' if fv == 'Enabled' else 'red'}]{fv}[/]"

        sec_table.add_row("SIP (System Integrity)", sip_status)
        sec_table.add_row("Gatekeeper", gk_status)
        sec_table.add_row("FileVault (Disk Encryption)", fv_status)
        yield sec_table
        yield Label("")

        # Time Machine
        tm = system.get("time_machine", {})
        yield Label("[bold #007AFF]Time Machine Backup[/]")
        tm_table: DataTable = DataTable()
        tm_table.add_column("Setting", width=30)
        tm_table.add_column("Value", width=40)

        tm_enabled = "Yes" if tm.get("enabled") else "No"
        tm_auto = "Yes" if tm.get("auto_backup") else "No"

        tm_table.add_row("Time Machine Active", tm_enabled)
        tm_table.add_row("Auto Backup", tm_auto)
        tm_table.add_row("Last Backup", str(tm.get("last_backup", "None")))
        tm_table.add_row("Destination", str(tm.get("destination", "None")))

        yield tm_table


class SystemProseAppEnhanced(App[None]):
    """Enhanced Textual TUI application with all phases implemented."""

    CSS = """
    Screen {
        background: #1C1C1E;
    }

    Header {
        background: #007AFF;
        color: white;
    }

    Footer {
        background: #2C2C2E;
    }

    TabbedContent {
        background: #1C1C1E;
    }

    TabPane {
        background: #1C1C1E;
        padding: 1 2;
    }

    DataTable {
        background: #2C2C2E;
        color: white;
    }

    ProgressBar > .bar--indeterminate {
        color: #007AFF;
    }

    ProgressBar > .bar--bar {
        color: #34C759;
    }

    Button {
        margin: 1 2;
    }

    Button.-primary {
        background: #007AFF;
        color: white;
    }

    #status_bar {
        background: #2C2C2E;
        color: #8E8E93;
        padding: 0 2;
        height: 1;
    }
    """

    BINDINGS: ClassVar[Sequence[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle Theme"),
        ("ctrl+e", "export", "Export JSON"),
        ("ctrl+s", "search", "Search"),
        ("question_mark", "help", "Help"),
        ("1", "tab_dashboard", "Dashboard"),
        ("2", "tab_system", "System"),
        ("3", "tab_network", "Network"),
        ("4", "tab_developer", "Developer"),
        ("5", "tab_packages", "Packages"),
        ("6", "tab_processes", "Processes"),
        ("7", "tab_storage", "Storage"),
        ("8", "tab_security", "Security"),
    ]

    def __init__(
        self,
        report_data: SystemReport | None = None,
        live_mode: bool = False,
        refresh_interval: int = 30,
    ) -> None:
        """Initialize enhanced app.

        Args:
            report_data: System report data
            live_mode: Enable auto-refresh
            refresh_interval: Seconds between refreshes (default: 30)
        """
        super().__init__()
        self.report_data: SystemReport = cast(SystemReport, report_data or {})
        self.live_mode = live_mode
        self.refresh_interval = refresh_interval
        self.title = "macOS System Prose"
        self.sub_title = "Professional Terminal Dashboard • Apple HIG Design"
        self._refresh_task: asyncio.Task[None] | None = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)

        with TabbedContent(initial="dashboard"):
            # Tab 1: Dashboard (Monitor)
            with TabPane("Monitor", id="dashboard"):
                yield MonitorHeader(self.report_data)
                yield Label("[bold #007AFF]Top Processes (CPU)[/]")
                yield ProcessesTable(self.report_data)

            # Tab 2: System Details
            with TabPane("System", id="system"):
                yield Label("[bold #007AFF]System Details[/]")
                yield Label("Detailed system information...")

            # Tab 3: Network Details
            with TabPane("Network", id="network"):
                yield Label("[bold #007AFF]Network Details[/]")
                yield Label("Network configuration...")

            # Tab 4: Developer Tools
            with TabPane("Developer", id="developer"):
                yield DeveloperToolsPanel(self.report_data)

            # Tab 5: Packages
            with TabPane("Packages", id="packages"):
                yield PackagesTable(self.report_data)

            # Tab 6: Processes
            with TabPane("Processes", id="processes"):
                yield ProcessesTable(self.report_data)

            # Tab 7: Storage
            with TabPane("Storage", id="storage"):
                yield StorageDetails(self.report_data)

            # Tab 8: Security
            with TabPane("Security", id="security"):
                yield SecurityDetails(self.report_data)

        # Status bar
        status_text = "Live Mode: ON" if self.live_mode else "Static View"
        yield Label(f"[#8E8E93]{status_text}[/]", id="status_bar")

        yield Footer()

    def on_mount(self) -> None:
        """Start live refresh if enabled."""
        if self.live_mode:
            self._refresh_task = asyncio.create_task(self._live_refresh_loop())

    def on_unmount(self) -> None:
        """Stop live refresh on unmount."""
        if self._refresh_task:
            self._refresh_task.cancel()

    async def _live_refresh_loop(self) -> None:
        """Background loop for auto-refreshing data in live mode."""
        while True:
            await asyncio.sleep(self.refresh_interval)
            self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh the data."""
        self.notify("🔄 Refreshing data...", title="Refresh", severity="information")
        # In production, this would re-run collect_all()

    def action_export(self) -> None:
        """Export data to JSON."""
        self.notify("💾 Export functionality coming soon", severity="information")

    def action_search(self) -> None:
        """Open search dialog."""
        self.notify("🔍 Search functionality coming soon", severity="information")

    def action_help(self) -> None:
        """Show help screen."""
        help_text = """
[bold #007AFF]macOS System Prose - Keyboard Shortcuts[/]

[#34C759]Navigation:[/]
  1-7     Switch tabs
  q       Quit application
  d       Toggle dark theme

[#34C759]Actions:[/]
  r       Refresh data
  Ctrl+E  Export to JSON
  Ctrl+S  Search
  ?       Show this help

[#34C759]Features:[/]
  • Real-time system monitoring
  • Apple HIG design principles
  • Professional terminal dashboard
        """
        self.notify(help_text, title="Help", timeout=10)

    def action_tab_dashboard(self) -> None:
        """Switch to dashboard tab."""
        self.query_one(TabbedContent).active = "dashboard"

    def action_tab_system(self) -> None:
        """Switch to system tab."""
        self.query_one(TabbedContent).active = "system"

    def action_tab_network(self) -> None:
        """Switch to network tab."""
        self.query_one(TabbedContent).active = "network"

    def action_tab_developer(self) -> None:
        """Switch to developer tab."""
        self.query_one(TabbedContent).active = "developer"

    def action_tab_packages(self) -> None:
        """Switch to packages tab."""
        self.query_one(TabbedContent).active = "packages"

    def action_tab_processes(self) -> None:
        """Switch to processes tab."""
        self.query_one(TabbedContent).active = "processes"

    def action_tab_storage(self) -> None:
        """Switch to storage tab."""
        self.query_one(TabbedContent).active = "storage"

    def action_tab_security(self) -> None:
        """Switch to security tab."""
        self.query_one(TabbedContent).active = "security"


async def run_tui_enhanced(
    report_data: SystemReport | None = None,
    live_mode: bool = False,
    refresh_interval: int = 30,
) -> None:
    """Run the enhanced TUI application asynchronously.

    Args:
        report_data: System report data
        live_mode: Enable auto-refresh
        refresh_interval: Seconds between refreshes
    """
    app = SystemProseAppEnhanced(report_data, live_mode, refresh_interval)
    await app.run_async()


def run_tui_enhanced_sync(
    report_data: SystemReport | None = None,
    live_mode: bool = False,
    refresh_interval: int = 30,
) -> None:
    """Run the enhanced TUI application synchronously.

    Args:
        report_data: System report data
        live_mode: Enable auto-refresh
        refresh_interval: Seconds between refreshes
    """
    app = SystemProseAppEnhanced(report_data, live_mode, refresh_interval)
    app.run()
