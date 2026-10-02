# Install And First Run

> **Audience:** End users. **Applies to:** The exact assigned release.
> **Last reviewed:** 2026-10-02. **Publication state:** Local draft.

Use the `docs\quick-start.html` or `docs\quick-start.md` shipped inside the
Application Package for exact commands. This page explains the flow.

## 1. Download Four Files

From the exact [GitHub release](https://github.com/J-Schulein/TowerScout/releases),
download:

- one CPU or support-assigned CUDA Application Package ZIP;
- its `.sha256` sidecar;
- the shared Model & Data Package ZIP; and
- its `.sha256` sidecar.

Use release `Assets`, not the green `Code` button or GitHub-generated source
archives. A draft, branch, or numerically newer tag is not approved by
inference.

## 2. Verify Before Extraction

Calculate SHA-256 for both ZIPs. Each value must match its sidecar and the value
displayed in the authoritative release record. Stop if any value is absent or
different.

## 3. Extract With File Explorer

Use `Extract All` on only the verified Application Package ZIP. A user-writable
path containing spaces is supported. Keep both ZIPs and both sidecars beside
the extracted package folder. Do not normally extract the Model & Data Package.

## 4. Run The Supplied Setup Wrapper

Open Windows PowerShell in the extracted folder and follow the exact shipped
Quick Start. The default setup path verifies prerequisites, checks both ZIPs,
imports assets into named volumes, pulls/starts the pinned image, and opens the
loopback browser application.

If co-location is not possible, the shipped guide shows how to pass both exact
quoted `-PackageZip` and `-AssetZip` paths.

## 5. Complete Setup Wizard

`setup_required` is normal before a provider is configured. Enter the approved
Google or Azure key privately in Setup Wizard or Settings. Do not send it to
support. When provider validation and asset checks pass, readiness should
become `ready`.

## 6. Run A Small Approved Smoke

Use a public/non-sensitive support-approved location. Estimate tiles first,
keep the area small, run detection, review results, and export only if the
local workflow permits it. Do not use a private investigation AOI for the first
smoke.

For later use, see [Everyday Commands](Everyday-Commands).
