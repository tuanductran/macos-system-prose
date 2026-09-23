from __future__ import annotations

from prose.oclp import build_oclp_compatibility


def test_apple_native_and_oclp_compatibility_are_distinct():
    result = build_oclp_compatibility(
        model_identifier="MacBookAir6,2",
        architecture="x86_64",
        current_macos_version="12.7.6",
        gpu_models=["Intel HD Graphics 5000"],
        max_os_supported="11",
        oclp_model_supported=True,
        root_patch_marker_detected=False,
        root_patch_evidence=False,
    )

    assert result["apple_native_supported"] is False
    assert result["oclp_model_supported"] is True
    assert result["oclp_os_supported"] is True
    assert result["root_patch_required"] is False
    assert result["root_patch_state"] == "unknown"
    assert result["hardware_patch_requirements"] == {
        "wifi": None,
        "bluetooth": None,
        "t1": None,
        "usb": None,
        "camera": None,
    }


def test_outside_documented_oclp_range_is_not_supported():
    result = build_oclp_compatibility(
        model_identifier="MacBookAir6,2",
        architecture="x86_64",
        current_macos_version="27.0",
        gpu_models=["Intel HD Graphics 5000"],
        max_os_supported="11",
        oclp_model_supported=True,
        root_patch_marker_detected=True,
        root_patch_evidence=True,
    )

    assert result["apple_native_supported"] is False
    assert result["oclp_os_supported"] is False
    assert result["root_patch_required"] is None
    assert result["root_patch_state"] == "detected"


def test_apple_silicon_model_is_not_marked_as_oclp_supported():
    result = build_oclp_compatibility(
        model_identifier="Mac14,2",
        architecture="arm64",
        current_macos_version="27.0",
        gpu_models=["Apple M1"],
        max_os_supported="27",
        oclp_model_supported=False,
        root_patch_marker_detected=False,
        root_patch_evidence=False,
    )

    assert result["apple_native_supported"] is True
    assert result["oclp_model_supported"] is False
    assert result["oclp_os_supported"] is False


def test_haswell_on_sequoia_requires_graphics_patch_and_metallib():
    result = build_oclp_compatibility(
        model_identifier="MacBookAir6,2",
        architecture="x86_64",
        current_macos_version="15.7",
        gpu_models=["Intel HD Graphics 5000 (Haswell)"],
        max_os_supported="11",
        oclp_model_supported=True,
        root_patch_marker_detected=False,
        root_patch_evidence=False,
    )

    assert result["oclp_os_supported"] is True
    assert result["root_patch_required"] is True
    assert result["root_patch_domains"] == ["graphics"]
    assert "metallib_support_pkg" in result["required_packages"]


def test_usb_11_evidence_maps_to_root_patch_on_ventura_and_newer():
    result = build_oclp_compatibility(
        model_identifier="MacBook5,1",
        architecture="x86_64",
        current_macos_version="13.7.8",
        gpu_models=[],
        max_os_supported="10.15",
        oclp_model_supported=True,
        root_patch_marker_detected=False,
        root_patch_evidence=False,
        hardware_evidence={"usb": True},
    )

    assert result["hardware_patch_requirements"]["usb"] is True
    assert "usb" in result["root_patch_domains"]
    assert result["root_patch_required"] is True


def test_usb_11_unknown_stays_unknown():
    result = build_oclp_compatibility(
        model_identifier="MacBook5,1",
        architecture="x86_64",
        current_macos_version="13.7.8",
        gpu_models=[],
        max_os_supported="10.15",
        oclp_model_supported=True,
        root_patch_marker_detected=False,
        root_patch_evidence=False,
        hardware_evidence={"usb": None},
    )

    assert result["hardware_patch_requirements"]["usb"] is None
    assert "usb" not in result["root_patch_domains"]
    assert result["root_patch_required"] is False
