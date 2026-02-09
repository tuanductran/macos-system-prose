"""Type definitions for macOS System Prose report structure.

This module defines all TypedDict schemas used throughout the project
to ensure type safety and clear data contracts.
"""

from __future__ import annotations

from typing import Literal, TypedDict


class NotInstalled(TypedDict):
    installed: Literal[False]


class TimeMachineInfo(TypedDict):
    enabled: bool
    last_backup: str | None
    destination: str | None
    auto_backup: bool


class SystemInfo(TypedDict):
    os: str
    macos_version: str
    macos_name: str
    model_name: str
    model_identifier: str
    marketing_name: str | None  # SMBIOS: "MacBook Air (13-inch, Mid 2013)"
    board_id: str | None  # SMBIOS: "Mac-7DF21CB3ED6977E5"
    kernel: str
    architecture: str
    uptime: str
    uptime_seconds: int
    boot_time: str
    load_average: str
    sip_enabled: bool
    gatekeeper_enabled: bool
    filevault_enabled: bool
    time_machine: TimeMachineInfo


class DisplayInfo(TypedDict):
    resolution: str
    refresh_rate: str
    color_depth: str
    external_displays: int
    edid_manufacturer: str | None
    edid_product_code: str | None
    edid_serial: str | None
    connector_type: str | None


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
    memory_gb: float | None
    thermal_pressure: list[str]
    gpu: list[str]
    displays: list[DisplayInfo]
    memory_pressure: MemoryPressure


class DiskHealthInfo(TypedDict):
    disk_name: str
    disk_type: str
    smart_status: str
    health_percentage: int | None


class PCIeDevice(TypedDict):
    name: str
    vendor_id: str | None
    device_id: str | None
    class_code: str | None
    pci_address: str | None


class USBDevice(TypedDict):
    name: str
    vendor_id: str | None
    product_id: str | None
    location_id: str | None
    speed: str | None


class AudioCodec(TypedDict):
    name: str
    codec_id: str | None
    layout_id: int | None
    vendor: str | None


class IORegistryInfo(TypedDict):
    pcie_devices: list[PCIeDevice]
    usb_devices: list[USBDevice]
    audio_codecs: list[AudioCodec]


class APFSVolume(TypedDict):
    name: str
    device: str  # e.g. "disk1s1"
    role: str  # e.g. "Data", "System", "Preboot", "Recovery", "VM"
    capacity_used_gb: float
    encrypted: bool
    filevault: bool


class APFSContainer(TypedDict):
    reference: str  # e.g. "disk1"
    physical_store: str  # e.g. "disk0s2"
    capacity_gb: float
    free_gb: float
    used_percent: float
    fusion: bool
    volumes: list[APFSVolume]


class DiskInfo(TypedDict):
    disk_total_gb: float
    disk_free_gb: float
    apfs_info: list[APFSContainer]
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
    globals: list[str] | None
    prefix: str | None
    formula: list[str] | None
    casks: list[str] | None
    active_ports: list[str] | None
    packages: list[str] | None


class BrewService(TypedDict):
    name: str
    status: str  # started, stopped, error
    user: str | None
    file: str | None


class PackageManagers(TypedDict):
    homebrew: PackageVersionInfo | NotInstalled
    macports: PackageVersionInfo | NotInstalled
    pipx: PackageVersionInfo | NotInstalled
    npm: PackageVersionInfo | NotInstalled
    yarn: PackageVersionInfo | NotInstalled
    pnpm: PackageVersionInfo | NotInstalled
    bun: PackageVersionInfo | NotInstalled
    homebrew_services: list[BrewService]


class ApplicationsInfo(TypedDict):
    electron_apps: list[str]
    all_apps: list[str]


class LaunchdService(TypedDict):
    label: str
    pid: int | None
    status: str
    last_exit_code: int | None


class EnvironmentInfo(TypedDict):
    shell: str | None
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
    wifi_ssid: str | None
    firewall_status: str
    local_interfaces: list[dict[str, str]]
    vpn_status: bool
    vpn_connections: list[str]
    vpn_apps: list[str]


class BatteryInfo(TypedDict):
    present: bool
    percentage: str | None
    cycle_count: int | None
    condition: str | None
    power_source: str | None


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
    user_name: str | None
    user_email: str | None
    core_editor: str | None
    credential_helper: str | None
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
    team_id: str | None


class CloudSyncInfo(TypedDict):
    icloud_enabled: bool
    icloud_status: str
    drive_enabled: bool
    storage_used: str | None


class SecurityInfo(TypedDict):
    security_tools: list[str]
    antivirus: list[str]
    tcc_permissions: list[TCCPermission]
    code_signing_sample: list[CodeSigningInfo]


class CloudInfo(TypedDict):
    sync_status: CloudSyncInfo


class NVRAMInfo(TypedDict):
    """NVRAM (Non-Volatile RAM) boot configuration and system variables."""

    boot_args: str  # kernel boot arguments
    csr_active_config: str  # System Integrity Protection config (hex)
    sip_disabled: bool  # SIP disabled via csr-active-config
    oclp_version: str | None  # OpenCore Patcher version from NVRAM
    oclp_settings: str | None  # OCLP-Settings bitmask
    secure_boot_model: str | None  # SecureBootModel for Apple Silicon
    hardware_model: str | None  # HardwareModel identifier
    nvram_variables_count: int  # Total NVRAM variable count


class StorageAnalysis(TypedDict):
    documents_gb: float
    downloads_gb: float
    desktop_gb: float
    library_gb: float
    caches_gb: float
    logs_gb: float
    total_user_data_gb: float


class FontInfo(TypedDict):
    system_fonts: int
    user_fonts: int
    total_fonts: int


class ShellCustomization(TypedDict):
    aliases_count: int
    functions_count: int
    rc_file: str
    rc_size_kb: float


class AMFIConfig(TypedDict):
    """AMFI (AppleMobileFileIntegrity) configuration."""

    amfi_value: str | None
    allow_task_for_pid: bool
    allow_invalid_signature: bool
    lv_enforce_third_party: bool


class OpenCorePatcherInfo(TypedDict):
    detected: bool
    version: str | None
    nvram_version: str | None  # From NVRAM OCLP-Version
    unsupported_os_detected: bool
    loaded_kexts: list[str]
    patched_frameworks: list[str]
    amfi_configuration: AMFIConfig | None
    boot_args: str | None


class SystemPreferences(TypedDict):
    trackpad_speed: float | None
    key_repeat_rate: int | None
    mouse_speed: float | None
    scroll_direction_natural: bool


class KernelParameters(TypedDict):
    max_files: int
    max_processes: int
    max_vnodes: int


class SystemLogs(TypedDict):
    critical_errors: list[str]
    warnings: list[str]
    log_period: str  # e.g. "last 1 hour"


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
    nvram: NVRAMInfo  # Phase 5: NVRAM inspection
    storage_analysis: StorageAnalysis
    fonts: FontInfo
    shell_customization: ShellCustomization
    opencore_patcher: OpenCorePatcherInfo
    system_preferences: SystemPreferences
    kernel_params: KernelParameters
    system_logs: SystemLogs
    ioregistry: IORegistryInfo  # Phase 3: IORegistry hardware detection
    collection_errors: list[str]  # Track any errors during data collection
