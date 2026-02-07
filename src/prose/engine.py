"""Main orchestration engine for macOS System Prose.

This module coordinates all data collection activities and generates
the final system report in both JSON and AI-optimized text formats.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from prose import utils
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
    collect_processes,
    collect_security_tools,
)
from prose.collectors.network import collect_network_info
from prose.collectors.packages import collect_package_managers
from prose.collectors.system import collect_disk_info, collect_hardware_info, collect_system_info
from prose.schema import SystemReport


def collect_all() -> SystemReport:
    """Execute all data collectors and compile a complete system report.

    This function orchestrates all data collection activities across
    system, hardware, network, packages, and developer tools.

    Returns:
        A complete SystemReport dictionary with all collected data.

    Raises:
        CollectorError: If any critical collector fails (non-critical failures
                       are logged but don't stop execution).
    """
    return {
        "timestamp": time.time(),
        "system": collect_system_info(),
        "hardware": collect_hardware_info(),
        "disk": collect_disk_info(),
        "top_processes": collect_processes(),
        "startup": collect_launch_items(),
        "login_items": collect_login_items(),
        "package_managers": collect_package_managers(),
        "developer_tools": collect_dev_tools(),
        "kexts": collect_kexts(),
        "applications": collect_electron_apps(),
        "environment": collect_environment_info(),
        "network": collect_network_info(),
        "battery": collect_battery_info(),
        "cron": collect_cron_jobs(),
        "diagnostics": collect_diagnostics(),
        "security": collect_security_tools(),
        "cloud": collect_cloud_sync(),
    }


def generate_ai_prompt(data: SystemReport) -> str:
    """Generate an AI-optimized prompt from the system report.

    Creates a structured prompt designed for LLM consumption, including
    context about the user's goals and the complete system report.

    Args:
        data: The complete system report.

    Returns:
        Formatted prompt string suitable for AI analysis.
    """
    return f"""
# macOS System Optimization & Analysis Report

You are an expert macOS Systems Engineer with specialization in performance tuning,
developer environment optimization, and system security.

Below is a comprehensive system report in JSON format. Your task is to:
1. Identify potential performance bottlenecks (CPU/Memory/Disk).
2. Spot redundant or conflicting developer tool installations
   (Multiple package managers/PATH duplicates).
3. Recommend security hardening based on SIP/Gatekeeper/FileVault status.
4. Propose cleanup for non-existent but referenced launch agents/daemons.
5. List specific commands to execute the proposed optimizations safely.

---
SYSTEM REPORT:
{json.dumps(data, indent=2)}
""".strip()


def main() -> int:
    """Main entry point for the CLI application.

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
    args = parser.parse_args()

    utils.VERBOSE = args.verbose
    utils.QUIET = args.quiet

    if sys.platform != "darwin":
        utils.log("This tool only supports macOS.", "error")
        return 1

    utils.log(" Starting macOS System Prose Report Collection...", "header")
    report = collect_all()

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

    utils.log("Collection complete.", "success")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        sys.exit(130)
