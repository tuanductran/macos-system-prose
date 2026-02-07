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

**Current Collectors (as of v1.1.0):**
- **system.py**: System info, hardware (with memory pressure), disk, Time Machine
- **network.py**: Network interfaces, VPN, DNS, firewall, Wi-Fi
- **packages.py**: Package managers (Homebrew services, npm, yarn, pnpm, bun, pipx, MacPorts)
- **developer.py**: Languages, SDKs, cloud tools, Docker (detailed), Git config, terminal emulators, shell frameworks, browsers, extensions
- **environment.py**: Processes, launch items, launchd services, kexts, system extensions, applications, battery, cron, diagnostics, security tools, TCC permissions, code signing, iCloud sync

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
- Version: 1.1.0 (Phase 2-4 features added)
- License: MIT
- Python: >=3.9
- Platform: macOS only (Darwin)

## 🔍 Key Implementation Details

### Schema Structure (src/prose/schema.py)

All data types are defined as `TypedDict`:

**Core System (18 sections total):**
- `SystemReport` - Top-level report structure
- `SystemInfo` - OS version, model, SIP/FileVault/Gatekeeper, Time Machine
- `HardwareInfo` - CPU, memory, GPU, thermal pressure, **memory pressure stats**
- `DiskInfo` - Disk usage, APFS volumes, S.M.A.R.T. health
- `NetworkInfo` - IPs, interfaces, DNS, Wi-Fi, firewall, VPN

**Package Management:**
- `PackageManagers` - Homebrew (**with services**), MacPorts, npm, yarn, pnpm, bun, pipx
- `BrewService` - Homebrew service status (name, status, user, file)

**Developer Tools:**
- `DeveloperToolsInfo` - Languages, SDKs, cloud tools, extensions, **Git config, terminal emulators, shell frameworks**
- `DockerInfo` - Docker daemon, **containers (DockerContainer)**, **images (DockerImage)**
- `GitConfig` - Git global config (user, email, aliases, settings)
- `BrowserInfo` - Browser detection with versions

**System Activity:**
- `EnvironmentInfo` - Shell, PATH, listening ports, **launchd services**
- `LaunchdService` - Service status with PID and exit codes
- `ProcessInfo` - Top processes (CPU/memory)
- `LaunchItems` - Launch agents/daemons
- `BatteryInfo` - Percentage, cycle count, condition

**Kernel & Extensions:**
- `KernelExtensionsInfo` - Third-party kexts, **system extensions (macOS 10.15+)**
- `SystemExtension` - Extension identifier, version, state, team ID

**Security & Privacy:**
- `SecurityInfo` - Security tools, antivirus, **TCC permissions, code signing sample**
- `TCCPermission` - Privacy permissions (camera, microphone, etc.)
- `CodeSigningInfo` - App signing verification (authority, validity, team ID)

**Cloud & Sync:**
- `CloudInfo` - iCloud sync status
- `CloudSyncInfo` - iCloud Drive, sync state, storage usage

**Diagnostics:**
- `DiagnosticsInfo` - Crash logs
- `CronInfo` - Cron jobs
- `ApplicationsInfo` - All apps (with version fallback support)

### Engine Flow (src/prose/engine.py)

1. `main()` - CLI argument parsing (--verbose, --quiet, --no-prompt, --output)
2. `collect_all()` - Orchestrates all collectors, returns `SystemReport`
3. `generate_ai_prompt(data)` - Creates LLM-optimized text report
4. Writes `macos_system_report.json` and `macos_system_report.txt`

### Collector Organization (v1.1.0)

**system.py** (172 lines):
- `collect_time_machine_info()` - Time Machine backup status
- `collect_display_info()` - Display specs (resolution, refresh rate)
- `collect_memory_pressure()` - **NEW** Real-time memory stats
- `collect_hardware_info()` - CPU, GPU, memory, thermal, **memory pressure**
- `collect_disk_health()` - S.M.A.R.T. disk health
- `collect_disk_info()` - Disk usage, APFS volumes, health
- `collect_system_info()` - OS version, SIP, FileVault, Gatekeeper

**network.py** (95 lines):
- `collect_network_info()` - IPs, interfaces, DNS, Wi-Fi, firewall, VPN

**packages.py** (104 lines):
- `collect_homebrew_services()` - **NEW** Homebrew service status
- `homebrew_info()`, `macports_info()`, `pipx_info()`
- `npm_global_info()`, `yarn_global_info()`, `pnpm_global_info()`, `bun_global_info()`
- `collect_package_managers()` - Aggregates all package managers

**developer.py** (218 lines):
- `collect_docker_info()` - **ENHANCED** Docker with container/image details
- `collect_browsers()` - Browser detection with versions
- `collect_languages()` - Node, Python, Go, Rust, Ruby, Java, PHP, Perl
- `collect_sdks()` - Xcode, Android SDK, Flutter
- `collect_cloud_devops()` - AWS, GCP, Terraform, kubectl, Helm
- `collect_databases()` - Redis, MongoDB, MySQL, PostgreSQL, SQLite
- `collect_version_managers()` - nvm, asdf, pyenv, rbenv, goenv, rustup
- `collect_extensions()` - VS Code, Cursor, Windsurf, Zed extensions
- `collect_editors()` - Detect installed code editors
- `collect_git_config()` - **NEW** Git global configuration
- `collect_terminal_emulators()` - **NEW** Terminal app detection
- `collect_shell_frameworks()` - **NEW** oh-my-zsh, starship, etc.
- `collect_dev_tools()` - Aggregates all developer tools

**environment.py** (265 lines):
- `collect_processes()` - Top 15 CPU/memory processes
- `collect_launch_items()` - Launch agents/daemons
- `collect_login_items()` - Login startup items
- `collect_launchd_services()` - **NEW** User domain services (top 50)
- `collect_environment_info()` - Shell, PATH, ports, **launchd services**
- `collect_battery_info()` - Battery health and status
- `collect_cron_jobs()` - User crontab
- `collect_diagnostics()` - Recent crash logs
- `collect_system_extensions()` - **NEW** macOS 10.15+ extensions
- `collect_kexts()` - Kernel extensions + **system extensions**
- `collect_all_applications()` - All apps with version detection
- `collect_electron_apps()` - Electron-based apps
- `collect_tcc_permissions()` - **NEW** TCC privacy permissions (requires FDA)
- `collect_code_signing_sample()` - **NEW** Code signing verification (sample 10 apps)
- `collect_cloud_sync()` - **NEW** iCloud Drive status
- `collect_security_tools()` - Security apps, antivirus, **TCC, code signing**

## 🚨 Common Pitfalls & Solutions

### Problem: Collector crashes on missing command
**Solution**: Always check with `which()` before running commands, use try-except blocks

### Problem: Command hangs indefinitely
**Solution**: Use `timeout` parameter in `run()` (default: 15s, adjust for slow commands like codesign)

### Problem: JSON parsing fails
**Solution**: Use `get_json_output()` which handles empty output and malformed JSON

### Problem: Tests fail on non-macOS systems
**Solution**: Add `sys.platform == "darwin"` checks, use `@pytest.mark.skipif` for macOS-only tests

### Problem: New field breaks schema
**Solution**: Always update `TypedDict` in schema.py BEFORE implementing collector

### Problem: App version detection fails (Phase 2 fix)
**Solution**: Use fallback keys: CFBundleShortVersionString → CFBundleVersion → CFBundleGetInfoString

### Problem: Memory pressure collection slow
**Solution**: Already optimized with 5s timeout and error suppression

### Problem: Code signing verification too slow
**Solution**: Limit to 10 app samples with 5s timeout per app

### Problem: TCC database requires Full Disk Access
**Solution**: Returns empty list gracefully, document FDA requirement in logs

## 📚 Additional Resources

- **GitHub Repo**: https://github.com/tuanductran/macos-system-prose
- **CI/CD Pipeline**: `.github/workflows/ci.yml` (test matrix: Python 3.9-3.12, macOS-latest)
- **Package Config**: `pyproject.toml` (Ruff, Mypy, pytest configs)
- **License**: MIT (see LICENSE file)

## 🎯 AI Agent Success Criteria

When working on this repository, you are successful if:
1. ✅ All collectors are properly typed and follow schema.py
2. ✅ Code passes ruff linting and formatting checks
3. ✅ All tests pass with good coverage (target: 30%+)
4. ✅ No system modifications are made (read-only guarantee)
5. ✅ Error handling is robust (one failure doesn't crash entire report)
6. ✅ Changes are minimal and surgical
7. ✅ Conventional commit format is used
8. ✅ Documentation is updated if user-facing changes are made
9. ✅ Performance is acceptable (<60s for full report, Phase 3/4 adds ~5-10s)
10. ✅ Privacy considerations respected (no PII, FDA requirements documented)

## 📊 Project Statistics (v1.1.0)

- **Total Lines of Code**: ~1,231 (collectors: 854, utils: 89, schema: 224, engine: 50)
- **Test Coverage**: 30% (25 tests passing)
- **Schema Completeness**: 100% (all Typedicts defined)
- **Collectors**: 5 modules, ~40 collection functions
- **Features**: 18 data collection sections
- **Platform**: macOS only (Darwin)
- **Dependencies**: Zero runtime (pure stdlib)
- **Python Support**: 3.9, 3.10, 3.11, 3.12

## 🚀 Version History

- **v1.0.0** (Initial): Basic system introspection (system, hardware, network, packages, developer tools)
- **v1.1.0** (Current):
  - **Phase 2**: Homebrew services, Docker details, Git config, Launchd services (+248 lines)
  - **Phase 3**: Memory pressure, System extensions, Terminal emulators, Shell frameworks
  - **Phase 4**: TCC permissions, Code signing verification, iCloud sync (+347 lines)
  - Total additions: ~595 lines across 6 files
  - New TypeDicts: BrewService, LaunchdService, DockerContainer, DockerImage, GitConfig, MemoryPressure, SystemExtension, TCCPermission, CodeSigningInfo, CloudSyncInfo, CloudInfo
