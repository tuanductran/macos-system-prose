# macOS System Prose

[![CI/CD](https://github.com/tuanductran/macos-system-prose/workflows/CI%2FCD/badge.svg)](https://github.com/tuanductran/macos-system-prose/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A **read-only** macOS system introspection tool that generates comprehensive, AI-optimized reports for performance analysis, security auditing, and developer environment optimization.

## 🎯 What It Does

`macos-system-prose` collects detailed system information without modifying anything on your Mac. It produces two outputs:

1. **`macos_system_report.json`** - Structured data for programmatic analysis
2. **`macos_system_report.txt`** - AI-optimized prompt for LLM consumption

Perfect for:
- 🔍 System health checks and auditing
- 🛠️ Developer environment debugging
- 🤖 AI-powered optimization recommendations
- 📊 Configuration inventory and compliance
- 🔒 Security posture assessment

## ✨ Features

### 🖥️ System & Hardware
- macOS version with marketing name (Monterey, Ventura, Sonoma, etc.)
- Hardware model, identifier, and architecture (Intel/Apple Silicon)
- CPU, GPU, memory specifications
- **Display information** (resolution, refresh rate, color depth)
- Disk usage and APFS volume information
- **S.M.A.R.T. disk health status**
- System Integrity Protection (SIP) status
- FileVault encryption status
- Gatekeeper configuration
- Thermal pressure monitoring
- **Time Machine backup status**

### 🌐 Network & Connectivity
- Public and local IP addresses
- Network interface details (MAC, subnet, gateway)
- DNS server configuration
- Wi-Fi SSID and connection status
- **VPN status and active connections**
- **VPN applications detection**
- Firewall status
- Active network routes

### 💻 Developer Environment
- **Languages**: Node.js, Python, Go, Rust, Ruby, Java, PHP, Perl
- **Package Managers**: Homebrew (formula + casks + **services**), MacPorts, npm, yarn, pnpm, bun, pipx
- **Version Managers**: nvm, asdf, pyenv, rbenv, goenv, rustup
- **SDKs & Tools**: Xcode, Android SDK, Flutter
- **Cloud/DevOps**: AWS CLI, GCP SDK, Terraform, kubectl, Helm
- **Databases**: Redis, MongoDB, MySQL, PostgreSQL, SQLite
- **IDE Extensions**: VS Code, Antigravity, Cursor, Windsurf, Zed
- **Browsers**: Chrome, Firefox, Safari, Edge, Brave, Opera, Arc, Vivaldi (with versions)
- **Docker**: Container/image counts, daemon status, **detailed container & image info**
- **Git**: **Global configuration** (user, email, aliases, settings)

### 🔧 System Activity & Diagnostics
- **Top Processes**: CPU/memory usage for resource-heavy processes
- **Launch Agents**: User agents, system agents/daemons
- **Launchd Services**: System services status with PID and exit codes (user domain)
- **Login Items**: Applications that launch at startup
- **Listening Ports**: Network ports with active listeners
- **Cron Jobs**: User crontab entries
- Third-party kernel extensions
- **All installed applications** (not just Electron)
- Electron-based applications
- Recent crash logs (IPS files)
- Battery health (cycle count, condition, power source)
- **Security tools** (Little Snitch, Lulu, etc.)
- **Antivirus software** detection

## 🚀 Getting Started

### Prerequisites

- **macOS**: Version 12 (Monterey) or later
- **Python**: 3.9 or higher
- **Command Line Tools**: Install with `xcode-select --install` (if needed)

### Installation

#### Option 1: From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

#### Option 2: Direct Install (Coming Soon)

```bash
# Install from PyPI (when published)
pip install macos-system-prose
```

### Usage

```bash
# Basic execution (generates both JSON and AI prompt)
python3 run.py

# With verbose output
python3 run.py --verbose

# Generate only JSON report (skip AI prompt)
python3 run.py --no-prompt

# Custom output location
python3 run.py --output custom_report.json

# Quiet mode (minimal output)
python3 run.py --quiet

# After installing as package
macos-prose --verbose
```

### Command-Line Options

```
usage: run.py [-h] [--verbose] [--quiet] [--no-prompt] [--output OUTPUT]

macOS System Prose - Generate comprehensive system reports

options:
  -h, --help       Show this help message and exit
  --verbose, -v    Enable verbose logging
  --quiet, -q      Suppress all non-error output
  --no-prompt      Skip generating AI optimization prompt
  --output OUTPUT  Custom output path for JSON report
```

## 📤 Output Examples

### JSON Report Structure

```json
{
  "timestamp": 1738908295.123,
  "system": {
    "os": "Darwin",
    "macos_version": "14.2.1",
    "macos_name": "Sonoma",
    "model_name": "MacBook Pro",
    "model_identifier": "Mac14,10",
    "kernel": "Darwin 23.2.0",
    "architecture": "arm64",
    "uptime": "5 days, 3:24",
    "sip_enabled": true,
    "gatekeeper_enabled": true,
    "filevault_enabled": true
  },
  "hardware": {
    "cpu": "Apple M3 Pro",
    "cpu_cores": 12,
    "memory_gb": 36.0,
    "thermal_pressure": ["Nominal"],
    "gpu": ["Apple M3 Pro"]
  },
  "disk": {
    "disk_total_gb": 994.66,
    "disk_free_gb": 487.23,
    "apfs_info": ["Macintosh HD (APFS): 994.66 GB total"]
  },
  "network": {
    "hostname": "MacBook-Pro.local",
    "primary_interface": "en0",
    "ipv4_address": "192.168.1.100",
    "public_ip": "203.0.113.42",
    "gateway": "192.168.1.1",
    "subnet_mask": "255.255.255.0",
    "mac_address": "a4:83:e7:xx:xx:xx",
    "dns_servers": ["1.1.1.1", "8.8.8.8"],
    "wifi_ssid": "MyNetwork",
    "firewall_status": "enabled"
  },
  "package_managers": {
    "homebrew": {
      "installed": true,
      "version": "4.2.5",
      "bin_path": "/opt/homebrew/bin/brew",
      "prefix": "/opt/homebrew",
      "formula": ["git", "node", "python@3.12", "wget"],
      "casks": ["visual-studio-code", "docker", "firefox"]
    },
    "npm": {
      "installed": true,
      "version": "10.2.4",
      "bin_path": "/usr/local/bin/npm",
      "globals": ["typescript", "eslint", "prettier"]
    }
  },
  "developer_tools": {
    "languages": {
      "node": "v20.11.0",
      "python3": "Python 3.12.1",
      "go": "go1.21.6",
      "rust": "rustc 1.75.0"
    },
    "sdks": {
      "xcode": "Xcode 15.2",
      "flutter": "Flutter 3.16.5",
      "android_sdk": "/Users/user/Library/Android/sdk"
    },
    "cloud_devops": {
      "aws": "aws-cli/2.15.10",
      "gcloud": "Google Cloud SDK 462.0.0",
      "terraform": "Terraform v1.7.0",
      "kubectl": "Client Version: v1.29.1"
    },
    "extensions": {
      "vscode": ["ms-python.python", "github.copilot", "esbenp.prettier-vscode"]
    }
  },
  "battery": {
    "present": true,
    "percentage": "82%",
    "cycle_count": 47,
    "condition": "Normal",
    "power_source": "AC Power"
  }
}
```

### AI Prompt Example

The generated `macos_system_report.txt` contains a structured prompt for LLMs:

```
# macOS System Optimization & Analysis Report

You are an expert macOS Systems Engineer with specialization in performance tuning,
developer environment optimization, and system security.

Below is a comprehensive system report in JSON format. Your task is to:
1. Identify potential performance bottlenecks (CPU/Memory/Disk).
2. Spot redundant or conflicting developer tool installations
   (Multiple package managers/PATH duplicates).
3. Recommend security hardening based on SIP/Gatekeeper/FileVault status.
4. Propose cleanup for non-existent but referenced launch agents/daemons.
5. List specific commands to execute the proposed optimizations safely.

---
SYSTEM REPORT:
{...complete JSON report...}
```

## 🛡️ Safety & Privacy

- **✅ Read-Only**: Never modifies system state (no writes, no installs, no config changes)
- **✅ Transparent**: Uses only standard macOS binaries (`system_profiler`, `scutil`, `sw_vers`, etc.)
- **✅ No PII**: Avoids collecting sensitive personal information where possible
- **✅ No Network Calls**: All data collection is local (except public IP detection)
- **✅ Open Source**: MIT licensed, fully auditable code

## 🏗️ Architecture

```
src/prose/
├── engine.py              # CLI entry point and orchestration
├── schema.py              # TypedDict schemas for all data structures
├── utils.py               # Command execution, logging, JSON parsing
├── exceptions.py          # Custom exception classes
└── collectors/            # Modular data collectors
    ├── system.py          # Hardware, OS, disk info
    ├── network.py         # Network, DNS, firewall
    ├── packages.py        # Package manager detection
    ├── developer.py       # Languages, SDKs, cloud tools, IDE extensions
    └── environment.py     # Processes, launch items, battery, diagnostics
```

**Design Principles:**
- **Modular**: Each collector is independent and can fail without crashing the entire report
- **Typed**: Full type safety with `TypedDict` schemas
- **Resilient**: Comprehensive error handling and timeouts for slow commands
- **Extensible**: Easy to add new collectors or data points

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Activate pre-commit checks (optional)
ruff check . --fix && ruff format .
```

### Code Quality

```bash
# Lint and auto-fix
ruff check . --fix

# Format code
ruff format .

# Type check
mypy src/prose --check-untyped-defs

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/prose --cov-report=term-missing

# Full CI simulation
ruff check . && ruff format --check . && pytest --cov=src/prose
```

### Project Standards

- **Python**: 3.9+ with type hints (`from __future__ import annotations`)
- **Linting**: Ruff (line length: 100 characters)
- **Testing**: pytest with coverage target: `src/prose`
- **Type Checking**: Mypy with partial strictness
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Write tests for new functionality
4. Ensure all checks pass (`ruff check . && pytest`)
5. Use conventional commit messages
6. Open a Pull Request

**Key Guidelines:**
- All collectors must be typed with schemas from `schema.py`
- Add tests for new collectors in `tests/test_collection.py`
- Use `verbose_log()` for debug output
- Wrap external commands in try-except blocks
- Never modify system state (read-only guarantee)

For detailed guidelines, see [AGENTS.md](AGENTS.md).

## 📊 Use Cases

### For System Administrators
- Quick health check of macOS machines
- Inventory management and asset tracking
- Configuration audits and compliance verification
- Security posture assessment (SIP, FileVault, Gatekeeper)

### For Developers
- Environment debugging and dependency resolution
- Identify conflicting package managers or PATH issues
- Detect redundant tool installations
- Performance bottleneck identification

### For AI/LLM Analysis
- Generate optimization recommendations
- Identify security hardening opportunities
- Suggest cleanup actions for unused services
- Provide context-aware system tuning advice

## 🗺️ Roadmap

- [ ] PyPI package publication
- [ ] Homebrew formula distribution
- [ ] Docker/Podman detection
- [ ] Browser extensions collector
- [ ] Comparison mode (diff two reports)
- [ ] HTML/Web dashboard output
- [ ] Plugin architecture for custom collectors
- [ ] Historical tracking and trending

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Tuan Duc Tran

## 🙏 Acknowledgments

- Built with Python and modern macOS system APIs
- Inspired by system profiling needs in AI/LLM workflows
- Thanks to the open-source community for tools and inspiration

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/tuanductran/macos-system-prose/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tuanductran/macos-system-prose/discussions)
- **Email**: tuanductran.dev@gmail.com
- **Security**: Please report security vulnerabilities privately via GitHub Security Advisories

---

**Made with ❤️ for the macOS development community**
