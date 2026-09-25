"""Main orchestration engine for macOS System Prose.

This module coordinates all data collection activities and generates
the final system report in both JSON and AI-optimized text formats.
"""

from __future__ import annotations

import asyncio
import sys
import time
from typing import cast

from prose import prompt as _prompt
from prose.collector_runner import (
    CollectorSpec,
    _async_collector,
    run_registered_collectors,
)
from prose import utils
from prose.cli import build_parser
from prose.collectors.advanced import (
    collect_fonts,
    collect_kernel_parameters,
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
from prose.collectors.oclp import collect_opencore_patcher
from prose.collectors.packages import collect_package_managers
from prose.collectors.system import collect_disk_info, collect_hardware_info, collect_system_info
from prose.datasets.smbios import SMBIOS_DATABASE
from prose.oclp import build_oclp_compatibility
from prose.report_builder import build_report
from prose.report_finalization import finalize_report
from prose.schema import (
    CollectionStatus,
    HardwareInfo,
    IORegistryInfo,
    KernelExtensionsInfo,
    OpenCorePatcherInfo,
    SystemInfo,
    SystemReport,
)
from prose.tui_dispatch import run_tui_mode


generate_ai_prompt = _prompt.generate_ai_prompt


def _build_collector_registry(
    *, include_sensitive_network: bool, mode: CollectionMode = "deep"
) -> tuple[CollectorSpec, ...]:
    """Return the single source of truth for independent collectors."""
    registry = (
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
    if mode == "deep":
        return registry
    expensive = {"storage_analysis", "fonts", "system_logs"}
    return tuple(spec for spec in registry if spec.name not in expensive)


async def collect_all(
    *, include_sensitive_network: bool = False, mode: CollectionMode = "deep"
) -> SystemReport:
    """Execute all independent collectors and compile a complete system report."""
    timestamp = time.time()
    registry = _build_collector_registry(
        include_sensitive_network=include_sensitive_network, mode=mode
    )

    async def run_collector(spec: CollectorSpec) -> tuple[object, float]:
        started = time.perf_counter()
        try:
            result = await asyncio.wait_for(spec.run(), timeout=spec.timeout_seconds)
        except TimeoutError as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            raise CollectorTimeoutError(
                f"collector exceeded {spec.timeout_seconds:g}s timeout",
                duration_ms,
            ) from exc
        return result, (time.perf_counter() - started) * 1000

    deep_registry = (
        _build_collector_registry(
            include_sensitive_network=include_sensitive_network,
            mode="deep",
        )
        if mode == "fast"
        else None
    )
    collected, collection_errors, collection_status = await run_registered_collectors(
        registry,
        deep_registry=deep_registry,
    )

    # These four typed views remain local because OCLP enrichment depends on them.
    system_info = cast(SystemInfo, collected["system_info"])
    hardware_info = cast(HardwareInfo, collected["hardware_info"])
    kext_info = cast(KernelExtensionsInfo, collected["kext_info"])
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
    except TimeoutError:
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

    return build_report(
        timestamp=timestamp,
        collected=collected,
        collection_errors=collection_errors,
        collection_status=collection_status,
        opencore_patcher=opencore_patcher,
        oclp_compatibility=oclp_compatibility,
    )


async def async_main() -> int:
    """Async main entry point for the CLI application.

    Parses command-line arguments, executes data collection,
    and saves reports to disk.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from prose import __version__

    args = build_parser(__version__).parse_args()

    utils.VERBOSE = args.verbose
    utils.QUIET = args.quiet

    if sys.platform != "darwin":
        utils.log("This tool only supports macOS.", "error")
        return 1

    if args.tui:
        utils.log("🚀 Launching Enhanced Terminal UI...", "header")
        if args.live:
            utils.log(f"Live mode enabled (refresh every {args.refresh_interval}s)", "info")
        utils.log("Collecting system data...", "info")
        report = await collect_all()
        return await run_tui_mode(
            report,
            live_mode=args.live,
            refresh_interval=args.refresh_interval,
        )

    utils.log(" Starting macOS System Prose Report Collection...", "header")
    report = await collect_all(
        include_sensitive_network=args.include_sensitive_network, mode=args.mode
    )

    return finalize_report(
        report,
        output=args.output,
        no_prompt=args.no_prompt,
        diff=args.diff,
    )


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
