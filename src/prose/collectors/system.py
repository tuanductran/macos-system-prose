from __future__ import annotations

import os
import platform
import re

from prose.schema import (
    DiskHealthInfo,
    DiskInfo,
    DisplayInfo,
    HardwareInfo,
    MemoryPressure,
    SystemInfo,
    TimeMachineInfo,
)
from prose.utils import get_json_output, log, run, verbose_log


def _get_uptime_seconds() -> int:
    """Get system uptime in seconds."""
    try:
        import time

        boot_time_output = run(["sysctl", "-n", "kern.boottime"]).strip()
        # Parse boot time string: { sec = 1770357120, usec = 0 }
        match = re.search(r"sec = (\d+)", boot_time_output)
        if match:
            boot_timestamp = int(match.group(1))
            return int(time.time()) - boot_timestamp
    except Exception:
        pass
    return 0


def collect_time_machine_info() -> TimeMachineInfo:
    """Collect Time Machine backup status and configuration."""
    try:
        # Check if Time Machine is enabled
        status_output = run(["tmutil", "status"], log_errors=False)
        enabled = "Running" in status_output or "BackupPhase" in status_output

        # Get last backup date
        last_backup = None
        try:
            latest = run(["tmutil", "latestbackup"], log_errors=False).strip()
            if latest and latest != "No" and not latest.startswith("Unable"):
                last_backup = latest
        except Exception:
            pass

        # Get destination info
        destination = None
        try:
            dest_info = run(["tmutil", "destinationinfo"], log_errors=False)
            if dest_info and "Name" in dest_info:
                for line in dest_info.splitlines():
                    if line.strip().startswith("Name"):
                        destination = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        # Check if auto backup is enabled
        auto_backup = False
        try:
            prefs = run(
                [
                    "defaults",
                    "read",
                    "/Library/Preferences/com.apple.TimeMachine",
                    "AutoBackup",
                ],
                log_errors=False,
            )
            auto_backup = prefs.strip() == "1"
        except Exception:
            pass

        return {
            "enabled": enabled,
            "last_backup": last_backup,
            "destination": destination,
            "auto_backup": auto_backup,
        }
    except Exception:
        return {
            "enabled": False,
            "last_backup": None,
            "destination": None,
            "auto_backup": False,
        }


def collect_system_info() -> SystemInfo:
    log("Collecting system information...")

    # Use new macOS version detector
    from prose.macos_versions import get_macos_version_info

    version_info = get_macos_version_info()
    version = version_info["version"]
    macos_name = version_info["marketing_name"]

    hw_data = get_json_output(["system_profiler", "SPHardwareDataType", "-json"])
    model_name, model_id = "Unknown Mac", "Unknown"

    if hw_data and isinstance(hw_data, dict) and "SPHardwareDataType" in hw_data:
        sp_hard = hw_data["SPHardwareDataType"]
        if isinstance(sp_hard, list) and len(sp_hard) > 0:
            info = sp_hard[0]
            if isinstance(info, dict):
                model_name = str(info.get("machine_name", "Mac"))
                model_id = str(info.get("machine_model", "Unknown"))

    # Enrich with SMBIOS data
    from prose.datasets.smbios import get_smbios_data

    smbios_data = get_smbios_data(model_id)
    marketing_name = smbios_data.get("marketing_name") if smbios_data else None
    board_id = smbios_data.get("board_id") if smbios_data else None
    cpu_generation = smbios_data.get("cpu_generation") if smbios_data else None
    max_os_supported = smbios_data.get("max_os_supported") if smbios_data else None

    if smbios_data:
        verbose_log(
            f"SMBIOS: {marketing_name} (Board: {board_id}, "
            f"CPU: {cpu_generation}, Max OS: {max_os_supported})"
        )

    return {
        "os": "macOS",
        "macos_version": version,
        "macos_name": macos_name,
        "model_name": model_name,
        "model_identifier": model_id,
        "marketing_name": marketing_name,
        "board_id": board_id,
        "cpu_generation": cpu_generation,
        "max_os_supported": max_os_supported,
        "kernel": run(["uname", "-r"]),
        "architecture": platform.machine(),
        "uptime": run(["uptime"]).split("load")[0].strip(),
        "uptime_seconds": _get_uptime_seconds(),
        "boot_time": run(["sysctl", "-n", "kern.boottime"]).strip(),
        "load_average": run(["sysctl", "-n", "vm.loadavg"]).strip(),
        "sip_enabled": "enabled" in run(["csrutil", "status"]).lower(),
        "gatekeeper_enabled": "enabled" in run(["spctl", "--status"]).lower(),
        "filevault_enabled": "on" in run(["fdesetup", "status"]).lower(),
        "time_machine": collect_time_machine_info(),
    }


def collect_display_info() -> list[DisplayInfo]:
    """Collect display information including resolution, refresh rate, and EDID data."""
    import plistlib
    from typing import Optional

    from prose.utils import parse_edid

    displays: list[DisplayInfo] = []

    # First, try to get EDID data from IORegistry
    edid_data_map: dict[str, dict[str, Optional[str]]] = {}
    try:
        output = run(
            ["ioreg", "-l", "-w0", "-r", "-a", "-c", "IODisplayConnect"],
            timeout=10,
            log_errors=False,
        )
        if output:
            plist = plistlib.loads(output.encode("utf-8"))
            if not isinstance(plist, list):
                plist = [plist]

            def extract_edid(node: dict) -> None:
                if not isinstance(node, dict):
                    return

                # Check for EDID data
                if "IODisplayEDID" in node:
                    edid_bytes = node["IODisplayEDID"]
                    if isinstance(edid_bytes, bytes):
                        edid_parsed = parse_edid(edid_bytes)

                        # Get connector type if available
                        connector = None
                        io_display_location = node.get("IODisplayLocation")
                        if io_display_location:
                            loc_str = str(io_display_location)
                            if "LVDS" in loc_str:
                                connector = "LVDS (Internal)"
                            elif "HDMI" in loc_str:
                                connector = "HDMI"
                            elif "DisplayPort" in loc_str or "DP" in loc_str:
                                connector = "DisplayPort"

                        # Use display name as key
                        display_name = node.get("IODisplayPrefsKey", "Unknown")
                        edid_data_map[str(display_name)] = {
                            **edid_parsed,
                            "connector_type": connector,
                        }

                # Recurse into children
                if "IORegistryEntryChildren" in node:
                    for child in node["IORegistryEntryChildren"]:
                        extract_edid(child)

            # plist is a list, iterate through all root nodes
            for node in plist:
                extract_edid(node)
            if edid_data_map:
                verbose_log(f"Found EDID data for {len(edid_data_map)} displays")
    except Exception as e:
        verbose_log(f"Error collecting EDID data: {e}")

    # Now collect display info from system_profiler
    try:
        data = get_json_output(["system_profiler", "SPDisplaysDataType", "-json"])
        if data and isinstance(data, dict) and "SPDisplaysDataType" in data:
            sp_displays = data["SPDisplaysDataType"]
            if isinstance(sp_displays, list):
                for card in sp_displays:
                    if isinstance(card, dict):
                        ndrvs = card.get("spdisplays_ndrvs", [])
                        if isinstance(ndrvs, list):
                            for display in ndrvs:
                                if isinstance(display, dict):
                                    resolution = str(
                                        display.get("_spdisplays_resolution", "Unknown")
                                    )

                                    # Get refresh rate (may be missing for internal displays)
                                    refresh = display.get("spdisplays_refresh_rate")
                                    if refresh:
                                        refresh_str = str(refresh)
                                    else:
                                        # Internal displays often don't report refresh rate
                                        # Check if it's an internal display
                                        conn_type = display.get("spdisplays_connection_type", "")
                                        if "internal" in str(conn_type).lower():
                                            refresh_str = "60 Hz"  # Default for internal displays
                                        else:
                                            refresh_str = "Unknown"

                                    depth = str(display.get("spdisplays_depth", "Unknown"))

                                    # Try to match with EDID data
                                    edid_info: dict[str, Optional[str]] = {
                                        "edid_manufacturer": None,
                                        "edid_product_code": None,
                                        "edid_serial": None,
                                        "connector_type": None,
                                    }

                                    # Try to find matching EDID data
                                    display_name = display.get("_name", "")
                                    for key, data_dict in edid_data_map.items():
                                        if display_name in key or key in display_name:
                                            mfg = data_dict.get("manufacturer_id")
                                            edid_info["edid_manufacturer"] = mfg
                                            prod = data_dict.get("product_code")
                                            edid_info["edid_product_code"] = prod
                                            serial = data_dict.get("serial_number")
                                            edid_info["edid_serial"] = serial
                                            conn = data_dict.get("connector_type")
                                            edid_info["connector_type"] = conn
                                            break

                                    # Fallback: detect connector from system_profiler
                                    if not edid_info["connector_type"]:
                                        conn_type = display.get("spdisplays_connection_type", "")
                                        if conn_type:
                                            edid_info["connector_type"] = str(conn_type)

                                    displays.append(
                                        {
                                            "resolution": resolution,
                                            "refresh_rate": refresh_str,
                                            "color_depth": depth,
                                            "external_displays": 1 if "_name" in display else 0,
                                            "edid_manufacturer": edid_info["edid_manufacturer"],
                                            "edid_product_code": edid_info["edid_product_code"],
                                            "edid_serial": edid_info["edid_serial"],
                                            "connector_type": edid_info["connector_type"],
                                        }
                                    )

        # If no displays found, add a default entry
        if not displays:
            displays.append(
                {
                    "resolution": "Unknown",
                    "refresh_rate": "Unknown",
                    "color_depth": "Unknown",
                    "external_displays": 0,
                    "edid_manufacturer": None,
                    "edid_product_code": None,
                    "edid_serial": None,
                    "connector_type": None,
                }
            )
    except Exception:
        displays.append(
            {
                "resolution": "Unknown",
                "refresh_rate": "Unknown",
                "color_depth": "Unknown",
                "external_displays": 0,
                "edid_manufacturer": None,
                "edid_product_code": None,
                "edid_serial": None,
                "connector_type": None,
            }
        )

    return displays


def collect_memory_pressure() -> MemoryPressure:
    """Collect real-time memory pressure statistics."""
    verbose_log("Collecting memory pressure stats...")

    pressure: MemoryPressure = {
        "level": "normal",
        "pages_free": 0,
        "pages_active": 0,
        "pages_inactive": 0,
        "pages_wired": 0,
        "swap_used": 0,
        "swap_free": 0,
    }

    try:
        # Get memory pressure level
        mp_output = run(["memory_pressure"], timeout=5, log_errors=False)
        if "warn" in mp_output.lower():
            pressure["level"] = "warn"
        elif "critical" in mp_output.lower():
            pressure["level"] = "critical"

        # Get vm_stat for detailed page statistics
        vm_output = run(["vm_stat"], log_errors=False)
        for line in vm_output.splitlines():
            if "Pages free:" in line:
                pressure["pages_free"] = int(re.sub(r"\D", "", line))
            elif "Pages active:" in line:
                pressure["pages_active"] = int(re.sub(r"\D", "", line))
            elif "Pages inactive:" in line:
                pressure["pages_inactive"] = int(re.sub(r"\D", "", line))
            elif "Pages wired down:" in line:
                pressure["pages_wired"] = int(re.sub(r"\D", "", line))

        # Get swap usage
        sysctl_output = run(["sysctl", "vm.swapusage"], log_errors=False)
        if "used" in sysctl_output:
            # Example: vm.swapusage: total = 1024.00M  used = 512.00M  free = 512.00M
            parts = sysctl_output.split()
            for i, part in enumerate(parts):
                if part == "used" and i + 2 < len(parts):
                    used_str = parts[i + 2].replace("M", "").replace("G", "000")
                    pressure["swap_used"] = int(float(used_str))
                elif part == "free" and i + 2 < len(parts):
                    free_str = parts[i + 2].replace("M", "").replace("G", "000")
                    pressure["swap_free"] = int(float(free_str))
    except Exception:
        pass

    return pressure


def collect_hardware_info() -> HardwareInfo:
    log("Collecting hardware information...")
    mem = run(["sysctl", "-n", "hw.memsize"])

    def _get_gpu_info():
        try:
            data = get_json_output(["system_profiler", "SPDisplaysDataType", "-json"])
            gpus = []
            if data and isinstance(data, dict):
                for card in data.get("SPDisplaysDataType", []):
                    model = card.get("sppci_model", "Unknown GPU")
                    vram = card.get("spdisplays_vram_shared") or card.get("spdisplays_vram")
                    if vram:
                        model += f" ({vram})"
                    gpus.append(model)
            return gpus
        except Exception:
            return ["Unknown"]

    return {
        "cpu": run(["sysctl", "-n", "machdep.cpu.brand_string"]),
        "cpu_cores": int(run(["sysctl", "-n", "hw.ncpu"]) or 0),
        "gpu": _get_gpu_info(),
        "memory_gb": round(int(mem) / 1024**3, 2) if mem.isdigit() else None,
        "thermal_pressure": run(["pmset", "-g", "therm"]).splitlines(),
        "displays": collect_display_info(),
        "memory_pressure": collect_memory_pressure(),
    }


def collect_disk_health() -> list[DiskHealthInfo]:
    """Collect S.M.A.R.T. status and disk health information."""
    health_info: list[DiskHealthInfo] = []
    try:
        # Get list of physical disks
        disks_output = run(["diskutil", "list"], timeout=10)
        disk_identifiers = []

        for line in disks_output.splitlines():
            if line.startswith("/dev/disk"):
                disk_id = line.split()[0].replace("/dev/", "")
                # Only check physical disks (disk0, disk1, etc., not disk0s1)
                if "s" not in disk_id.split("disk")[1]:
                    disk_identifiers.append(disk_id)

        # Get info for each disk
        for disk_id in disk_identifiers:
            try:
                info_output = run(["diskutil", "info", disk_id], timeout=10, log_errors=False)

                disk_name = "Unknown"
                disk_type = "Unknown"
                smart_status = "Not Supported"

                for line in info_output.splitlines():
                    line = line.strip()
                    if line.startswith("Device / Media Name:"):
                        disk_name = line.split(":", 1)[1].strip()
                    elif line.startswith("Solid State:"):
                        disk_type = "SSD" if "Yes" in line else "HDD"
                    elif line.startswith("SMART Status:"):
                        smart_status = line.split(":", 1)[1].strip()

                health_info.append(
                    {
                        "disk_name": f"{disk_id} - {disk_name}",
                        "disk_type": disk_type,
                        "smart_status": smart_status,
                        "health_percentage": None,  # macOS doesn't expose percentage directly
                    }
                )
            except Exception:
                continue
    except Exception:
        pass

    return health_info


def collect_disk_info() -> DiskInfo:
    log("Collecting disk information...")
    stat = os.statvfs("/")
    return {
        "disk_total_gb": round(stat.f_blocks * stat.f_frsize / 1024**3, 2),
        "disk_free_gb": round(stat.f_bavail * stat.f_frsize / 1024**3, 2),
        "apfs_info": run(["diskutil", "apfs", "list"], timeout=30).splitlines(),
        "disk_health": collect_disk_health(),
    }
