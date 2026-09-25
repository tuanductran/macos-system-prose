# Platform Compatibility

## CI-validated combinations

| Platform | Architecture | Python | Validation |
|---|---|---|---|
| macOS 15 | arm64 (Apple silicon) | 3.14 smoke + 3.9–3.14 matrix on `macos-latest` | Full tests / integration |
| macOS 15 | x86_64 (Intel) | 3.14 smoke | Full test suite |

`macos-latest` currently maps to an Apple-silicon runner. The repository keeps `macos-15` and `macos-15-intel` as deterministic compatibility baselines. GitHub also provides `macos-26` and `macos-26-intel`; those are current OS labels but are not yet part of this project's required compatibility baseline.

## Scope

- The project is macOS-only and uses macOS-native commands such as `system_profiler`, `sysctl`, `diskutil`, `ioreg`, `nvram`, `defaults`, and `log`.
- Python 3.9–3.14 is covered by the main arm64 matrix.
- Intel is covered by a separate Python 3.14 compatibility smoke test to avoid duplicating the full Python matrix.
- Apple-silicon-specific CPU/chip parsing uses `SPHardwareDataType` `chip_type`; Intel parsing retains the CPU label path.
- Missing architecture-specific signals must remain unknown rather than being interpreted as evidence that a feature is absent.
- Security-state commands (`csrutil`, `spctl`, and `fdesetup`) preserve unavailable or unrecognized output as `null`/unknown rather than coercing it to `false`.

## OCLP compatibility is a separate contract

OCLP compatibility is not equivalent to native macOS support. The OCLP knowledge model is source-dated and tracks its supported target range separately from the runtime architecture contract.

Current upstream OCLP documentation targets macOS Big Sur 11.x through Sequoia 15.x. macOS 26/Tahoe project metadata must not be treated as proof of OCLP support.

## Known limitations

- The current CI contract does not execute the full Python-version matrix on Intel; Intel receives a dedicated Python 3.14 smoke test.
- Some collectors depend on permissions or macOS services and may legitimately return unknown/empty values.
- Platform-sensitive command output can change across macOS releases; deterministic fixtures cover the current Intel/Apple-silicon parsing contract, while unavailable security signals remain explicitly unknown.
- Root-patch state is evidence-driven and is not inferred solely from OCLP non-detection.