"""
IOKit and NVRAM access utilities using ctypes (no external dependencies).

This module provides low-level access to macOS IOKit framework and NVRAM
using only Python stdlib (ctypes + subprocess), avoiding pyobjc dependency.
"""

from __future__ import annotations

from prose.schema import AMFIConfig
from prose.utils import run, verbose_log


def read_nvram(variable: str, uuid: str | None = None) -> str | None:
    """
    Read NVRAM variable using nvram command.

    Args:
        variable: NVRAM variable name (e.g., "OCLP-Version")
        uuid: Optional UUID scope (e.g., "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102")

    Returns:
        Variable value as string, or None if not found

    Example:
        >>> read_nvram("OCLP-Version", "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102")
        '2.4.1-RELEASE'
    """
    try:
        # Build variable name with UUID prefix if provided
        var_name = f"{uuid}:{variable}" if uuid else variable

        # Use nvram command to read variable
        output = run(["nvram", var_name], log_errors=False)

        if not output or "not found" in output.lower():
            return None

        # Parse output format: "variable_name	value"
        if "\t" in output:
            parts = output.split("\t", 1)
            if len(parts) == 2:
                value = parts[1].strip()
                verbose_log(f"NVRAM {var_name} = {value}")
                return value

        # Alternative format: "variable_name value" (no tab)
        if " " in output:
            parts = output.split(" ", 1)
            if len(parts) == 2:
                return parts[1].strip()

        return None
    except Exception as e:
        verbose_log(f"Failed to read NVRAM {variable}: {e}")
        return None


def read_nvram_all() -> dict[str, str]:
    """
    Read all NVRAM variables.

    Returns:
        Dictionary of variable name -> value

    Example:
        >>> nvram = read_nvram_all()
        >>> nvram.get("boot-args")
        'debug=0x100'
    """
    try:
        output = run(["nvram", "-p"], log_errors=False)
        nvram_dict = {}

        for line in output.splitlines():
            if "\t" in line:
                var, val = line.split("\t", 1)
                nvram_dict[var.strip()] = val.strip()

        verbose_log(f"Read {len(nvram_dict)} NVRAM variables")
        return nvram_dict
    except (OSError, ValueError) as e:
        verbose_log(f"Failed to read all NVRAM variables: {e}")
        return {}


def get_boot_args() -> str | None:
    """Get boot-args NVRAM variable."""
    return read_nvram("boot-args")


def get_csr_active_config() -> str | None:
    """Get csr-active-config (SIP configuration)."""
    return read_nvram("csr-active-config")


def parse_amfi_boot_arg(boot_args: str | None) -> AMFIConfig:
    """
    Parse AMFI (AppleMobileFileIntegrity) boot argument bitmask.

    AMFI flags:
    - 0x1: ALLOW_TASK_FOR_PID
    - 0x2: ALLOW_INVALID_SIGNATURE
    - 0x4: LV_ENFORCE_THIRD_PARTY

    Args:
        boot_args: Boot arguments string (e.g., "amfi=0x80 debug=0x100")

    Returns:
        Dictionary with AMFI flags and raw value

    Example:
        >>> parse_amfi_boot_arg("amfi=0x80")
        {'amfi_value': '0x80', 'allow_invalid_signature': True, ...}
    """
    result: AMFIConfig = {
        "amfi_value": None,
        "allow_task_for_pid": False,
        "allow_invalid_signature": False,
        "lv_enforce_third_party": False,
    }

    if not boot_args or "amfi=" not in boot_args:
        return result

    # Extract amfi value (e.g., "amfi=0x80" -> "0x80")
    for arg in boot_args.split():
        if arg.startswith("amfi="):
            amfi_str = arg.split("=", 1)[1]
            result["amfi_value"] = amfi_str

            try:
                # Parse hex or decimal value
                amfi_int = int(amfi_str, 16 if "0x" in amfi_str else 10)

                # Check bitmask flags
                result["allow_task_for_pid"] = bool(amfi_int & 0x1)
                result["allow_invalid_signature"] = bool(amfi_int & 0x2)
                result["lv_enforce_third_party"] = bool(amfi_int & 0x4)

                verbose_log(f"AMFI configuration: {amfi_str} (flags: {amfi_int:08b})")
            except ValueError:
                pass

            break

    return result


# OCLP NVRAM UUID constants
OCLP_NVRAM_UUID = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"
SECURE_BOOT_UUID = "94B73556-2197-4702-82A8-3E1337DAFBFB"


def get_oclp_nvram_version() -> str | None:
    """Get OCLP-Version from NVRAM (indicates OCLP boot)."""
    return read_nvram("OCLP-Version", OCLP_NVRAM_UUID)


def get_oclp_nvram_settings() -> str | None:
    """Get OCLP-Settings from NVRAM (patch configuration)."""
    return read_nvram("OCLP-Settings", OCLP_NVRAM_UUID)


def get_secure_boot_model() -> str | None:
    """Get SecureBootModel from NVRAM."""
    return read_nvram("HardwareModel", SECURE_BOOT_UUID)


__all__ = [
    "OCLP_NVRAM_UUID",
    "SECURE_BOOT_UUID",
    "get_boot_args",
    "get_csr_active_config",
    "get_oclp_nvram_settings",
    "get_oclp_nvram_version",
    "get_secure_boot_model",
    "parse_amfi_boot_arg",
    "read_nvram",
    "read_nvram_all",
]
