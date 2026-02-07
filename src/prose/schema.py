"""Type definitions for macOS System Prose report structure.

This module defines all TypedDict schemas used throughout the project
to ensure type safety and clear data contracts.
"""

from __future__ import annotations

from typing import Literal, Optional, TypedDict, Union


class NotInstalled(TypedDict):
    installed: Literal[False]


class SystemInfo(TypedDict):
    os: str
    macos_version: str
    macos_name: str
    model_name: str
    model_identifier: str
    kernel: str
    architecture: str
    uptime: str
    sip_enabled: bool
    gatekeeper_enabled: bool
    filevault_enabled: bool


class HardwareInfo(TypedDict):
    cpu: str
    cpu_cores: int
    memory_gb: Optional[float]
    thermal_pressure: list[str]
    gpu: list[str]


class DiskInfo(TypedDict):
    disk_total_gb: float
    disk_free_gb: float
    apfs_info: list[str]


class ProcessInfo(TypedDict):
    pid: int
    cpu_percent: float
    mem_percent: float
    command: str


class LaunchItems(TypedDict):
    user_agents: list[str]
    system_agents: list[str]
    system_daemons: list[str]


class PackageVersionInfo(TypedDict):
    installed: Literal[True]
    version: str
    bin_path: str
    globals: Optional[list[str]]
    prefix: Optional[str]
    formula: Optional[list[str]]
    casks: Optional[list[str]]
    active_ports: Optional[list[str]]
    packages: Optional[list[str]]


class PackageManagers(TypedDict):
    homebrew: Union[PackageVersionInfo, NotInstalled]
    macports: Union[PackageVersionInfo, NotInstalled]
    pipx: Union[PackageVersionInfo, NotInstalled]
    npm: Union[PackageVersionInfo, NotInstalled]
    yarn: Union[PackageVersionInfo, NotInstalled]
    pnpm: Union[PackageVersionInfo, NotInstalled]
    bun: Union[PackageVersionInfo, NotInstalled]


class ApplicationsInfo(TypedDict):
    electron_apps: list[str]


class EnvironmentInfo(TypedDict):
    shell: Optional[str]
    python_executable: str
    python_version: str
    path_entries: list[str]
    path_duplicates: list[str]
    listening_ports: list[str]


class NetworkInfo(TypedDict):
    hostname: str
    primary_interface: str
    ipv4_address: str
    public_ip: str
    gateway: str
    subnet_mask: str
    mac_address: str
    dns_servers: list[str]
    wifi_ssid: Optional[str]
    firewall_status: str
    local_interfaces: list[dict[str, str]]


class BatteryInfo(TypedDict):
    present: bool
    percentage: Optional[str]
    cycle_count: Optional[int]
    condition: Optional[str]
    power_source: Optional[str]


class CronInfo(TypedDict):
    user_crontab: list[str]


class DiagnosticsInfo(TypedDict):
    recent_crashes: list[str]


class DeveloperToolsInfo(TypedDict):
    languages: dict[str, str]
    sdks: dict[str, str]
    cloud_devops: dict[str, str]
    databases: dict[str, str]
    version_managers: dict[str, str]
    infra: dict[str, str]
    extensions: dict[str, list[str]]
    editors: list[str]


class KernelExtensionsInfo(TypedDict):
    third_party_kexts: list[str]


class SystemReport(TypedDict):
    timestamp: float
    system: SystemInfo
    hardware: HardwareInfo
    disk: DiskInfo
    top_processes: list[ProcessInfo]
    startup: LaunchItems
    login_items: list[str]
    package_managers: PackageManagers
    developer_tools: DeveloperToolsInfo
    kexts: KernelExtensionsInfo
    applications: ApplicationsInfo
    environment: EnvironmentInfo
    network: NetworkInfo
    battery: BatteryInfo
    cron: CronInfo
    diagnostics: DiagnosticsInfo
