# AGENTS.md

This file provides critical guidance to AI coding agents (Claude, Cursor, Copilot, etc.) when
working with the `macos-system-prose` repository.

## 📖 Repository Overview

`macos-system-prose` is a **read-only** macOS system introspection tool that collects comprehensive
system data and generates AI-optimized reports for performance analysis, security auditing, and
developer environment optimization.

**Core Capabilities:**
- **System Introspection**: Hardware, OS version, SIP/FileVault/Gatekeeper status, thermal pressure
- **Developer Environment**: Languages (Node, Python, Go, Rust, Ruby, Java, PHP, Perl), SDKs (Xcode, Android, Flutter), Cloud/DevOps tools (AWS, GCP, Terraform, kubectl, helm), databases
- **Package Managers**: Homebrew, MacPorts, npm, yarn, pnpm, bun, pipx (with global package lists)
- **IDE Extensions**: VS Code, Cursor, Windsurf, Zed extension detection
- **Network & Connectivity**: Public IP, local interfaces, gateway, DNS, Wi-Fi SSID, firewall status
- **System Activity**: Top processes, launch agents/daemons, login items, listening ports, cron jobs
- **Diagnostics**: Battery health, recent crash logs (IPS files), kernel extensions, Electron apps

**Output Formats:**
- `macos_system_report.json` - Structured data for programmatic use
- `macos_system_report.txt` - AI-optimized prompt for LLM analysis

## 🏗️ Project Architecture

```text
macos-system-prose/
├── src/prose/
│   ├── __init__.py
│   ├── engine.py              # Main orchestration engine and CLI entry point
│   ├── schema.py              # TypedDict definitions for all data structures
│   ├── utils.py               # Command execution, logging, JSON parsing
│   ├── exceptions.py          # Custom exception classes
│   └── collectors/            # Modular data collection modules
│       ├── __init__.py
│       ├── system.py          # System info, hardware, disk (97 lines)
│       ├── network.py         # Network, DNS, firewall, Wi-Fi (96 lines)
│       ├── packages.py        # Package managers (146 lines)
│       ├── developer.py       # Languages, SDKs, cloud tools, extensions (195 lines)
│       └── environment.py     # Processes, launch items, battery, diagnostics (165 lines)
├── tests/
│   ├── __init__.py
│   ├── test_collection.py     # Integration tests for collectors
│   ├── test_exceptions.py     # Exception handling tests
│   └── test_utils.py          # Utility function tests
├── .github/
│   ├── workflows/
│   │   └── ci.yml             # CI/CD pipeline (lint, test, security scan)
│   └── ISSUE_TEMPLATE/        # GitHub issue templates
├── run.py                     # Development entry point (adds src to path)
├── pyproject.toml             # Project metadata, dependencies, tool configs
├── LICENSE                    # MIT License
├── README.md                  # User-facing documentation
└── AGENTS.md                  # This file (AI agent instructions)
```

## 🛠️ Development Standards

### 1. Code Style & Quality

- **Python Version**: 3.9+ (use `from __future__ import annotations` for forward compatibility)
- **Type Safety**: All functions MUST be typed. Use `TypedDict` schemas from `src/prose/schema.py`
- **Linting**: Ruff (line length: 100 chars, target: py39)
- **Type Checking**: Mypy with partial strictness
- **Testing**: pytest with coverage (target: src/prose)

**Before committing:**
```bash
ruff check . --fix
ruff format .
mypy src/prose --check-untyped-defs
pytest --cov=src/prose
```

### 2. Collector Implementation Guidelines

**Architecture:**
- Each collector module exports typed collection functions (e.g., `collect_system_info() -> SystemInfo`)
- `engine.py` orchestrates all collectors in `collect_all() -> SystemReport`
- All schemas are defined in `schema.py` using `TypedDict`

**Best Practices:**
- **Error Resilience**: Wrap external commands in try-except. One collector failure MUST NOT crash the entire report
- **Direct System Access**: Prefer `system_profiler`, `scutil`, `sw_vers` over hardcoded mappings
- **JSON Parsing**: Use `get_json_output()` wrapper for commands with `--json` flags (npm, pnpm, brew)
- **Timeout Management**: Use `timeout` parameter in `run()` for slow commands (diskutil, network diagnostics)
- **Logging**: Use `verbose_log()` for debug output, `log()` for user-facing messages

**Utilities (src/prose/utils.py):**
- `run(cmd, timeout, log_errors)` - Execute shell command with timeout
- `which(cmd)` - Check if command exists in PATH
- `get_version(cmd)` - Extract version string from command output
- `get_json_output(cmd)` - Parse JSON from command output
- `log(msg, level)` - Colored logging (info/success/warning/error/header)
- `verbose_log(msg)` - Debug logging (only shown with --verbose)

### 3. Data Privacy & Security

- **Read-Only**: NEVER modify system state. No writes, no installs, no configuration changes
- **PII Filtering**: Avoid collecting usernames, file paths with home directories, credentials
- **Safe Commands**: Only use standard macOS binaries or well-known package managers
- **Transparency**: All commands are logged in verbose mode for auditability

## 🧪 Testing Strategy

**Unit Tests** (`tests/test_*.py`):
- Test each collector independently with mocked system calls
- Test error handling for missing commands/permissions
- Test schema compliance (TypedDict validation)

**Integration Tests** (`.github/workflows/ci.yml`):
- Full system report generation on macOS runners
- JSON structure validation
- Coverage reporting to Codecov

**Running Tests:**
```bash
# All tests
pytest

# With coverage
pytest --cov=src/prose --cov-report=term-missing

# Specific test file
pytest tests/test_collection.py -v
```

## 🛡️ Operational Protocols

### 1. Adding New Data Points

1. **Schema First**: Update `src/prose/schema.py` with new TypedDict fields
2. **Implement Collector**: Add collection logic to appropriate collector module
3. **Update Engine**: Integrate collector call in `engine.py:collect_all()`
4. **Add Tests**: Write unit tests in `tests/test_collection.py`
5. **Update Docs**: Document in README.md if user-facing

### 2. Modifying Existing Collectors

- **Minimal Changes**: Only modify what's necessary
- **Backwards Compatibility**: Don't break existing JSON structure
- **Test Coverage**: Ensure tests pass after changes
- **Verbose Logging**: Add `verbose_log()` calls for debugging

### 3. Commit Conventions

Use conventional commits:
- `feat:` - New features or collectors
- `fix:` - Bug fixes
- `refactor:` - Code restructuring without behavior change
- `docs:` - Documentation updates
- `test:` - Test additions or fixes
- `chore:` - Build/tooling updates

**Examples:**
```
feat: add PostgreSQL version detection to database collector
fix: handle missing Wi-Fi interface gracefully
refactor: extract common version parsing logic to utils
docs: update AGENTS.md with new collector guidelines
```

## 🚀 Development Workflow

### Initial Setup

```bash
# Clone repository
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running the Tool

```bash
# Development (via run.py)
python3 run.py --verbose

# As installed package
macos-prose --verbose

# Generate only JSON (skip AI prompt)
python3 run.py --no-prompt

# Custom output location
python3 run.py --output custom_report.json

# Quiet mode (minimal output)
python3 run.py --quiet
```

### Development Commands

```bash
# Lint and format
ruff check . --fix && ruff format .

# Type check
mypy src/prose --check-untyped-defs

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/prose --cov-report=html

# Full CI simulation
ruff check . && ruff format --check . && pytest --cov=src/prose
```

## 📦 Package Structure

**Entry Points:**
- `macos-prose` command → `prose.engine:main()`
- `run.py` → development entry point (adds src to path, calls `prose.engine:main()`)

**Build System:**
- Hatchling (PEP 621 compliant)
- `src-layout` with `src/prose` as package root
- No runtime dependencies (pure Python stdlib)
- Dev dependencies: ruff, pytest, pytest-cov, mypy

**Metadata:**
- Package name: `macos-system-prose`
- Version: 1.0.0
- License: MIT
- Python: >=3.9
- Platform: macOS only (Darwin)

## 🔍 Key Implementation Details

### Schema Structure (src/prose/schema.py)

All data types are defined as `TypedDict`:
- `SystemReport` - Top-level report structure (15 sections)
- `SystemInfo` - OS version, model, SIP/FileVault/Gatekeeper
- `HardwareInfo` - CPU, memory, GPU, thermal pressure
- `DiskInfo` - Disk usage, APFS volumes
- `NetworkInfo` - IPs, interfaces, DNS, Wi-Fi, firewall
- `PackageManagers` - Union types for installed/not installed
- `DeveloperToolsInfo` - Languages, SDKs, cloud tools, extensions
- `EnvironmentInfo` - Shell, PATH, listening ports
- `BatteryInfo` - Percentage, cycle count, condition
- `DiagnosticsInfo` - Crash logs

### Engine Flow (src/prose/engine.py)

1. `main()` - CLI argument parsing (--verbose, --quiet, --no-prompt, --output)
2. `collect_all()` - Orchestrates all collectors, returns `SystemReport`
3. `generate_ai_prompt(data)` - Creates LLM-optimized text report
4. Writes `macos_system_report.json` and `macos_system_report.txt`

### Collector Organization

- **system.py**: `collect_system_info()`, `collect_hardware_info()`, `collect_disk_info()`
- **network.py**: `collect_network_info()`
- **packages.py**: `collect_package_managers()` (7 package managers)
- **developer.py**: `collect_languages()`, `collect_sdks()`, `collect_cloud_devops()`, `collect_databases()`, `collect_version_managers()`, `collect_infra()`, `collect_extensions()`, `collect_editors()`, `collect_dev_tools()`
- **environment.py**: `collect_processes()`, `collect_launch_items()`, `collect_login_items()`, `collect_kexts()`, `collect_electron_apps()`, `collect_environment_info()`, `collect_battery_info()`, `collect_cron_jobs()`, `collect_diagnostics()`

## 🚨 Common Pitfalls & Solutions

### Problem: Collector crashes on missing command
**Solution**: Always check with `which()` before running commands, use try-except blocks

### Problem: Command hangs indefinitely
**Solution**: Use `timeout` parameter in `run()` (default: 30s)

### Problem: JSON parsing fails
**Solution**: Use `get_json_output()` which handles empty output and malformed JSON

### Problem: Tests fail on non-macOS systems
**Solution**: Add `sys.platform == "darwin"` checks, use `@pytest.mark.skipif` for macOS-only tests

### Problem: New field breaks schema
**Solution**: Always update `TypedDict` in schema.py BEFORE implementing collector

## 📚 Additional Resources

- **GitHub Repo**: https://github.com/tuanductran/macos-system-prose
- **CI/CD Pipeline**: `.github/workflows/ci.yml` (test matrix: Python 3.9-3.12, macOS-latest)
- **Package Config**: `pyproject.toml` (Ruff, Mypy, pytest configs)
- **License**: MIT (see LICENSE file)

## 🎯 AI Agent Success Criteria

When working on this repository, you are successful if:
1. ✅ All collectors are properly typed and follow schema.py
2. ✅ Code passes ruff linting and formatting checks
3. ✅ All tests pass with good coverage
4. ✅ No system modifications are made (read-only guarantee)
5. ✅ Error handling is robust (one failure doesn't crash entire report)
6. ✅ Changes are minimal and surgical
7. ✅ Conventional commit format is used
8. ✅ Documentation is updated if user-facing changes are made
