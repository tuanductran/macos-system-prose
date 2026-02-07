"""Type definitions for macOS System Prose report structure.

This module defines all TypedDict schemas used throughout the project
to ensure type safety and clear data contracts.
"""

from __future__ import annotations

from typing import Literal, Optional, TypedDict, Union


class NotInstalled(TypedDict):
    installed: Literal[False]


class TimeMachineInfo(TypedDict):
    enabled: bool
    last_backup: Optional[str]
    destination: Optional[str]
    auto_backup: bool


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
    time_machine: TimeMachineInfo


class DisplayInfo(TypedDict):
    resolution: str
    refresh_rate: str
    color_depth: str
    external_displays: int


class MemoryPressure(TypedDict):
    level: str  # normal, warn, critical
    pages_free: int
    pages_active: int
    pages_inactive: int
    pages_wired: int
    swap_used: int
    swap_free: int


class HardwareInfo(TypedDict):
    cpu: str
    cpu_cores: int
    memory_gb: Optional[float]
    thermal_pressure: list[str]
    gpu: list[str]
    displays: list[DisplayInfo]
    memory_pressure: MemoryPressure


class DiskHealthInfo(TypedDict):
    disk_name: str
    disk_type: str
    smart_status: str
    health_percentage: Optional[int]


class DiskInfo(TypedDict):
    disk_total_gb: float
    disk_free_gb: float
    apfs_info: list[str]
    disk_health: list[DiskHealthInfo]


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


class BrewService(TypedDict):
    name: str
    status: str  # started, stopped, error
    user: Optional[str]
    file: Optional[str]


class PackageManagers(TypedDict):
    homebrew: Union[PackageVersionInfo, NotInstalled]
    macports: Union[PackageVersionInfo, NotInstalled]
    pipx: Union[PackageVersionInfo, NotInstalled]
    npm: Union[PackageVersionInfo, NotInstalled]
    yarn: Union[PackageVersionInfo, NotInstalled]
    pnpm: Union[PackageVersionInfo, NotInstalled]
    bun: Union[PackageVersionInfo, NotInstalled]
    homebrew_services: list[BrewService]


class ApplicationsInfo(TypedDict):
    electron_apps: list[str]
    all_apps: list[str]


class LaunchdService(TypedDict):
    label: str
    pid: Optional[int]
    status: str
    last_exit_code: Optional[int]


class EnvironmentInfo(TypedDict):
    shell: Optional[str]
    python_executable: str
    python_version: str
    path_entries: list[str]
    path_duplicates: list[str]
    listening_ports: list[str]
    launchd_services: list[LaunchdService]


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
    vpn_status: bool
    vpn_connections: list[str]
    vpn_apps: list[str]


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


class DockerContainer(TypedDict):
    id: str
    name: str
    image: str
    status: str
    ports: str
    created: str


class DockerImage(TypedDict):
    repository: str
    tag: str
    id: str
    size: str
    created: str


class DockerInfo(TypedDict):
    installed: bool
    version: str
    running: bool
    containers_total: int
    containers_running: int
    images_count: int
    containers: list[DockerContainer]
    images: list[DockerImage]


class GitConfig(TypedDict):
    user_name: Optional[str]
    user_email: Optional[str]
    core_editor: Optional[str]
    credential_helper: Optional[str]
    aliases: dict[str, str]
    other_settings: dict[str, str]


class BrowserInfo(TypedDict):
    name: str
    installed: bool
    version: str
    path: str


class DeveloperToolsInfo(TypedDict):
    languages: dict[str, str]
    sdks: dict[str, str]
    cloud_devops: dict[str, str]
    databases: dict[str, str]
    version_managers: dict[str, str]
    infra: dict[str, str]
    extensions: dict[str, list[str]]
    editors: list[str]
    docker: DockerInfo
    browsers: list[BrowserInfo]
    git_config: GitConfig
    terminal_emulators: list[str]
    shell_frameworks: dict[str, str]


class SystemExtension(TypedDict):
    identifier: str
    version: str
    state: str
    team_id: str


class KernelExtensionsInfo(TypedDict):
    third_party_kexts: list[str]
    system_extensions: list[SystemExtension]


class TCCPermission(TypedDict):
    app: str
    service: str  # camera, microphone, screen-recording, accessibility, etc.
    allowed: bool


class CodeSigningInfo(TypedDict):
    app_name: str
    identifier: str
    authority: str
    valid: bool
    team_id: Optional[str]


class CloudSyncInfo(TypedDict):
    icloud_enabled: bool
    icloud_status: str
    drive_enabled: bool
    storage_used: Optional[str]


class SecurityInfo(TypedDict):
    security_tools: list[str]
    antivirus: list[str]
    tcc_permissions: list[TCCPermission]
    code_signing_sample: list[CodeSigningInfo]


class CloudInfo(TypedDict):
    sync_status: CloudSyncInfo


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
    security: SecurityInfo
    cloud: CloudInfo
