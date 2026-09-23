# Security Policy

## Supported versions

Security fixes are applied to the latest version on the `main` branch.

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues.

For a suspected vulnerability, use GitHub's private vulnerability reporting for this repository when available. Include:

- affected version or commit;
- macOS version and hardware model, when relevant;
- reproduction steps;
- expected and observed behavior;
- logs or proof of concept with secrets and personal data removed.

Do not include passwords, API tokens, private keys, public IP addresses, MAC addresses, Wi-Fi SSIDs, or other sensitive system identity data in a report.

## GitHub Actions security

Workflow changes should preserve least-privilege `GITHUB_TOKEN` permissions. Third-party Actions are pinned to immutable commit SHAs where practical.
