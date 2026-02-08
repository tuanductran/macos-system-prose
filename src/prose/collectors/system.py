from __future__ import annotations

import asyncio
import os
import platform
import plistlib
import re
import subprocess
from typing import cast

from prose.constants import Timeouts
from prose.datasets.smbios import get_smbios_data
from prose.macos_versions import get_macos_version_info
from prose.schema import (
    APFSContainer,
    APFSVolume,
    DiskHealthInfo,
    DiskInfo,
    DisplayInfo,
    HardwareInfo,
    MemoryPressure,
    SystemInfo,
    TimeMachineInfo,
)
from prose.utils import (
    async_get_json_output,
    async_run_command,
    log,
    run,
    verbose_log,
)


async def _get_uptime_seconds() -> int:
    """Get system uptime in seconds."""
    try:
        import time

        boot_time_output = await async_run_command(["sysctl", "-n", "kern.boottime"])
        boot_time_output = boot_time_output.strip()
        # Parse boot time string: { sec = 1770357120, usec = 0 }
        match = re.search(r"sec = (\d+)", boot_time_output)
        if match:
            boot_timestamp = int(match.group(1))
            return int(time.time()) - boot_timestamp
    except (OSError, ValueError) as e:
        verbose_log(f"Failed to get uptime seconds from sysctl: {e}")
    return 0


async def collect_time_machine_info() -> TimeMachineInfo:
    """Collect Time Machine backup status and configuration."""
    try:
        # Run all Time Machine commands concurrently
        status_output, latest_backup, dest_info, prefs = await asyncio.gather(
            async_run_command(["tmutil", "status"], log_errors=False),
            async_run_command(["tmutil", "latestbackup"], log_errors=False),
            async_run_command(["tmutil", "destinationinfo"], log_errors=False),
            async_run_command(
                [
                    "defaults",
                    "read",
                    "/Library/Preferences/com.apple.TimeMachine",
                    "AutoBackup",
                ],
                log_errors=False,
            ),
        )

        # Check if Time Machine is enabled
        enabled = "Running" in status_output or "BackupPhase" in status_output

        # Get last backup date
        last_backup = None
        latest_backup = latest_backup.strip()
        if latest_backup and latest_backup != "No" and not latest_backup.startswith("Unable"):
            last_backup = latest_backup

        # Get destination info
        destination = None
        if dest_info and "Name" in dest_info:
            for line in dest_info.splitlines():
                if line.strip().startswith("Name"):
                    destination = line.split(":", 1)[1].strip()
                    break

        # Check if auto backup is enabled
        auto_backup = prefs.strip() == "1"

        return {
            "enabled": enabled,
            "last_backup": last_backup,
            "destination": destination,
            "auto_backup": auto_backup,
        }
    except (OSError, ValueError, IndexError) as e:
        verbose_log(f"Failed to collect Time Machine info: {e}")
        return {
            "enabled": False,
            "last_backup": None,
            "destination": None,
            "auto_backup": False,
        }


def _parse_uptime(raw: str) -> str:
    """Parse uptime output into clean human-readable format.

    Input:  '10:02  up 3 days,  5:17, 3 users,'
    Output: 'up 3 days, 5:17'
    """
    # Remove leading timestamp (e.g. "10:02  ")
    if "up" in raw:
        idx = raw.index("up")
        raw = raw[idx:]
    # Remove trailing ", N users," and whitespace
    raw = re.sub(r",\s*\d+\s+users?,?\s*$", "", raw)
    # Collapse whitespace
    return re.sub(r"\s{2,}", " ", raw).strip()


def _parse_boot_time(raw: str) -> str:
    """Parse kern.boottime sysctl output into ISO-like timestamp.

    Input:  '{ sec = 1770471959, usec = 528688 } Sat Feb  7 20:45:59 2026'
    Output: 'Sat Feb 7 20:45:59 2026'
    """
    # Extract the human-readable date after the closing brace
    if "}" in raw:
        date_part = raw.split("}", 1)[1].strip()
        if date_part:
            return re.sub(r"\s{2,}", " ", date_part)
    return raw


def _parse_load_average(raw: str) -> str:
    """Parse vm.loadavg sysctl output into clean format.

    Input:  '{ 13.16 12.04 11.45 }'
    Output: '13.16 12.04 11.45'
    """
    return raw.strip().strip("{").strip("}").strip()


# CoreGraphics color depth constants → human-readable
_COLOR_DEPTH_MAP: dict[str, str] = {
    "CGSThirtytwoBitColor": "32-bit Color",
    "CGSTwentyfourBitColor": "24-bit Color",
    "CGSSixteenBitColor": "16-bit Color",
    "CGSEightBitColor": "8-bit Color",
}


def _humanize_color_depth(raw: str) -> str:
    """Convert CoreGraphics depth constant to human-readable string."""
    return _COLOR_DEPTH_MAP.get(raw, raw)


# system_profiler connector type constants → human-readable
_CONNECTOR_TYPE_MAP: dict[str, str] = {
    "spdisplays_internal": "Internal",
    "spdisplays_displayport": "DisplayPort",
    "spdisplays_hdmi": "HDMI",
    "spdisplays_thunderbolt": "Thunderbolt",
    "spdisplays_vga": "VGA",
    "spdisplays_dvi": "DVI",
}


def _humanize_connector_type(raw: str) -> str:
    """Convert system_profiler connector constant to human-readable string."""
    return _CONNECTOR_TYPE_MAP.get(raw, raw)


async def _check_sip_enabled() -> bool:
    """Check SIP status from the first line of csrutil output only.

    csrutil status output can contain 'enabled' in sub-field descriptions
    even when SIP itself is disabled/unknown. Only the first line is authoritative:
      "System Integrity Protection status: enabled."
      "System Integrity Protection status: disabled."
      "System Integrity Protection status: unknown (Custom Configuration)."
    """
    output = await async_run_command(["csrutil", "status"])
    if not output:
        return False
    first_line = output.splitlines()[0].lower()
    return "enabled" in first_line and "unknown" not in first_line


async def _get_marketing_name_from_system() -> str | None:
    """Get the exact marketing name from macOS SystemProfiler preferences.

    macOS stores the precise model name (e.g., "MacBook Air (13-inch, Early 2014)")
    in com.apple.SystemProfiler "CPU Names". This distinguishes models that share
    the same model identifier but were released in different years.
    """
    try:
        output = await async_run_command(
            ["defaults", "read", "com.apple.SystemProfiler", "CPU Names"],
            log_errors=False,
        )
        if output:
            match = re.search(r'"[^"]+"\s*=\s*"([^"]+)"', output)
            if match:
                return match.group(1)
    except (OSError, ValueError) as e:
        verbose_log(f"Failed to get marketing name from system preferences: {e}")
    return None


async def _get_board_id_from_ioreg() -> str | None:
    """Get the board-id directly from IORegistry hardware.

    Reads IOPlatformExpertDevice to get the actual board-id burned into firmware,
    rather than relying on a static database lookup.
    """
    try:
        output = await async_run_command(
            ["ioreg", "-c", "IOPlatformExpertDevice", "-d2"],
            log_errors=False,
        )
        if output:
            match = re.search(r'"board-id"\s*=\s*<"([^"]+)">', output)
            if match:
                return match.group(1)
    except (OSError, ValueError) as e:
        verbose_log(f"Failed to get board-id from IORegistry: {e}")
    return None


async def collect_system_info() -> SystemInfo:
    log("Collecting system information...")

    version_info = get_macos_version_info()
    version = version_info["version"]
    macos_name = f"macOS {version_info['name']}"

    # Run all independent commands concurrently
    results = await asyncio.gather(
        async_get_json_output(["system_profiler", "SPHardwareDataType", "-json"]),
        _get_marketing_name_from_system(),
        _get_board_id_from_ioreg(),
        async_run_command(["uname", "-r"]),
        async_run_command(["uptime"]),
        _get_uptime_seconds(),
        async_run_command(["sysctl", "-n", "kern.boottime"]),
        async_run_command(["sysctl", "-n", "vm.loadavg"]),
        _check_sip_enabled(),
        async_run_command(["spctl", "--status"]),
        async_run_command(["fdesetup", "status"]),
        collect_time_machine_info(),
    )

    # Explicit type assignments to help mypy
    hw_data = cast("dict[str, list[dict[str, str | int | float]]]", results[0])
    system_marketing_name = cast("str | None", results[1])
    system_board_id = cast("str | None", results[2])
    kernel_raw = cast(str, results[3])
    uptime_raw = cast(str, results[4])
    uptime_seconds = cast(int, results[5])
    boot_time_raw = cast(str, results[6])
    load_avg_raw = cast(str, results[7])
    sip_enabled = cast(bool, results[8])
    gatekeeper_raw = cast(str, results[9])
    filevault_raw = cast(str, results[10])
    time_machine = cast(TimeMachineInfo, results[11])

    # Parse hardware data
    model_name, model_id = "Unknown Mac", "Unknown"
    if hw_data and isinstance(hw_data, dict) and "SPHardwareDataType" in hw_data:
        sp_hard = hw_data["SPHardwareDataType"]
        if isinstance(sp_hard, list) and len(sp_hard) > 0:
            info = sp_hard[0]
            if isinstance(info, dict):
                model_name = str(info.get("machine_name", "Mac"))
                model_id = str(info.get("machine_model", "Unknown"))

    # Fall back to SMBIOS database for fields the system doesn't provide
    smbios_data = get_smbios_data(model_id)
    marketing_name = system_marketing_name or (
        smbios_data.get("marketing_name") if smbios_data else None
    )
    board_id = system_board_id or (smbios_data.get("board_id") if smbios_data else None)
    cpu_generation = smbios_data.get("cpu_generation") if smbios_data else None
    max_os_supported = smbios_data.get("max_os_supported") if smbios_data else None

    if marketing_name:
        source = "system" if system_marketing_name else "SMBIOS"
        verbose_log(
            f"Model: {marketing_name} (source: {source}, Board: {board_id}, "
            f"CPU gen: {cpu_generation}, Max OS: {max_os_supported})"
        )

    # Non-blocking operation
    architecture = platform.machine()

    # Parse kernel string
    kernel = kernel_raw.strip()

    return SystemInfo(
        os="Darwin",
        macos_version=version,
        macos_name=macos_name,
        model_name=model_name,
        model_identifier=model_id,
        marketing_name=marketing_name,
        board_id=board_id,
        cpu_generation=cpu_generation,
        max_os_supported=max_os_supported,
        kernel=kernel,
        architecture=architecture,
        uptime=_parse_uptime(uptime_raw.split("load")[0]),
        uptime_seconds=uptime_seconds,
        boot_time=_parse_boot_time(boot_time_raw),
        load_average=_parse_load_average(load_avg_raw),
        sip_enabled=sip_enabled,
        gatekeeper_enabled="enabled" in gatekeeper_raw.lower(),
        filevault_enabled="on" in filevault_raw.lower(),
        time_machine=time_machine,
    )


async def collect_display_info() -> list[DisplayInfo]:
    """Collect display information including resolution, refresh rate, and EDID data."""
    import plistlib

    from prose.utils import parse_edid

    displays: list[DisplayInfo] = []

    # Run both IORegistry and system_profiler concurrently
    ioreg_output, sp_data = await asyncio.gather(
        async_run_command(
            ["ioreg", "-l", "-w0", "-r", "-a", "-c", "IODisplayConnect"],
            timeout=Timeouts.FAST,
            log_errors=False,
        ),
        async_get_json_output(["system_profiler", "SPDisplaysDataType", "-json"]),
    )

    # First, parse EDID data from IORegistry
    edid_data_map: dict[str, dict[str, str | None]] = {}
    try:
        if ioreg_output:
            plist = plistlib.loads(ioreg_output.encode("utf-8"))
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

    # Now process display info from system_profiler
    try:
        if sp_data and isinstance(sp_data, dict) and "SPDisplaysDataType" in sp_data:
            sp_displays = sp_data["SPDisplaysDataType"]
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

                                    depth = _humanize_color_depth(
                                        str(display.get("spdisplays_depth", "Unknown"))
                                    )

                                    # Try to match with EDID data
                                    edid_info: dict[str, str | None] = {
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
                                            edid_info["connector_type"] = _humanize_connector_type(
                                                str(conn_type)
                                            )

                                    displays.append(
                                        {
                                            "resolution": resolution,
                                            "refresh_rate": refresh_str,
                                            "color_depth": depth,
                                            "external_displays": (
                                                0
                                                if "internal"
                                                in str(
                                                    display.get("spdisplays_connection_type", "")
                                                ).lower()
                                                else 1
                                            ),
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
    except (KeyError, TypeError, ValueError, IndexError) as e:
        verbose_log(f"Failed to process display info from system_profiler: {e}")
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


async def collect_memory_pressure() -> MemoryPressure:
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
        # Run all memory commands concurrently
        mp_output, vm_output, sysctl_output = await asyncio.gather(
            async_run_command(["memory_pressure"], timeout=Timeouts.FAST, log_errors=False),
            async_run_command(["vm_stat"], log_errors=False),
            async_run_command(["sysctl", "vm.swapusage"], log_errors=False),
        )

        # Get memory pressure level
        if "warn" in mp_output.lower():
            pressure["level"] = "warn"
        elif "critical" in mp_output.lower():
            pressure["level"] = "critical"

        # Get vm_stat for detailed page statistics
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
        if "used" in sysctl_output:
            # Example: vm.swapusage: total = 1024.00M  used = 512.00M  free = 512.00M
            parts = sysctl_output.split()
            for i, part in enumerate(parts):
                if part == "used" and i + 2 < len(parts):
                    used_str = parts[i + 2]
                    if used_str.endswith("G"):
                        pressure["swap_used"] = int(float(used_str[:-1]) * 1024)
                    else:
                        pressure["swap_used"] = int(float(used_str.replace("M", "")))
                elif part == "free" and i + 2 < len(parts):
                    free_str = parts[i + 2]
                    if free_str.endswith("G"):
                        pressure["swap_free"] = int(float(free_str[:-1]) * 1024)
                    else:
                        pressure["swap_free"] = int(float(free_str.replace("M", "")))
    except (OSError, ValueError, IndexError) as e:
        verbose_log(f"Failed to collect memory pressure stats: {e}")

    return pressure


async def collect_hardware_info() -> HardwareInfo:
    log("Collecting hardware information...")

    async def _get_gpu_info():
        try:
            data = await async_get_json_output(["system_profiler", "SPDisplaysDataType", "-json"])
            gpus = []
            if data and isinstance(data, dict):
                for card in data.get("SPDisplaysDataType", []):
                    model = card.get("sppci_model", "Unknown GPU")
                    vram = card.get("spdisplays_vram_shared") or card.get("spdisplays_vram")
                    if vram:
                        model += f" ({vram})"
                    gpus.append(model)
            return gpus
        except (OSError, KeyError, TypeError, ValueError) as e:
            verbose_log(f"Failed to collect GPU info: {e}")
            return ["Unknown"]

    # Run all independent commands concurrently
    mem, cpu, cpu_cores_raw, gpu_info, thermal, displays, memory_pressure = await asyncio.gather(
        async_run_command(["sysctl", "-n", "hw.memsize"]),
        async_run_command(["sysctl", "-n", "machdep.cpu.brand_string"]),
        async_run_command(["sysctl", "-n", "hw.ncpu"]),
        _get_gpu_info(),
        async_run_command(["pmset", "-g", "therm"]),
        collect_display_info(),
        collect_memory_pressure(),
    )

    return {
        "cpu": cpu,
        "cpu_cores": int(cpu_cores_raw) if cpu_cores_raw else 0,
        "gpu": gpu_info,
        "memory_gb": round(int(mem) / 1024**3, 2) if mem.isdigit() else None,
        "thermal_pressure": thermal.splitlines(),
        "displays": displays,
        "memory_pressure": memory_pressure,
    }


def collect_disk_health() -> list[DiskHealthInfo]:
    """Collect S.M.A.R.T. status and disk health information."""
    health_info: list[DiskHealthInfo] = []
    try:
        # Get list of physical disks
        disks_output = run(["diskutil", "list"], timeout=Timeouts.FAST)
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
                info_output = run(
                    ["diskutil", "info", disk_id],
                    timeout=Timeouts.FAST,
                    log_errors=False,
                )

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
            except (OSError, ValueError, IndexError) as e:
                verbose_log(f"Failed to collect health info for disk {disk_id}: {e}")
                continue
    except (OSError, ValueError) as e:
        verbose_log(f"Failed to collect disk list: {e}")

    return health_info


def _bytes_to_gb(b: int) -> float:
    """Convert bytes to GB, rounded to 2 decimals."""
    return round(b / 1024**3, 2)


def _parse_apfs_containers() -> list[APFSContainer]:
    """Parse APFS container/volume info via ``diskutil apfs list -plist``."""
    try:
        raw = subprocess.run(
            ["diskutil", "apfs", "list", "-plist"],
            capture_output=True,
            timeout=Timeouts.SLOW,
        )
        if raw.returncode != 0 or not raw.stdout:
            return []
        data = plistlib.loads(raw.stdout)

        containers: list[APFSContainer] = []
        for c in data.get("Containers", []):
            ceiling = c.get("CapacityCeiling", 0)
            free = c.get("CapacityFree", 0)
            used = ceiling - free
            used_pct = round(used / ceiling * 100, 1) if ceiling > 0 else 0.0

            volumes: list[APFSVolume] = []
            for v in c.get("Volumes", []):
                roles = v.get("Roles", [])
                volumes.append(
                    {
                        "name": v.get("Name", "Unknown"),
                        "device": v.get("DeviceIdentifier", ""),
                        "role": roles[0] if roles else "Unknown",
                        "capacity_used_gb": _bytes_to_gb(v.get("CapacityInUse", 0)),
                        "encrypted": v.get("Encryption", False),
                        "filevault": v.get("FileVault", False),
                    }
                )

            stores = c.get("PhysicalStores", [])
            containers.append(
                {
                    "reference": c.get("ContainerReference", ""),
                    "physical_store": stores[0].get("DeviceIdentifier", "") if stores else "",
                    "capacity_gb": _bytes_to_gb(ceiling),
                    "free_gb": _bytes_to_gb(free),
                    "used_percent": used_pct,
                    "fusion": c.get("Fusion", False),
                    "volumes": volumes,
                }
            )
        return containers
    except (OSError, TypeError, KeyError, ValueError) as e:
        verbose_log(f"Failed to parse APFS containers: {e}")
        return []


def collect_disk_info() -> DiskInfo:
    log("Collecting disk information...")
    stat = os.statvfs("/")
    return {
        "disk_total_gb": round(stat.f_blocks * stat.f_frsize / 1024**3, 2),
        "disk_free_gb": round(stat.f_bavail * stat.f_frsize / 1024**3, 2),
        "apfs_info": _parse_apfs_containers(),
        "disk_health": collect_disk_health(),
    }
