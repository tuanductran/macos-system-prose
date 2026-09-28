from __future__ import annotations

from unittest.mock import patch


class TestOCLPArchitecture:
    @patch("prose.collectors.oclp.platform.machine", return_value="arm64")
    def test_apple_silicon_never_reports_oclp(self, mock_machine):
        from prose.collectors.oclp import collect_opencore_patcher

        with patch("prose.collectors.oclp.get_oclp_nvram_version", return_value="2.5.1"):
            info = collect_opencore_patcher(loaded_kexts=["Lilu (1.7.0)"])

        assert info["detected"] is False
        assert info["detection_confidence"] == "none"
        assert info["detection_signals"] == ["apple_silicon_unsupported"]
        assert info["version"] is None
        assert info["loaded_kexts"] == []

    @patch("prose.collectors.oclp.platform.machine", return_value="x86_64")
    @patch("prose.collectors.oclp.utils.run")
    @patch("prose.collectors.oclp.get_oclp_nvram_version", return_value="2.5.1")
    @patch("prose.collectors.oclp.get_opencore_nvram_version", return_value="1.0.4")
    @patch("prose.collectors.oclp.get_boot_args", return_value="")
    @patch("prose.collectors.oclp.Path.exists", return_value=False)
    def test_intel_oclp_evidence_is_detected(
        self,
        mock_exists,
        mock_boot_args,
        mock_opencore_version,
        mock_oclp_version,
        mock_run,
        mock_machine,
    ):
        from prose.collectors.oclp import collect_opencore_patcher

        mock_run.side_effect = [
            "14.7.8",
            "Model Identifier: MacBookAir6,2",
            "",
        ]
        info = collect_opencore_patcher(loaded_kexts=[])

        assert info["detected"] is True
        assert info["detection_confidence"] == "high"
        assert "oclp_nvram_version" in info["detection_signals"]
        assert info["version"] == "2.5.1"
