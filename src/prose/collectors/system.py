from __future__ import annotations

import os
import platform

from prose.schema import DiskInfo, HardwareInfo, SystemInfo
from prose.utils import get_json_output, log, run


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
    }


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
    }


def collect_disk_info() -> DiskInfo:
    log("Collecting disk information...")
    stat = os.statvfs("/")
    return {
        "disk_total_gb": round(stat.f_blocks * stat.f_frsize / 1024**3, 2),
        "disk_free_gb": round(stat.f_bavail * stat.f_frsize / 1024**3, 2),
        "apfs_info": run(["diskutil", "apfs", "list"], timeout=30).splitlines(),
    }
