# Before You Install

> **Audience:** End users and Local IT. **Applies to:** The exact assigned
> release. **Last reviewed:** 2026-10-02. **Publication state:** Local draft.

## Confirm The Supported Environment

- Windows 11 on AMD64.
- Hardware virtualization and WSL 2 allowed by local policy.
- A modern browser.
- Normal outbound HTTPS access to the exact GitHub release, GHCR, and the
  selected map provider.
- Release-specific free disk for the ZIPs, image, extraction, and named
  volumes. CUDA needs materially more space than CPU.
- Docker Desktop installed, approved, and running for the default path.
- One site/user-owned restricted Google Maps or Azure Maps key.

Podman and GPU are not automatic alternatives. Use them only when support
assigns that exact path and confirms its additional prerequisites.

## Unsigned Package Boundary

The package's PowerShell scripts are intentionally unsigned. The supplied
`.cmd` and `.bat` wrappers use a process-scoped PowerShell execution-policy
setting; they do not change persistent machine policy.

The standard package supports only endpoints where the user and organization
permit that wrapper path. If trusted Authenticode signing, WDAC/AppLocker,
constrained-language approval, SmartScreen/EDR approval, or an organization
allowlist is required, stop and use the Local IT process. Do not select `Run
anyway` for unverified files, disable endpoint protection, or weaken persistent
execution policy.

## Stop Before Downloading If

- you do not have an exact release URL or tag from the release owner/support;
- the release record does not display authoritative SHA-256 values;
- Docker Desktop is unavailable or not approved and support has not assigned
  Podman;
- the workstation cannot meet the release's disk/network requirements;
- the required provider account/key is not approved; or
- site policy requires a signature or allowlist that is not already approved.

Continue with [Choose Your Setup](Choose-Your-Setup).
