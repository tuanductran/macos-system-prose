# macOS System Prose

[![CI/CD](https://github.com/tuanductran/macos-system-prose/workflows/CI%2FCD/badge.svg)](https://github.com/tuanductran/macos-system-prose/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A **read-only** macOS introspection tool that collects system facts through specialized collectors and generates structured reports for AI analysis, security auditing, and development-environment inspection.

Built with **zero runtime dependencies** using only Python 3.9+ standard library.

## Key Features

- **🔒 Read-Only** - Never modifies system state; no root/sudo required
- **📊 Comprehensive Data** - 28 data sections
- **🎯 Type-Safe** - 49 TypedDict schemas, full MyPy compliance, PEP 561 compliant
- **⚡ Async-First** - Parallel data collection via `asyncio.gather()`
- **🔍 OCLP-Aware** - Separates OpenCore/OCLP detection evidence from root-patch evidence
- **🎨 Apple HIG TUI** - Professional terminal UI with Apple Human Interface Guidelines design
- **🌐 Multi-Format** - JSON, TXT (AI-optimized), Interactive TUI

## Architecture & Statistics

### Code Metrics

| Metric | Count | Details |
|--------|-------|---------|
| **Production Code** | 7,096 lines | 25 Python modules |
| **Test Suite** | CI source of truth | Tests and coverage are reported by GitHub Actions |
| **Functions** | 105 total | 62 collectors + 43 utilities |
| **TypedDict Schemas** | 49 | Strict type contracts |
| **Test Results** | CI source of truth | Pass count and coverage are reported by GitHub Actions |
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

### Security & Activity

> TCC collection currently reports database availability; it does not claim to enumerate effective per-app permissions.

- **Processes**: Top 100 by CPU/Memory with command info
- **TCC**: Database availability and collection status
- **Code Signing**: Sample verification of system binaries
- **Security Tools**: Antivirus, EDR, monitoring software detection
- **Launch Items**: User/system agents, daemons, login items
- **Launchd Services**: Active services with PID and status
- **Open Ports**: Network listeners with process info
- **Cron Jobs**: Scheduled tasks (user + system)

### OpenCore / OCLP Detection

The report keeps separate evidence for the OpenCore bootloader, OCLP application, and possible root-patch state. NVRAM OCLP/OpenCore versions and the OCLP application are stronger signals than the presence of individual kexts. Loaded kexts and observed framework paths are reported as evidence, not treated as proof of OCLP.

The AI prompt also avoids blanket SIP advice: OCLP documentation states that SIP requirements vary by OS, model, and whether root patching is required.

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

This project uses **uv** for Python environment and dependency management. uv manages the project virtual environment and can install the required Python version automatically. The repository pins Python 3.14 as the local default while CI explicitly tests Python 3.9 through 3.14.

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose
uv sync --all-extras
```

If uv is not installed, use the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The project requires uv 0.12.x. The `.python-version` file provides the local default Python version; CI overrides it for each supported Python version. uv's project workflow uses `.venv` and `uv run` so commands execute inside the managed environment.

## Usage

### Basic Commands

```bash
# Generate JSON + TXT reports (network identity redacted by default)
macos-prose

# Launch interactive TUI (htop-style monitor)
macos-prose --tui --live

# Quiet mode (no console output)
macos-prose --quiet

# Custom output path
macos-prose -o /path/to/report.json

# Compare two reports
macos-prose --diff previous_report.json

# Include network identity and public IP (explicit opt-in)
macos-prose --include-sensitive-network

# Verbose mode (detailed logging)
macos-prose --verbose

# Fast mode: skip expensive storage/font/log collectors
macos-prose --mode fast

# Deep mode: collect every report section (default)
macos-prose --mode deep
```

### Development Mode

```bash
# Run without manually activating .venv
uv run macos-prose --help
```

### Python API

```python
import asyncio
from prose.engine import collect_all

# Collect system data
report = asyncio.run(collect_all())
# Fast mode skips expensive storage/font/log collectors:
# report = asyncio.run(collect_all(mode="fast"))
# Deep mode is the default and collects every section.
# Opt in to network identity only when required:
# report = asyncio.run(collect_all(include_sensitive_network=True))

# Access data
print(f"macOS: {report['system']['macos_version']}")
print(f"Model: {report['system']['model_identifier']}")
print(f"OCLP: {report['opencore_patcher']['detected']}")
print(f"OCLP confidence: {report['opencore_patcher']['detection_confidence']}")
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

- ✅ **Redacted network mode by default** - hostname, local IP, gateway, MAC address and SSID are not exported as identifying values
- ✅ **No public-IP request by default** - the collector does not contact an external IP service unless explicitly requested
- ✅ **No Telemetry** - zero analytics or data collection
- ⚠️ **Local report data can still be sensitive** - process names, application names, package/tool versions and diagnostics may identify software installed on the Mac
- 🔓 **Explicit opt-in for network identity** - use `--include-sensitive-network` only when those values are needed

### Command Execution Safety

- Timeouts on all commands (5-120s)
- Specific exception handling (OSError, ValueError)
- Permission validation before TCC.db access
- No arbitrary command execution

## Output Examples

### JSON Structure

```json
{
  "report_schema": "macos-system-prose/system-report",
  "report_schema_version": 1,
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
uv sync --all-extras
```

### Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src/prose --cov-report=term-missing

# Specific test file
uv run pytest tests/test_smbios.py -v

# With verbose output
uv run pytest -vv
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
uv run ruff check . && uv run ruff format --check . && uv run mypy src/prose --check-untyped-defs && uv run pytest
```

### Project Structure

```text
macos-system-prose/
├── src/prose/
│   ├── main.py                 # CLI entry point
│   ├── engine.py               # report orchestration and AI prompt rendering
│   ├── schema.py               # typed report contracts
│   ├── utils.py                # stable utility facade
│   ├── collectors/             # focused system data collectors
│   │   ├── system.py
│   │   ├── environment.py
│   │   ├── developer.py
│   │   ├── network.py
│   │   ├── packages.py
│   │   ├── advanced.py
│   │   ├── oclp.py             # isolated OpenCore/OCLP detection
│   │   └── ioregistry.py
│   ├── tui/                    # optional Textual UI
│   ├── datasets/               # bundled reference data
│   ├── diff.py                 # report comparison
│   ├── oclp.py                 # OCLP compatibility model
│   ├── iokit.py                # IOKit/NVRAM access
│   ├── macos_versions.py       # macOS version metadata
│   ├── constants.py
│   └── exceptions.py
├── tests/                      # unit, mocked and integration tests
├── data/                       # versioned reference datasets
├── docs/                       # maintained project documentation
├── scripts/                    # explicit maintenance tooling
├── .github/workflows/          # CI and autofix workflows
├── pyproject.toml
├── uv.lock
├── README.md
├── AGENTS.md
├── SECURITY.md
└── LICENSE
```

The repository intentionally does not keep a separate examples/ tree or a development-only run.py launcher. The packaged CLI is the single supported entry point.

Repository hygiene is enforced through the root `.gitignore`; generated reports, caches, local state and credentials are intentionally excluded from version control.

## CI/CD

Automated testing on every push via GitHub Actions:

- **Python Versions**: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- **Platforms**: macOS arm64 plus an explicit macOS Intel compatibility smoke test
- **Checks**: Linting (Ruff), formatting, type checking (MyPy), tests (Pytest), integration report, and security scan
- **Coverage**: generated as `coverage.xml` and retained as a GitHub Actions artifact
- **Matrix**: 6 Python versions × full test suite, plus Intel compatibility

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the current feature plan. The roadmap intentionally separates implemented facts from future work; test counts and coverage are produced by CI rather than maintained as README claims.

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
