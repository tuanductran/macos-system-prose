# OpenCore Legacy Patcher Reference

**Reviewed:** 2026-09-24  
**Upstream:** Dortania OpenCore Legacy Patcher

This document is a source-backed reference for the OCLP evidence model used by `macos-system-prose`. It is not a substitute for the upstream OCLP guide and does not infer a security posture from OCLP presence or absence.

## Current upstream facts

The current OCLP documentation describes the project as targeting Intel Macs and documents macOS **Big Sur 11.x through Sequoia 15.x** as its supported target range. The upstream FAQ also says versions outside that documented range are not supported. Keep this separate from Apple's macOS release stream: this repository contains macOS 26/Tahoe metadata, but that does **not** make OCLP 15.x documentation evidence for macOS 26 support.

The upstream changelog currently has **2.5.1** as its latest release entry. Release/version information is kept as source metadata and must not be used to recommend an upgrade for a particular machine.

## Evidence model

The collector intentionally separates:

1. **OpenCore evidence** — for example the OpenCore NVRAM version.
2. **OCLP application evidence** — OCLP NVRAM version or the installed `OpenCore-Patcher.app`.
3. **Root-patch evidence** — the observed root-patch marker and patched framework evidence.
4. **Hardware evidence** — IORegistry observations for Wi-Fi, Bluetooth, T1, USB 1.1 and camera components.
5. **Compatibility model** — Apple-native support, OCLP model support, OCLP documented OS range, root-patch requirements and observed state.

These signals must not be collapsed into a single claim such as “OCLP is installed, therefore SIP is disabled” or “OCLP is absent, therefore SIP is enabled.”

## Root patches

OCLP's patch documentation describes on-disk patches for legacy graphics, wireless, Bluetooth and other hardware-specific cases. Some systems also require support packages such as KDK or MetallibSupportPkg after updates.

The project therefore reports **requirements and evidence separately**:

- `root_patch_required`: compatibility/model logic
- `root_patch_state`: observed state (`not_detected`, `detected`, `unknown`)
- `root_patch_domains`: affected hardware domains
- `required_packages`: documented support packages
- `hardware_evidence`: what the current machine exposes
- `hardware_patch_requirements`: normalized requirement evidence

An unknown signal remains unknown; absence of an observed signal is not proof that the corresponding hardware or patch is absent.

## Version and update handling

OCLP's update guide describes application, OpenCore and root-patch updates as separate stages. It also documents special handling around major/minor macOS updates and post-update root patching.

`macos-system-prose` should therefore avoid language such as “fully up to date” unless it has independently collected the relevant application, OpenCore and root-patch versions.

## Relationship to Apple security state

OCLP documentation discusses SIP, Secure Boot and root patching in the context of unsupported hardware and OS combinations. Those concepts are evidence sources, not a license for the collector or AI prompt to infer security state.

For this project:

- SIP comes from the collected system/security evidence.
- Code-signing state comes from the code-signing collector.
- OCLP detection comes from OCLP/OpenCore evidence.
- Root-patch state comes from explicit patch evidence.
- Compatibility is a separate, typed model.

## Machine-readable source

The canonical machine-readable knowledge used by the application is:

`data/oclp_knowledge.json`

It includes explicit source URLs and a `checked_at` timestamp. Update the JSON when upstream OCLP documentation changes, then review the corresponding tests and prompt contract.

## Upstream references

- OCLP FAQ
- OCLP Supported Models
- OCLP Updating guide
- OCLP Patch Explanation
- OCLP Changelog

See the URLs in `data/oclp_knowledge.json` for the exact source locations.
