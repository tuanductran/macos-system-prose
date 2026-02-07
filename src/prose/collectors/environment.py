from __future__ import annotations

import os
import re
from pathlib import Path

from prose.schema import (
    ApplicationsInfo,
    BatteryInfo,
    CronInfo,
    DiagnosticsInfo,
    EnvironmentInfo,
    KernelExtensionsInfo,
    LaunchItems,
    ProcessInfo,
    SecurityInfo,
)
from prose.utils import get_app_version, log, run, verbose_log


def collect_processes() -> list[ProcessInfo]:
    log("Collecting process information...")
    try:
        ps = run(["ps", "-A", "-o", "pid,%cpu,%mem,comm", "-r"])
        processes: list[ProcessInfo] = []
        for line in ps.splitlines()[1:16]:
            parts = line.split()
            if len(parts) >= 4:
                processes.append(
                    {
                        "pid": int(parts[0]),
                        "cpu_percent": float(parts[1]),
                        "mem_percent": float(parts[2]),
                        "command": " ".join(parts[3:]),
                    }
                )
        return processes
    except Exception:
        return []


def collect_launch_items() -> LaunchItems:
    log("Collecting startup items...")

    def _scan_dir(d):
        p = Path(d).expanduser()
        return [str(f) for f in p.glob("*.plist")] if p.exists() else []

    return {
        "user_agents": _scan_dir("~/Library/LaunchAgents"),
        "system_agents": _scan_dir("/Library/LaunchAgents"),
        "system_daemons": _scan_dir("/Library/LaunchDaemons"),
    }


def collect_login_items() -> list[str]:
    script = 'tell application "System Events" to get name of every login item'
    try:
        out = run(["osascript", "-e", script], timeout=10)
        return [item for item in out.split(", ") if item] if out else []
    except Exception:
        return []


def collect_environment_info() -> EnvironmentInfo:
    log("Collecting environment info...")
    path_entries = os.environ.get("PATH", "").split(":")
    seen = set()
    dupes = []
    for x in path_entries:
        if x in seen:
            dupes.append(x)
        else:
            seen.add(x)

    ports = []
    try:
        netstat = run(["netstat", "-anp", "tcp"])
        for line in netstat.splitlines():
            if "LISTEN" in line:
                parts = line.split()
                port = parts[3] if len(parts) > 3 else "Unknown"
                if port not in ports:
                    ports.append(port)
    except Exception:
        pass

    return {
        "shell": os.environ.get("SHELL"),
        "python_executable": run(["which", "python3"]),
        "python_version": run(["python3", "--version"]),
        "path_entries": path_entries,
        "path_duplicates": list(set(dupes)),
        "listening_ports": sorted(ports),
    }


def collect_battery_info() -> BatteryInfo:
    log("Collecting battery information...")
    out = run(["pmset", "-g", "batt"])
    present = "InternalBattery" in out
    cycle_count = None
    condition = None
    if present:
        try:
            data = run(["system_profiler", "SPPowerDataType"])
            for line in data.splitlines():
                line = line.strip()
                if "Cycle Count:" in line:
                    cycle_count = int(line.split(":")[1].strip())
                elif "Condition:" in line:
                    condition = line.split(":")[1].strip()
        except Exception:
            pass
    return {
        "present": present,
        "percentage": out.split("\t")[1].split(";")[0] if present and "\t" in out else None,
        "cycle_count": cycle_count,
        "condition": condition,
        "power_source": out.split("'")[1] if "'" in out else "Unknown",
    }


def collect_cron_jobs() -> CronInfo:
    log("Collecting cron jobs...")
    try:
        # Suppress errors as it's common to have no crontab
        out = run(["crontab", "-l"], log_errors=False)
        return {"user_crontab": out.splitlines()} if out else {"user_crontab": []}
    except Exception:
        return {"user_crontab": []}


def collect_diagnostics() -> DiagnosticsInfo:
    log("Collecting diagnostic logs...")
    diag_dir = Path("~/Library/Logs/DiagnosticReports").expanduser()
    crashes = []
    if diag_dir.exists():
        files = sorted(diag_dir.glob("*.ips"), key=os.path.getmtime, reverse=True)
        crashes = [f.name for f in files[:5]]
    return {"recent_crashes": crashes}


def collect_kexts() -> KernelExtensionsInfo:
    log("Checking kernel extensions...")
    kexts = []
    try:
        out = run(["kextstat", "-l"])
        for line in out.splitlines():
            if "com.apple" not in line and not line.startswith("Index"):
                match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+)\s\(([^)]+)\)", line)
                if match:
                    kexts.append(f"{match.group(1)} ({match.group(2)})")
    except Exception:
        pass
    return {"third_party_kexts": kexts}


def collect_all_applications() -> list[str]:
    """Collect all installed applications from /Applications and ~/Applications."""
    all_apps = []

    # Scan /Applications
    app_dir = Path("/Applications")
    if app_dir.exists():
        for app in app_dir.glob("*.app"):
            try:
                app_name = app.name.replace(".app", "")
                ver = get_app_version(app)
                if ver:
                    all_apps.append(f"{app_name}@{ver}")
                else:
                    all_apps.append(app_name)
            except Exception:
                continue

    # Scan ~/Applications
    user_app_dir = Path.home() / "Applications"
    if user_app_dir.exists():
        for app in user_app_dir.glob("*.app"):
            try:
                app_name = app.name.replace(".app", "")
                ver = get_app_version(app)
                if ver:
                    all_apps.append(f"{app_name}@{ver}")
                else:
                    all_apps.append(app_name)
            except Exception:
                continue

    return sorted(list(set(all_apps)))


def collect_electron_apps() -> ApplicationsInfo:
    log("Scanning for Electron apps...")
    electron_apps = []
    app_dir = Path("/Applications")
    if app_dir.exists():
        for app in app_dir.glob("*.app"):
            try:
                if (app / "Contents/Frameworks/Electron Framework.framework").exists():
                    ver = get_app_version(app)
                    electron_apps.append(f"{app.name}@{ver}" if ver else app.name)
            except Exception:
                continue

    verbose_log("Collecting all installed applications...")
    all_apps = collect_all_applications()

    return {
        "electron_apps": sorted(electron_apps),
        "all_apps": all_apps,
    }


def collect_security_tools() -> SecurityInfo:
    """Detect security and privacy tools installed on the system."""
    log("Detecting security tools...")
    security_tools = []
    antivirus = []

    # Security/Privacy tools
    security_apps = {
        "Little Snitch": "/Applications/Little Snitch.app",
        "Lulu": "/Applications/LuLu.app",
        "BlockBlock": "/Applications/BlockBlock Helper.app",
        "OverSight": "/Applications/OverSight.app",
        "ReiKey": "/Applications/ReiKey.app",
        "KnockKnock": "/Applications/KnockKnock.app",
        "RansomWhere": "/Applications/RansomWhere.app",
        "NetiquetteApp": "/Applications/Netiquette.app",
    }

    # Antivirus software
    antivirus_apps = {
        "Malwarebytes": "/Applications/Malwarebytes.app",
        "Avast": "/Applications/Avast.app",
        "Norton": "/Applications/Norton Security.app",
        "McAfee": "/Applications/McAfee/McAfee Security.app",
        "Bitdefender": "/Applications/Bitdefender Antivirus.app",
        "Kaspersky": "/Applications/Kaspersky Internet Security.app",
        "Sophos": "/Applications/Sophos/Sophos Home.app",
        "ESET": "/Applications/ESET Cybersecurity.app",
    }

    # Check security tools
    for tool_name, tool_path in security_apps.items():
        if Path(tool_path).exists():
            ver = get_app_version(Path(tool_path))
            if ver:
                security_tools.append(f"{tool_name}@{ver}")
            else:
                security_tools.append(tool_name)

    # Check antivirus
    for av_name, av_path in antivirus_apps.items():
        if Path(av_path).exists():
            ver = get_app_version(Path(av_path))
            if ver:
                antivirus.append(f"{av_name}@{ver}")
            else:
                antivirus.append(av_name)

    return {
        "security_tools": sorted(security_tools),
        "antivirus": sorted(antivirus),
    }
