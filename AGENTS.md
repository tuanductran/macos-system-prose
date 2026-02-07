# AGENTS.md

Instructions for AI coding agents (Claude, Cursor, Copilot, etc.) when working with the `macos-system-prose` repository.

## Overview

`macos-system-prose` is a **read-only** introspection tool on Darwin (macOS) that collects comprehensive system data and generates optimized reports for AI performance analysis, security auditing, and development environment optimization.

**Key Capabilities:**

- **System**: Darwin/macOS version (SMBIOS enrichment), SIP/FileVault/Gatekeeper, thermal, memory pressure, Time Machine, EDID display parsing
- **Developer**: 8 languages, 3 SDKs, 5 cloud tools, 5 databases, 10 version managers, 5 IDEs, 8 browsers, 8 terminal emulators, 7 shell frameworks
- **Package Management**: Homebrew (formula + cask + service), MacPorts, npm, yarn, pnpm, bun, pipx
- **Network**: Public/local IP, DNS, Wi-Fi, VPN detection, firewall
- **Activity**: Processes, launch agents/daemons, launchd services, login items, open ports, cron jobs
- **Security**: Security tools, antivirus, TCC permissions, code signing verification
- **Hardware**: IORegistry (PCIe, USB, audio codecs), NVRAM
- **OCLP**: OpenCore Legacy Patcher detection via 7 methods (NVRAM, AMFI, SMBIOS, kexts, etc.)
- **Advanced**: Storage analysis, fonts, shell customization, system preferences, kernel parameters, system logs

**Outputs:**

- `macos_system_report.json` — Structured data
- `macos_system_report.txt` — Optimized prompt for LLMs (OCLP-aware)
- `macos_system_report.html` — Visual dashboard (dark theme)

## Project Architecture

```text
macos-system-prose/
├── src/prose/
│   ├── engine.py              # CLI, orchestration, AI prompt generation
│   ├── schema.py              # 47 TypedDicts defining data structure
│   ├── utils.py               # Command execution, logging, EDID parsing
│   ├── exceptions.py          # Custom exceptions
│   ├── iokit.py               # NVRAM access via subprocess
│   ├── macos_versions.py      # macOS version detection and mapping
│   ├── html_report.py         # HTML dashboard generation
│   ├── diff.py                # Report comparison logic
│   ├── py.typed               # PEP 561 type marker
│   ├── datasets/
│   │   └── smbios.py          # SMBIOS database and legacy Mac detection
│   └── collectors/            # 7 data collector modules
│       ├── system.py          # System, hardware, display, disk, EDID
│       ├── network.py         # Network, DNS, firewall, Wi-Fi, VPN
│       ├── packages.py        # Package managers, Homebrew services
│       ├── developer.py       # Languages, SDKs, Docker, browsers, extensions
│       ├── environment.py     # Processes, launch items, security, NVRAM, apps
│       ├── advanced.py        # Storage, fonts, OCLP, preferences, logs
│       └── ioregistry.py      # IORegistry: PCIe, USB, audio codecs
├── tests/                     # 10 test files + conftest.py (~107 tests)
│   ├── conftest.py            # Factory functions creating 5 in-memory fixture profiles
│   ├── test_collection.py     # Collector integration tests
│   ├── test_display.py        # EDID parsing and display detection
│   ├── test_exceptions.py     # Exception handling
│   ├── test_fixtures.py       # Schema validation with factory fixtures
│   ├── test_ioregistry.py     # IORegistry collector
│   ├── test_smbios.py         # SMBIOS database and legacy Mac detection
│   ├── test_utils.py          # Utility functions
│   ├── test_html_report.py    # HTML generation tests
│   ├── test_engine.py         # Engine orchestration tests
│   └── test_diff.py           # Diff logic tests
├── scripts/
│   ├── scrape_macos_versions.py # Scrape macOS versions from Apple Support
│   └── scrape_smbios_models.py  # Scrape Mac models from EveryMac
├── data/                      # Runtime data (DO NOT EDIT MANUALLY)
│   ├── macos_versions.json    # 22 macOS versions
│   └── smbios_models.json     # 70+ Mac models
├── .github/workflows/ci.yml   # CI/CD: lint, test, integration, security scan
├── run.py                     # Development entry point
├── pyproject.toml             # Metadata, dependencies, tool config
├── renovate.json              # Renovate dependency updates
├── LICENSE                    # MIT License
├── README.md                  # User documentation
└── AGENTS.md                  # This file
```

## Development Standards

### Code Style

- **Python**: 3.9+ (`from __future__ import annotations`)
- **Type Safety**: Every function MUST have type hints. Use `TypedDict` from `schema.py`.
- **Linting**: Ruff (100 chars/line, target py39, rules: E, F, I, N, W, B).
- **Type Checking**: Mypy (partial strict, see `pyproject.toml`).
- **Testing**: pytest with coverage (target: `src/prose`).

**Before Committing:**

```bash
ruff check . --fix
ruff format .
mypy src/prose --check-untyped-defs
pytest --cov=src/prose
```

### Collector Guidelines

**Architecture:**

- Each collector exports a typed function (e.g., `collect_system_info() -> SystemInfo`).
- `engine.py` orchestrates all collectors in `collect_all() -> SystemReport` (27 sections).
- All schemas are defined in `schema.py` using `TypedDict` (47 classes).

**7 Collectors (100+ functions total):**

| Module | Functions | Functionality |
| --- | --- | --- |
| `system.py` | 17 | System info + SMBIOS, hardware + memory pressure, display + EDID, disk + S.M.A.R.T., Time Machine |
| `network.py` | 4 | Network interfaces, VPN detection, DNS, firewall, Wi-Fi |
| `packages.py` | 9 | Homebrew (formula + cask + service), MacPorts, pipx, npm, yarn, pnpm, bun |
| `developer.py` | 13 | Languages, SDKs, clouds, Docker, browsers, extensions, editors, Git config, terminals, shell frameworks |
| `environment.py` | 18 | Processes, launch items, launchd services, kexts, system extensions, apps, Electron, security, TCC, code signing, iCloud, NVRAM, battery, cron, diagnostics |
| `advanced.py` | 8 | Storage analysis, fonts, shell customization, OCLP detection (7 methods), system preferences, kernel parameters, system logs |
| `ioregistry.py` | 4 | PCIe devices, USB devices, audio codecs from IORegistry |

**Principles:**

- **Fault Tolerance**: Wrap commands in try-except. A collector error MUST NOT crash the entire report.
- **System Access**: Prefer `system_profiler`, `scutil`, `sw_vers`, `ioreg` over hardcoded paths.
- **Parse JSON**: Use `get_json_output()` for commands with `--json` flags.
- **Timeouts**: Use `timeout` in `run()` (default 15s, increase for slow commands).
- **Logging**: `verbose_log()` for debugging, `log()` for user info.
- **Apple HIG**: Output values must be human-readable (e.g., `"32-bit Color"` instead of `"CGSThirtytwoBitColor"`, `"255.255.255.0"` instead of `"0xffffff00"`).

### Utility API

**`utils.py` (9 functions):**

| Function | Description |
| --- | --- |
| `run(cmd, description, timeout, log_errors, capture_stderr)` | Execute shell command with timeout |
| `which(cmd)` | Find command path (resolve symlinks) |
| `get_version(cmd)` | Get version string from command |
| `get_json_output(cmd)` | Parse JSON output from command |
| `get_app_version(app_path)` | Get .app version (3 fallback keys) |
| `safe_glob(path, pattern)` | Safe glob with error handling |
| `parse_edid(edid_bytes)` | Parse EDID display identification data |
| `log(msg, level)` | Colored logging (info/success/warning/error/header) |
| `verbose_log(msg)` | Debug logging (only visible with `--verbose`) |

**`iokit.py` (8 functions):**

| Function | Description |
| --- | --- |
| `read_nvram(variable, uuid)` | Read NVRAM variable via `nvram` command |
| `read_nvram_all()` | Read all NVRAM variables |
| `get_boot_args()` | Get boot-args |
| `get_csr_active_config()` | Get SIP configuration |
| `parse_amfi_boot_arg(boot_args)` | Parse AMFI bitmask flag |
| `get_oclp_nvram_version()` | Get OCLP version from NVRAM |
| `get_oclp_nvram_settings()` | Get OCLP settings from NVRAM |
| `get_secure_boot_model()` | Get SecureBootModel from NVRAM |

**`datasets/smbios.py` (5 functions):**

- 70+ Mac models with marketing name, board ID, CPU generation, max OS supported, stock GPU.
- `get_smbios_data(model_identifier)` — Lookup model metadata.
- `is_legacy_mac(model_identifier, current_macos_version)` — Check for unsupported OS.

### Security and Privacy

- **Read-Only**: NEVER change system state.
- **PII Filtering**: Avoid collecting usernames, home paths, credentials.
- **Safe Commands**: Use only standard macOS binaries.
- **Transparency**: All commands are logged in verbose mode.

## Testing

**10 Test Files + conftest.py (~107 tests):**

| File | Content |
| --- | --- |
| `test_collection.py` | Integration tests for system collectors (Darwin only) |
| `test_utils.py` | run, which, get_version, get_json_output, get_app_version, parse_edid |
| `test_exceptions.py` | ProseError, CollectorError, SystemCommandError, UnsupportedPlatformError |
| `test_display.py` | EDID parsing and display info collection (mock + real data) |
| `test_fixtures.py` | Schema validation with 5 fixture profiles |
| `test_ioregistry.py` | IORegistry collector (PCIe, USB, audio) with mock plist |
| `test_smbios.py` | SMBIOS database integrity, lookup, legacy Mac detection |
| `test_html_report.py` | HTML reporting logic |
| `test_diff.py` | Report comparison logic |
| `test_engine.py` | Engine orchestration and prompt generation logic |

**5 Fixture Profiles (conftest.py — in-memory):**

1. `macbookair6-2_monterey_oclp` — Intel MacBook Air 2013, OCLP
2. `macbookpro18-1_sequoia_m1pro` — Apple Silicon M1 Pro, Sequoia
3. `macbookpro18-1_ventura_m1` — Apple Silicon M1, Ventura
4. `imac19-1_bigsur_intel` — Intel iMac 2019, Big Sur, Docker
5. `macmini8-1_sonoma_server` — Intel Mac mini 2018, Sonoma

**CI/CD (`ci.yml`):**

- Test matrix: Python 3.9–3.14 on macOS-latest
- Ruff lint + format check
- Mypy type check (soft fail)
- pytest + coverage → Codecov
- Integration test: full report + JSON/TXT validation
- Security scan: Trivy on ubuntu-latest

```bash
pytest                                           # All tests
pytest --cov=src/prose --cov-report=term-missing # With coverage
pytest tests/test_smbios.py -v                   # Specific file
```

## Workflow

### Adding a New Data Point

1. Add a new `TypedDict` in `schema.py`.
2. Add the field to `SystemReport` in `schema.py`.
3. Implement the collector function.
4. Integrate it into `engine.py:collect_all()`.
5. Write unit tests.
6. Update fixtures in `conftest.py`.
7. Update `README.md` if user-facing.

### Modifying an Existing Collector

- Minimal changes.
- Do not break the JSON structure.
- Ensure tests pass.
- Add `verbose_log()` for debugging.

### Commit Convention

- `feat:` — New feature
- `fix:` — Bug fix
- `refactor:` — Refactoring
- `docs:` — Documentation
- `test:` — Tests
- `chore:` — Build/tooling

## Development Setup

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

```bash
python3 run.py --verbose       # Verbose run
python3 run.py --no-prompt     # JSON only
python3 run.py -o report.json  # Custom output path
python3 run.py --quiet         # Minimum output
python3 run.py --html          # HTML output
macos-prose --verbose          # Installed package entry point
```

```bash
ruff check . --fix && ruff format .                # Lint + format
mypy src/prose --check-untyped-defs                # Type check
pytest --cov=src/prose --cov-report=html           # Test + coverage
ruff check . && ruff format --check . && pytest --cov=src/prose  # Full CI simulation
```

## Technical Details

### Schema (schema.py — 47 TypedDicts)

**SystemReport** has 27 keys: `timestamp`, `system`, `hardware`, `disk`, `top_processes`, `startup`, `login_items`, `package_managers`, `developer_tools`, `kexts`, `applications`, `environment`, `network`, `battery`, `cron`, `diagnostics`, `security`, `cloud`, `nvram`, `storage_analysis`, `fonts`, `shell_customization`, `opencore_patcher`, `system_preferences`, `kernel_params`, `system_logs`, `ioregistry`

### Engine Flow (engine.py)

1. `main()` — Parse CLI arguments (`-v`, `-q`, `--no-prompt`, `-o`, `--diff`, `--html`)
2. `collect_all()` — Orchestrate collectors → `SystemReport`
3. If `--diff`: `diff_reports()` compares with baseline
4. If `--html`: `generate_html_report()` creates dashboard
5. `generate_ai_prompt(data)` — Create OCLP-aware prompt for LLMs
6. Write `macos_system_report.json`, `macos_system_report.txt`, and optionally `.html`

### OCLP Detection (advanced.py — 7 methods)

1. NVRAM `OCLP-Version` (most reliable)
2. `/Applications/OpenCore-Patcher.app` directory
3. Root patch marker plist
4. OCLP signature kexts (AMFIPass, RestrictEvents, Lilu, WhateverGreen, etc.)
5. Patched system frameworks
6. SMBIOS-based unsupported OS detection
7. Boot-args AMFI configuration parsing

### Runtime Data (`data/` directory)

- `macos_versions.json` — 22 macOS versions with metadata. Updated via `python3 scripts/scrape_macos_versions.py --write`.
- `smbios_models.json` — 70 Mac models. Updated via `python3 scripts/scrape_smbios_models.py --write`.
- **DO NOT EDIT JSON FILES MANUALLY** unless absolutely necessary.

### Package

- Entry point: `macos-prose` → `prose.engine:main()`
- Build: Hatchling (PEP 621), src-layout
- Dependencies: No runtime dependencies (pure Python stdlib)
- Dev Dependencies: ruff, pytest, pytest-cov, mypy

## Common Issues

| Issue | Solution |
| --- | --- |
| Collector crash (missing command) | Always check `which()`, use try-except |
| Command hangs | Use `timeout` in `run()` (default 15s) |
| JSON parse error | Use `get_json_output()` to handle empty/error JSON |
| Test fail on non-Darwin | Use `sys.platform == "darwin"` check |
| New field breaks schema | Update TypedDict in `schema.py` BEFORE implementation |
| App version detection fail | 3 fallback keys: CFBundleShortVersionString → CFBundleVersion → CFBundleGetInfoString |
| Code signing slow | Limit to 5 app samples, timeout 3s/app |
| TCC database needs FDA | Return empty list on PermissionDenied |
| `codesign` writes to stderr | Use `capture_stderr=True` in `run()` |
| NVRAM null bytes (OCLP) | Clean with `.replace("%00", "").replace("\x00", "")` |
| Raw API values | Use lookup maps to humanize (e.g., `_COLOR_DEPTH_MAP`, `_CONNECTOR_TYPE_MAP`) |

## Success Criteria

1. All collectors are typed and follow `schema.py`.
2. Code passes `ruff check .` and `ruff format --check .`.
3. All tests pass (`pytest`).
4. No system state changes (read-only).
5. Robust error handling (one error does not crash the report).
6. Minimal and accurate changes.
7. Conventional commits.
8. Documentation updated for user-facing changes.
9. Privacy respected (no PII).
10. Human-readable output values per Apple HIG.

## Project Statistics

| Metric | Value |
| --- | --- |
| Total Source Lines | ~4,800 (16 Python modules) |
| Collector Lines | ~2,800 (7 modules) |
| TypedDict Classes | 47 |
| Total Functions | ~110 |
| SMBIOS Models | 70+ |
| Tests | 107 (10 files + conftest.py) |
| Fixture Profiles | 5 (in-memory) |
| SystemReport Sections | 27 |
| Platform | Darwin (macOS) |
| Runtime Dependencies | 0 (pure stdlib) |
| Python CI Matrix | 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 |
