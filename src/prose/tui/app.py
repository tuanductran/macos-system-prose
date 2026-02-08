"""Main Textual application for macOS System Prose TUI."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, TabbedContent, TabPane

from prose.schema import SystemReport


class SystemInfoCard(Static):
    """Widget displaying system information."""

    def __init__(self, data: SystemReport) -> None:
        """Initialize system info card with data."""
        super().__init__()
        self.data = data

    def render(self) -> str:
        """Render system information."""
        system = self.data.get("system", {})
        model = system.get("model_name", "Unknown")
        identifier = system.get("model_identifier", "Unknown")
        macos = system.get("marketing_name", "Unknown")
        arch = system.get("architecture", "Unknown")
        board_id = system.get("board_id", "Unknown")

        return f"""[bold cyan]System Information[/bold cyan]

[yellow]Model:[/yellow] {model}
[yellow]Identifier:[/yellow] {identifier}
[yellow]macOS:[/yellow] {macos}
[yellow]Architecture:[/yellow] {arch}
[yellow]Board ID:[/yellow] {board_id}
"""


class SecurityCard(Static):
    """Widget displaying security status."""

    def __init__(self, data: SystemReport) -> None:
        """Initialize security card with data."""
        super().__init__()
        self.data = data

    def render(self) -> str:
        """Render security status."""
        system = self.data.get("system", {})
        sip = system.get("sip_enabled", False)
        filevault = system.get("filevault_enabled", False)
        gatekeeper = system.get("gatekeeper_enabled", False)

        sip_badge = "[green]✓ Enabled[/green]" if sip else "[red]✗ Disabled[/red]"
        fv_badge = "[green]✓ Enabled[/green]" if filevault else "[red]✗ Disabled[/red]"
        gk_badge = "[green]✓ Enabled[/green]" if gatekeeper else "[red]✗ Disabled[/red]"

        return f"""[bold cyan]Security Status[/bold cyan]

[yellow]SIP:[/yellow]        {sip_badge}
[yellow]FileVault:[/yellow]  {fv_badge}
[yellow]Gatekeeper:[/yellow] {gk_badge}
"""


class HardwareCard(Static):
    """Widget displaying hardware information."""

    def __init__(self, data: SystemReport) -> None:
        """Initialize hardware card with data."""
        super().__init__()
        self.data = data

    def render(self) -> str:
        """Render hardware information."""
        hardware = self.data.get("hardware", {})
        cpu = hardware.get("cpu_model", "Unknown")
        cores = hardware.get("cpu_cores", 0)
        memory = hardware.get("memory_total", "Unknown")
        gpu = hardware.get("gpu_vendor", "Unknown")

        mem_pressure = hardware.get("memory_pressure", {})
        mem_level = mem_pressure.get("level", "Unknown")
        swap_used = mem_pressure.get("swap_used", "Unknown")

        mem_color = "green" if mem_level == "normal" else "yellow" if mem_level == "warn" else "red"

        return f"""[bold cyan]Hardware[/bold cyan]

[yellow]CPU:[/yellow] {cpu}
[yellow]Cores:[/yellow] {cores}
[yellow]Memory:[/yellow] {memory}
[yellow]GPU:[/yellow] {gpu}

[yellow]Memory Pressure:[/yellow] [{mem_color}]{mem_level}[/{mem_color}]
[yellow]Swap Used:[/yellow] {swap_used}
"""


class DeveloperCard(Static):
    """Widget displaying developer tools."""

    def __init__(self, data: SystemReport) -> None:
        """Initialize developer card with data."""
        super().__init__()
        self.data = data

    def render(self) -> str:
        """Render developer tools information."""
        dev = self.data.get("developer_tools", {})
        docker = dev.get("docker", {})
        git = dev.get("git", {})

        docker_status = docker.get("status", "not installed")
        docker_version = docker.get("version", "N/A")
        docker_containers = docker.get("containers_running", 0) + docker.get(
            "containers_stopped", 0
        )
        docker_images = docker.get("images", 0)

        git_user = git.get("user_name", "Not configured")
        git_email = git.get("user_email", "Not configured")

        docker_color = "green" if docker_status == "running" else "red"

        return f"""[bold cyan]Developer Tools[/bold cyan]

[yellow]Docker:[/yellow] [{docker_color}]{docker_status}[/{docker_color}] (v{docker_version})
[yellow]Containers:[/yellow] {docker_containers}
[yellow]Images:[/yellow] {docker_images}

[yellow]Git User:[/yellow] {git_user}
[yellow]Git Email:[/yellow] {git_email}
"""


class PackagesCard(Static):
    """Widget displaying package managers."""

    def __init__(self, data: SystemReport) -> None:
        """Initialize packages card with data."""
        super().__init__()
        self.data = data

    def render(self) -> str:
        """Render package managers information."""
        pkgs = self.data.get("package_managers", {})
        brew = pkgs.get("homebrew", {})
        npm_pkg = pkgs.get("npm", {})
        yarn_pkg = pkgs.get("yarn", {})

        brew_formulas = brew.get("formulas", 0) if brew.get("installed") else 0
        brew_casks = brew.get("casks", 0) if brew.get("installed") else 0
        npm_count = npm_pkg.get("packages", 0) if npm_pkg.get("installed") else 0
        yarn_count = yarn_pkg.get("packages", 0) if yarn_pkg.get("installed") else 0

        return f"""[bold cyan]Package Managers[/bold cyan]

[yellow]Homebrew:[/yellow]
  • Formulas: {brew_formulas}
  • Casks: {brew_casks}

[yellow]npm:[/yellow] {npm_count} packages
[yellow]Yarn:[/yellow] {yarn_count} packages
"""


class SystemProseApp(App[None]):
    """Textual TUI application for macOS System Prose."""

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
    }

    Footer {
        background: $panel;
    }

    .card {
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
        height: auto;
    }

    #top-row {
        height: auto;
    }

    #bottom-row {
        height: auto;
    }

    Button {
        margin: 1 2;
    }
    """

    BINDINGS: ClassVar[Sequence[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle Dark"),
    ]

    def __init__(self, report_data: SystemReport | None = None) -> None:
        """Initialize app with optional report data."""
        super().__init__()
        self.report_data: SystemReport = report_data or {}  # Type annotation added
        self.title = "macOS System Prose TUI"
        self.sub_title = "Professional Terminal Dashboard"

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)

        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                with Vertical(id="top-row"):
                    with Horizontal():
                        yield SystemInfoCard(self.report_data).add_class("card")
                        yield SecurityCard(self.report_data).add_class("card")
                    with Horizontal():
                        yield HardwareCard(self.report_data).add_class("card")
                        yield DeveloperCard(self.report_data).add_class("card")
                with Vertical(id="bottom-row"):
                    with Horizontal():
                        yield PackagesCard(self.report_data).add_class("card")
                        yield Button("Refresh Data", id="refresh_btn", variant="primary")

        yield Footer()

    def action_refresh(self) -> None:
        """Refresh the data."""
        self.notify("Refreshing data...", severity="information")
        # In future, we'll implement async refresh here

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "refresh_btn":
            self.action_refresh()


async def run_tui(report_data: SystemReport | None = None) -> None:
    """Run the TUI application."""
    app = SystemProseApp(report_data)
    await app.run_async()


def run_tui_sync(report_data: SystemReport | None = None) -> None:
    """Run the TUI application synchronously."""
    app = SystemProseApp(report_data)
    app.run()
