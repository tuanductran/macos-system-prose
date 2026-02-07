from __future__ import annotations

import os
import platform

from prose.schema import DiskHealthInfo, DiskInfo, DisplayInfo, HardwareInfo, SystemInfo, TimeMachineInfo
from prose.utils import get_json_output, log, run, verbose_log


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
            prefs = run(["defaults", "read", "/Library/Preferences/com.apple.TimeMachine", "AutoBackup"], log_errors=False)
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
    # Get version and name directly from system
    version = run(["sw_vers", "-productVersion"])

    # Try to get marketing name from system license or profiler
    macos_name = "macOS"
    try:
        # Method 1: Check the license file (usually contains the marketing name)
        license_path = (
            "/System/Library/CoreServices/Setup Assistant.app"
            "/Contents/Resources/en.lproj/OSXSoftwareLicense.rtf"
        )
        if os.path.exists(license_path):
            name_match = run(["grep", "-oE", "macOS [a-zA-Z ]+", license_path])
            if name_match:
                macos_name = name_match.splitlines()[0].strip()

        # Method 2: Fallback to system_profiler if name still generic
        if macos_name == "macOS":
            sw_data = get_json_output(["system_profiler", "SPSoftwareDataType", "-json"])
            if sw_data and "SPSoftwareDataType" in sw_data:
                os_ver_str = sw_data["SPSoftwareDataType"][0].get("os_version", "")
                if "macOS" in os_ver_str:
                    # Often looks like "macOS 12.7.6 (21H1320)"
                    macos_name = os_ver_str.split("(")[0].strip()
    except Exception:
        pass

    hw_data = get_json_output(["system_profiler", "SPHardwareDataType", "-json"])
    model_name, model_id = "Unknown Mac", "Unknown"

    if hw_data and "SPHardwareDataType" in hw_data:
        info = hw_data["SPHardwareDataType"][0]
        model_name = info.get("machine_name", "Mac")
        model_id = info.get("machine_model", "Unknown")

    return {
        "os": "macOS",
        "macos_version": version,
        "macos_name": macos_name,
        "model_name": model_name,
        "model_identifier": model_id,
        "kernel": run(["uname", "-r"]),
        "architecture": platform.machine(),
        "uptime": run(["uptime"]).split("load")[0].strip(),
        "sip_enabled": "enabled" in run(["csrutil", "status"]).lower(),
        "gatekeeper_enabled": "enabled" in run(["spctl", "--status"]).lower(),
        "filevault_enabled": "on" in run(["fdesetup", "status"]).lower(),
        "time_machine": collect_time_machine_info(),
    }


def collect_display_info() -> list[DisplayInfo]:
    """Collect display information including resolution and refresh rate."""
    displays = []
    try:
        data = get_json_output(["system_profiler", "SPDisplaysDataType", "-json"])
        if data and "SPDisplaysDataType" in data:
            for card in data["SPDisplaysDataType"]:
                for display in card.get("spdisplays_ndrvs", []):
                    resolution = display.get("_spdisplays_resolution", "Unknown")
                    refresh = display.get("spdisplays_refresh_rate", "Unknown")
                    depth = display.get("spdisplays_depth", "Unknown")
                    
                    displays.append({
                        "resolution": resolution,
                        "refresh_rate": refresh,
                        "color_depth": depth,
                        "external_displays": 1 if "_name" in display else 0,
                    })
        
        # If no displays found, add a default entry
        if not displays:
            displays.append({
                "resolution": "Unknown",
                "refresh_rate": "Unknown",
                "color_depth": "Unknown",
                "external_displays": 0,
            })
    except Exception:
        displays.append({
            "resolution": "Unknown",
            "refresh_rate": "Unknown",
            "color_depth": "Unknown",
            "external_displays": 0,
        })
    
    return displays


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
    }


def collect_disk_health() -> list[DiskHealthInfo]:
    """Collect S.M.A.R.T. status and disk health information."""
    health_info = []
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
                
                health_info.append({
                    "disk_name": f"{disk_id} - {disk_name}",
                    "disk_type": disk_type,
                    "smart_status": smart_status,
                    "health_percentage": None,  # macOS doesn't expose percentage directly
                })
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
