"""Main orchestration engine for macOS System Prose.

This module coordinates all data collection activities and generates
the final system report in both JSON and AI-optimized text formats.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, cast

from prose import utils
from prose.collectors.advanced import (
    collect_fonts,
    collect_kernel_parameters,
    collect_opencore_patcher,
    collect_shell_customization,
    collect_storage_analysis,
    collect_system_logs,
    collect_system_preferences,
)
from prose.collectors.developer import collect_dev_tools
from prose.collectors.environment import (
    collect_battery_info,
    collect_cloud_sync,
    collect_cron_jobs,
    collect_diagnostics,
    collect_electron_apps,
    collect_environment_info,
    collect_kexts,
    collect_launch_items,
    collect_login_items,
    collect_nvram_variables,  # Phase 5
    collect_processes,
    collect_security_tools,
)
from prose.collectors.ioregistry import collect_ioregistry_info  # Phase 3
from prose.collectors.network import collect_network_info
from prose.collectors.packages import collect_package_managers
from prose.collectors.system import collect_disk_info, collect_hardware_info, collect_system_info
from prose.datasets.smbios import SMBIOS_DATABASE
from prose.diff import diff_reports, format_diff
from prose.oclp import build_oclp_compatibility
from prose.schema import (
    ApplicationsInfo,
    BatteryInfo,
    CollectionStatus,
    CloudInfo,
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


@dataclass(frozen=True)
class CollectorSpec:
    """Typed registration for one independent report collector."""

    name: str
    run: Callable[[], Awaitable[object]]
    default: object
    timeout_seconds: float


class CollectorTimeoutError(TimeoutError):
    """Raised when a collector exceeds its configured execution timeout."""

    def __init__(self, message: str, duration_ms: float) -> None:
        super().__init__(message)
        self.duration_ms = duration_ms


def _async_collector(collector: Callable[[], object]) -> Callable[[], Awaitable[object]]:
    """Adapt a synchronous collector to the async collector registry."""

    async def run_collector() -> object:
        return await asyncio.to_thread(collector)

    return run_collector


def _build_collector_registry(*, include_sensitive_network: bool) -> tuple[CollectorSpec, ...]:
    """Return the single source of truth for independent collectors."""
    return (
        CollectorSpec("system_info", collect_system_info, {}, 30),
        CollectorSpec("hardware_info", collect_hardware_info, {}, 30),
        CollectorSpec("disk_info", _async_collector(collect_disk_info), {}, 60),
        CollectorSpec("top_processes", _async_collector(collect_processes), [], 15),
        CollectorSpec("startup", _async_collector(collect_launch_items), {}, 15),
        CollectorSpec("login_items", _async_collector(collect_login_items), [], 15),
        CollectorSpec("package_managers", _async_collector(collect_package_managers), {}, 60),
        CollectorSpec("developer_tools", collect_dev_tools, {}, 60),
        CollectorSpec(
            "kext_info",
            _async_collector(collect_kexts),
            {"third_party_kexts": [], "system_extensions": []},
            30,
        ),
        CollectorSpec("applications", _async_collector(collect_electron_apps), {}, 60),
        CollectorSpec("environment", _async_collector(collect_environment_info), {}, 60),
        CollectorSpec(
            "network",
            lambda: asyncio.to_thread(
                collect_network_info, include_sensitive=include_sensitive_network
            ),
            {},
            30,
        ),
        CollectorSpec("battery", _async_collector(collect_battery_info), {}, 30),
        CollectorSpec("cron", _async_collector(collect_cron_jobs), {}, 15),
        CollectorSpec("diagnostics", _async_collector(collect_diagnostics), {}, 30),
        CollectorSpec("security", _async_collector(collect_security_tools), {}, 30),
        CollectorSpec("cloud", _async_collector(collect_cloud_sync), {}, 30),
        CollectorSpec("nvram", _async_collector(collect_nvram_variables), {}, 30),
        CollectorSpec("storage_analysis", _async_collector(collect_storage_analysis), {}, 120),
        CollectorSpec("fonts", _async_collector(collect_fonts), {}, 30),
        CollectorSpec("shell_customization", _async_collector(collect_shell_customization), {}, 15),
        CollectorSpec("system_preferences", _async_collector(collect_system_preferences), {}, 30),
        CollectorSpec("kernel_params", _async_collector(collect_kernel_parameters), {}, 30),
        CollectorSpec("system_logs", _async_collector(collect_system_logs), {}, 60),
        CollectorSpec(
            "ioregistry",
            _async_collector(collect_ioregistry_info),
            {
                "pcie_devices": [],
                "usb_devices": [],
                "audio_codecs": [],
                "wifi": {"present": None, "components": []},
                "bluetooth": {"present": None, "controllers": []},
                "t1": {"present": None, "components": []},
                "usb_1_1": {"present": None, "controllers": []},
                "camera": {"present": None, "components": []},
            },
            60,
        ),
    )


async def collect_all(*, include_sensitive_network: bool = False) -> SystemReport:
    """Execute all independent collectors and compile a complete system report."""
    timestamp = time.time()
    registry = _build_collector_registry(include_sensitive_network=include_sensitive_network)

    async def run_collector(spec: CollectorSpec) -> tuple[object, float]:
        started = time.perf_counter()
        try:
            result = await asyncio.wait_for(spec.run(), timeout=spec.timeout_seconds)
        except asyncio.TimeoutError as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            raise CollectorTimeoutError(
                f"collector exceeded {spec.timeout_seconds:g}s timeout",
                duration_ms,
            ) from exc
        return result, (time.perf_counter() - started) * 1000

    results = await asyncio.gather(
        *(run_collector(spec) for spec in registry),
        return_exceptions=True,
    )

    collection_errors: list[str] = []
    collection_status: dict[str, CollectionStatus] = {}
    collected: dict[str, object] = {}

    for spec, result in zip(registry, results):
        if isinstance(result, BaseException):
            error_message = f"{type(result).__name__}: {result!s}"
            status = "timeout" if isinstance(result, TimeoutError) else "error"
            collection_errors.append(f"{spec.name}: {error_message}")
            collection_status[spec.name] = {
                "status": status,
                "error": error_message,
                "duration_ms": round(result.duration_ms, 3)
                if isinstance(result, CollectorTimeoutError)
                else None,
                "timeout_seconds": spec.timeout_seconds,
            }
            utils.verbose_log(f"Collector failed: {spec.name}: {error_message}")
            collected[spec.name] = spec.default
        else:
            value, duration_ms = result
            collection_status[spec.name] = {
                "status": "ok",
                "error": None,
                "duration_ms": round(duration_ms, 3),
                "timeout_seconds": spec.timeout_seconds,
            }
            collected[spec.name] = value

    # The registry above guarantees these keys exist; casts document each report field.
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

    # Collect opencore_patcher with dependency on kext_info
    # This must run after kexts are collected
    # kext_info is guaranteed to be a dict (KernelExtensionsInfo) after exception handling
    opencore_started = time.perf_counter()
    opencore_timeout = 60.0
    try:
        third_party_kexts = kext_info.get("third_party_kexts", [])
        opencore_patcher = await asyncio.wait_for(
            asyncio.to_thread(
                collect_opencore_patcher,
                third_party_kexts,
            ),
            timeout=opencore_timeout,
        )
    except asyncio.TimeoutError:
        duration_ms = (time.perf_counter() - opencore_started) * 1000
        error_message = f"TimeoutError: collector exceeded {opencore_timeout:g}s timeout"
        collection_errors.append(f"opencore_patcher: {error_message}")
        collection_status["opencore_patcher"] = {
            "status": "timeout",
            "error": error_message,
            "duration_ms": round(duration_ms, 3),
            "timeout_seconds": opencore_timeout,
        }
        utils.verbose_log(f"Collector failed: opencore_patcher: {error_message}")
        opencore_patcher = OpenCorePatcherInfo(
            detected=False,
            detection_confidence="none",
            detection_signals=[],
            version=None,
            nvram_version=None,
            opencore_version=None,
            unsupported_os_detected=False,
            root_patch_marker_detected=False,
            loaded_kexts=[],
            patched_frameworks=[],
            amfi_configuration=None,
            boot_args=None,
        )
    except Exception as e:
        duration_ms = (time.perf_counter() - opencore_started) * 1000
        error_msg = f"opencore_patcher: {type(e).__name__} - {e!s}"
        collection_errors.append(error_msg)
        collection_status["opencore_patcher"] = {
            "status": "error",
            "error": f"{type(e).__name__}: {e!s}",
            "duration_ms": round(duration_ms, 3),
            "timeout_seconds": opencore_timeout,
        }
        utils.verbose_log(f"Collector failed: {error_msg}")
        opencore_patcher = OpenCorePatcherInfo(
            detected=False,
            detection_confidence="none",
            detection_signals=[],
            version=None,
            nvram_version=None,
            opencore_version=None,
            unsupported_os_detected=False,
            root_patch_marker_detected=False,
            loaded_kexts=[],
            patched_frameworks=[],
            amfi_configuration=None,
            boot_args=None,
        )
    else:
        duration_ms = (time.perf_counter() - opencore_started) * 1000
        collection_status["opencore_patcher"] = {
            "status": "ok",
            "error": None,
            "duration_ms": round(duration_ms, 3),
            "timeout_seconds": opencore_timeout,
        }

    system_identifier = str(system_info.get("model_identifier", ""))
    smbios_data = SMBIOS_DATABASE.get(system_identifier)
    raw_gpu_models = hardware_info.get("gpu", [])
    gpu_models = (
        [str(model) for model in raw_gpu_models] if isinstance(raw_gpu_models, list) else []
    )
    oclp_model_supported = bool(smbios_data) and system_info.get("architecture") == "x86_64"
    oclp_compatibility = build_oclp_compatibility(
        model_identifier=system_identifier,
        architecture=str(system_info.get("architecture", "")),
        current_macos_version=str(system_info.get("macos_version", "")),
        gpu_models=gpu_models,
        max_os_supported=smbios_data.get("max_os_supported") if smbios_data else None,
        oclp_model_supported=oclp_model_supported,
        root_patch_marker_detected=bool(opencore_patcher.get("root_patch_marker_detected", False)),
        root_patch_evidence=bool(opencore_patcher.get("patched_frameworks", [])),
        hardware_evidence={
            "wifi": ioregistry["wifi"]["present"],
            "bluetooth": ioregistry["bluetooth"]["present"],
            "t1": ioregistry["t1"]["present"],
            "usb": ioregistry["usb_1_1"]["present"],
            "camera": ioregistry["camera"]["present"],
        },
    )

    # mypy cannot infer types from asyncio.gather with return_exceptions=True
    # All results are runtime-validated above and guaranteed to be correct types
    # The type:ignore comments document this limitation rather than hide bugs
    return {
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


def generate_ai_prompt(data: SystemReport) -> str:
    """Generate a system prompt for AI analysis.

    Creates an AI-ready prompt with role definition, context about the system
    (including OpenCore Patcher detection for context-aware recommendations),
    and the complete JSON data for analysis.

    Args:
        data: The complete system report.

    Returns:
        System prompt formatted for AI consumption.
    """
    oclp = data["opencore_patcher"]
    is_oclp_user = oclp["detected"]

    # OpenCore context
    compatibility = data["oclp_compatibility"]
    oclp_context = ""
    hardware_patch_requirements_json = json.dumps(
        compatibility.get("hardware_patch_requirements", {}), sort_keys=True
    )

    if is_oclp_user:
        kexts_str = (
            ", ".join(str(kext) for kext in oclp["loaded_kexts"][:3])
            if oclp["loaded_kexts"]
            else "None"
        )
        amfi_str = (
            oclp["amfi_configuration"]["amfi_value"] if oclp["amfi_configuration"] else "Unknown"
        )
        oclp_context = f"""
## OpenCore Legacy Patcher Detected

This system shows **OpenCore Legacy Patcher signals**.

Detected OCLP version: **{oclp["version"] or "Unknown"}**.
Use documented compatibility data; OCLP does not imply support for every newer macOS version.

**OCLP Configuration:**
- OCLP NVRAM Version: {oclp["nvram_version"] or "Unknown"}
- OpenCore Version: {oclp["opencore_version"] or "Unknown"}
- Detection confidence: {oclp["detection_confidence"]}
- Detection signals: {", ".join(oclp["detection_signals"]) or "None"}
- Root-patch marker observed: {"Yes" if oclp["root_patch_marker_detected"] else "No"}
- Unsupported OS: {"✓ Yes" if oclp["unsupported_os_detected"] else "✗ No"}
- AMFI Config: {amfi_str}
- Boot Args: {oclp["boot_args"] or "None"}
- Loaded Kexts: {len(oclp["loaded_kexts"])} installed ({kexts_str})
- Patched Frameworks: {len(oclp["patched_frameworks"])} detected
- Apple-native compatibility: {compatibility.get("apple_native_supported", "Unknown")}
- OCLP documented OS compatibility: {compatibility.get("oclp_os_supported", "Unknown")}
- Root patch required: {compatibility.get("root_patch_required", "Unknown")}
- Root patch observed: {compatibility.get("root_patch_state", "Unknown")}
- Root patch domains: {", ".join(compatibility.get("root_patch_domains", [])) or "None"}
- Required support packages: {", ".join(compatibility.get("required_packages", [])) or "None"}
- Hardware evidence: {json.dumps(compatibility.get("hardware_evidence", {}), sort_keys=True)}
- Hardware patch requirements: {hardware_patch_requirements_json}

**IMPORTANT - OCLP-Specific Recommendations:**
- Do not assume SIP must be fully disabled; OCLP SIP requirements depend on the \
macOS version, model, and whether root patches are required.
- Do not recommend removing OCLP-managed kexts or patches merely because they are third-party.
- Distinguish OpenCore bootloader detection from OCLP root-patch state before \
making remediation advice.
- Consider hardware limitations of unsupported Mac models
- Wi-Fi/Bluetooth patches may be present and necessary
- Graphics acceleration patches are critical for performance
- Some system updates may break patches - advise caution with OS updates
"""
    else:
        oclp_context = """
## Standard macOS Configuration

This system is running standard macOS without OpenCore Legacy Patcher.
Standard security recommendations apply (SIP enabled, signed kexts only, etc.).
"""

    # Generate prompt
    sys_admin_role = (
        "You are an expert macOS system administrator and performance analyst. "
        "Your task is to analyze the provided system data and provide actionable insights."
    )

    timestamp = datetime.fromtimestamp(data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    # Collection errors section
    errors_section = ""
    if data.get("collection_errors"):
        errors_list = "\n".join(f"- {err}" for err in data["collection_errors"])
        errors_section = f"""
## ⚠️ Collection Warnings

Some data collectors encountered errors during execution:

{errors_list}

**Note:** These errors may result in incomplete data in certain sections.
The analysis should account for missing information.

---
"""

    prompt = f"""# macOS System Analysis Assistant
Generated: {timestamp}

{sys_admin_role}

{oclp_context}

{errors_section}

---

## 1. Analysis Logic & Instructions

### Core Tasks
1. **Security Posture**: SIP, FileVault, Gatekeeper, Firewall, unsigned apps, TCC.
2. **Performance**: Memory pressure, swap, disk usage, CPU load, bottlenecks.
3. **Dev Environment**: Languages, tools, package managers, git, shell.
4. **Health Check**: Battery, SMART status, logs, kexts, daemons.
5. **Optimization**: Cleanup, tuning, hardening, backups.

### Operating Rules
1. **Be Concise**: Focus on actionable insights, not data regurgitation.
2. **Prioritize**: Critical issues first, then important, then optional.
3. **Context-Aware**: {
        "OCLP SYSTEM DETECTED - Adjust for unsupported hardware/patches."
        if is_oclp_user
        else "Standard macOS system."
    }
4. **Specific**: Provide exact commands or steps where applicable.
5. **Realistic**: Consider the hardware constraints (especially for OCLP users on older Macs).

---

## 2. System Data (JSON)

The following JSON object contains the complete system state snapshot.

```json
{json.dumps(data, indent=2)}
```

---

**End of System Report**
"""

    return prompt.strip()


async def async_main() -> int:
    """Async main entry point for the CLI application.

    Parses command-line arguments, executes data collection,
    and saves reports to disk.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from prose import __version__

    parser = argparse.ArgumentParser(description="macOS System Prose Collector")
    parser.add_argument(
        "--version",
        action="version",
        version=f"macos-system-prose {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all console output",
    )
    parser.add_argument(
        "--include-sensitive-network",
        action="store_true",
        help="Opt in to collecting network identity data and public IP (default: redacted)",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip generating AI-optimized text prompt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="macos_system_report.json",
        help="Output JSON file path (default: %(default)s)",
    )
    parser.add_argument(
        "--diff",
        help="Compare current report with a previous JSON report",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch interactive terminal UI",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live refresh mode in TUI",
    )
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=30,
        help="Refresh interval in seconds for live TUI mode (default: %(default)s)",
    )
    args = parser.parse_args()

    utils.VERBOSE = args.verbose
    utils.QUIET = args.quiet

    if sys.platform != "darwin":
        utils.log("This tool only supports macOS.", "error")
        return 1

    # TUI mode: launch interactive terminal interface
    if args.tui:
        try:
            from prose.tui.app_enhanced import run_tui_enhanced
        except ImportError:
            utils.log(
                "TUI mode requires textual. Install with: pip install -e '.[tui]'",
                "error",
            )
            return 1

        utils.log("🚀 Launching Enhanced Terminal UI...", "header")
        if args.live:
            utils.log(f"Live mode enabled (refresh every {args.refresh_interval}s)", "info")
        utils.log("Collecting system data...", "info")
        report = await collect_all()
        utils.log("✓ Data collected. Starting TUI...", "success")

        try:
            # Use async version since we're already in an async context
            await run_tui_enhanced(
                report, live_mode=args.live, refresh_interval=args.refresh_interval
            )
            return 0
        except Exception as e:
            utils.log(f"TUI failed: {e}", "error")
            return 1

    utils.log(" Starting macOS System Prose Report Collection...", "header")
    report = await collect_all(include_sensitive_network=args.include_sensitive_network)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        utils.log(f"Report saved to: {os.path.abspath(args.output)}", "success")
    except Exception as e:
        utils.log(f"Failed to save report: {e}", "error")
        return 1

    if not args.no_prompt:
        prompt_file = Path(args.output).with_suffix(".txt")
        try:
            prompt_content = generate_ai_prompt(report)
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt_content)
            utils.log(f"AI Prompt saved to: {os.path.abspath(prompt_file)}", "success")
        except Exception as e:
            utils.log(f"Failed to save AI prompt: {e}", "error")

    if args.diff:
        diff_path = Path(args.diff)
        if diff_path.exists():
            try:
                with open(diff_path, encoding="utf-8") as f:
                    old_data = json.load(f)

                utils.log(f"Comparing with: {args.diff}", "header")
                changes = diff_reports(old_data, report)
                if changes:
                    diff_lines = format_diff(changes)
                    for line in diff_lines:
                        utils.log(line, "info")
                else:
                    utils.log("No differences found.", "success")
            except Exception as e:
                utils.log(f"Failed to compare reports: {e}", "error")
        else:
            utils.log(f"Diff target not found: {args.diff}", "error")

    utils.log("Collection complete.", "success")
    return 0


def main() -> int:
    """Synchronous wrapper for the async main entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    return asyncio.run(async_main())


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        utils.log("\nInterrupted by user. Exiting...", "warning")
        sys.exit(130)
