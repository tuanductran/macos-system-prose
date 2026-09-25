"""Tests for final report assembly."""

from __future__ import annotations

from typing import cast

from prose.engine import _build_collector_registry
from prose.oclp import OCLPCompatibilityInfo
from prose.report_builder import build_report
from prose.schema import OpenCorePatcherInfo


def test_build_report_preserves_collected_fields() -> None:
    """Report assembly should map every registered collector to its public field."""
    collected = {
        spec.name: spec.default
        for spec in _build_collector_registry(include_sensitive_network=False)
    }
    opencore_patcher = cast(
        OpenCorePatcherInfo,
        {
            "detected": False,
            "detection_confidence": "none",
            "detection_signals": [],
            "version": None,
            "nvram_version": None,
            "opencore_version": None,
            "unsupported_os_detected": False,
            "root_patch_marker_detected": False,
            "loaded_kexts": [],
            "patched_frameworks": [],
            "amfi_configuration": None,
            "boot_args": None,
        },
    )
    oclp_compatibility = cast(
        OCLPCompatibilityInfo,
        {
            "apple_native_supported": None,
            "oclp_model_supported": False,
            "oclp_os_supported": False,
            "oclp_target_os_min": None,
            "oclp_target_os_max": None,
            "root_patch_required": False,
            "root_patch_state": "unknown",
            "root_patch_domains": [],
            "required_packages": [],
            "hardware_evidence": {},
            "hardware_patch_requirements": {},
            "knowledge_schema_version": 1,
            "knowledge_checked_at": None,
            "knowledge_sources": [],
        },
    )

    report = build_report(
        timestamp=123.0,
        collected=collected,
        collection_errors=["example"],
        collection_status={},
        opencore_patcher=opencore_patcher,
        oclp_compatibility=oclp_compatibility,
    )

    assert report["timestamp"] == 123.0
    assert report["system"] == {}
    assert report["hardware"] == {}
    assert report["kexts"] == {"third_party_kexts": [], "system_extensions": []}
    assert report["opencore_patcher"] == opencore_patcher
    assert report["oclp_compatibility"] == oclp_compatibility
    assert report["collection_errors"] == ["example"]
