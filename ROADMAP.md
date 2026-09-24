# Roadmap

## v1.1 — Correctness and trustworthy diagnostics

- [x] Remove stale HTML integration-test expectations.
- [x] Make network identity/public-IP collection opt-in.
- [x] Distinguish OCLP detection evidence from root-patch evidence.
- [x] Add macOS 27 metadata.
- [x] Add collector status/error metadata so missing data is distinguishable from collector failure.
- [x] Replace parallel collector/default arrays with a typed collector registry.
- [x] Add privacy/redaction contract tests for sensitive collectors and redact credential-bearing Git configuration.

## v1.2 — OCLP-aware knowledge model

- [x] Add dated Apple OSS references for Darwin/XNU, launchd, system commands and IOKit terminology.

- [x] Separate Apple-native compatibility from OCLP compatibility.
- [x] Track OpenCore bootloader version independently from OCLP version.
- [x] Model root-patch requirements and observed patch state separately.
- [x] Add hardware-specific GPU, Wi-Fi, Bluetooth, T1, camera and USB evidence fields.
- [x] Keep hardware compatibility evidence typed and separate from collector compatibility rules.
- [x] Add versioned OCLP knowledge fixtures sourced from official Dortania documentation.
- [x] Normalize hardware evidence into source-backed root-patch requirements without promoting unknown evidence.
- [x] Propagate OCLP hardware evidence and patch requirements into the AI prompt contract.

## v1.3 — Diagnostics quality

- [x] Add failure-injection tests for all registered collectors.
- [ ] Add per-collector timeout and execution metadata.
- [ ] Add fast/deep collection modes for expensive filesystem and log collectors.
- [ ] Replace recursive diff casts with a JSON-value type.
- [ ] Add machine-readable report schema/version metadata.

## Security and maintenance

- [x] Pin all third-party GitHub Actions to immutable commit SHAs.
- [x] Minimize workflow write permissions.
- [x] Add a security policy and reproducible CI audit checklist.
- [x] Keep Apple and OCLP knowledge explicitly dated and source-attributed.


