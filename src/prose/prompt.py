"""AI prompt generation for macOS System Prose reports."""

from __future__ import annotations

import json
from datetime import datetime

from prose.schema import SystemReport


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

This system does not show the collected OpenCore Legacy Patcher signals.
Do not infer SIP, code-signing, root-patch, or other security state from OCLP non-detection;
Use the collected security and system fields as the evidence source.
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
