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


def _analyze_security_posture(data: SystemReport) -> list[str]:
    """Extract security issues and recommendations."""
    issues = []

    # Critical security checks
    if not data["system"]["sip_enabled"]:
        issues.append("🔴 CRITICAL: System Integrity Protection (SIP) is DISABLED")
    if not data["system"]["filevault_enabled"]:
        issues.append("🟡 WARNING: FileVault disk encryption is DISABLED")
    if not data["system"]["gatekeeper_enabled"]:
        issues.append("🟡 WARNING: Gatekeeper is DISABLED (apps from anywhere can run)")

    # Firewall status
    if data["network"]["firewall_status"].lower() != "on":
        issues.append("🟡 WARNING: Firewall is disabled")

    # Code signing issues
    if data["security"]["code_signing_sample"]:
        invalid_apps = [
            app["app_name"] for app in data["security"]["code_signing_sample"] if not app["valid"]
        ]
        if invalid_apps:
            issues.append(
                f"🟡 WARNING: {len(invalid_apps)} apps have invalid signatures: "
                f"{', '.join(invalid_apps[:3])}"
            )

    return issues if issues else ["🟢 Security posture is good"]


def _analyze_performance(data: SystemReport) -> list[str]:
    """Extract performance concerns."""
    concerns = []

    # Memory pressure
    mp = data["hardware"]["memory_pressure"]
    if mp["level"] == "critical":
        concerns.append(
            f"🔴 CRITICAL: Memory pressure is CRITICAL "
            f"(Swap: {mp['swap_used']}MB, Free: {mp['pages_free']} pages)"
        )
    elif mp["level"] == "warn":
        concerns.append(
            f"🟡 WARNING: Memory pressure is elevated "
            f"(Swap: {mp['swap_used']}MB, Free: {mp['pages_free']} pages)"
        )

    # Disk space
    disk = data["disk"]
    if "disk_free_gb" in disk and "disk_total_gb" in disk:
        try:
            free_gb = disk["disk_free_gb"]
            total_gb = disk["disk_total_gb"]
            if total_gb > 0:
                usage_pct = ((total_gb - free_gb) / total_gb) * 100
                if usage_pct > 90:
                    concerns.append(
                        f"🔴 CRITICAL: Disk is {usage_pct:.0f}% full ({free_gb:.1f}GB free)"
                    )
                elif usage_pct > 80:
                    concerns.append(f"🟡 WARNING: Disk is {usage_pct:.0f}% full")
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    # Top CPU processes
    high_cpu = [p for p in data["top_processes"] if p["cpu_percent"] > 50]
    if high_cpu:
        concerns.append(
            f"🟡 {len(high_cpu)} processes using >50% CPU: "
            f"{', '.join(p['command'][:30] for p in high_cpu[:3])}"
        )

    return concerns if concerns else ["🟢 Performance is healthy"]


def _analyze_developer_environment(data: SystemReport) -> list[str]:
    """Extract developer environment insights."""
    insights = []
    dev = data["developer_tools"]

    # PATH duplicates
    if data["environment"]["path_duplicates"]:
        dupes = len(data["environment"]["path_duplicates"])
        insights.append(f"🟡 {dupes} duplicate PATH entries detected")

    # Docker status
    if dev["docker"]["installed"] and not dev["docker"]["running"]:
        insights.append("ℹ️ Docker is installed but not running")
    elif dev["docker"]["running"]:
        insights.append(
            f"🟢 Docker: {dev['docker']['containers_running']}/{dev['docker']['containers_total']} "
            f"containers running, {dev['docker']['images_count']} images"
        )

    # Git config
    git = dev["git_config"]
    if not git["user_name"] or not git["user_email"]:
        insights.append("🟡 Git user.name or user.email not configured")

    # Homebrew services
    brew_services = data["package_managers"].get("homebrew_services", [])
    running_services = [s for s in brew_services if s["status"] == "started"]
    if running_services:
        insights.append(
            f"ℹ️ {len(running_services)} Homebrew services running: "
            f"{', '.join(s['name'] for s in running_services[:5])}"
        )

    # Multiple package managers
    pkg_mgrs = []
    for mgr in ["homebrew", "macports", "npm", "yarn", "pnpm", "bun", "pipx"]:
        pkg = data["package_managers"].get(mgr, {})
        if isinstance(pkg, dict) and pkg.get("installed"):
            pkg_mgrs.append(mgr)
    if len(pkg_mgrs) > 4:
        insights.append(f"ℹ️ {len(pkg_mgrs)} package managers installed: {', '.join(pkg_mgrs)}")

    return insights if insights else ["ℹ️ Developer environment looks clean"]


def _format_system_overview(data: SystemReport) -> str:
    """Create Apple-style system overview section."""
    sys = data["system"]
    hw = data["hardware"]

    # Format memory
    mem_gb = hw.get("memory_gb", 0)
    mem_str = f"{mem_gb}GB" if mem_gb else "Unknown"

    return f"""
## System Overview

**Model**: {sys["model_name"]} ({sys["model_identifier"]})
**macOS**: {sys["macos_name"]} {sys["macos_version"]}
**Processor**: {hw["cpu"]}
**Memory**: {mem_str}
**Architecture**: {sys["architecture"]}
**Uptime**: {sys["uptime"]}
""".strip()


def _format_key_statistics(data: SystemReport) -> str:
    """Format key statistics in Apple-style."""
    stats = []

    # Applications
    all_apps = data["applications"]["all_apps"]
    electron_apps = data["applications"]["electron_apps"]
    stats.append(f"**Applications**: {len(all_apps)} installed ({len(electron_apps)} Electron)")

    # Developer tools
    dev = data["developer_tools"]
    langs = len([v for v in dev["languages"].values() if v != "Not Found"])
    stats.append(f"**Languages**: {langs} configured")

    # Services
    launchd = len(data["environment"]["launchd_services"])
    stats.append(f"**Services**: {launchd} launchd services")

    # Network
    ports = len(data["environment"]["listening_ports"])
    stats.append(f"**Network**: {ports} listening ports")

    return "\n".join(stats)


def generate_ai_prompt(data: SystemReport) -> str:
    """Generate an optimized AI analysis prompt.

    Creates a clean, focused prompt highlighting key insights and security issues
    instead of dumping raw JSON data.

    Args:
        data: The complete system report.

    Returns:
        Formatted prompt with actionable insights.
    """
    security_issues = _analyze_security_posture(data)
    performance_concerns = _analyze_performance(data)
    dev_insights = _analyze_developer_environment(data)

    return f"""
# macOS System Analysis

{_format_system_overview(data)}

---

## 🎯 Key Statistics

{_format_key_statistics(data)}

---

## 🔒 Security Analysis

{chr(10).join(security_issues)}

**Recommendations:**
• Enable FileVault disk encryption if not active
• Keep System Integrity Protection (SIP) enabled
• Enable macOS Firewall for network protection
• Verify all installed applications are from trusted sources

---

## ⚡️ Performance Analysis

{chr(10).join(performance_concerns)}

**Recommendations:**
• Monitor memory pressure - close unused applications if elevated
• Keep disk usage below 80% for optimal performance
• Investigate high CPU processes if system feels slow
• Consider upgrading RAM if memory pressure is frequently critical

---

## 💻 Developer Environment

{chr(10).join(dev_insights)}

**Environment Details:**
• **Package Managers**: {", ".join(
    k for k, v in data["package_managers"].items()
    if k != "homebrew_services" and isinstance(v, dict) and v.get("installed")
)}
• **Shell**: {data["environment"]["shell"]}
• **Terminal**: {", ".join(data["developer_tools"]["terminal_emulators"])
    if data["developer_tools"]["terminal_emulators"] else "Default Terminal"}
• **Shell Framework**: {", ".join(data["developer_tools"]["shell_frameworks"].keys())
    if data["developer_tools"]["shell_frameworks"] else "None"}
• **Git User**: {data["developer_tools"]["git_config"]["user_name"] or "Not configured"}

---

## ☁️ Cloud & Backup

**iCloud Drive**: {"✓ Enabled" if data["cloud"]["sync_status"]["icloud_enabled"] else "✗ Disabled"}
**Time Machine**: {"✓ Enabled" if data["system"]["time_machine"]["enabled"] else "✗ Disabled"}
**Last Backup**: {data["system"]["time_machine"]["last_backup"] or "Never"}

**Recommendations:**
• Enable Time Machine for automatic backups
• Verify iCloud Drive sync if using cloud storage
• Keep at least one local backup of important data

---

## 📊 Detailed Report

For complete system details, refer to the JSON report file.

**Key Sections Available:**
• Hardware specifications and displays
• Network configuration and VPN status
• All installed applications with versions
• Launch agents and background services
• Kernel extensions and system extensions
• Battery health and power management
• Developer tools and IDE extensions
• Security tools and antivirus software

---

## 🎯 Recommended Actions

**Critical** (Do immediately):
{chr(10).join(
    "• " + issue.replace("🔴 CRITICAL: ", "")
    for issue in security_issues + performance_concerns if "🔴" in issue
) or "• None - system is healthy"}

**Important** (Do soon):
{chr(10).join(
    "• " + issue.replace("🟡 WARNING: ", "")
    for issue in security_issues + performance_concerns + dev_insights if "🟡" in issue
) or "• None - no warnings"}

**Optional** (Consider):
{chr(10).join(
    "• " + issue.replace("ℹ️ ", "") for issue in dev_insights if "ℹ️" in issue
) or "• Review developer environment for optimization opportunities"}

---

**Report Generated**: {data["timestamp"]}
**macOS Version**: {data["system"]["macos_version"]}
**Tool Version**: 1.1.0
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
