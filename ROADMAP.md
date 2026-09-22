# Roadmap

## v1.1 — Correctness and trustworthy diagnostics

- [x] Remove stale HTML integration-test expectations.
- [x] Make network identity/public-IP collection opt-in.
- [x] Distinguish OCLP detection evidence from root-patch evidence.
- [x] Add macOS 27 metadata.
- [ ] Add collector status/error metadata so missing data is distinguishable from collector failure.
- [ ] Replace parallel collector/default arrays with a typed collector registry.
- [ ] Add privacy/redaction contract tests for every sensitive collector.

## v1.2 — OCLP-aware knowledge model

- [ ] Separate Apple-native compatibility from OCLP compatibility.
- [ ] Track OpenCore bootloader version independently from OCLP version.
- [ ] Model root-patch requirements and observed patch state separately.
- [ ] Add hardware-specific GPU, Wi-Fi, Bluetooth, T1 and USB compatibility facts.
- [ ] Add versioned OCLP knowledge fixtures sourced from official Dortania documentation.

## v1.3 — Diagnostics quality

- [ ] Add failure-injection tests for all collectors.
- [ ] Add per-collector timeout and execution metadata.
- [ ] Add fast/deep collection modes for expensive filesystem and log collectors.
- [ ] Replace recursive diff casts with a JSON-value type.
- [ ] Add machine-readable report schema/version metadata.

## Security and maintenance

- [ ] Pin all third-party GitHub Actions to immutable commit SHAs.
- [ ] Minimize workflow write permissions.
- [ ] Add a security policy and reproducible CI audit checklist.
- [ ] Keep Apple and OCLP knowledge explicitly dated and source-attributed.
