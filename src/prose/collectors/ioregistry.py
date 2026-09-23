"""IORegistry hardware detection using ioreg command.

This module uses the `ioreg` command to extract detailed hardware information
from the macOS I/O Registry, including PCIe devices, USB devices, and audio codecs.
"""

from __future__ import annotations

import plistlib

from prose.constants import Timeouts
from prose.schema import (
    AudioCodec,
    BluetoothEvidence,
    CameraEvidence,
    HardwareComponentEvidence,
    IORegistryInfo,
    PCIeDevice,
    T1Evidence,
    USB11Evidence,
    USBDevice,
    WiFiEvidence,
)
from prose.utils import log, run, verbose_log


def collect_pcie_devices() -> list[PCIeDevice]:
    """Collect PCIe devices from IORegistry.

    Returns:
        List of PCIe device information dictionaries.
    """
    verbose_log("Collecting PCIe devices from IORegistry...")
    devices: list[PCIeDevice] = []

    try:
        # Get PCIe device tree in XML plist format
        output = run(
            ["ioreg", "-l", "-w0", "-r", "-a", "-c", "IOPCIDevice"],
            timeout=Timeouts.FAST,
            log_errors=False,
        )

        if not output:
            return devices

        # Parse XML plist (may return a list or a dict)
        plist_data = plistlib.loads(output.encode("utf-8"))
        if isinstance(plist_data, dict):
            plist_data = [plist_data]
        if not isinstance(plist_data, list):
            return devices

        def extract_pcie_devices(node: dict) -> None:
            if not isinstance(node, dict):
                return

            # Check if this node is a PCIe device
            io_name = node.get("IOName")
            if io_name:
                device: PCIeDevice = {
                    "name": str(io_name),
                    "vendor_id": None,
                    "device_id": None,
                    "class_code": None,
                    "pci_address": None,
                }

                # Extract vendor/device IDs
                if "vendor-id" in node:
                    vendor_data = node["vendor-id"]
                    if isinstance(vendor_data, bytes) and len(vendor_data) >= 2:
                        device["vendor_id"] = f"0x{int.from_bytes(vendor_data[:2], 'little'):04x}"

                if "device-id" in node:
                    device_data = node["device-id"]
                    if isinstance(device_data, bytes) and len(device_data) >= 2:
                        device["device_id"] = f"0x{int.from_bytes(device_data[:2], 'little'):04x}"

                # Extract class code
                if "class-code" in node:
                    class_data = node["class-code"]
                    if isinstance(class_data, bytes) and len(class_data) >= 4:
                        device["class_code"] = f"0x{int.from_bytes(class_data[:4], 'little'):08x}"

                # Extract PCI address (bus:device:function)
                pcidebug = node.get("pcidebug", "")
                if isinstance(pcidebug, str) and ":" in pcidebug:
                    # Parse something like "0:31:3" or similar
                    device["pci_address"] = pcidebug.split()[0] if " " in pcidebug else pcidebug

                # Only add if we have meaningful data
                if device["vendor_id"] or device["device_id"]:
                    devices.append(device)

            # Recurse into children
            if "IORegistryEntryChildren" in node:
                for child in node["IORegistryEntryChildren"]:
                    extract_pcie_devices(child)

        # plist_data is a list, iterate through all root nodes
        for node in plist_data:
            extract_pcie_devices(node)
        verbose_log(f"Found {len(devices)} PCIe devices")

    except Exception as e:
        verbose_log(f"Error collecting PCIe devices: {e}")

    return devices


def collect_usb_devices() -> list[USBDevice]:
    """Collect USB devices from IORegistry.

    Returns:
        List of USB device information dictionaries.
    """
    verbose_log("Collecting USB devices from IORegistry...")
    devices: list[USBDevice] = []

    try:
        # Get USB device tree in XML plist format
        # Use -c IOUSBHostDevice (class-based) instead of -p IOUSB (plane-based)
        # because -p IOUSB -r -a returns empty on some macOS versions
        output = run(
            ["ioreg", "-c", "IOUSBHostDevice", "-r", "-a"],
            timeout=Timeouts.FAST,
            log_errors=False,
        )

        if not output:
            return devices

        # Parse XML plist (may return a list or a dict)
        plist_data = plistlib.loads(output.encode("utf-8"))
        if isinstance(plist_data, dict):
            plist_data = [plist_data]
        if not isinstance(plist_data, list):
            return devices

        def extract_usb_devices(node: dict) -> None:
            if not isinstance(node, dict):
                return

            # Check if this node is a USB device
            usb_product_name = node.get("USB Product Name")
            io_name = node.get("IOName")

            if usb_product_name or (io_name and "USB" in str(io_name)):
                device: USBDevice = {
                    "name": str(usb_product_name or io_name or "Unknown USB Device"),
                    "vendor_id": None,
                    "product_id": None,
                    "location_id": None,
                    "speed": None,
                }

                # Extract vendor/product IDs
                if "idVendor" in node:
                    vendor = node["idVendor"]
                    if isinstance(vendor, int):
                        device["vendor_id"] = f"0x{vendor:04x}"

                if "idProduct" in node:
                    product = node["idProduct"]
                    if isinstance(product, int):
                        device["product_id"] = f"0x{product:04x}"

                # Extract location ID
                if "locationID" in node:
                    location = node["locationID"]
                    if isinstance(location, int):
                        device["location_id"] = f"0x{location:08x}"

                # Extract USB speed
                if "Device Speed" in node:
                    speed = node["Device Speed"]
                    if isinstance(speed, int):
                        # USB speeds: 1.5 Mbps (Low), 12 Mbps (Full), 480 Mbps (High)
                        speed_map = {
                            0: "1.5 Mbps (Low Speed)",
                            1: "12 Mbps (Full Speed)",
                            2: "480 Mbps (High Speed)",
                            3: "5 Gbps (SuperSpeed)",
                            4: "10 Gbps (SuperSpeed+)",
                        }
                        device["speed"] = speed_map.get(speed, f"{speed}")

                # Only add if we have meaningful data (vendor/product IDs)
                if device["vendor_id"] and device["product_id"]:
                    devices.append(device)

            # Recurse into children
            if "IORegistryEntryChildren" in node:
                for child in node["IORegistryEntryChildren"]:
                    extract_usb_devices(child)

        # plist_data is a list, iterate through all root nodes
        for node in plist_data:
            extract_usb_devices(node)
        verbose_log(f"Found {len(devices)} USB devices")

    except Exception as e:
        verbose_log(f"Error collecting USB devices: {e}")

    return devices


def collect_audio_codecs() -> list[AudioCodec]:
    """Collect audio codec information from IORegistry.

    Returns:
        List of audio codec information dictionaries.
    """
    verbose_log("Collecting audio codecs from IORegistry...")
    codecs: list[AudioCodec] = []

    try:
        # Get audio devices from IORegistry
        output = run(
            ["ioreg", "-l", "-w0", "-r", "-a", "-c", "IOHDACodecDevice"],
            timeout=Timeouts.FAST,
            log_errors=False,
        )

        if not output:
            # Try alternative audio device classes
            output = run(
                ["ioreg", "-l", "-w0", "-r", "-a", "-c", "AppleHDACodec"],
                timeout=Timeouts.FAST,
                log_errors=False,
            )

        if not output:
            return codecs

        # Parse XML plist (may return a list or a dict)
        plist_data = plistlib.loads(output.encode("utf-8"))
        if isinstance(plist_data, dict):
            plist_data = [plist_data]
        if not isinstance(plist_data, list):
            return codecs

        # Recursively extract audio codecs
        def extract_audio_codecs(node: dict) -> None:
            if not isinstance(node, dict):
                return

            io_name = node.get("IOName")
            io_class = str(node.get("IOObjectClass", ""))

            # Match on IOObjectClass (IOHDACodecDevice) since IOName is often empty
            is_codec = "HDACodec" in io_class or (
                io_name and ("Codec" in str(io_name) or "Audio" in str(io_name))
            )
            if is_codec and "IOHDACodecVendorID" in node:
                codec: AudioCodec = {
                    "name": str(io_name or io_class or "HDA Codec"),
                    "codec_id": None,
                    "layout_id": None,
                    "vendor": None,
                }

                # Extract codec ID
                if "IOHDACodecVendorID" in node:
                    codec_id = node["IOHDACodecVendorID"]
                    if isinstance(codec_id, int):
                        codec["codec_id"] = f"0x{codec_id:08x}"
                        # Parse vendor from codec ID (upper 16 bits)
                        vendor_id = (codec_id >> 16) & 0xFFFF
                        codec["vendor"] = f"0x{vendor_id:04x}"

                # Extract layout ID
                if "layout-id" in node:
                    layout_data = node["layout-id"]
                    if isinstance(layout_data, bytes) and len(layout_data) >= 4:
                        layout_id = int.from_bytes(layout_data[:4], "little")
                        codec["layout_id"] = layout_id
                    elif isinstance(layout_data, int):
                        codec["layout_id"] = layout_data

                # Alternative layout ID location
                if not codec["layout_id"] and "AppleHDACodecLayoutID" in node:
                    layout = node["AppleHDACodecLayoutID"]
                    if isinstance(layout, int):
                        codec["layout_id"] = layout

                # Only add if we have meaningful data
                if codec["codec_id"] or codec["layout_id"]:
                    codecs.append(codec)

            # Recurse into children
            if "IORegistryEntryChildren" in node:
                for child in node["IORegistryEntryChildren"]:
                    extract_audio_codecs(child)

        # plist_data is a list, iterate through all root nodes
        for node in plist_data:
            extract_audio_codecs(node)
        verbose_log(f"Found {len(codecs)} audio codecs")

    except Exception as e:
        verbose_log(f"Error collecting audio codecs: {e}")

    return codecs


def _component_from_pcie(device: PCIeDevice) -> HardwareComponentEvidence:
    """Normalize a PCIe device as hardware evidence without compatibility rules."""
    return {
        "name": device["name"],
        "vendor_id": device["vendor_id"],
        "device_id": device["device_id"],
        "product_id": None,
        "class_name": device["class_code"],
        "source": "ioreg:IOPCIDevice",
    }


def _component_from_usb(device: USBDevice) -> HardwareComponentEvidence:
    """Normalize a USB device as hardware evidence without compatibility rules."""
    return {
        "name": device["name"],
        "vendor_id": device["vendor_id"],
        "device_id": None,
        "product_id": device["product_id"],
        "class_name": device["speed"],
        "source": "ioreg:IOUSBHostDevice",
    }


def _text(device: HardwareComponentEvidence) -> str:
    return " ".join(
        value.lower() for value in (device["name"], device["class_name"] or "") if value
    )


def _build_hardware_evidence(
    pcie_devices: list[PCIeDevice],
    usb_devices: list[USBDevice],
) -> tuple[WiFiEvidence, BluetoothEvidence, T1Evidence, USB11Evidence, CameraEvidence]:
    """Extract hardware observations; absence of a match remains unknown."""
    pcie = [_component_from_pcie(device) for device in pcie_devices]
    usb = [_component_from_usb(device) for device in usb_devices]
    all_devices = pcie + usb

    wifi = [
        device
        for device in all_devices
        if any(
            token in _text(device)
            for token in ("wifi", "wi-fi", "airport", "bcm943", "atheros", "wireless")
        )
    ]
    bluetooth = [
        device
        for device in usb
        if any(
            token in _text(device) for token in ("bluetooth", "bcm207", "bcm204", "bluetoothhost")
        )
    ]
    t1 = [
        device
        for device in all_devices
        if "t1" in _text(device) or "apple security" in _text(device)
    ]
    usb_11 = [
        device
        for device in pcie
        if any(token in _text(device) for token in ("ohci", "uhci", "usb 1.1"))
    ]
    camera = [
        device
        for device in all_devices
        if any(
            token in _text(device)
            for token in ("isight", "facetime camera", "applecamera", "camera")
        )
    ]

    return (
        {"present": True if wifi else None, "components": wifi},
        {"present": True if bluetooth else None, "controllers": bluetooth},
        {"present": True if t1 else None, "components": t1},
        {"present": True if usb_11 else None, "controllers": usb_11},
        {"present": True if camera else None, "components": camera},
    )


def collect_ioregistry_info() -> IORegistryInfo:
    """Collect comprehensive IORegistry hardware observations."""
    log("Collecting IORegistry hardware information...")

    pcie_devices = collect_pcie_devices()
    usb_devices = collect_usb_devices()
    audio_codecs = collect_audio_codecs()
    wifi, bluetooth, t1, usb_11, camera = _build_hardware_evidence(pcie_devices, usb_devices)

    return {
        "pcie_devices": pcie_devices,
        "usb_devices": usb_devices,
        "audio_codecs": audio_codecs,
        "wifi": wifi,
        "bluetooth": bluetooth,
        "t1": t1,
        "usb_1_1": usb_11,
        "camera": camera,
    }
