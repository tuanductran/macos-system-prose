"""OpenCore and OpenCore Legacy Patcher collectors.

Detection is evidence-based and does not infer security state from absence of OCLP signals.
"""

from __future__ import annotations

import re
from pathlib import Path

from prose import utils
from prose.datasets.smbios import is_legacy_mac
from prose.iokit import (
    get_boot_args,
    get_oclp_nvram_version,
    get_opencore_nvram_version,
    parse_amfi_boot_arg,
)
from prose.schema import OpenCorePatcherInfo


def collect_opencore_patcher(loaded_kexts: list[str] | None = None) -> OpenCorePatcherInfo:
    """Inspect OpenCore/OCLP signals without conflating them with root-patch state.

    OCLP-Version and the OpenCore version in OCLP's NVRAM namespace are strong
    signals. The presence of individual kexts or modified framework paths is
    only evidence that should be reported, not proof that OCLP is installed.
    """
    current_os = utils.run(["sw_vers", "-productVersion"], log_errors=False).strip()

    model_info = utils.run(
        ["system_profiler", "SPHardwareDataType"],
        log_errors=False,
    )
    current_model = ""
    for line in model_info.splitlines():
        if "Model Identifier" in line and ":" in line:
            current_model = line.split(":", 1)[1].strip()
            break

    detection_signals: list[str] = []
    detected = False
    version: str | None = None
    nvram_version = get_oclp_nvram_version()
    opencore_version = get_opencore_nvram_version()

    if nvram_version:
        detected = True
        detection_signals.append("oclp_nvram_version")
        version = nvram_version.replace("\x00", "").replace("%00", "")

    oclp_app = Path("/Applications/OpenCore-Patcher.app")
    if oclp_app.exists():
        detected = True
        detection_signals.append("oclp_application")
        if not version:
            version_output = utils.run(
                [
                    "defaults",
                    "read",
                    "/Applications/OpenCore-Patcher.app/Contents/Info.plist",
                    "CFBundleShortVersionString",
                ],
                log_errors=False,
            )
            if version_output:
                version = version_output.strip()

    root_patch_marker = Path("/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist")
    root_patch_marker_detected = root_patch_marker.exists()
    if root_patch_marker_detected:
        detected = True
        detection_signals.append("root_patch_marker")

    if opencore_version:
        detection_signals.append("opencore_nvram_version")

    if loaded_kexts is None:
        kextstat_output = utils.run(["kextstat", "-l"], log_errors=False)
        loaded_kexts = []
        for line in kextstat_output.splitlines():
            if "com.apple" not in line and not line.startswith("Index"):
                match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+)\s\(([^)]+)\)", line)
                if match:
                    loaded_kexts.append(f"{match.group(1)} ({match.group(2)})")

    oclp_kext_patterns = [
        "AMFIPass",
        "RestrictEvents",
        "Lilu",
        "WhateverGreen",
        "FeatureUnlock",
        "AutoPkgInstaller",
        "RSRHelper",
        "AirportBrcmFixup",
        "DebugEnhancer",
        "CryptexFixup",
    ]
    observed_kexts = [
        kext_info
        for kext_info in loaded_kexts
        if any(pattern in kext_info for pattern in oclp_kext_patterns)
    ]

    observed_frameworks: list[str] = []
    framework_paths = [
        "/System/Library/Extensions/AppleIntelHDGraphics.kext",
        "/System/Library/Extensions/AppleIntelHD3000Graphics.kext",
        "/System/Library/Extensions/AppleIntelSNBGraphicsFB.kext",
        "/System/Library/Extensions/IOBluetoothFamily.kext",
    ]
    for path in framework_paths:
        if Path(path).exists():
            observed_frameworks.append(path)

    unsupported_os_detected = bool(
        current_os and current_model and is_legacy_mac(current_model, current_os)
    )

    if unsupported_os_detected and observed_kexts:
        detection_signals.append("unsupported_os_plus_oclp_like_kexts")

    boot_args = get_boot_args()
    amfi_config = parse_amfi_boot_arg(boot_args) if boot_args else None

    if detected or root_patch_marker_detected:
        confidence = "high"
    elif unsupported_os_detected and observed_kexts:
        confidence = "low"
        detection_signals.append("inferred_from_hardware_and_kexts")
    else:
        confidence = "none"

    clean_nvram_version = (
        nvram_version.replace("\x00", "").replace("%00", "") if nvram_version else None
    )

    return {
        "detected": detected,
        "detection_confidence": confidence,
        "detection_signals": detection_signals,
        "version": version,
        "nvram_version": clean_nvram_version,
        "opencore_version": opencore_version,
        "unsupported_os_detected": unsupported_os_detected,
        "root_patch_marker_detected": root_patch_marker_detected,
        "loaded_kexts": observed_kexts[:10],
        "patched_frameworks": observed_frameworks,
        "amfi_configuration": amfi_config if amfi_config and amfi_config["amfi_value"] else None,
        "boot_args": boot_args,
    }
