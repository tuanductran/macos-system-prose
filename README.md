# macOS System Prose

[![CI/CD](https://github.com/tuanductran/macos-system-prose/workflows/CI%2FCD/badge.svg)](https://github.com/tuanductran/macos-system-prose/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A **production-grade, read-only** macOS introspection tool that collects comprehensive system data through **105 specialized functions** across **7 collector modules** and generates optimized reports for AI analysis, security auditing, and development environment optimization.

Built with **zero runtime dependencies** using only Python 3.9+ standard library.

## Key Features

- **🔒 100% Read-Only** - Never modifies system state, no root/sudo required
- **📊 Comprehensive Data** - 28 data sections
- **🎯 Type-Safe** - 49 TypedDict schemas, full MyPy compliance, PEP 561 compliant
- **⚡ Async-First** - Parallel data collection via `asyncio.gather()`
- **🔍 OCLP-Aware** - 5 detection methods for OpenCore Legacy Patcher
- **🎨 Apple HIG TUI** - Professional terminal UI with Apple Human Interface Guidelines design
- **🌐 Multi-Format** - JSON, TXT (AI-optimized), Interactive TUI

## Architecture & Statistics

### Code Metrics

| Metric | Count | Details |
|--------|-------|---------|
| **Production Code** | 7,096 lines | 25 Python modules |
| **Test Code** | 2,412 lines | 12 test modules |
| **Functions** | 105 total | 62 collectors + 43 utilities |
| **TypedDict Schemas** | 49 | Strict type contracts |
| **Test Coverage** | 93 tests | 100% pass rate, 64% coverage |
| **Data Sections** | 28 | SystemReport output |
| **Dependencies** | 0 runtime | Pure Python stdlib |

### Output Formats

1. **JSON** (~31KB) - Structured data for programmatic analysis
2. **TXT** (~33KB) - LLM-optimized prompt with OCLP intelligence
3. **TUI** - Interactive htop-style terminal monitor (requires `textual`)

## Data Collection Capabilities

### System & Hardware (5 sections)

- **System**: macOS version, SIP/FileVault/Gatekeeper status
- **Hardware**: CPU, GPU, RAM, thermal pressure, memory pressure
- **Displays**: Resolution, refresh rate, EDID parsing (manufacturer, serial, year)
- **Storage**: Disk info, APFS volumes, SMART health status
- **Battery**: Cycle count, health, charging status (laptops only)

### Network & Connectivity (4 sections)

- **Network**: Interfaces, IPv4/IPv6, MAC addresses, subnet masks
- **Public/Local IP**: External and internal IP detection
- **DNS**: Name servers, search domains
- **Security**: Firewall status, VPN detection

### Development Environment (8 sections)

- **Languages**: Python, Node.js, Ruby, Go, Rust, Swift, Java, PHP
- **SDKs**: Xcode, Android SDK, Flutter SDK
- **Cloud/DevOps**: Docker (containers/images), AWS CLI, Azure CLI, gcloud, Terraform
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
- **Version Managers**: pyenv, nvm, rbenv, rustup, goenv, jenv, sdkman
- **Editors**: VS Code (extensions), JetBrains IDEs, Sublime, Atom, TextMate
- **Browsers**: Chrome, Firefox, Safari, Edge, Arc, Brave (with extension counts)
- **Terminals**: iTerm2, Alacritty, Kitty, Hyper, Warp, WezTerm

### Package Managers (7 managers)

- Homebrew (formula + casks + services)
- MacPorts (active ports)
- npm globals
- Yarn globals
- pnpm globals
- Bun globals
- pipx packages

### Security & Activity (6 sections)

- **Processes**: Top 100 by CPU/Memory with command info
- **TCC Permissions**: Full Disk Access, camera, microphone, accessibility
- **Code Signing**: Sample verification of system binaries
- **Security Tools**: Antivirus, EDR, monitoring software detection
- **Launch Items**: User/system agents, daemons, login items
- **Launchd Services**: Active services with PID and status
- **Open Ports**: Network listeners with process info
- **Cron Jobs**: Scheduled tasks (user + system)

### OCLP Detection (5 methods)

- NVRAM variables (OCLP-Version, boot-args)
- AMFI configuration (AppleMobileFileIntegrity bypass)
- Loaded kexts (Lilu, WhateverGreen, FeatureUnlock, etc.)
- Patched frameworks (CoreDisplay, IOSurface)
- System integrity analysis

### Advanced Analysis (5 sections)

- **Storage Breakdown**: Documents, Downloads, Desktop, Library, Caches, Logs
- **Fonts**: System + user font counts
- **Shell Customization**: Aliases, functions, rc file analysis
- **System Preferences**: Trackpad, keyboard, mouse settings
- **Kernel Parameters**: Max files, processes, vnodes
- **Diagnostic Logs**: Recent errors and warnings

## Installation

### Requirements

- **Platform**: macOS 10.15 Catalina or later
- **Python**: 3.9 - 3.14
- **Permissions**: Standard user (no root/sudo)

### Quick Start

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,tui]"
```

## Usage

### Basic Commands

```bash
# Generate JSON + TXT reports
macos-prose

# Launch interactive TUI (htop-style monitor)
macos-prose --tui --live

# Quiet mode (no console output)
macos-prose --quiet

# Custom output path
macos-prose -o /path/to/report.json

# Compare two reports
macos-prose --diff previous_report.json

# Verbose mode (detailed logging)
macos-prose --verbose
```

### Development Mode

```bash
# Use run.py without installing
python3 run.py --help
```

### Python API

```python
import asyncio
from prose.engine import collect_all

# Collect system data
report = asyncio.run(collect_all())

# Access data
print(f"macOS: {report['system']['macos_version']}")
print(f"Model: {report['system']['model_identifier']}")
print(f"OCLP: {report['opencore_patcher']['detected']}")
```

## Interactive TUI Features

Launch with `macos-prose --tui --live` for real-time monitoring:

### Monitor Dashboard

- **System**: macOS version, model, uptime, load average
- **CPU**: Usage percentage with progress bar
- **Memory**: RAM usage, pressure level, swap info
- **Disk**: Storage capacity, usage, free space with visual bar
- **Processes**: Top 100 processes by CPU/Memory (live updating)

### Deep Dive Tabs

- **Storage**: APFS volumes, capacity, health status
- **Security**: SIP, Gatekeeper, FileVault, Time Machine status
- **Network**: Interfaces, IP addresses, DNS servers, firewall
- **Developer**: Installed languages, SDKs, Docker info
- **OCLP**: Detection status, version, loaded kexts, boot args
- **Packages**: Homebrew, npm, MacPorts packages
- **Advanced**: System preferences, kernel parameters

### Controls

- `q` - Quit
- `r` - Manual refresh
- `Tab` - Switch tabs
- Auto-refresh: Configurable interval (default: 2s)

## Safety & Privacy

### Read-Only Guarantee

- ✅ **No System Modifications** - Tool never writes to system files or settings
- ✅ **No Root Required** - All operations via standard user permissions
- ✅ **Safe Commands** - Uses macOS built-ins: `system_profiler`, `scutil`, `ioreg`, `diskutil`
- ✅ **No Shell Injection** - All commands use list arguments, never `shell=True`

### Privacy Protection

- ✅ **No PII** - Avoids usernames, full paths, credentials
- ✅ **Local Only** - All processing on your Mac, no network calls
- ✅ **No Telemetry** - Zero analytics or data collection
- ✅ **Metadata Only** - File sizes/counts, not contents

### Command Execution Safety

- Timeouts on all commands (5-120s)
- Specific exception handling (OSError, ValueError)
- Permission validation before TCC.db access
- No arbitrary command execution

## Output Examples

### JSON Structure

```json
{
  "timestamp": 1770540883.888627,
  "system": {
    "os": "Darwin",
    "macos_version": "12.7.6",
    "macos_name": "macOS Monterey",
    "model_identifier": "MacBookAir6,2",
    "sip_enabled": false,
    "filevault_enabled": false
  },
  "hardware": {
    "cpu": "Intel(R) Core(TM) i5-4260U CPU @ 1.40GHz",
    "cpu_cores": 4,
    "memory_gb": 4.0,
    "gpu": ["Intel HD Graphics 5000 (1536 MB)"]
  },
  "opencore_patcher": {
    "detected": true,
    "version": "2.4.1",
    "loaded_kexts": ["Lilu", "WhateverGreen", "FeatureUnlock"]
  }
}
```

### AI-Optimized TXT Prompt

The text output is specifically formatted for AI/LLM analysis with:

- ✅ OCLP awareness and safety warnings
- ✅ Hardware limitations context
- ✅ Compatibility recommendations
- ✅ Security posture analysis
- ✅ Performance optimization hints

## Development

### Setup

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,tui]"
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/prose --cov-report=term-missing

# Specific test file
pytest tests/test_smbios.py -v

# With verbose output
pytest -vv
```

### Code Quality

```bash
# Lint with Ruff
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Type check with MyPy
mypy src/prose --check-untyped-defs

# Full CI simulation
ruff check . && ruff format --check . && mypy src/prose --check-untyped-defs && pytest
```

### Project Structure

```text
macos-system-prose/
├── src/prose/                    # Production code (6,965 lines)
│   ├── __init__.py               # Package exports (__version__, __author__)
│   ├── main.py                   # CLI entry point
│   ├── engine.py                 # Orchestration & AI prompt generation (4 functions)
│   ├── schema.py                 # 49 TypedDict schemas for type safety
│   ├── utils.py                  # Command execution & utilities (11 functions)
│   ├── exceptions.py             # Custom exception classes (4 types)
│   ├── iokit.py                  # NVRAM access via subprocess (8 functions)
│   ├── macos_versions.py         # macOS version detection (6 functions)
│   ├── diff.py                   # Report comparison (2 functions)
│   ├── parsers.py                # Text parsing utilities (11 functions)
│   ├── constants.py              # Application constants & defaults
│   ├── py.typed                  # PEP 561 type marker
│   ├── collectors/               # Data collection modules (62 functions)
│   │   ├── __init__.py           # Collector exports
│   │   ├── system.py             # OS, hardware, displays, disk (9 functions)
│   │   ├── network.py            # Network, DNS, firewall, VPN (4 functions)
│   │   ├── packages.py           # Package managers (9 functions)
│   │   ├── developer.py          # Languages, SDKs, tools (12 functions)
│   │   ├── environment.py        # Processes, security, apps (17 functions)
│   │   ├── advanced.py           # Storage, fonts, OCLP, logs (7 functions)
│   │   └── ioregistry.py         # IORegistry parsing (4 functions)
│   ├── datasets/
│   │   ├── __init__.py           # Dataset exports
│   │   └── smbios.py             # Legacy Mac detection
│   └── tui/                      # Terminal UI (optional)
│       ├── __init__.py           # TUI exports
│       ├── app.py                # Basic TUI implementation
│       └── app_enhanced.py       # Enhanced TUI with Apple HIG design
├── tests/                        # Test suite (2,412 lines, 93 tests)
│   ├── conftest.py               # Pytest fixtures (5 profiles)
│   ├── test_smbios.py            # Legacy Mac detection tests
│   ├── test_utils.py             # Utility tests (25 tests)
│   ├── test_display.py           # EDID parsing tests (12 tests)
│   ├── test_ioregistry.py        # IORegistry tests (13 tests)
│   ├── test_fixtures.py          # Schema validation (22 tests)
│   ├── test_engine.py            # Engine tests (4 tests)
│   ├── test_diff.py              # Diff tests (3 tests)
│   ├── test_exceptions.py        # Exception tests (4 tests)
│   ├── test_collectors_mocked.py # Collector mocks (7 tests)
│   └── test_collection.py        # Integration tests (3 tests)
├── data/                         # Reference data (DO NOT EDIT MANUALLY)
│   └── macos_versions.json       # 22 macOS versions (10.0 - 15.x)
├── scripts/                      # Maintenance scripts
│   └── scrape_macos_versions.py  # Update macOS version data
├── examples/                     # Example scripts
│   ├── README.md                 # Examples documentation
│   └── tui_demo.py               # TUI demo with mock data
├── .github/workflows/
│   └── ci.yml                    # CI/CD: Python 3.9-3.14 matrix
├── run.py                        # Development entry point
├── pyproject.toml                # PEP 621 metadata, build config
├── README.md                     # This file
├── AGENTS.md                     # AI agent instructions
├── LICENSE                       # MIT License
└── .gitignore                    # Git ignore rules
```

## CI/CD

Automated testing on every push via GitHub Actions:

- **Python Versions**: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- **Platform**: macOS-latest
- **Checks**: Linting (Ruff), Type checking (MyPy), Tests (Pytest), Coverage
- **Matrix**: 6 Python versions × full test suite

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed feature plans and development timeline.

**Quick overview:**

- ✅ **Completed**: JSON/TXT reports, Interactive TUI, Diff mode, Full type safety, 93 tests, Python 3.9-3.14
- 🚧 **In Progress**: PyPI package publication
- 📋 **Planned**: Homebrew formula, Plugin architecture, Historical tracking, PDF/Markdown export, HTML/Web dashboard output

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow code style (Ruff + MyPy clean)
4. Add tests for new features
5. Ensure all tests pass (`pytest`)
6. Submit a pull request

### Code Standards

- **Type Safety**: All functions must have type hints
- **Testing**: Maintain 100% test pass rate
- **Linting**: Ruff clean (`ruff check .`)
- **Type Checking**: MyPy clean (`mypy src/prose`)
- **Documentation**: Docstrings for public APIs
- **Python**: 3.9+ compatible (use `from __future__ import annotations`)

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

- **Apple** - For macOS and comprehensive system APIs
- **OCLP Team** - For OpenCore Legacy Patcher
- **Python Community** - For excellent stdlib and tooling
- **Textual** - For beautiful terminal UI framework

## Support

- **Issues**: [GitHub Issues](https://github.com/tuanductran/macos-system-prose/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tuanductran/macos-system-prose/discussions)
- **Documentation**: This README + [AGENTS.md](AGENTS.md)

## Legal

**Trademarks:** "macOS", "Apple", "Darwin", and "IOKit" are trademarks of Apple Inc. Used for descriptive purposes only.

**Disclaimer:** This is an independent open source project, NOT affiliated with Apple Inc.

**License:** MIT (see [LICENSE](LICENSE))

---

**Built with ❤️ for macOS power users, developers, and AI engineers**
