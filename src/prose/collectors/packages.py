from __future__ import annotations

import re
from typing import Union, cast

from prose.schema import BrewService, NotInstalled, PackageManagers, PackageVersionInfo
from prose.utils import get_json_output, log, run, verbose_log, which


def homebrew_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Homebrew...")
    if not which("brew"):
        return cast(NotInstalled, {"installed": False})
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["brew", "--version"]).splitlines()[0],
            "bin_path": which("brew") or "Unknown",
            "prefix": run(["brew", "--prefix"]),
            "formula": run(["brew", "list", "--formula"], timeout=30).splitlines(),
            "casks": run(["brew", "list", "--cask"], timeout=30).splitlines(),
        },
    )


def macports_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking MacPorts...")
    if not which("port"):
        return cast(NotInstalled, {"installed": False})
    lines = run(["port", "installed", "active"]).splitlines()
    prose_lines = [line.strip() for line in lines if line.strip()]
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["port", "version"]).lower().replace("version:", "").strip(),
            "bin_path": which("port") or "Unknown",
            "active_ports": prose_lines,
        },
    )


def pipx_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking pipx...")
    if not which("pipx"):
        return cast(NotInstalled, {"installed": False})
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["pipx", "--version"]),
            "bin_path": which("pipx") or "Unknown",
            "packages": [
                line for line in run(["pipx", "list"]).splitlines() if line.startswith("package")
            ],
        },
    )


def npm_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking npm globals...")
    if not which("npm"):
        return cast(NotInstalled, {"installed": False})
    globals_list = []
    data = get_json_output(["npm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, dict):
        dependencies = data.get("dependencies", {})
        if isinstance(dependencies, dict):
            for name, info in dependencies.items():
                if isinstance(info, dict):
                    version = info.get("version", "unknown")
                    globals_list.append(f"{name}@{version}")
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["npm", "--version"]),
            "bin_path": which("npm") or "Unknown",
            "globals": sorted(globals_list),
        },
    )


def yarn_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Yarn globals...")
    if not which("yarn"):
        return cast(NotInstalled, {"installed": False})
    globals_list = []
    output = run(["yarn", "global", "list", "--depth=0"]).splitlines()
    for line in output:
        if "info" in line and "@" in line:
            parts = line.split('"')
            if len(parts) >= 2:
                globals_list.append(parts[1])
        elif line.strip().startswith("- "):
            globals_list.append(line.strip().replace("- ", ""))
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["yarn", "--version"]),
            "bin_path": which("yarn") or "Unknown",
            "globals": sorted(globals_list),
        },
    )


def pnpm_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking PNPM globals...")
    if not which("pnpm"):
        return cast(NotInstalled, {"installed": False})
    globals_list = []
    data = get_json_output(["pnpm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, list):
        for project in data:
            if isinstance(project, dict):
                dependencies = project.get("dependencies", {})
                if isinstance(dependencies, dict):
                    for name, info in dependencies.items():
                        if isinstance(info, dict):
                            version = info.get("version", "unknown")
                            globals_list.append(f"{name}@{version}")
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["pnpm", "--version"]),
            "bin_path": which("pnpm") or "Unknown",
            "globals": sorted(list(set(globals_list))),
        },
    )


def bun_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Bun globals...")
    if not which("bun"):
        return cast(NotInstalled, {"installed": False})
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
    return cast(
        PackageVersionInfo,
        {
            "installed": True,
            "version": run(["bun", "--version"]),
            "bin_path": which("bun") or "Unknown",
            "globals": globals_list,
        },
    )


def collect_homebrew_services() -> list[BrewService]:
    """Collect Homebrew services status."""
    verbose_log("Checking Homebrew services...")
    services = []

    if not which("brew"):
        return services

    try:
        output = run(["brew", "services", "list"], timeout=15)
        lines = output.splitlines()

        # Skip header line
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                status = parts[1]
                user = parts[2] if len(parts) > 2 and parts[2] != "none" else None
                file_path = parts[3] if len(parts) > 3 else None

                services.append(
                    {
                        "name": name,
                        "status": status,
                        "user": user,
                        "file": file_path,
                    }
                )
    except Exception:
        pass

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
