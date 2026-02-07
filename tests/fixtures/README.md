# Test Fixtures

This directory contains sample system reports from various Mac configurations for testing and validation.

## Fixtures

### macbookair6-2_monterey_oclp.json
- **Model**: MacBook Air (Mid 2013, MacBookAir6,2)
- **OS**: macOS Monterey 12.7.6
- **Architecture**: Intel x86_64 (i5-4260U)
- **OCLP**: Yes (v2.4.1) with 6 kexts
- **Memory**: 4 GB
- **Storage**: 256 GB SSD
- **Package Manager**: MacPorts
- **Special Features**:
  - OpenCore Legacy Patcher with 6 kexts
  - MacPorts installed (no Homebrew)
  - Terminal emulator detection
  - Code signing with team IDs
  - Active iCloud sync

### macbookpro18-1_ventura_m1.json
- **Model**: MacBook Pro 13" (2021, MacBookPro18,1)
- **OS**: macOS Ventura 13.6.9
- **Architecture**: Apple Silicon arm64 (M1)
- **OCLP**: No
- **Memory**: 16 GB
- **Storage**: 256 GB SSD
- **Package Manager**: Homebrew
- **Special Features**:
  - Native Apple Silicon support
  - Homebrew installed
  - iTerm + Terminal
  - Go and Rust installed
  - Chrome browser installed

### imac19-1_bigsur_intel.json
- **Model**: iMac 27" (2019, iMac19,1)
- **OS**: macOS Big Sur 11.7.10
- **Architecture**: Intel x86_64 (i5-8500)
- **OCLP**: No
- **Memory**: 32 GB
- **Storage**: 1 TB SSD
- **Package Manager**: Homebrew
- **Special Features**:
  - 5K Retina display
  - Docker installed and running
  - Xcode installed
  - Warp terminal
  - Desktop Mac (no battery)

## Adding New Fixtures

To add a new fixture:

1. Generate a report on the target Mac:
   ```bash
   python3 run.py --output report.json --no-prompt
   ```

2. Copy to fixtures with descriptive name:
   ```bash
   cp report.json tests/fixtures/[model]_[os]_[features].json
   ```

3. Add description to this README

4. Run validation:
   ```bash
   pytest tests/test_fixtures.py -v
   ```

## Naming Convention

Format: `[model]_[os]_[special-features].json`

Examples:
- `macbookpro16-1_ventura_m1.json` - M1 MacBook Pro on Ventura
- `imac19-1_bigsur_intel.json` - Intel iMac on Big Sur
- `macmini9-1_sonoma_m2.json` - M2 Mac mini on Sonoma
- `macbookair6-2_monterey_oclp.json` - OCLP-patched MacBook Air

## Usage in Tests

```python
import json
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
with open(fixtures_dir / "macbookair6-2_monterey_oclp.json") as f:
    data = json.load(f)
```

## Test Coverage

Current fixtures test:
- ✅ Intel (x86_64) and Apple Silicon (arm64) architectures
- ✅ OpenCore Legacy Patcher configurations
- ✅ Different macOS versions (Big Sur, Monterey, Ventura)
- ✅ Homebrew vs MacPorts package managers
- ✅ Desktop (iMac) vs Laptop (MacBook) configurations
- ✅ Various hardware specs (4GB to 32GB RAM, 256GB to 1TB storage)
- ✅ Different developer tool setups
