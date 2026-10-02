# TowerScout Project Overview

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-02
**Audience**: Package users, Local IT, support leads, and release reviewers
**Runtime scope**: The CPU Application Package is the primary path; the CUDA
12.8 Application Package, Podman CPU, Docker GPU, and Podman GPU are
support-assigned paths after workstation-specific engine, Compose-provider,
and NVIDIA validation.

TowerScout is a local web application for identifying likely cooling towers
from satellite and aerial imagery. Cooling towers can be relevant during
Legionnaires' disease outbreak investigations and registry-building work.

This document is the package-local project overview used by the running
app Resource Links section.

## What The Package Provides

The package provides a Windows-first local path:

- A GitHub Release CPU Application Package ZIP for normal users.
- A GitHub Release CUDA 12.8 Application Package ZIP for support-validated
  NVIDIA GPU workstations.
- A shared GitHub Release Model & Data Package ZIP used by both package
  variants.
- A pinned GHCR container image digest in each Application Package.
- Docker Desktop primary runtime configuration, with qualified Podman
  package-runtime support when a site explicitly chooses that path.
- A CPU-safe default launcher.
- Optional Docker and Podman GPU launch controls for validated NVIDIA hosts.
- Windows setup, bootstrap, launch, stop, status, log, asset import, and TLS CA
  helper scripts.
- Package-local docs.
- Source, license, provider, model, data, SBOM, image, and release-manifest
  notices.
- A separate asset bundle contract for model weights and ZIP-code data.

The normal user path is package-based. Source checkout, Python virtual
environment, and Conda setup guides are legacy/source-install support material,
not the preferred package path.

## What Users Need Installed

Package users need Windows 11 AMD64, PowerShell, a modern browser, normal outbound
internet access, WSL 2/hardware virtualization support for Docker Desktop, and
Docker Desktop installed, approved, and running as the primary engine.
Plan for at least `15 GB` of free disk space for the CPU package. The measured
CUDA image is `14.4 GB`; plan for at least `35 GB` free for pull/unpack and
runtime data, or `60 GB` for a support-directed source qualification build.
Podman is a qualified support path only when support tells the user to use it
and the workstation already has a running Podman machine plus an approved
Compose provider. Users also need one site/user-owned restricted Google Maps or
Azure Maps provider key.

The CUDA package expects Volta-or-newer NVIDIA hardware, while release support
is limited to exact combinations named in release notes. Maxwell and Pascal
use the CPU path. GPU hosts need a current NVIDIA or OEM production Windows
driver that lists the exact GPU. Do not install a Linux display driver in WSL;
Podman CDI must be refreshed and reverified after Windows driver updates.

The package path does not require Git, Python, Conda, Node.js, VS Code, or a
source-code checkout.

The Windows PowerShell scripts in the control package are intentionally
unsigned. Users run the supplied `.cmd`/`.bat` wrappers, which use a process-
scoped execution-policy setting without changing persistent machine policy.
The standard package supports only endpoints where that path is permitted.
Trusted-publisher, WDAC/AppLocker, constrained-language, or organization-
allowlisting requirements need site-administrator approval and are outside the
standard support claim.

## Main Workflow

A typical TowerScout user:

1. Opens the TowerScout GitHub Releases page, selects the exact release support
   provided, and downloads the assigned Application Package variant, the shared
   Model & Data Package, and matching checksum files from the release `Assets`
   section.
2. Compares each ZIP's local SHA-256 and sidecar with the value displayed in
   the authoritative release record before extracting or unblocking it.
3. Extracts only the Application Package ZIP, leaves the Model & Data Package
   ZIP beside the extracted folder, and runs `setup-towerscout.cmd` for first
   setup so the package can find the asset ZIP, verify checksums, import
   assets, and start TowerScout.
4. Uses `start.bat -Engine docker -Gpu off` for later direct launches.
5. Configures Google Maps or Azure Maps in Setup Wizard or Settings.
6. Chooses a provider.
7. Defines a search area.
8. Estimates tile count.
9. Runs detection.
10. Reviews detections and adds manual corrections.
11. Exports CSV, KML, or dataset results.

The User Guide is available in the running app Resource Links section and at:

```text
http://localhost:5000/docs/user-guide.html
```

## Release Boundary

The supported target is:

- Windows 11 AMD64.
- Single-user local use.
- CPU baseline.
- Normal outbound internet access.
- CPU Application Package on Docker Desktop as the primary runtime, with
  qualified Podman package-runtime support only where explicitly approved.
- One site/user-owned restricted Google Maps or Azure Maps provider key.

Out of scope for the current package path: macOS, ARM64, air-gapped or fully
offline installs, VDI, shared multi-user hosting, managed remote deployment,
native installer behavior, and signature-enforcing managed endpoints without
separate site approval or allowlisting.

GPU launch is optional and support-assigned. The default launch remains
CPU-safe. The CPU package rejects `-Gpu on`; Docker GPU and Podman GPU use the
CUDA package only after support validates the selected engine's NVIDIA
container path and readiness reports `selected_device=cuda`.

## Provider Keys

TowerScout uses Google Maps or Azure Maps browser SDKs. Browser map SDK keys are
visible to someone with access to the running browser app. For this package, provider
keys are expected to be site/user-owned and restricted. Unrestricted shared
TowerScout project keys are unsupported.

Users and sites should configure provider-side restrictions, API/service
scoping, quotas, billing alerts, monitoring, and key rotation according to
local policy.

## License And Source

The YOLO-enabled package/image is not Apache-2.0-only. It is distributed
with AGPL-3.0 obligations because it includes Ultralytics YOLOv5 runtime source
and YOLO-derived detector weights.

The release package includes:

- `LICENSE`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md`
- `PROVIDER_TERMS.md`
- `SOURCE.txt`
- `SBOM.txt`
- `IMAGE.txt`
- `release-manifest.v1.json`

When TowerScout is running, the local source/license notice is available from
these local routes:

```text
http://localhost:5000/license      formatted browser page
http://localhost:5000/license.txt  plain-text combined notices
```

## Research Article And Videos

Research article:

```text
https://pubmed.ncbi.nlm.nih.gov/38906615/
```

Video guides:

```text
https://www.youtube.com/@thaddeussegura8452/videos
```
