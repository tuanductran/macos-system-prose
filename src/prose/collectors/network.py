from __future__ import annotations

import os

from prose.schema import NetworkInfo
from prose.utils import log, run


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
                    mask = parts[parts.index("netmask") + 1]
            if line.startswith("ether "):
                mac = line.split()[1]

    # 3. DNS Servers
    dns = []
    scutil_dns = run(["scutil", "--dns"])
    for line in scutil_dns.splitlines():
        line = line.strip()
        if "nameserver[" in line:
            server = line.split(":")[1].strip()
            if server not in dns:
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
        "firewall_status": run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]
        ).strip(),
        "local_interfaces": local_interfaces,
    }
