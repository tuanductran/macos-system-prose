## OpenCore Legacy Patcher Detected

This system shows **OpenCore Legacy Patcher signals**.

Detected OCLP version: **$oclp_version**.
Use documented compatibility data; OCLP does not imply support for every newer macOS version.

**OCLP Configuration:**
- OCLP NVRAM Version: $oclp_nvram_version
- OpenCore Version: $opencore_version
- Detection confidence: $detection_confidence
- Detection signals: $detection_signals
- Root-patch marker observed: $root_patch_marker
- Unsupported OS: $unsupported_os
- AMFI Config: $amfi_value
- Boot Args: $boot_args
- Loaded Kexts: $kexts_count installed ($kexts_str)
- Patched Frameworks: $frameworks_count detected
- Apple-native compatibility: $apple_native_supported
- OCLP documented OS compatibility: $oclp_os_supported
- Root patch required: $root_patch_required
- Root patch observed: $root_patch_state
- Root patch domains: $root_patch_domains
- Required support packages: $required_packages
- Hardware evidence: $hardware_evidence_json
- Hardware patch requirements: $hardware_patch_requirements_json

**IMPORTANT - OCLP-Specific Recommendations:**
- Do not assume SIP must be fully disabled; OCLP SIP requirements depend on the macOS version, model, and whether root patches are required.
- Do not recommend removing OCLP-managed kexts or patches merely because they are third-party.
- Distinguish OpenCore bootloader detection from OCLP root-patch state before making remediation advice.
- Consider hardware limitations of unsupported Mac models
- Wi-Fi/Bluetooth patches may be present and necessary
- Graphics acceleration patches are critical for performance
- Some system updates may break patches - advise caution with OS updates
