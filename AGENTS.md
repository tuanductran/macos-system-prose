# AGENTS.md

## Project

macos-system-prose is a read-only macOS introspection and reporting tool. It collects system facts through focused collectors, validates them against TypedDict contracts, and emits structured and AI-oriented reports.

## Source of truth

- src/prose/ is production code.
- tests/ is the executable contract.
- data/ contains versioned reference datasets.
- docs/ contains maintained documentation.
- pyproject.toml is the tool and package configuration.
- uv.lock is committed and must stay in sync with dependency changes.
- CI is the source of truth for supported Python versions and final verification.

## Architecture

```text
src/prose/
├── main.py                 # CLI entry point
├── engine.py               # report orchestration and AI prompt rendering
├── schema.py               # TypedDict report contracts
├── utils.py                # compatibility facade for shared helpers
├── collectors/
│   ├── system.py           # OS, hardware, displays and storage
│   ├── environment.py      # processes, startup, security and environment
│   ├── developer.py        # developer tools and SDKs
│   ├── network.py          # network and connectivity
│   ├── packages.py         # package managers
│   ├── advanced.py         # storage, fonts, preferences and diagnostics
│   ├── oclp.py             # OpenCore/OCLP evidence collection
│   └── ioregistry.py       # IORegistry evidence
├── tui/                    # optional Textual UI
├── datasets/               # bundled lookup data
├── iokit.py                # NVRAM/IOKit helpers
├── oclp.py                 # OCLP compatibility model
├── macos_versions.py       # macOS metadata
├── diff.py                 # report comparison
├── constants.py
└── exceptions.py
```

Keep each collector focused on one domain. Do not add unrelated collection logic to engine.py, utils.py, or another collector merely because it is convenient.

## Development

Use uv:

```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src/prose --check-untyped-defs
uv run pytest
```

The supported Python range is 3.9–3.14. Runtime dependencies remain zero; optional TUI/development dependencies belong in the appropriate extras.

## Code standards

- Use from __future__ import annotations.
- Keep public functions typed and prefer the existing TypedDict contracts.
- Do not introduce Any into production code.
- Keep subprocess calls argument-vector based; never use shell=True.
- Put explicit timeouts on external commands.
- Preserve graceful degradation when a macOS command or permission is unavailable.
- Keep privacy-sensitive values out of verbose logs.
- Never infer security state from the absence of OCLP/OpenCore evidence.
- Avoid collecting user document contents or credentials.
- Prefer small focused modules over another large catch-all utility or collector file.
- Add regression tests for behavior and privacy contracts when changing collectors.

## Git and repository hygiene

Do not commit:

- virtual environments, caches, coverage output or build artifacts;
- generated reports;
- local configuration or credentials;
- editor/OS metadata;
- temporary scraper output.

The root .gitignore is intentionally small and project-specific. Maintained documentation belongs in version control.

## Testing expectations

Before merging a functional change:

1. Run Ruff lint and formatting checks.
2. Run MyPy.
3. Run the complete pytest suite.
4. Run the repository CI workflow.
5. Review the changed-file list for accidental files or generated artifacts.

For security/privacy changes, also search changed paths for raw credentials, network identity, NVRAM values and verbose logging.

## Data and documentation

Reference data must remain source-backed and dated where applicable. Maintenance scripts should be explicit and deterministic. Do not add demo fixtures merely to illustrate the API; use tests/fixtures when synthetic data is required for automated verification.

## Safety model

This project is read-only. A collector may inspect system state but must not modify settings, install software, write system files, or require root privileges.

When documenting security, OCLP, Apple OSS or compatibility behavior, distinguish collected evidence from inference and cite the underlying source where practical.
