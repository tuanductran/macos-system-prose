"""OCLP compatibility knowledge and report enrichment.

Knowledge in this module is intentionally small and source-backed. It distinguishes
Apple-native compatibility from the documented OCLP target range and does not infer
that root patches are installed merely because OCLP is detected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast


class OCLPCompatibilityInfo(TypedDict):
    apple_native_supported: bool | None
    oclp_model_supported: bool
    oclp_os_supported: bool
    oclp_target_os_min: int
    oclp_target_os_max: int
    root_patch_required: bool | None
    root_patch_state: str
    root_patch_domains: list[str]
    required_packages: list[str]
    hardware_evidence: dict[str, bool | None]
    knowledge_schema_version: int
    knowledge_checked_at: str
    hardware_evidence: dict[str, bool | None]
    knowledge_sources: list[str]


def _load_knowledge() -> dict[str, object]:
    path = Path(__file__).resolve().parent.parent.parent / "data" / "oclp_knowledge.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return cast(dict[str, object], json.load(handle))


_KNOWLEDGE = _load_knowledge()
_TARGET_OS = _KNOWLEDGE.get("target_os", {})
_SOURCES = _KNOWLEDGE.get("sources", {})


def _parse_major(version: str) -> int | None:
    try:
        return int(version.split(".", 1)[0])
    except (ValueError, IndexError):
        return None


def _native_supported(max_os_supported: str, current_version: str) -> bool | None:
    current = _parse_major(current_version)
    max_version = _parse_major(max_os_supported)
    if current is None or max_version is None:
        return None
    return current <= max_version


def build_oclp_compatibility(
    *,
    model_identifier: str,
    architecture: str,
    current_macos_version: str,
    gpu_models: list[str],
    max_os_supported: str | None,
    oclp_model_supported: bool,
    root_patch_marker_detected: bool,
    root_patch_evidence: bool,
    hardware_evidence: dict[str, bool | None] | None = None,
) -> OCLPCompatibilityInfo:
    """Build compatibility facts without conflating requirements and observed state."""
    del model_identifier, architecture

    current_major = _parse_major(current_macos_version)
    target_os = cast(dict[str, object], _TARGET_OS) if isinstance(_TARGET_OS, dict) else {}
    target_min_value = target_os.get("minimum_major", 11)
    target_max_value = target_os.get("maximum_major", 15)
    target_min = int(target_min_value) if isinstance(target_min_value, (int, str)) else 11
    target_max = int(target_max_value) if isinstance(target_max_value, (int, str)) else 15

    oclp_os_supported = (
        current_major is not None
        and target_min <= current_major <= target_max
        and oclp_model_supported
    )

    apple_native_supported = (
        _native_supported(max_os_supported, current_macos_version) if max_os_supported else None
    )

    root_patch_state = (
        "detected" if root_patch_marker_detected or root_patch_evidence else "unknown"
    )

    gpu_text = " ".join(gpu_models).lower()
    os_names = {
        11: "big_sur",
        12: "monterey",
        13: "ventura",
        14: "sonoma",
        15: "sequoia",
    }
    gpu_rules = _KNOWLEDGE.get("root_patch", {})
    root_patch = cast(dict[str, object], gpu_rules) if isinstance(gpu_rules, dict) else {}
    requirements_value = root_patch.get("gpu_requirements", {})
    package_rules_value = root_patch.get("package_requirements", {})
    requirements = (
        cast(dict[str, object], requirements_value) if isinstance(requirements_value, dict) else {}
    )
    package_rules = (
        cast(dict[str, object], package_rules_value)
        if isinstance(package_rules_value, dict)
        else {}
    )
    os_key = os_names.get(current_major or 0)
    matches_value = requirements.get(os_key, []) if os_key else []
    matches = cast(list[str], matches_value) if isinstance(matches_value, list) else []
    root_patch_domains = ["graphics"] if any(token in gpu_text for token in matches) else []
    required_packages: list[str] = []
    for package, tokens_value in package_rules.items():
        tokens = cast(list[str], tokens_value) if isinstance(tokens_value, list) else []
        if (
            any(token in gpu_text for token in tokens)
            and (package != "kdk" or (current_major is not None and current_major >= 13))
            and (
                package != "metallib_support_pkg"
                or (current_major is not None and current_major >= 15)
            )
        ):
            required_packages.append(package)
    hardware_facts = hardware_evidence or {}
    for domain in ("wifi", "bluetooth", "t1", "usb", "camera"):
        if hardware_facts.get(domain) is True and domain not in root_patch_domains:
            root_patch_domains.append(domain)

    root_patch_required = bool(root_patch_domains) if oclp_os_supported else None

    source_map = cast(dict[str, object], _SOURCES) if isinstance(_SOURCES, dict) else {}
    source_values = [value for value in source_map.values() if isinstance(value, str)]
    schema_version_value = _KNOWLEDGE.get("schema_version", 1)
    schema_version = (
        int(schema_version_value) if isinstance(schema_version_value, (int, str)) else 1
    )
    checked_at = _KNOWLEDGE.get("checked_at", "")
    return {
        "apple_native_supported": apple_native_supported,
        "oclp_model_supported": oclp_model_supported,
        "oclp_os_supported": oclp_os_supported,
        "oclp_target_os_min": target_min,
        "oclp_target_os_max": target_max,
        "root_patch_required": root_patch_required,
        "root_patch_state": root_patch_state,
        "root_patch_domains": root_patch_domains,
        "required_packages": required_packages,
        "hardware_evidence": {
            key: value for key, value in hardware_facts.items()
            if key in {"wifi", "bluetooth", "t1", "usb", "camera"}
        },
        "knowledge_schema_version": schema_version,
        "knowledge_checked_at": str(checked_at),
        "knowledge_sources": source_values,
    }


__all__ = ["OCLPCompatibilityInfo", "build_oclp_compatibility"]
