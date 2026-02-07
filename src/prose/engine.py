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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, cast

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
from prose.diff import diff_reports, format_diff
from prose.html_report import generate_html_report
from prose.schema import SystemReport


async def collect_all() -> SystemReport:
    """Execute all data collectors concurrently and compile a complete system report.

    This function orchestrates all data collection activities across
    system, hardware, network, packages, and developer tools using asyncio
    for parallel execution. Synchronous collectors are run in thread pools
    to achieve true parallelism.

    Returns:
        A complete SystemReport dictionary with all collected data.

    Raises:
        CollectorError: If any critical collector fails (non-critical failures
                       are logged but don't stop execution).
    """
    # Collect timestamp at the start
    timestamp = time.time()

    # Run all independent collectors concurrently using asyncio.to_thread
    # This runs sync functions in separate threads for parallel execution
    # Using return_exceptions=True to prevent one failure from crashing the entire report
    results = await asyncio.gather(
        asyncio.to_thread(collect_system_info),
        asyncio.to_thread(collect_hardware_info),
        asyncio.to_thread(collect_disk_info),
        asyncio.to_thread(collect_processes),
        asyncio.to_thread(collect_launch_items),
        asyncio.to_thread(collect_login_items),
        asyncio.to_thread(collect_package_managers),
        asyncio.to_thread(collect_dev_tools),
        asyncio.to_thread(collect_kexts),
        asyncio.to_thread(collect_electron_apps),
        asyncio.to_thread(collect_environment_info),
        asyncio.to_thread(collect_network_info),
        asyncio.to_thread(collect_battery_info),
        asyncio.to_thread(collect_cron_jobs),
        asyncio.to_thread(collect_diagnostics),
        asyncio.to_thread(collect_security_tools),
        asyncio.to_thread(collect_cloud_sync),
        asyncio.to_thread(collect_nvram_variables),
        asyncio.to_thread(collect_storage_analysis),
        asyncio.to_thread(collect_fonts),
        asyncio.to_thread(collect_shell_customization),
        asyncio.to_thread(collect_system_preferences),
        asyncio.to_thread(collect_kernel_parameters),
        asyncio.to_thread(collect_system_logs),
        asyncio.to_thread(collect_ioregistry_info),
        return_exceptions=True,
    )

    # Unpack results - if any collector raised an exception, we'll get the exception object
    # We handle exceptions by logging and using default/empty values
    (
        system_info,
        hardware_info,
        disk_info,
        top_processes,
        startup,
        login_items,
        package_managers,
        developer_tools,
        kext_info,
        applications,
        environment,
        network,
        battery,
        cron,
        diagnostics,
        security,
        cloud,
        nvram,
        storage_analysis,
        fonts,
        shell_customization,
        system_preferences,
        kernel_params,
        system_logs,
        ioregistry,
    ) = results

    # Handle any exceptions by providing default values
    if isinstance(kext_info, Exception):
        from prose.schema import KernelExtensionsInfo

        kext_info = KernelExtensionsInfo(third_party_kexts=[], system_extensions=[])
        utils.verbose_log(f"Kexts collection failed: {kext_info}")

    # Collect opencore_patcher with dependency on kext_info
    # This must run after kexts are collected
    opencore_patcher = await asyncio.to_thread(
        collect_opencore_patcher, kext_info["third_party_kexts"]
    )

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
        "system_preferences": system_preferences,
        "kernel_params": kernel_params,
        "system_logs": system_logs,
        "ioregistry": ioregistry,
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
    oclp_context = ""
    if is_oclp_user:
        kexts_str = ", ".join(oclp["loaded_kexts"][:3]) if oclp["loaded_kexts"] else "None"
        amfi_str = (
            oclp["amfi_configuration"]["amfi_value"] if oclp["amfi_configuration"] else "Unknown"
        )
        oclp_context = f"""
## OpenCore Legacy Patcher Detected

This system is running **OpenCore Legacy Patcher v{oclp["version"]}**,
which enables newer macOS versions on unsupported hardware.

**OCLP Configuration:**
- NVRAM Version: {oclp["nvram_version"] or "Unknown"}
- Unsupported OS: {"✓ Yes" if oclp["unsupported_os_detected"] else "✗ No"}
- AMFI Config: {amfi_str}
- Boot Args: {oclp["boot_args"] or "None"}
- Loaded Kexts: {len(oclp["loaded_kexts"])} installed ({kexts_str})
- Patched Frameworks: {len(oclp["patched_frameworks"])} detected

**IMPORTANT - OCLP-Specific Recommendations:**
- DO NOT recommend disabling SIP (required for OCLP root patches)
- DO NOT recommend removing "unsigned" kexts (OCLP patches are intentional)
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

    prompt = f"""# macOS System Analysis Assistant
Generated: {timestamp}

{sys_admin_role}

{oclp_context}

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
    parser = argparse.ArgumentParser(description="macOS System Prose Collector")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--no-prompt", action="store_true")
    parser.add_argument("-o", "--output", default="macos_system_report.json")
    parser.add_argument("--diff", help="Compare current report with a previous JSON report")
    parser.add_argument("--html", action="store_true", help="Generate a beautiful HTML dashboard")
    args = parser.parse_args()

    utils.VERBOSE = args.verbose
    utils.QUIET = args.quiet

    if sys.platform != "darwin":
        utils.log("This tool only supports macOS.", "error")
        return 1

    utils.log(" Starting macOS System Prose Report Collection...", "header")
    report = await collect_all()

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
                with open(diff_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)

                utils.log(f"Comparing with: {args.diff}", "header")
                changes = diff_reports(old_data, cast(Dict[str, Any], report))
                if changes:
                    diff_lines = format_diff(changes)
                    for line in diff_lines:
                        print(line)
                else:
                    utils.log("No differences found.", "success")
            except Exception as e:
                utils.log(f"Failed to compare reports: {e}", "error")
        else:
            utils.log(f"Diff target not found: {args.diff}", "error")

    if args.html:
        html_file = Path(args.output).with_suffix(".html")
        try:
            html_content = generate_html_report(cast(Dict[str, Any], report))
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            utils.log(f"HTML Dashboard saved to: {os.path.abspath(html_file)}", "success")
        except Exception as e:
            utils.log(f"Failed to generate HTML dashboard: {e}", "error")

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
        print("\nInterrupted by user. Exiting...")
        sys.exit(130)
