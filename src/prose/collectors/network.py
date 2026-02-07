from __future__ import annotations

import os
import struct

from prose.schema import NetworkInfo
from prose.utils import log, run, which


def _hex_mask_to_dotted(hex_mask: str) -> str:
    """Convert hex subnet mask to dotted-decimal notation.

    Example: '0xffffff00' → '255.255.255.0'
    """
    try:
        val = int(hex_mask, 16)
        return ".".join(str(b) for b in struct.pack("!I", val))
    except (ValueError, struct.error):
        return hex_mask


def _parse_firewall_status(raw: str) -> str:
    """Parse socketfilterfw output into clean status string.

    Input:  'Firewall is enabled. (State = 1)'
    Output: 'Enabled'
    """
    raw = raw.strip().lower()
    if "enabled" in raw:
        return "Enabled"
    if "disabled" in raw:
        return "Disabled"
    return raw.strip() or "Unknown"


def collect_vpn_info() -> tuple[bool, list[str], list[str]]:
    """Detect VPN connections and VPN applications."""
    vpn_active = False
    vpn_connections = []
    vpn_apps = []

    try:
        # Check for VPN interfaces (utun, ppp, ipsec)
        ifconfig_output = run(["ifconfig"])
        for line in ifconfig_output.splitlines():
            if line.startswith(("utun", "ppp", "ipsec")):
                interface = line.split(":")[0]
                vpn_connections.append(interface)
                vpn_active = True

        # Check scutil for VPN services
        scutil_output = run(["scutil", "--nc", "list"], log_errors=False)
        for line in scutil_output.splitlines():
            if "Connected" in line or "Connecting" in line:
                vpn_active = True
                # Extract service name
                parts = line.strip().split('"')
                if len(parts) >= 2:
                    vpn_connections.append(parts[1])

        # Check for common VPN apps
        vpn_app_paths = {
            "Tailscale": "/Applications/Tailscale.app",
            "WireGuard": "/Applications/WireGuard.app",
            "OpenVPN Connect": "/Applications/OpenVPN Connect.app",
            "Cisco AnyConnect": "/Applications/Cisco/Cisco AnyConnect Secure Mobility Client.app",
            "NordVPN": "/Applications/NordVPN.app",
            "ExpressVPN": "/Applications/ExpressVPN.app",
            "ProtonVPN": "/Applications/ProtonVPN.app",
            "Tunnelblick": "/Applications/Tunnelblick.app",
        }

        for vpn_name, vpn_path in vpn_app_paths.items():
            if os.path.exists(vpn_path):
                vpn_apps.append(vpn_name)

        # Check if tailscale daemon is running
        if which("tailscale"):
            status = run(["tailscale", "status"], timeout=5, log_errors=False)
            if status and "Logged out" not in status:
                vpn_active = True
                if "Tailscale" not in vpn_apps:
                    vpn_apps.append("Tailscale (CLI)")

    except Exception:
        pass

    return vpn_active, list(set(vpn_connections)), vpn_apps


def collect_network_info() -> NetworkInfo:
    log("Collecting detailed network information...")

    # 1. Primary Interface & Gateway
    route_out = run(["route", "-n", "get", "default"])
    interface = "Unknown"
    gateway = "Unknown"
    for line in route_out.splitlines():
        if "interface:" in line:
            interface = line.split(":")[1].strip()
        if "gateway:" in line:
            gateway = line.split(":")[1].strip()

    # 2. Local IP, Mask, MAC
    ipv4 = "Unknown"
    mask = "Unknown"
    mac = "Unknown"
    if interface != "Unknown":
        ifconfig = run(["ifconfig", interface])
        for line in ifconfig.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                parts = line.split()
                ipv4 = parts[1]
                if "netmask" in line:
                    raw_mask = parts[parts.index("netmask") + 1]
                    mask = _hex_mask_to_dotted(raw_mask) if raw_mask.startswith("0x") else raw_mask
            if line.startswith("ether "):
                mac = line.split()[1]

    # 3. DNS Servers
    dns: list[str] = []
    scutil_dns = run(["scutil", "--dns"])
    for line in scutil_dns.splitlines():
        line = line.strip()
        if "nameserver[" in line and " : " in line:
            server = line.split(" : ", 1)[1].strip()
            if server and server not in dns:
                dns.append(server)

    # 4. Public IP
    public_ip = run(["curl", "-s", "--max-time", "2", "https://ifconfig.me"]) or "Timeout/Unknown"

    # 5. Wi-Fi SSID
    wifi_ssid = None
    airport_path = (
        "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    )
    if os.path.exists(airport_path):
        airport_out = run([airport_path, "-I"])
        for line in airport_out.splitlines():
            if " SSID:" in line and " BSSID:" not in line:
                wifi_ssid = line.split(":")[1].strip()

    # 6. Local Interfaces
    local_interfaces = []
    try:
        hw_ports = run(["networksetup", "-listallhardwareports"])
        current_port = ""
        for line in hw_ports.splitlines():
            if "Hardware Port:" in line:
                current_port = line.split(":")[1].strip()
            if "Device:" in line:
                dev = line.split(":")[1].strip()
                status = run(["ifconfig", dev])
                ip = "None"
                for s_line in status.splitlines():
                    if "inet " in s_line:
                        ip = s_line.strip().split()[1]
                        break
                local_interfaces.append({"name": current_port, "device": dev, "ipv4": ip})
    except Exception:
        pass

    # VPN Information
    vpn_status, vpn_conns, vpn_apps_list = collect_vpn_info()

    return {
        "hostname": run(["hostname"]),
        "primary_interface": interface,
        "ipv4_address": ipv4,
        "public_ip": public_ip,
        "gateway": gateway,
        "subnet_mask": mask,
        "mac_address": mac,
        "dns_servers": dns,
        "wifi_ssid": wifi_ssid,
        "firewall_status": _parse_firewall_status(
            run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
        ),
        "local_interfaces": local_interfaces,
        "vpn_status": vpn_status,
        "vpn_connections": vpn_conns,
        "vpn_apps": vpn_apps_list,
    }
