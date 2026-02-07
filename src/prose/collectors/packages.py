from __future__ import annotations

import re
from typing import Union

from prose.schema import NotInstalled, PackageManagers, PackageVersionInfo
from prose.utils import get_json_output, log, run, which


def homebrew_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Homebrew...")
    if not which("brew"):
        return {"installed": False}
    return {
        "installed": True,
        "version": run(["brew", "--version"]).splitlines()[0],
        "bin_path": which("brew") or "Unknown",
        "prefix": run(["brew", "--prefix"]),
        "formula": run(["brew", "list", "--formula"], timeout=30).splitlines(),
        "casks": run(["brew", "list", "--cask"], timeout=30).splitlines(),
    }


def macports_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking MacPorts...")
    if not which("port"):
        return {"installed": False}
    lines = run(["port", "installed", "active"]).splitlines()
    prose_lines = [line.strip() for line in lines if line.strip()]
    return {
        "installed": True,
        "version": run(["port", "version"]).lower().replace("version:", "").strip(),
        "bin_path": which("port") or "Unknown",
        "active_ports": prose_lines,
    }


def pipx_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking pipx...")
    if not which("pipx"):
        return {"installed": False}
    return {
        "installed": True,
        "version": run(["pipx", "--version"]),
        "bin_path": which("pipx") or "Unknown",
        "packages": [
            line for line in run(["pipx", "list"]).splitlines() if line.startswith("package")
        ],
    }


def npm_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking npm globals...")
    if not which("npm"):
        return {"installed": False}
    globals_list = []
    data = get_json_output(["npm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, dict):
        dependencies = data.get("dependencies", {})
        for name, info in dependencies.items():
            version = info.get("version", "unknown")
            globals_list.append(f"{name}@{version}")
    return {
        "installed": True,
        "version": run(["npm", "--version"]),
        "bin_path": which("npm") or "Unknown",
        "globals": sorted(globals_list),
    }


def yarn_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Yarn globals...")
    if not which("yarn"):
        return {"installed": False}
    globals_list = []
    output = run(["yarn", "global", "list", "--depth=0"]).splitlines()
    for line in output:
        if "info" in line and "@" in line:
            parts = line.split('"')
            if len(parts) >= 2:
                globals_list.append(parts[1])
        elif line.strip().startswith("- "):
            globals_list.append(line.strip().replace("- ", ""))
    return {
        "installed": True,
        "version": run(["yarn", "--version"]),
        "bin_path": which("yarn") or "Unknown",
        "globals": sorted(globals_list),
    }


def pnpm_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking PNPM globals...")
    if not which("pnpm"):
        return {"installed": False}
    globals_list = []
    data = get_json_output(["pnpm", "list", "-g", "--depth=0", "--json"])
    if data and isinstance(data, list):
        for project in data:
            dependencies = project.get("dependencies", {})
            for name, info in dependencies.items():
                version = info.get("version", "unknown")
                globals_list.append(f"{name}@{version}")
    return {
        "installed": True,
        "version": run(["pnpm", "--version"]),
        "bin_path": which("pnpm") or "Unknown",
        "globals": sorted(list(set(globals_list))),
    }


def bun_global_info() -> Union[PackageVersionInfo, NotInstalled]:
    log("Checking Bun globals...")
    if not which("bun"):
        return {"installed": False}
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
    return {
        "installed": True,
        "version": run(["bun", "--version"]),
        "bin_path": which("bun") or "Unknown",
        "globals": globals_list,
    }


def collect_package_managers() -> PackageManagers:
    return {
        "homebrew": homebrew_info(),
        "macports": macports_info(),
        "pipx": pipx_info(),
        "npm": npm_global_info(),
        "yarn": yarn_global_info(),
        "pnpm": pnpm_global_info(),
        "bun": bun_global_info(),
    }
