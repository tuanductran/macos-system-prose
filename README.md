# macOS System Prose

[![CI/CD](https://github.com/tuanductran/macos-system-prose/workflows/CI%2FCD/badge.svg)](https://github.com/tuanductran/macos-system-prose/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A **read-only** introspection tool for Darwin (macOS) that collects comprehensive system data and generates optimized reports for AI performance analysis, security auditing, and development environment optimization.

## What This Tool Does

`macos-system-prose` gathers detailed system information without modifying anything on your Mac. It produces three main outputs:

1. **`macos_system_report.json`** — Structured data for programmatic analysis.
2. **`macos_system_report.txt`** — Optimized prompt for LLMs (OCLP-aware).
3. **`macos_system_report.html`** — Visual dashboard for human review.

### AI Prompt

The generated prompt is context-aware:

- **OCLP Detection**: Automatically detects OpenCore Legacy Patcher and adjusts recommendations (e.g., avoids suggesting SIP enablement if it breaks patches).
- **Security Analysis**: SIP, FileVault, Firewall, code signing, TCC permissions.
- **Performance Analysis**: Memory pressure, disk usage, heavy CPU processes.
- **Developer Environment**: Git config, Docker status, PATH issues.
- **System Health**: Battery cycles, S.M.A.R.T. status, system logs, kernel extensions.
- **Optimization**: Prioritized recommendations (Critical → Important → Optional).

## Features

### System & Hardware

- Darwin/macOS version with marketing name and **SMBIOS enrichment** (board ID, CPU generation, max supported OS).
- Hardware model, identifier, architecture (Intel/Apple Silicon).
- CPU, GPU, memory stats.
- **Memory Pressure**: Real-time statistics (wired/active/inactive/free, swap usage).
- **Display**: Resolution, refresh rate, color depth (human-readable), **EDID parsing** for manufacturer info.
- Disk usage, APFS volumes, **S.M.A.R.T. disk health**.
- SIP, FileVault, Gatekeeper status.
- Thermal pressure monitoring.
- **Time Machine** backup status.

### Network & Connectivity

- Public and local IP addresses.
- Network interfaces (MAC address, subnet mask, gateway).
- DNS server configuration.
- Wi-Fi SSID and connection status.
- **VPN detection** (app + interface checks).
- Firewall status.

### Developer Environment

- **Languages**: Node.js, Python, Go, Rust, Ruby, Java, PHP, Perl.
- **Package Managers**: Homebrew (formula + cask + **service**), MacPorts, npm, yarn, pnpm, bun, pipx.
- **Version Managers**: nvm, asdf, pyenv, fnm, rvm, rbenv, goenv, volta, mise, rustup.
- **SDKs & Tools**: Xcode, Android SDK, Flutter.
- **Cloud/DevOps**: AWS CLI, GCP SDK, Terraform, kubectl, Helm.
- **Databases**: Redis, MongoDB, MySQL, PostgreSQL, SQLite.
- **IDE Extensions**: VS Code, Cursor, Windsurf, Zed.
- **Browsers**: Chrome, Firefox, Safari, Edge, Brave, Opera, Arc, Vivaldi (with versions).
- **Docker**: Daemon status, minimal container/image stats.
- **Git**: Global configuration (user, email, aliases).
- **Terminal Emulators**: Terminal, iTerm, Warp, Hyper, Alacritty, Kitty, Ghostty, WezTerm, Rio.
- **Shell Frameworks**: oh-my-zsh, oh-my-bash, starship, powerlevel10k, zinit, antigen, Fig.

### System Activity & Diagnostics

- **Top Processes**: Heavy CPU/memory consumers.
- **Launch Agents/Daemons**: User agents and system daemons.
- **Launchd Services**: Service status with PID and exit code (user domain).
- **Login Items**: Apps launching at startup.
- **Listening Ports**: Active network listeners.
- **Cron Jobs**: User crontab entries.
- **Kernel Extensions**: Third-party kexts.
- **System Extensions**: macOS 10.15+ security extensions.
- **Application Inventory**: Version detection with fallback strategies.
- **Electron Apps**: Electron-based app detection.
- **Crash Logs**: Recent IPS files.
- **Battery**: Cycle count, health condition, power source.

### Security & Privacy

- **Security Tools**: Little Snitch, Lulu, BlockBlock, OverSight, etc.
- **Antivirus**: AV software detection.
- **Code Signing**: Verification (sampled 5 apps, 3s timeout).
- **TCC Permissions**: Privacy database checks (requires Full Disk Access).

### Advanced Hardware

- **IORegistry**: PCIe devices, USB devices, audio codecs.
- **NVRAM**: Boot args, CSR/SIP config, SecureBoot model, OCLP settings.

### OpenCore Legacy Patcher (OCLP)

Advanced detection methods for unsupported Macs running newer macOS versions:

1. NVRAM `OCLP-Version` variable.
2. `/Applications/OpenCore-Patcher.app` presence.
3. Root patch marker plist.
4. OCLP signature kexts (AMFIPass, RestrictEvents, Lilu, WhateverGreen, etc.).
5. Patched system frameworks.
6. SMBIOS-based unsupported OS detection (70+ Mac models in database).
7. Boot-args AMFI configuration parsing.

### Advanced Analysis

- **Storage Analysis**: Cache sizes, log sizes, user directory usage.
- **Fonts**: System and user font counts.
- **Shell Customization**: Shell type, framework detection, alias/function counts.
- **System Preferences**: Trackpad, key repeat, mouse speed, scroll direction.
- **Kernel Parameters**: sysctl values (max files, max procs).
- **System Logs**: Recent critical/error entries.

### Cloud & Sync

- **iCloud**: Drive status, sync status, storage usage.

## Getting Started

### Requirements

- **Darwin**: macOS 10.15 (Catalina) or later.
- **Python**: 3.9 or higher.
- **Command Line Tools**: `xcode-select --install` (if needed).

### Installation

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

### Usage

```bash
# Generate JSON + AI Prompt (default)
python3 run.py

# Generate beautiful HTML Dashboard
python3 run.py --html

# Compare with a previous report
python3 run.py --diff baseline.json

# Verbose output (recommended for debugging)
python3 run.py --verbose

# JSON only (skip prompt generation)
python3 run.py --no-prompt

# Custom output path
python3 run.py -o report.json

# Minimal output
python3 run.py --quiet

# Only installed package usage
macos-prose --verbose --html
```

### Command Line Options

```text
usage: run.py [-h] [-v] [-q] [--no-prompt] [-o OUTPUT] [--diff DIFF] [--html]

macOS System Prose Collector

options:
  -h, --help            Show this help message and exit
  -v, --verbose         Enable verbose logging
  -q, --quiet           Show only errors
  --no-prompt           Skip AI prompt generation
  -o, --output OUTPUT   Custom output path for JSON report
  --diff DIFF           Compare current report with a baseline JSON
  --html                Generate HTML dashboard with dark theme
```

## New Features

### 🎨 HTML Dashboard

Generate a stunning HTML report with:

- Dark theme with glassmorphism effects.
- Gradient backgrounds and hover animations.
- Responsive grid layout.
- Status badges (Enabled/Disabled).

```bash
python3 run.py --html
# Generates: macos_system_report.html
```

### 🔍 Diff Mode

Compare two system reports to track changes over time:

```bash
# Create baseline
python3 run.py -o baseline.json

# ... later ...

# Compare current state with baseline
python3 run.py --diff baseline.json
```

Output shows:

- `+` Added items
- `-` Removed items
- `*` Changed items

### 🔄 Data Scrapers

Update internal databases automatically:

```bash
# Update macOS versions from Apple Support
python3 scripts/scrape_macos_versions.py --write

# Update SMBIOS models from EveryMac
python3 scripts/scrape_smbios_models.py --write
```

## Example Output

### JSON Report Structure

```json
{
  "timestamp": 1738908295.123,
  "system": {
    "os": "Darwin",
    "macos_version": "12.7.6",
    "macos_name": "macOS Monterey",
    "model_name": "MacBook Air",
    "model_identifier": "MacBookAir6,2",
    "marketing_name": "MacBook Air (13-inch, Early 2014)",
    "cpu_generation": "Haswell",
    "max_os_supported": "Big Sur",
    "sip_enabled": false,
    "gatekeeper_enabled": true
  },
  "hardware": {
    "cpu": "Intel(R) Core(TM) i5-4260U CPU @ 1.40GHz",
    "memory_pressure": {
      "level": "normal",
      "pages_free": 12345
    }
  },
  "opencore_patcher": {
    "detected": true,
    "version": "2.4.1",
    "unsupported_os_detected": true
  }
}
```

### AI Prompt Structure

Found in `macos_system_report.txt`:

```markdown
# macOS System Analysis Assistant

You are an expert macOS system administrator and performance analyst.

## OpenCore Legacy Patcher Detected
(or "## Standard macOS Configuration")

## Analysis Tasks
1. Security Posture
2. Performance Analysis
3. Developer Environment
4. System Health
5. Optimization Recommendations

## System Data (JSON)
{...complete JSON report...}
```

## Safety & Privacy

- **Read-Only**: Never modifies system state.
- **Transparent**: Uses standard macOS binaries (`system_profiler`, `scutil`, `nvram`, etc.).
- **No PII**: Avoids collecting sensitive personal information.
- **Local Execution**: No network calls (except optionally checking public IP).
- **Open Source**: MIT licensed and fully auditable.

## Development

See [AGENTS.md](AGENTS.md) for detailed architecture and contribution guidelines.

### Setup

```bash
pip install -e ".[dev]"
```

### Quality Checks

```bash
ruff check . --fix              # Lint & fix
mypy src/prose --check-untyped-defs  # Type check
pytest                          # Run tests
```

## Comparisons & Roadmap

- [x] Comparison mode (diff two reports)
- [x] HTML/Web dashboard output
- [ ] Export as PyPI package
- [ ] Homebrew formula
- [ ] Plugin architecture for custom collectors
- [ ] Historical tracking and trending

## License

MIT License — see [LICENSE](LICENSE).

Copyright (c) 2026 Tuan Duc Tran

## Support

- **Issues**: [GitHub Issues](https://github.com/tuanductran/macos-system-prose/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tuanductran/macos-system-prose/discussions)
- **Email**: <tuanductran.dev@gmail.com>
