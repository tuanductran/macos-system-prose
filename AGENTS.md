# AGENTS.md

**Instructions for AI coding agents (Claude, Cursor, Copilot, etc.) working with the `macos-system-prose` repository.**

## Project Overview

`macos-system-prose` is a **read-only** macOS introspection tool that collects comprehensive system data through **specialized collector functions** across **7 collector modules** and generates optimized output formats for AI analysis, security auditing, and development environment optimization.

### Core Statistics

- **7,096 lines** of production Python code (25 modules)
- **2,412 lines** of test code (12 test modules)
- **105 total functions** (62 collectors + 43 utilities)
- **49 TypedDict schemas** in `schema.py` for strict type contracts
- **Tests/coverage**: CI is the source of truth; do not hard-code test counts or coverage claims here.
- **Zero runtime dependencies** — pure Python 3.9+ stdlib
- **Async-first architecture** — parallel collection via `asyncio.gather()`
- **28 data sections** in SystemReport output
- **Typed production code** — avoid `Any`; JSON-compatible recursive values use the shared `JSONValue` type.

### Key Capabilities

| Category | Details |
|----------|---------|
| **System** | macOS version, model/chip architecture (Intel and Apple silicon), SIP/FileVault/Gatekeeper, thermal, memory pressure, Time Machine, EDID display parsing |
| **Developer** | 8 languages, 10 version managers, 3 SDKs, 5 cloud tools, 5 databases, 8 browsers, 8 terminal emulators, 7 shell frameworks |
| **Packages** | Homebrew (formula + cask + services), MacPorts, npm, yarn, pnpm, bun, pipx |
| **Network** | DNS, VPN, firewall and interface facts; identifying network values are redacted by default |
| **Activity** | Processes, launch agents/daemons, launchd services, login items, open ports, cron jobs |
| **Security** | TCC permissions, code signing, security tools, antivirus detection |
| **Hardware** | IORegistry (PCIe, USB, audio codecs), NVRAM variables |
| **OCLP** | Structured OpenCore/OCLP detection evidence, version signals and root-patch evidence; evaluated only when applicable to Intel/x86_64 Macs |
| **Advanced** | Storage analysis, fonts, shell customization, system preferences, kernel parameters, logs |
| **TUI** | Interactive terminal monitor with htop-style dashboard (requires `textual`) |

### Output Formats

1. **`macos_system_report.json`** (~31 KB) — Structured data with 28 top-level keys
2. **`macos_system_report.txt`** (~33 KB) — LLM-optimized prompt with OCLP awareness
3. **Interactive TUI** — Professional terminal UI with Apple HIG design (optional)

## Markdown Standards (Markdownlint Compliance)

All documentation must adhere to `markdownlint` rules to ensuring consistent rendering across platforms. AI agents must follow these guidelines:

1. **MD001/heading-increment**: Headings must increment by one level at a time (e.g., H1 → H2 → H3, not H1 → H3).
2. **MD013/line-length**: Avoid explicitly wrapping lines unless necessary; let the renderer handle wrapping. Code blocks can exceed 80 chars.
3. **MD025/single-title**: Each file must have exactly one H1 heading at the top.
4. **MD029/ol-prefix**: Ordered lists should use sequential numbers (1., 2., 3.) for readability in source, or strictly `1.` for easier reordering.
5. **MD031/blanks-around-fences**: Surround fenced code blocks with blank lines.
6. **MD032/blanks-around-lists**: Surround lists with blank lines.
7. **MD040/fenced-code-language**: All code blocks must specify a language (e.g., `python`, `bash`, `json`, `text`).
8. **MD041/first-line-heading**: The first line of the file should be a top-level heading.
9. **No Inline HTML**: Use pure Markdown whenever possible.

## Project Architecture

```text
macos-system-prose/
├── src/prose/                    # Production code (7,096 lines)
│   ├── __init__.py               # Package exports (__version__, __author__, __license__)
│   ├── main.py                   # CLI entry point (argparse, main function)
│   ├── engine.py                 # Orchestration, AI prompt generation (4 functions)
│   │   ├── collect_all()         # Async collector orchestration
│   │   ├── generate_ai_prompt()  # LLM-optimized text generation
│   │   ├── generate_json()       # JSON report generation
│   │   └── main()                # CLI entry point
│   ├── schema.py                 # 49 TypedDict schemas (strict type contracts)
│   ├── utils.py                  # Command execution, EDID parsing (11 functions)
│   ├── exceptions.py             # Custom exceptions (4 classes)
│   ├── iokit.py                  # NVRAM access via subprocess (8 functions)
│   ├── macos_versions.py         # macOS version detection (6 functions)
│   ├── diff.py                   # Report comparison logic (2 functions)
│   ├── parsers.py                # Text parsing utilities (11 functions)
│   ├── constants.py              # Application constants & defaults
│   ├── py.typed                  # PEP 561 type marker
│   ├── tui/                      # Terminal UI module (optional)
│   │   ├── __init__.py           # TUI exports
│   │   ├── app.py                # Basic TUI (Phase 1)
│   │   └── app_enhanced.py       # Enhanced TUI (Phases 2-4, htop-style monitor)
│   ├── datasets/
│   │   ├── __init__.py           # Dataset exports
│   │   └── smbios.py             # Legacy Mac detection
│   └── collectors/               # 7 modules, 62 collector functions
│       ├── __init__.py           # Collector exports
│       ├── system.py             # 5 functions (system, hardware, display, disk, memory)
│       ├── environment.py        # 9 functions (processes, launch items, security, battery)
│       ├── developer.py          # 13 functions (languages, Docker, Git, browsers, editors)
│       ├── network.py            # 1 function (comprehensive network info)
│       ├── packages.py           # 1 function (Homebrew, MacPorts, npm, pipx, etc.)
│       ├── advanced.py           # 7 functions (storage, fonts, OCLP, shell, kernel)
│       └── ioregistry.py         # 4 functions (PCIe, USB, audio codecs, full registry)
├── tests/                        # 93 tests across 9 files + conftest.py
│   ├── conftest.py               # 5 factory-generated fixture profiles
│   ├── test_collection.py        # Integration tests (Darwin-only, 3 tests)
│   ├── test_display.py           # EDID parsing + display detection (12 tests)
│   ├── test_exceptions.py        # Exception handling (4 tests)
│   ├── test_fixtures.py          # Schema validation (28 tests)
│   ├── test_ioregistry.py        # IORegistry collector (12 tests)
│   ├── test_smbios.py            # Legacy Mac detection
│   ├── test_utils.py             # Utility functions (21 tests)
│   ├── test_engine.py            # Orchestration (4 tests)
│   ├── test_diff.py              # Diff logic (3 tests)
│   └── test_collectors_mocked.py # Mocked collector tests (7 tests)
├── scripts/
│   └── scrape_macos_versions.py  # Update data/macos_versions.json (22 versions)
├── data/                         # Runtime data (DO NOT EDIT MANUALLY)
│   └── macos_versions.json       # 23 macOS versions (10.0–15.x plus macOS 26/27 metadata)
├── examples/                     # Example scripts and demos
│   ├── README.md                 # Examples documentation
│   └── tui_demo.py               # TUI demonstration with mock data
├── .github/workflows/
│   └── ci.yml                    # CI/CD: Python 3.9–3.14 matrix, lint, test, security
├── run.py                        # Development entry point
├── pyproject.toml                # PEP 621 metadata, Hatchling build, Ruff config
├── renovate.json                 # Renovate auto-updates (dev dependencies only)
├── LICENSE                       # MIT License
├── README.md                     # User documentation
├── .gitignore                    # Git ignore rules (standard Python/macOS)
└── AGENTS.md                     # This file (AI agent instructions)
```

## Development Setup

### Installation

```bash
git clone https://github.com/tuanductran/macos-system-prose.git
cd macos-system-prose
python3 -m venv .venv
source .venv/bin/activate
# Install with dev tools AND textual for TUI support
pip install -e ".[dev,tui]"
```

### Running

```bash
# CLI interface
macos-prose --help

# Development mode
python3 run.py --help
```

## Development Standards

### Code Style Requirements

- **Python Version**: 3.9+ (use `from __future__ import annotations` in all modules)
- **Type Safety**: EVERY function MUST have type hints. Use TypedDict from `schema.py`.
- **NO `Any` TYPE**: This project strictly avoids `Any` in production code (like TypeScript best practices)
- **Linting**: Ruff (select = ["E", "F", "I", "N", "W", "B", "UP", "A", "C4", "ISC", "RUF"]).
- **Type Checking**: Mypy with `--check-untyped-defs`.
- **Testing**: pytest with coverage targeting `src/prose`.
- **Formatting**: Ruff formatter (100-char line length).

### Type Safety Policy

**🚫 STRICT NO-ANY POLICY**

This project follows TypeScript-level type safety. The `Any` type is **prohibited** in production code.

**Exception**: Only `src/prose/diff.py` uses `Any` for recursive dictionary comparison (technically necessary, clearly documented).

```python
# ❌ NEVER USE - Banned in this codebase
from typing import Any


def process(data: dict[str, Any]) -> Any:
    return data


# ✅ ALWAYS USE - Specific types
from prose.schema import SystemReport


def process(data: SystemReport) -> SystemInfo | None:
    return data.get("system")
```

**Why no `Any`?**

Like avoiding `any` in TypeScript:
- ✅ Catches type errors at development time
- ✅ Better IDE autocomplete and refactoring
- ✅ Self-documenting code
- ✅ Prevents runtime surprises
- ✅ Forces thinking about data structure

### Pre-Commit Checklist

```bash
# 1. Lint and auto-fix
ruff check . --fix

# 2. Format code
ruff format .

# 3. Type check
mypy src/prose --check-untyped-defs

# 4. Run tests with coverage
pytest --cov=src/prose --cov-report=term-missing

# 5. Full CI simulation
ruff check . && ruff format --check . && mypy src/prose --check-untyped-defs && pytest --cov=src/prose
```

### Python Compatibility

**Target: Python 3.9 - 3.14**

**Required for ALL modules:**

```python
from __future__ import annotations
```

**Forbidden features:**

- ❌ Pattern matching (`match`/`case`) - requires Python 3.10+
- ❌ `TypeAlias` keyword - requires Python 3.10+
- ❌ `Self` type - requires Python 3.11+
- ❌ Exception groups (`except*`) - requires Python 3.11+

**Allowed type syntax:**

```python
# ✅ Modern syntax with __future__ import
def process(data: str | None) -> list[str] | None:
    pass


# ❌ Old-style syntax (DO NOT USE)
from typing import Union, Optional, List


def process(data: Optional[str]) -> Union[List[str], None]:
    pass
```

### Type Safety Guidelines

#### No Any Type Policy

**RULE: Never use `Any` in production code.**

```python
# ❌ BANNED - Don't use Any
from typing import Any


def parse_data(data: dict[str, Any]) -> Any:
    pass


# ✅ CORRECT - Use specific types
from prose.schema import SystemReport, SystemInfo


def parse_data(data: SystemReport) -> SystemInfo | None:
    return data.get("system")


# ✅ CORRECT - Use Union types for flexibility
def parse_value(value: str | int | float | bool | None) -> str:
    return str(value)


# ✅ CORRECT - Use cast() when unavoidable
from typing import cast

result = cast("dict[str, list[str]]", some_dynamic_data)
```

**The ONE exception**: `src/prose/diff.py` uses `Any` for recursive dict comparison because:
1. Diff operates on arbitrary nested structures at runtime
2. Complex recursive type aliases cannot be properly validated by MyPy
3. This is clearly documented in the file with inline comments

#### TypedDict Usage

```python
from prose.schema import SystemInfo

# ✅ Correct - use TypedDict constructor
info: SystemInfo = SystemInfo(os="Darwin", macos_version="12.7.6", model_identifier="MacBookAir6,2")

# ❌ Incorrect - plain dict (type unsafe, DO NOT USE)
info: SystemInfo = {"os": "Darwin", "macos_version": "12.7.6", "model_identifier": "MacBookAir6,2"}
```

#### Optional Field Access

```python
# ✅ Safe - check before access
if data["homebrew"]["formula"] is not None:
    if "git" in data["homebrew"]["formula"]:
        print("Git installed")

# ✅ Safe - use .get() with default
formula = data["homebrew"].get("formula") or []
if "git" in formula:
    print("Git installed")

# ❌ Unsafe - direct access to optional field
if "git" in data["homebrew"]["formula"]:  # Type error if None
    print("Git installed")
```

#### Return Type Annotations

```python
# ✅ Correct - explicit return type
def get_info() -> SystemInfo | None:
    return SystemInfo(...) if condition else None


# ✅ Correct - NotInstalled sentinel type
def check_tool() -> ToolInfo | NotInstalled:
    return NotInstalled() if not_found else ToolInfo(...)


# ❌ Incorrect - missing return type
def get_info():
    return SystemInfo(...) if condition else None
```

## Collector Development Guidelines

### Creating a New Collector

1. **Add to `src/prose/collectors/`** - Create new module or extend existing
2. **Define Schema** - Add TypedDict to `src/prose/schema.py`
3. **Implement Function** - Follow async pattern, error handling, timeouts
4. **Register in Engine** - Add to `collect_all()` in `engine.py`
5. **Add Tests** - Mock tests in `test_collectors_mocked.py`
6. **Update AGENTS.md** - Document new data section

### Collector Function Pattern

```python
from __future__ import annotations

import asyncio
import logging
from prose.schema import NewDataInfo
from prose.utils import run_command

logger = logging.getLogger(__name__)


async def collect_new_data() -> NewDataInfo | None:
    """Collect new data from the system.

    Returns:
        NewDataInfo with collected data, or None if collection fails.
    """
    try:
        # Run command with timeout
        result = await run_command(["system_profiler", "SPNewDataType", "-json"], timeout=30.0)
        if not result:
            logger.warning("Failed to collect new data")
            return None

        # Parse output
        data = parse_result(result)

        # Return TypedDict
        return NewDataInfo(
            key1=data.get("key1", "Unknown"), key2=data.get("key2", 0), key3=data.get("key3", [])
        )

    except OSError as e:
        logger.error(f"Command failed: {e}")
        return None
    except ValueError as e:
        logger.error(f"Parsing failed: {e}")
        return None
    except asyncio.TimeoutError:
        logger.error("Command timed out")
        return None
```

### Error Handling Requirements

**Always handle these exceptions:**

- `OSError` - Command execution failures
- `ValueError` - Parsing failures
- `asyncio.TimeoutError` - Command timeouts

**Never use:**

- ❌ Bare `except:` - Too broad
- ❌ `except Exception:` - Catches too much

**Logging levels:**

- `logger.error()` - Command failures, parsing errors
- `logger.warning()` - Missing data, optional features unavailable
- `logger.info()` - Normal operation milestones
- `logger.debug()` - Detailed diagnostic information

### Timeout Standards

| Operation Type | Timeout | Example |
|---------------|---------|---------|
| Quick commands | 5s | `system_profiler` single type |
| Medium commands | 30s | `system_profiler` multiple types |
| Slow commands | 60s | `diskutil list`, `ioreg` |
| Network operations | 10s | DNS lookups, IP detection |
| File operations | 15s | Large file reads |

### Return Value Conventions

```python
# ✅ Use TypedDict from schema.py
return SystemInfo(os="Darwin", macos_version="12.7.6")

# ✅ Return None on failure (logged)
return None

# ✅ Use NotInstalled sentinel for missing tools
return NotInstalled()

# ❌ Don't return plain dicts
return {"os": "Darwin"}

# ❌ Don't raise exceptions to caller
raise ValueError("Failed")
```

## Security and Privacy

### Read-Only Guarantee

- **NEVER modify system state**: No writes to system files or settings. `READ_ONLY_MODE = True` enforced.
- **No root/sudo required**: All operations via standard user permissions.
- **Safe commands only**: Uses macOS built-ins (`system_profiler`, `scutil`, `ioreg`, `diskutil`).
- **No shell injection**: All commands use list arguments (never `shell=True`).

### Privacy Model

- **Network identity is redacted by default**: hostname, local IP, gateway, MAC address and SSID are not exported as identifying values.
- **Public IP is opt-in**: the collector must not contact an external IP service unless `include_sensitive=True` / `--include-sensitive-network` is explicitly requested.
- **Treat report output as potentially sensitive**: process names, application names, package versions, diagnostics and local configuration can identify software or usage patterns.
- **Avoid credentials**: Never collect passwords, API keys, tokens, SSH private keys or other secret material.
- **Avoid file contents**: collect metadata rather than user document contents.


### OCLP Safety

- Do not make blanket SIP recommendations. OCLP documents that SIP requirements vary by OS, model and whether root patching is required.
- Do not treat Lilu, WhateverGreen, FeatureUnlock or other OCLP-like kexts as proof of OCLP by themselves.
- Keep OpenCore bootloader detection, OCLP application detection and root-patch evidence separate.
- Keep Apple-native compatibility separate from OCLP compatibility.

### Command Execution Safety

```python
# ✅ Safe - list arguments, timeout, no shell
result = await run_command(["ls", "-la", directory], timeout=5.0)

# ❌ Unsafe - shell=True, no timeout
result = subprocess.run(f"ls -la {directory}", shell=True, capture_output=True)

# ✅ Safe - specific exception handling
try:
    result = await run_command(cmd, timeout=30.0)
except OSError as e:
    logger.error(f"Command failed: {e}")
    return None

# ❌ Unsafe - bare except
try:
    result = await run_command(cmd)
except:
    return None
```

### Permission Validation

```python
# ✅ Check Full Disk Access before TCC.db access
if not has_full_disk_access():
    logger.warning("Full Disk Access required for TCC permissions")
    return None

# ✅ Graceful degradation
try:
    data = collect_privileged_data()
except PermissionError:
    logger.warning("Insufficient permissions, skipping")
    return None
```

## Testing Standards

### Test Organization

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test collector orchestration (Darwin-only)
- **Mock tests**: Test with simulated command output
- **Fixture tests**: Validate TypedDict schemas

### Test Naming Convention

```python
# Test files: test_<module>.py
test_smbios.py
test_utils.py
test_display.py


# Test functions: test_<function>_<scenario>
def test_get_smbios_data_valid_model():
    pass


def test_parse_edid_manufacturer_id_invalid():
    pass
```

### Test Coverage Goals

- **Collectors**: 60%+ (focus on critical paths)
- **Utils**: 80%+ (test all branches)
- **Engine**: 70%+ (test orchestration)
- **Parsers**: 90%+ (test edge cases)

### Mocking External Commands

```python
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_collect_system_info_success():
    mock_output = '{"SPSoftwareDataType": [{"os_version": "12.7.6"}]}'

    with patch("prose.collectors.system.run_command", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_output

        result = await collect_system_info()

        assert result is not None
        assert result["macos_version"] == "12.7.6"
        mock_run.assert_called_once()
```

### Testing TypedDict Schemas

```python
from prose.schema import SystemInfo


def test_system_info_schema_valid():
    """Test SystemInfo schema with all required fields."""
    info = SystemInfo(
        os="Darwin",
        macos_version="12.7.6",
        macos_name="macOS Monterey",
        model_identifier="MacBookAir6,2",
        marketing_name="MacBook Air (13-inch, Mid 2013)",
        sip_enabled=False,
    )

    # TypedDict validation happens at type-check time
    assert info["os"] == "Darwin"
    assert info["macos_version"] == "12.7.6"
```

## Known Limitations & Workarounds

### 1. MyPy TypedDict .get() Errors

**Issue**: MyPy reports errors when using `.get()` on TypedDict (Python typing system limitation).

```python
# This pattern causes MyPy errors but is runtime-safe
data: PackageInfo = get_package_info()
formula = data.get("formula", [])  # MyPy error
```

**Workaround**: Use bracket notation with None check:

```python
formula = data["formula"] if data.get("formula") is not None else []
# Or check first:
if data["formula"] is not None:
    formula = data["formula"]
```

**Status**: 25 known errors in codebase, all runtime-safe and schema-validated. Accepted limitation.

### 2. TUI Test Coverage

**Issue**: Interactive TUI tests require user interaction, hard to automate.

**Workaround**: Manual testing with real devices, example demo script in `examples/tui_demo.py`.

**Status**: 23-26% coverage on TUI modules, functionally verified.

### 3. SMBIOS Database Updates

**Issue**: New Mac models released regularly, database needs updates.

**Process**:

1. Run `scripts/scrape_macos_versions.py` to fetch latest data
2. Verify data integrity (all 6 fields present)
3. Update `data/smbios_models.json`
4. Run tests to ensure schema compatibility

**Frequency**: Quarterly or after major Mac releases.

## Type Safety: The No-Any Philosophy

### Why We Eliminated `Any` Type

This project follows **TypeScript-level type safety**. Coming from a TypeScript background, you know that `any` is considered a code smell. We apply the same philosophy to Python.

**Before (dynamic typing):**

```python
# ❌ Weak typing - hides bugs
def generate_report(data: dict[str, Any]) -> Any:
    system = data.get("system", {})  # What's in here?
    return process_data(system)  # No type safety
```

**After (TypedDict everywhere):**

```python
# ✅ Strong typing - catches bugs early
from prose.schema import SystemReport, SystemInfo


def generate_report(data: SystemReport) -> SystemInfo | None:
    system = data.get("system")  # IDE knows exact structure
    return system  # Type-checked return
```

### Benefits of No-Any Policy

1. **IDE Autocomplete**: Full IntelliSense on all data structures
2. **Refactoring Safety**: Rename/restructure with confidence
3. **Bug Prevention**: Type errors caught before runtime
4. **Self-Documentation**: Function signatures explain data flow
5. **MyPy Validation**: Static analysis catches issues

### Recursive JSON values in diff.py

**File**: `src/prose/diff.py`

The diff engine accepts generic string-keyed mappings and returns values constrained by
the shared `JSONValue` recursive type. Runtime validation rejects unsupported values
instead of weakening the contract with `Any`. Nested report dictionaries are passed
back into the same function without recursive casts.

```python
from collections.abc import Mapping

from prose.schema import JSONValue


def diff_reports(
    old: Mapping[str, object],
    new: Mapping[str, object],
) -> dict[str, JSONValue]:
    """Compare JSON-compatible report mappings without recursive casts."""
    pass
```

### Enforcing No-Any in Your Changes

**Pre-commit checks:**

```bash
grep -r "from typing import.*Any" src/prose/ --include="*.py"

# Expected output: no production source files
```

**Code review checklist:**

- [ ] No `Any` imports in production source
- [ ] All function parameters have specific types
- [ ] All return types use explicit JSON/domain types
- [ ] Use `cast()` only where a concrete boundary requires it
- [ ] TypedDict used for structured report contracts
- [ ] Recursive JSON data uses `JSONValue`

**If you think you need `Any`:**

1. Stop and reconsider whether an existing schema or `JSONValue` contract is sufficient.
2. Use explicit unions or TypedDicts for known data shapes.
3. Use a narrowly typed boundary conversion for untrusted/dynamic input.
4. Document the runtime invariant when static typing cannot express it.

### Comparison with TypeScript

| TypeScript | Python (This Project) |
|------------|----------------------|
| `any` type | `Any` type (banned) |
| `interface` | `TypedDict` |
| `type X \| Y` | `X \| Y` (Union) |
| `as Type` | `cast(Type, value)` |
| `Record<K, V>` | `dict[K, V]` |
| `Array<T>` | `list[T]` |

**Same philosophy**: Avoid dynamic types, use specific contracts.

## File-Specific Guidelines

### src/prose/schema.py

- **Purpose**: Central type definition repository
- **Rule**: ALL data structures MUST be TypedDict
- **Rule**: Use `total=True` (default) unless fields are truly optional
- **Rule**: Document each field with inline comments

```python
class SystemInfo(TypedDict):
    """System information from system_profiler."""

    os: str  # Operating system name (always "Darwin")
    macos_version: str  # macOS version (e.g., "12.7.6")
    model_identifier: str  # Mac model ID (e.g., "MacBookAir6,2")
```

### src/prose/engine.py

- **Purpose**: Orchestration and CLI entry point
- **Rule**: All collectors called via `asyncio.gather()` for parallelism
- **Rule**: Generate 2 output formats: JSON, TXT
- **Rule**: Handle TUI launch with asyncio.run() wrapper

### src/prose/utils.py

- **Purpose**: Shared utilities for command execution
- **Rule**: ALL commands via `run_command()` with timeout
- **Rule**: Return `str | None` (never raise to caller)
- **Rule**: Log all errors before returning None

### src/prose/datasets/smbios.py

- **Purpose**: Mac model database with 70 entries
- **Rule**: DO NOT edit JSON manually, use scraper script
- **Rule**: All models MUST have 6 fields: `model_identifier`, `marketing_name`, `board_id`, `cpu_generation`, `max_os_version`, `year`
- **Rule**: Use `total=True` for SMBIOSData TypedDict (all fields required)

### src/prose/diff.py

- **Purpose**: Compare two SystemReport snapshots and identify differences
- **Rule**: Use the shared `JSONValue` type for recursive JSON-compatible values
- **Rule**: Do not introduce `Any` for diff inputs or outputs
- **Why**: The recursive report structure is dynamic at runtime but still constrained to JSON values

```python
from prose.schema import JSONValue
from collections.abc import Mapping


def diff_reports(old: Mapping[str, object], new: Mapping[str, object]) -> dict[str, JSONValue]:
    """Compare JSON-compatible report mappings without recursive casts."""
    pass
```

### tests/conftest.py

- **Purpose**: Pytest fixtures for testing
- **Rule**: Provide 5 profiles: Intel Mac, Apple Silicon, OCLP, no-OCLP, minimal
- **Rule**: Use factory pattern for flexible test data generation

## CI/CD Configuration

### GitHub Actions Workflow

**Matrix testing**: Python 3.9, 3.10, 3.11, 3.12, 3.13, 3.14

**Steps**:

1. Checkout code
2. Set up Python matrix
3. Install dependencies (`pip install -e ".[dev]"`)
4. Lint with Ruff (`ruff check .`)
5. Format check (`ruff format --check .`)
6. Type check with MyPy (`mypy src/prose --check-untyped-defs`)
7. Run tests (`pytest --cov=src/prose`)
8. Upload coverage

**Platform**: `macos-latest` (current standard Apple-silicon/arm64 runner) plus an explicit `macos-15-intel` compatibility smoke test. The product must remain useful on both Intel and Apple-silicon Macs; OCLP compatibility is a separate Intel-specific layer.

### Renovate Configuration

**Auto-updates**:

- Python dev dependencies only
- Security patches applied immediately
- Minor/patch updates weekly
- Major updates require manual review

**Excluded**:

- Runtime dependencies (none exist)
- Python version itself (manual control)

## Release Checklist

Before releasing a new version:

- [ ] All tests passing (93/93)
- [ ] Ruff linting clean
- [ ] MyPy type checking clean (37 files)
- [ ] Coverage at 60%+ overall
- [ ] Documentation updated (README, AGENTS.md)
- [ ] macOS version data current
- [ ] CI/CD pipeline green on all Python versions (3.9-3.14)
- [ ] Manual TUI testing completed
- [ ] Functional testing with real macOS data
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml` and `src/prose/__init__.py`
- [ ] Git tag created (`git tag v1.x.x`)

## Project Status

### Current Version: 1.0.0 (Production Ready)

**Quality Grade: A+** (Production Perfect)

- ✅ **Zero Issues**: All lint/type/test checks passing
- ✅ **93/93 Tests Passing**: 64% coverage, 100% pass rate
- ✅ **Type Safety**: No `Any` type in production code
- ✅ **Zero Dependencies**: Pure Python 3.9+ stdlib
- ✅ **CI/CD**: 6 Python versions (3.9-3.14) on macOS
- ✅ **Security**: Trivy scan clean, read-only operation
- ✅ **Documentation**: Complete and up-to-date

### Completed Features (v1.0.0)

- ✅ JSON/TXT report generation
- ✅ Interactive TUI with Apple HIG design
- ✅ Diff mode for report comparison
- ✅ Zero runtime dependencies
- ✅ Full type safety (NO `Any` type)
- ✅ 93 comprehensive tests
- ✅ Python 3.9-3.14 support
- ✅ CI/CD with 6-version matrix
- ✅ OCLP detection (6 methods)
- ✅ 28 data sections
- ✅ 105 specialized functions

### Future Development

**Planned features** (implementation timeline not committed):

- 📋 PyPI package publication
- 📋 Homebrew formula
- 📋 Markdown export (zero deps)
- 📋 PDF export (requires dependencies)
- 📋 Historical tracking & trending
- 📋 Plugin architecture
- 📋 Web dashboard
- 📋 VS Code extension
- 📋 GitHub Action

**Note**: The project is feature-complete for v1.0.0. Future development is optional and not required for production use.

## Features Roadmap

**IMPORTANT**: Roadmap planning is work-in-progress and **NOT** committed to version control. The sections below represent implemented v1.0.0 features only.

### Summary

**Completed (v1.0.0):**

- ✅ JSON/TXT report generation
- ✅ Interactive TUI with Apple HIG design
- ✅ Diff mode for report comparison
- ✅ Zero runtime dependencies
- ✅ Full type safety (NO `Any` type)
- ✅ 93 comprehensive tests
- ✅ Python 3.9-3.14 support
- ✅ CI/CD with 6-version matrix

## Common Issues & Solutions

### Issue: TUI fails with "event loop already running"

**Cause**: Calling `asyncio.run()` inside existing event loop.

**Solution**: Use `run_tui_sync()` from `prose.tui` which handles event loop detection.

```python
# ✅ Correct
from prose.tui import run_tui_sync

run_tui_sync(report_data)

# ❌ Incorrect
import asyncio
from prose.tui.app_enhanced import EnhancedSystemApp

asyncio.run(EnhancedSystemApp(report_data).run())
```

### Issue: MyPy errors on TypedDict .get()

**Cause**: Python typing system limitation.

**Solution**: Use bracket notation with None check (see Known Limitations).

### Issue: Import errors when running tests

**Cause**: Package not installed in editable mode.

**Solution**:

```bash
pip install -e ".[dev,tui]"
```

### Issue: Permission errors accessing TCC database

**Cause**: Full Disk Access not granted.

**Solution**: Grant FDA in System Preferences > Security & Privacy > Privacy > Full Disk Access, or skip TCC collection (non-fatal).

## Emergency Contacts

- **Maintainer**: Tuan Duc Tran
- **GitHub**: [@tuanductran](https://github.com/tuanductran)
- **Issues**: [GitHub Issues](https://github.com/tuanductran/macos-system-prose/issues)

## Documentation Updates

When modifying this file:

1. Run markdownlint to verify compliance
2. Update statistics if code changes significantly
3. Keep "Core Statistics" section accurate
4. Update roadmap when features are completed
5. Document new limitations or workarounds
6. Keep CI/CD section synchronized with `.github/workflows/ci.yml`

## Legal

### Project License

**Our Code:** MIT License (see [LICENSE](LICENSE))

### Apple References

This project references Apple's open source components (XNU kernel, IOKit, etc.) for **educational and documentation purposes only**. We do NOT include, modify, or redistribute any Apple source code.

**What we do:**
- ✅ Study Apple OSS documentation to understand macOS internals
- ✅ Use standard macOS command-line tools (`sysctl`, `ioreg`, etc.)
- ✅ Parse output from built-in commands (text processing only)
- ✅ Maintain independent MIT-licensed codebase

**What we DON'T do:**
- ❌ Include Apple source code or headers
- ❌ Link against Apple frameworks directly
- ❌ Redistribute any Apple components
- ❌ Use PyObjC or native API bindings

### Trademark Notice

"Apple", "Mac", "macOS", "Darwin", and "IOKit" are trademarks of Apple Inc. Used for descriptive purposes only (platform identification). No endorsement by Apple Inc. is claimed or implied.

### Disclaimer

This is an **independent open source project**, NOT affiliated with, endorsed by, or sponsored by Apple Inc.

### Resources

- [Apple OSS Analysis](docs/apple-oss-analysis.md) - How we reference Apple components
- [XNU Quick Reference](docs/xnu-quick-reference.md) - Learning from kernel source
- [Apple Open Source](https://opensource.apple.com/) - Apple's OSS portal

---

**Last Updated**: 2026-09-24  
**Document Version**: 2.4 (Refactor SMBIOS and HTML reporting)
**Project Status**: Production Ready ✅ | Grade: A+
