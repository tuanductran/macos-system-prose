# Platform Compatibility

## CI-validated combinations

| Platform | Architecture | Python | Validation |
|---|---|---|---|
| macOS 26 | arm64 (Apple silicon) | 3.11–3.14 | Full test matrix + integration |
| macOS 15 | arm64 (Apple silicon) | 3.14 | Compatibility smoke test + report generation |
| macOS 15 | x86_64 (Intel) | 3.14 | Compatibility smoke test + report generation |

The primary CI matrix is pinned to `macos-26` (Apple silicon). The repository keeps `macos-15` and `macos-15-intel` as deterministic compatibility baselines so both current Apple-silicon and Intel execution paths are exercised. GitHub documents `macos-26` and `macos-15` as Apple-silicon labels and `macos-15-intel` as an Intel label. Intel macOS runner support is scheduled to end after the macOS 15 runner image retires in Fall 2027.

## Scope

- The project is macOS-only and uses macOS-native commands such as `system_profiler`, `sysctl`, `diskutil`, `ioreg`, `nvram`, `defaults`, and `log`.
- Python 3.11–3.14 is covered by the main arm64 matrix.
- Intel is covered by a separate Python 3.14 compatibility smoke test to avoid duplicating the full Python matrix.
- Apple-silicon-specific CPU/chip parsing uses `SPHardwareDataType` `chip_type`; Intel parsing retains the CPU label path.
- Missing architecture-specific signals must remain unknown rather than being interpreted as evidence that a feature is absent.
- Security-state commands (`csrutil`, `spctl`, and `fdesetup`) preserve unavailable or unrecognized output as `null`/unknown rather than coercing it to `false`.

## Runtime target vs CI validation

The package metadata targets macOS 10.15+, but the CI contract is narrower: macOS 15 and macOS 26 are the currently validated runtime environments. Older macOS versions are not treated as continuously validated compatibility targets unless a dedicated CI job is added.

## OCLP compatibility is a separate contract

OCLP compatibility is not equivalent to native macOS support. The OCLP knowledge model is source-dated and tracks its supported target range separately from the runtime architecture contract.

Current upstream OCLP documentation targets macOS Big Sur 11.x through Sequoia 15.x. macOS 26/Tahoe project metadata must not be treated as proof of OCLP support.

## Known limitations

- The current CI contract does not execute the full Python-version matrix on Intel; Intel receives a dedicated Python 3.14 smoke test.
- Some collectors depend on permissions or macOS services and may legitimately return unknown/empty values.
- Platform-sensitive command output can change across macOS releases; deterministic fixtures cover the current Intel/Apple-silicon parsing contract, while unavailable security signals remain explicitly unknown.
- Root-patch state is evidence-driven and is not inferred solely from OCLP non-detection.