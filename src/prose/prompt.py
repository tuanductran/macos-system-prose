"""AI prompt generation for macOS System Prose reports.

The prose wording of the generated prompt (role definition, section
headings, operating rules, OCLP guidance, etc.) lives in editable Markdown
files under ``templates/`` at the repo root -- the same convention already
used by ``prose.oclp`` for its knowledge base in ``data/``. This file only
holds the *logic* that decides which values go into those templates; editing
the wording no longer requires touching Python at all.

Templates use the standard-library ``string.Template`` ``$identifier``
syntax (stdlib-only, no extra runtime dependency -- this project ships with
zero runtime dependencies by design; see AGENTS.md). ``safe_substitute`` is
used throughout so that a stray ``$`` inside collected system data (e.g. a
boot arg or path) can never raise instead of just being left as-is.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import cache
from pathlib import Path
from string import Template

from prose.schema import SystemReport


_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@cache
def _load_template(name: str) -> Template:
    """Load and cache a Markdown prompt template by file name."""
    return Template((_TEMPLATES_DIR / name).read_text(encoding="utf-8"))


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
        oclp_context = _load_template("oclp_detected.md").safe_substitute(
            oclp_version=oclp["version"] or "Unknown",
            oclp_nvram_version=oclp["nvram_version"] or "Unknown",
            opencore_version=oclp["opencore_version"] or "Unknown",
            detection_confidence=oclp["detection_confidence"],
            detection_signals=", ".join(oclp["detection_signals"]) or "None",
            root_patch_marker="Yes" if oclp["root_patch_marker_detected"] else "No",
            unsupported_os="✓ Yes" if oclp["unsupported_os_detected"] else "✗ No",
            amfi_value=amfi_str,
            boot_args=oclp["boot_args"] or "None",
            kexts_count=len(oclp["loaded_kexts"]),
            kexts_str=kexts_str,
            frameworks_count=len(oclp["patched_frameworks"]),
            apple_native_supported=compatibility.get("apple_native_supported", "Unknown"),
            oclp_os_supported=compatibility.get("oclp_os_supported", "Unknown"),
            root_patch_required=compatibility.get("root_patch_required", "Unknown"),
            root_patch_state=compatibility.get("root_patch_state", "Unknown"),
            root_patch_domains=", ".join(compatibility.get("root_patch_domains", [])) or "None",
            required_packages=", ".join(compatibility.get("required_packages", [])) or "None",
            hardware_evidence_json=json.dumps(
                compatibility.get("hardware_evidence", {}), sort_keys=True
            ),
            hardware_patch_requirements_json=hardware_patch_requirements_json,
        )
    else:
        oclp_context = _load_template("oclp_standard.md").safe_substitute()

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
        errors_section = _load_template("collection_warnings.md").safe_substitute(
            errors_list=errors_list
        )

    context_aware_note = (
        "OCLP SYSTEM DETECTED - Adjust for unsupported hardware/patches."
        if is_oclp_user
        else "Standard macOS system."
    )

    prompt = _load_template("main_prompt.md").safe_substitute(
        timestamp=timestamp,
        sys_admin_role=sys_admin_role,
        oclp_context=oclp_context,
        errors_section=errors_section,
        context_aware_note=context_aware_note,
        json_data=json.dumps(data, indent=2),
    )

    return prompt.strip()
