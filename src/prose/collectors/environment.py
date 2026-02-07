from __future__ import annotations

import os
import re
from pathlib import Path

from prose.schema import (
    ApplicationsInfo,
    BatteryInfo,
    CloudInfo,
    CloudSyncInfo,
    CodeSigningInfo,
    CronInfo,
    DiagnosticsInfo,
    EnvironmentInfo,
    KernelExtensionsInfo,
    LaunchdService,
    LaunchItems,
    ProcessInfo,
    SecurityInfo,
    SystemExtension,
    TCCPermission,
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


def collect_launchd_services() -> list[LaunchdService]:
    """Collect launchd services status for user and system domains."""
    verbose_log("Collecting launchd services...")
    services = []

    try:
        # Get user domain services
        output = run(["launchctl", "list"], timeout=15)
        for line in output.splitlines()[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 3:
                pid_str = parts[0]
                exit_code_str = parts[1]
                label = parts[2]

                # Parse PID (can be "-" for not running)
                pid = int(pid_str) if pid_str != "-" else None

                # Parse exit code (can be "-" or number)
                exit_code = None
                if exit_code_str != "-":
                    try:
                        exit_code = int(exit_code_str)
                    except ValueError:
                        pass

                # Determine status
                if pid is not None:
                    status = "running"
                elif exit_code == 0:
                    status = "stopped"
                else:
                    status = "error"

                services.append(
                    {
                        "label": label,
                        "pid": pid,
                        "status": status,
                        "last_exit_code": exit_code,
                    }
                )

        # Limit to top 50 services to avoid huge output
        services = services[:50]
    except Exception:
        pass

    return services


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
        "python_executable": "/usr/bin/python3",  # System Python, not venv
        "python_version": run(["/usr/bin/python3", "--version"]),
        "path_entries": path_entries,
        "path_duplicates": list(set(dupes)),
        "listening_ports": sorted(ports),
        "launchd_services": collect_launchd_services(),
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


def collect_system_extensions() -> list[SystemExtension]:
    """Collect macOS 10.15+ system extensions."""
    verbose_log("Checking system extensions...")
    extensions = []

    try:
        output = run(["systemextensionsctl", "list"], timeout=10, log_errors=False)
        # Parse output which has format like:
        # enabled	active	teamID	bundleID (version)	name	[state]
        for line in output.splitlines():
            if line.strip() and not line.startswith("---") and not line.startswith("enabled"):
                parts = line.split()
                if len(parts) >= 3:
                    # Try to extract bundle ID and version
                    bundle_info = " ".join(parts[2:])
                    match = re.search(r"([A-Z0-9]+)\s+([^\s]+)\s+\(([^)]+)\)", bundle_info)
                    if match:
                        extensions.append(
                            {
                                "identifier": match.group(2),
                                "version": match.group(3),
                                "state": parts[0] if len(parts) > 0 else "unknown",
                                "team_id": match.group(1),
                            }
                        )
    except Exception:
        pass

    return extensions


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
    return {
        "third_party_kexts": kexts,
        "system_extensions": collect_system_extensions(),
    }


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
        "tcc_permissions": collect_tcc_permissions(),
        "code_signing_sample": collect_code_signing_sample(),
    }


def collect_tcc_permissions() -> list[TCCPermission]:
    """Collect TCC (Transparency, Consent, Control) privacy permissions."""
    verbose_log("Checking TCC privacy permissions...")
    permissions: list[TCCPermission] = []

    # Note: Reading TCC database requires Full Disk Access permission
    # We'll try common services via tccutil if available
    try:
        # Alternative: Check if we can read the TCC database (requires FDA)
        tcc_db = Path.home() / "Library/Application Support/com.apple.TCC/TCC.db"
        if tcc_db.exists():
            verbose_log("TCC database found but requires Full Disk Access to read")
            # We can't reliably read this without FDA, so skip
        else:
            verbose_log("TCC database not accessible")
    except Exception:
        pass

    # Return empty list as we can't reliably get this without FDA
    # Users can enable this manually if needed
    return permissions


def collect_code_signing_sample() -> list[CodeSigningInfo]:
    """Sample code signing verification for installed apps (first 10 apps)."""
    verbose_log("Sampling code signing verification...")
    signing_info: list[CodeSigningInfo] = []

    try:
        app_dir = Path("/Applications")
        if app_dir.exists():
            apps = list(app_dir.glob("*.app"))[:10]  # Sample first 10 apps

            for app in apps:
                try:
                    output = run(["codesign", "-dvv", str(app)], timeout=5, log_errors=False)

                    identifier = ""
                    authority = ""
                    team_id = None
                    valid = False

                    for line in output.splitlines():
                        if "Identifier=" in line:
                            identifier = line.split("=", 1)[1]
                        elif "Authority=" in line:
                            authority = line.split("=", 1)[1]
                        elif "TeamIdentifier=" in line:
                            team_id = line.split("=", 1)[1]

                    # Check if signature is valid
                    verify_output = run(
                        ["codesign", "--verify", "--verbose", str(app)],
                        timeout=5,
                        log_errors=False,
                    )
                    valid = "valid on disk" in verify_output.lower()

                    signing_info.append(
                        {
                            "app_name": app.name.replace(".app", ""),
                            "identifier": identifier,
                            "authority": authority,
                            "valid": valid,
                            "team_id": team_id,
                        }
                    )
                except Exception:
                    continue
    except Exception:
        pass

    return signing_info


def collect_cloud_sync() -> CloudInfo:
    """Collect iCloud and cloud sync status."""
    verbose_log("Checking cloud sync status...")

    sync_info: CloudSyncInfo = {
        "icloud_enabled": False,
        "icloud_status": "Unknown",
        "drive_enabled": False,
        "storage_used": None,
    }

    try:
        # Check if iCloud Drive is enabled
        icloud_dir = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"
        if icloud_dir.exists():
            sync_info["icloud_enabled"] = True
            sync_info["drive_enabled"] = True

        # Try to get iCloud status via brctl (requires macOS 10.15+)
        brctl_output = run(["brctl", "status"], timeout=5, log_errors=False)
        if brctl_output:
            if "logged in" in brctl_output.lower():
                sync_info["icloud_status"] = "Active"
            elif "not logged in" in brctl_output.lower():
                sync_info["icloud_status"] = "Not logged in"
            else:
                sync_info["icloud_status"] = "Unknown"

            # Try to extract storage info
            for line in brctl_output.splitlines():
                if "storage" in line.lower() or "used" in line.lower():
                    parts = line.split()
                    if len(parts) > 1:
                        sync_info["storage_used"] = " ".join(parts[1:])
                        break
    except Exception:
        pass

    return {"sync_status": sync_info}
