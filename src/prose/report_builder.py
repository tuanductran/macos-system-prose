"""Build the final typed macOS System Prose report."""

from __future__ import annotations

from typing import cast

from prose.oclp import OCLPCompatibilityInfo
from prose.schema import (
    REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
    ApplicationsInfo,
    BatteryInfo,
    CloudInfo,
    CollectionStatus,
    CronInfo,
    DeveloperToolsInfo,
    DiagnosticsInfo,
    DiskInfo,
    EnvironmentInfo,
    FontInfo,
    HardwareInfo,
    IORegistryInfo,
    KernelExtensionsInfo,
    KernelParameters,
    LaunchItems,
    NetworkInfo,
    NVRAMInfo,
    OpenCorePatcherInfo,
    PackageManagers,
    ProcessInfo,
    SecurityInfo,
    ShellCustomization,
    StorageAnalysis,
    SystemInfo,
    SystemLogs,
    SystemPreferences,
    SystemReport,
)


def build_report(
    *,
    timestamp: float,
    collected: dict[str, object],
    collection_errors: list[str],
    collection_status: dict[str, CollectionStatus],
    opencore_patcher: OpenCorePatcherInfo,
    oclp_compatibility: OCLPCompatibilityInfo,
) -> SystemReport:
    """Assemble collected values and derived metadata into the public report."""
    system_info = cast(SystemInfo, collected["system_info"])
    hardware_info = cast(HardwareInfo, collected["hardware_info"])
    disk_info = cast(DiskInfo, collected["disk_info"])
    top_processes = cast(list[ProcessInfo], collected["top_processes"])
    startup = cast(LaunchItems, collected["startup"])
    login_items = cast(list[str], collected["login_items"])
    package_managers = cast(PackageManagers, collected["package_managers"])
    developer_tools = cast(DeveloperToolsInfo, collected["developer_tools"])
    kext_info = cast(KernelExtensionsInfo, collected["kext_info"])
    applications = cast(ApplicationsInfo, collected["applications"])
    environment = cast(EnvironmentInfo, collected["environment"])
    network = cast(NetworkInfo, collected["network"])
    battery = cast(BatteryInfo, collected["battery"])
    cron = cast(CronInfo, collected["cron"])
    diagnostics = cast(DiagnosticsInfo, collected["diagnostics"])
    security = cast(SecurityInfo, collected["security"])
    cloud = cast(CloudInfo, collected["cloud"])
    nvram = cast(NVRAMInfo, collected["nvram"])
    storage_analysis = cast(StorageAnalysis, collected["storage_analysis"])
    fonts = cast(FontInfo, collected["fonts"])
    shell_customization = cast(ShellCustomization, collected["shell_customization"])
    system_preferences = cast(SystemPreferences, collected["system_preferences"])
    kernel_params = cast(KernelParameters, collected["kernel_params"])
    system_logs = cast(SystemLogs, collected["system_logs"])
    ioregistry = cast(IORegistryInfo, collected["ioregistry"])

    return {
        "report_schema": REPORT_SCHEMA,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "timestamp": timestamp,
        "system": system_info,
        "hardware": hardware_info,
        "disk": disk_info,
        "top_processes": top_processes,
        "startup": startup,
        "login_items": login_items,
        "package_managers": package_managers,
        "developer_tools": developer_tools,
        "kexts": kext_info,
        "applications": applications,
        "environment": environment,
        "network": network,
        "battery": battery,
        "cron": cron,
        "diagnostics": diagnostics,
        "security": security,
        "cloud": cloud,
        "nvram": nvram,
        "storage_analysis": storage_analysis,
        "fonts": fonts,
        "shell_customization": shell_customization,
        "opencore_patcher": opencore_patcher,
        "oclp_compatibility": oclp_compatibility,
        "system_preferences": system_preferences,
        "kernel_params": kernel_params,
        "system_logs": system_logs,
        "ioregistry": ioregistry,
        "collection_errors": collection_errors,
        "collection_status": collection_status,
    }
