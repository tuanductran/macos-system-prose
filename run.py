#!/usr/bin/env python3
"""Development entry point for macos-system-prose.

This script provides a convenient way to run the tool during development
without installing the package. For production use, install with pip and
use the 'macos-prose' command.
"""

from __future__ import annotations

import sys
from pathlib import Path


# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from prose.engine import main


if __name__ == "__main__":
    sys.exit(main())
