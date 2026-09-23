"""Mocked unit tests for collectors to ensure logic works across systems."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose.collectors.advanced import collect_opencore_patcher
from prose.collectors.developer import collect_dev_tools
from prose.collectors.environment import collect_environment_info
from prose.collectors.ioregistry import collect_ioregistry_info
from prose.collectors.network import (
    _hex_mask_to_dotted,
    _parse_firewall_status,
    collect_network_info,
)
from prose.collectors.packages import collect_package_managers


class TestNetworkCollectorMocked:
    def test_hex_mask_to_dotted(self):
        assert _hex_mask_to_dotted("0xffffff00") == "255.255.255.0"
        assert _hex_mask_to_dotted("0xff000000") == "255.0.0.0"
        assert _hex_mask_to_dotted("invalid") == "invalid"

    def test_parse_firewall_status(self):
        assert _parse_firewall_status("Firewall is enabled. (State = 1)") == "Enabled"
        assert _parse_firewall_status("Firewall is disabled. (State = 0)") == "Disabled"
        assert _parse_firewall_status("") == "Unknown"

    @patch("prose.collectors.network.run")
    @patch("prose.collectors.network.os.path.exists")
    def test_collect_network_info(self, mock_exists, mock_run):
        # Mocking route get default
        def side_effect(cmd, **kwargs):
            if cmd == ["route", "-n", "get", "default"]:
                return "   interface: en0\n   gateway: 192.168.1.1"
            if cmd == ["ifconfig", "en0"]:
                return (
                    "en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500\n"
                    "\tether a1:b2:c3:d4:e5:f6\n"
                    "\tinet 192.168.1.10 netmask 0xffffff00 broadcast 192.168.1.255"
                )
            if cmd == ["scutil", "--dns"]:
                return "DNS configuration\n  nameserver[0] : 1.1.1.1\n  nameserver[1] : 8.8.8.8"
            if cmd[0] == "curl":
                return "1.2.3.4"
            if cmd == ["hostname"]:
                return "Test-Mac"
            if cmd == ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]:
                return "Firewall is enabled. (State = 1)"
            if cmd == ["networksetup", "-listallhardwareports"]:
                return "Hardware Port: Wi-Fi\nDevice: en0\nEthernet Address: a1:b2:c3:d4:e5:f6"
            if cmd == ["ifconfig"]:
                return "lo0: ...\nen0: ..."
            if cmd == ["scutil", "--nc", "list"]:
                return ""
            return ""

        mock_run.side_effect = side_effect
        mock_exists.return_value = False

        info = collect_network_info(include_sensitive=True)
        assert info["hostname"] == "Test-Mac"
        assert info["ipv4_address"] == "192.168.1.10"
        assert info["public_ip"] == "1.2.3.4"
        assert info["dns_servers"] == ["1.1.1.1", "8.8.8.8"]
        assert info["firewall_status"] == "Enabled"
        assert info["privacy_mode"] == "full"

    @patch("prose.collectors.network.run")
    def test_collect_network_info_redacts_identity(self, mock_run):
        def side_effect(cmd, **kwargs):
            if cmd == ["route", "-n", "get", "default"]:
                return "interface: en0\ngateway: 192.168.1.1"
            if cmd == ["ifconfig", "en0"]:
                return "en0:\n\\tinet 192.168.1.10 netmask 0xffffff00\n\\tether a1:b2:c3:d4:e5:f6"
            if cmd == ["scutil", "--dns"]:
                return "nameserver[0] : 1.1.1.1"
            if cmd == ["networksetup", "-listallhardwareports"]:
                return "Hardware Port: Wi-Fi\nDevice: en0"
            if cmd == ["ifconfig"]:
                return "en0: ..."
            if cmd == ["scutil", "--nc", "list"]:
                return ""
            if cmd == ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]:
                return "Firewall is enabled. (State = 1)"
            if cmd[0] == "curl":
                raise AssertionError("public IP must not be requested in redacted mode")
            if cmd == ["hostname"]:
                raise AssertionError("hostname must not be requested in redacted mode")
            return ""

        mock_run.side_effect = side_effect
        info = collect_network_info()
        assert info["privacy_mode"] == "redacted"
        assert info["hostname"] == "[REDACTED]"
        assert info["public_ip"] == "Not collected"
        assert info["primary_interface"] == "[REDACTED]"
        assert info["mac_address"] == "[REDACTED]"
        assert info["dns_servers"] == []
        assert info["vpn_connections"] == []
        assert info["vpn_apps"] == []
        assert info["wifi_ssid"] is None
        assert all(item["ipv4"] == "[REDACTED]" for item in info["local_interfaces"])


class TestPackagesCollectorMocked:
    @patch("prose.collectors.packages.run")
    @patch("prose.collectors.packages.get_json_output")
    @patch("prose.collectors.packages.which")
    def test_collect_package_managers(self, mock_which, mock_json, mock_run):
        def side_effect(cmd, **kwargs):
            if "brew" in cmd:
                if "--version" in cmd:
                    return "Homebrew 4.2.5"
                if "--prefix" in cmd:
                    return "/opt/homebrew"
                if "list" in cmd and "--formula" in cmd:
                    return "git\nnode"
                if "list" in cmd and "--cask" in cmd:
                    return "visual-studio-code"
                if "services" in cmd:
                    return "Name  Status  User  File\nredis started user  ..."
            if "npm" in cmd and "--version" in cmd:
                return "10.2.4"
            return ""

        mock_run.side_effect = side_effect
        mock_which.side_effect = lambda x: f"/usr/local/bin/{x}"
        mock_json.return_value = {"dependencies": {"typescript": {"version": "5.3.3"}}}

        info = collect_package_managers()
        assert info["homebrew"]["installed"] is True
        assert info["homebrew"]["version"] == "Homebrew 4.2.5"
        assert info["homebrew"]["formula"] is not None
        assert "git" in info["homebrew"]["formula"]
        assert info["npm"]["installed"] is True
        assert info["npm"]["version"] == "10.2.4"


class TestDeveloperCollectorMocked:
    @patch("prose.collectors.developer.run")
    @patch("prose.collectors.developer.which")
    @patch("prose.collectors.developer.os.path.exists")
    def test_collect_dev_tools(self, mock_exists, mock_which, mock_run):
        import asyncio

        mock_run.return_value = "v1.2.3"
        mock_which.return_value = "/path/to/tool"
        mock_exists.return_value = True

        info = asyncio.run(collect_dev_tools())
        assert isinstance(info, dict)
        assert "languages" in info
        assert "docker" in info


class TestGitConfigPrivacy:
    @patch("prose.collectors.developer.run")
    @patch("prose.collectors.developer.which", return_value="/usr/bin/git")
    def test_git_config_redacts_credential_material(self, mock_which, mock_run):
        mock_run.return_value = (
            "user.name=Test User\\n"
            "user.email=test@example.com\\n"
            "credential.helper=store\\n"
            "http.https://example.com.extraheader=Authorization: Bearer secret-token\\n"
            "remote.origin.url=https://user:secret@example.com/repo.git\\n"
            "alias.safe=log --oneline\\n"
        )

        from prose.collectors.developer import collect_git_config

        info = collect_git_config()
        assert info["user_name"] == "Test User"
        assert info["user_email"] == "test@example.com"
        assert info["credential_helper"] == "[CONFIGURED]"
        assert info["other_settings"]["http.https://example.com.extraheader"] == "[REDACTED]"
        assert info["other_settings"]["remote.origin.url"] == "[REDACTED]"
        assert info["aliases"]["safe"] == "log --oneline"


class TestEnvironmentCollectorMocked:
    @patch("prose.collectors.environment.run")
    @patch("prose.collectors.environment.collect_launchd_services")
    def test_collect_environment_info(self, mock_services, mock_run):
        mock_run.return_value = "Python 3.12.1"
        mock_services.return_value = []

        with patch.dict(
            "prose.collectors.environment.os.environ",
            {"SHELL": "/bin/zsh", "PATH": "/usr/bin:/bin"},
        ):
            info = collect_environment_info()
            assert info["shell"] == "/bin/zsh"
            assert "Python 3.12.1" in info["python_version"]


class TestAdvancedCollectorMocked:
    @patch("prose.collectors.advanced.utils.run")
    @patch("prose.collectors.advanced.get_oclp_nvram_version")
    def test_collect_opencore_patcher(self, mock_oclp_nvram, mock_run):
        mock_run.return_value = "MacBookAir6,2"
        mock_oclp_nvram.return_value = "2.2.0"

        with patch("prose.collectors.advanced.Path.exists", return_value=False):
            info = collect_opencore_patcher()
            assert info["detected"] is True
            assert info["version"] == "2.2.0"
            assert info["detection_confidence"] == "high"
            assert "oclp_nvram_version" in info["detection_signals"]


class TestIORegistryHardwareEvidence:
    @patch("prose.collectors.ioregistry.run")
    def test_no_evidence_is_unknown_not_absent(self, mock_run):
        mock_run.return_value = ""
        info = collect_ioregistry_info()
        assert info["wifi"]["present"] is None
        assert info["bluetooth"]["present"] is None
        assert info["t1"]["present"] is None
        assert info["usb_1_1"]["present"] is None
        assert info["camera"]["present"] is None

    @patch("prose.collectors.ioregistry.run")
    def test_evidence_domains(self, mock_run):
        pcie = """<?xml version="1.0"?>
<plist version="1.0"><array>
<dict><key>IOName</key><string>AirPort BCM94360</string>
<key>vendor-id</key><data>IAc=</data><key>device-id</key><data>AAE=</data></dict>
<dict><key>IOName</key><string>USB OHCI Controller</string>
<key>vendor-id</key><data>AAAAAA==</data><key>device-id</key><data>AAE=</data></dict>
</array></plist>"""
        usb = """<?xml version="1.0"?>
<plist version="1.0"><array>
<dict><key>USB Product Name</key><string>Bluetooth USB Host Controller</string>
<key>idVendor</key><integer>1452</integer><key>idProduct</key><integer>1</integer></dict>
<dict><key>USB Product Name</key><string>FaceTime Camera</string>
<key>idVendor</key><integer>1452</integer><key>idProduct</key><integer>2</integer></dict>
</array></plist>"""

        def side_effect(cmd, **kwargs):
            if "-c" in cmd and "IOPCIDevice" in cmd:
                return pcie
            if "IOUSBHostDevice" in cmd:
                return usb
            return ""

        mock_run.side_effect = side_effect

        info = collect_ioregistry_info()
        assert info["wifi"]["present"] is True
        assert info["bluetooth"]["present"] is True
        assert info["usb_1_1"]["present"] is True
        assert info["camera"]["present"] is True
