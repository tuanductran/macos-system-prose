from __future__ import annotations

import re

from prose.schema import BrewService, NotInstalled, PackageManagers, PackageVersionInfo
from prose.utils import Timeouts, get_json_output, log, run, verbose_log, which


def homebrew_info() -> PackageVersionInfo | NotInstalled:
    """Get Homebrew package manager information."""
    log("Checking Homebrew...")
    if not which("brew"):
        return NotInstalled(installed=False)
    return PackageVersionInfo(
        installed=True,
        version=run(["brew", "--version"]).splitlines()[0],
        bin_path=which("brew") or "Unknown",
        prefix=run(["brew", "--prefix"]),
        formula=run(["brew", "list", "--formula"], timeout=Timeouts.SLOW).splitlines(),
        casks=run(["brew", "list", "--cask"], timeout=Timeouts.SLOW).splitlines(),
        globals=None,
        active_ports=None,
        packages=None,
    )


def macports_info() -> PackageVersionInfo | NotInstalled:
    """Get MacPorts package manager information."""
    log("Checking MacPorts...")
    if not which("port"):
        return NotInstalled(installed=False)
    lines = run(["port", "installed", "active"]).splitlines()
    prose_lines = [line.strip() for line in lines if line.strip()]
    return PackageVersionInfo(
        installed=True,
        version=run(["port", "version"]).lower().replace("version:", "").strip(),
        bin_path=which("port") or "Unknown",
        active_ports=prose_lines,
        globals=None,
        prefix=None,
        formula=None,
        casks=None,
        packages=None,
    )


def pipx_info() -> PackageVersionInfo | NotInstalled:
    """Get pipx package manager information."""
    log("Checking pipx...")
    if not which("pipx"):
        return NotInstalled(installed=False)
    return PackageVersionInfo(
        installed=True,
        version=run(["pipx", "--version"]),
        bin_path=which("pipx") or "Unknown",
        packages=[
            line for line in run(["pipx", "list"]).splitlines() if line.startswith("package")
        ],
        globals=None,
        prefix=None,
        formula=None,
        casks=None,
        active_ports=None,
    )


def npm_global_info() -> PackageVersionInfo | NotInstalled:
    """Get npm package manager and global packages information."""
    log("Checking npm globals...")
    if not which("npm"):
        return NotInstalled(installed=False)
    globals_list = []
    data = get_json_output(["npm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, dict):
        dependencies = data.get("dependencies", {})
        if isinstance(dependencies, dict):
            for name, info in dependencies.items():
                if isinstance(info, dict):
                    version = info.get("version", "Unknown")
                    globals_list.append(f"{name}@{version}")
    return PackageVersionInfo(
        installed=True,
        version=run(["npm", "--version"]),
        bin_path=which("npm") or "Unknown",
        globals=sorted(globals_list),
        prefix=None,
        formula=None,
        casks=None,
        active_ports=None,
        packages=None,
    )


def yarn_global_info() -> PackageVersionInfo | NotInstalled:
    """Get Yarn package manager and global packages information."""
    log("Checking Yarn globals...")
    if not which("yarn"):
        return NotInstalled(installed=False)
    version = run(["yarn", "--version"])
    globals_list = []
    # Yarn v2+ (Berry) removed `yarn global` command
    major_version = int(version.split(".")[0]) if version and version[0].isdigit() else 1
    if major_version < 2:
        output = run(["yarn", "global", "list", "--depth=0"]).splitlines()
        for line in output:
            if "info" in line and "@" in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    globals_list.append(parts[1])
            elif line.strip().startswith("- "):
                globals_list.append(line.strip().replace("- ", ""))
    return PackageVersionInfo(
        installed=True,
        version=version,
        bin_path=which("yarn") or "Unknown",
        globals=sorted(globals_list),
        prefix=None,
        formula=None,
        casks=None,
        active_ports=None,
        packages=None,
    )


def pnpm_global_info() -> PackageVersionInfo | NotInstalled:
    """Get PNPM package manager and global packages information."""
    log("Checking PNPM globals...")
    if not which("pnpm"):
        return NotInstalled(installed=False)
    globals_list = []
    data = get_json_output(["pnpm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, list):
        for project in data:
            if isinstance(project, dict):
                dependencies = project.get("dependencies", {})
                if isinstance(dependencies, dict):
                    for name, info in dependencies.items():
                        if isinstance(info, dict):
                            version = info.get("version", "Unknown")
                            globals_list.append(f"{name}@{version}")
    return PackageVersionInfo(
        installed=True,
        version=run(["pnpm", "--version"]),
        bin_path=which("pnpm") or "Unknown",
        globals=sorted(set(globals_list)),
        prefix=None,
        formula=None,
        casks=None,
        active_ports=None,
        packages=None,
    )


def bun_global_info() -> PackageVersionInfo | NotInstalled:
    """Get Bun package manager and global packages information."""
    log("Checking Bun globals...")
    if not which("bun"):
        return NotInstalled(installed=False)
    globals_list = []
    # Suppress errors as bun might be installed but not fully configured
    output = run(["bun", "pm", "ls", "-g"], log_errors=False).splitlines()
    for line in output:
        if "no binaries found" in line:
            continue
        parts = line.split()
        if parts:
            candidate = parts[-1]
            if "@" in candidate:
                clean_cand = re.sub(r"[^\w@\./-]", "", candidate)
                if clean_cand:
                    globals_list.append(clean_cand)
    return PackageVersionInfo(
        installed=True,
        version=run(["bun", "--version"]),
        bin_path=which("bun") or "Unknown",
        globals=sorted(set(globals_list)),
        prefix=None,
        formula=None,
        casks=None,
        active_ports=None,
        packages=None,
    )


def collect_homebrew_services() -> list[BrewService]:
    """Collect Homebrew services status."""
    verbose_log("Checking Homebrew services...")
    services: list[BrewService] = []

    if not which("brew"):
        return services

    try:
        output = run(["brew", "services", "list"], timeout=Timeouts.STANDARD)
        lines = output.splitlines()

        # Skip header line
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                status = parts[1]
                user = parts[2] if len(parts) > 2 and parts[2] != "none" else None
                file_path = parts[3] if len(parts) > 3 else None

                service: BrewService = {
                    "name": name,
                    "status": status,
                    "user": user,
                    "file": file_path,
                }
                services.append(service)
    except (OSError, ValueError, IndexError) as e:
        verbose_log(f"Failed to collect Homebrew services: {e}")

    return services


def collect_package_managers() -> PackageManagers:
    return {
        "homebrew": homebrew_info(),
        "macports": macports_info(),
        "pipx": pipx_info(),
        "npm": npm_global_info(),
        "yarn": yarn_global_info(),
        "pnpm": pnpm_global_info(),
        "bun": bun_global_info(),
        "homebrew_services": collect_homebrew_services(),
    }
