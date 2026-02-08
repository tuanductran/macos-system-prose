import asyncio
import sys
import unittest
from pathlib import Path

# Add the src directory to sys.path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prose.collectors.system import collect_system_info
from prose.utils import run


class TestMacOSProse(unittest.TestCase):
    def test_mac_platform(self):
        """Verify we are indeed on macOS before running deep tests."""
        self.assertEqual(sys.platform, "darwin")

    def test_sw_vers(self):
        """Check if sw_vers command works."""
        out = run(["sw_vers", "-productVersion"])
        self.assertTrue(len(out) > 0)

    def test_system_info_struct(self):
        """Verify system_info returns expected keys."""
        info = asyncio.run(collect_system_info())
        self.assertIn("macos_version", info)
        self.assertIn("model_identifier", info)
        self.assertIn("kernel", info)


if __name__ == "__main__":
    unittest.main()
