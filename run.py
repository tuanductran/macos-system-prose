from __future__ import annotations

import sys
from pathlib import Path

# Add src to sys.path to support src-layout
sys.path.insert(0, str(Path(__file__).parent / "src"))

from prose.engine import main

if __name__ == "__main__":
    sys.exit(main())
