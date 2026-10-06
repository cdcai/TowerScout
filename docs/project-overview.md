# TowerScout Project Overview

The authoritative release record controls the exact supported package. Verify
its public SHA-256 values before extracting either downloaded ZIP.

**Applies to**: The next documentation-aligned Windows release.

**Last reviewed**: 2026-10-02.

**Audience**: End users, Local IT, repository maintainers, and people deciding
whether TowerScout fits their needs.

## What TowerScout Does

TowerScout runs on one Windows 11 x64 computer and helps a person review aerial
or satellite images for possible cooling towers. A machine-learning model
suggests locations; a human reviews, corrects, and exports the results.
TowerScout does not confirm that a structure is a cooling tower and does not
replace investigation or public-health judgment.

## What You Choose

Users make three independent choices among supported options:

1. **Docker Desktop or Podman Desktop** as the local container engine.
2. **CPU or a compatible NVIDIA GPU** for model processing.
3. **Google Maps or Azure Maps** for maps, imagery, search, and geocoding.

The project does not assign these choices. Each option still has requirements:
the final release record identifies exact tested engine/GPU combinations, and
the user or organization owns provider accounts, billing, keys, quotas, and
usage rights. CPU is the simplest processing path; GPU requires the
`-cuda128` package and exact supported NVIDIA prerequisites.

## What The Release Contains

The public GitHub release provides:

- one CPU Application Package ZIP and checksum;
- one CUDA 12.8 Application Package ZIP and checksum;
- one shared Model & Data Package ZIP and checksum; and
- a release record containing authoritative SHA-256 values, exact image
  digests, tested-support scope, source identity, and known limitations.

Users download one Application Package variant, not both. Docker or Podman
then downloads the matching digest-pinned container image from GHCR. The Model
& Data ZIP imports model weights and ZIP-code data into persistent named
volumes. GitHub's automatic source archives are not installation packages.

## Beginner Requirements

- Windows 11, 64-bit x64 processor, supported Windows build, and hardware
  virtualization.
- WSL 2 and one allowed/running container engine.
- At least the final release's tested RAM and free-disk requirement (plan at
  least 15 GB for CPU or 35 GB for CUDA unless the release says more).
- Internet access to the exact GitHub release, GHCR, and selected map provider.
- One provider credential prepared using the
  [credential walkthrough](quick-start.md#prepare-one-map-provider-credential).
- Python 3.12 only when using TowerScout's tested package-local Podman Compose
  provider.
- For GPU: a listed NVIDIA GPU/driver/engine combination; Podman additionally
  needs validated NVIDIA CDI.

Users do not need Git, Node.js, Conda, a source checkout, or a manual container
image download for the normal package path.

## Credential And Privacy Boundary

TowerScout currently accepts one credential per provider and uses it in both
browser and application requests. The browser can see that credential. Use a
dedicated limited provider project/account, API restrictions, quotas, alerts,
monitoring, and rotation. A site that requires split browser/server
credentials, Microsoft Entra ID, or a credential that is never browser-visible
is outside the current configuration model.

Search areas, imagery, provider responses, session data, logs, uploads, and
exports may be sensitive. Keep them under approved local custody. Never place
keys, `.env`, private AOIs, raw logs/screenshots, traces, certificate details,
or investigation exports in public support records.

## Windows Security Boundary

The Application Package is intentionally unsigned. Supported `.cmd` and
`.bat` wrappers start Windows PowerShell with a process-only setting; they do
not change persistent execution policy. Signature-enforcing or organization-
allowlisted endpoints are outside the standard claim. Do not disable
SmartScreen, Defender/EDR, WDAC/AppLocker, TLS verification, or another
organizational control.

Before extraction, compare each ZIP's calculated SHA-256 with both its
downloaded sidecar and the authoritative value printed in the final release
record.

## Storage And Lifecycle

TowerScout binds its browser interface to `localhost`. Docker and Podman each
use separate named volumes for configuration, models, data, logs, sessions,
temporary review data, uploads, and cache. Normal stop/start and reboot retain
those volumes. Switching engines does not migrate data. Important results
should be exported to an approved folder; internal session data is not a
backup.

## Where To Start

Use [Quick Start](quick-start.md) for a complete beginner path. The
[User Guide](user-guide.md) explains normal work after installation. The
[Local IT Administrator Guide](local-it-administrator-guide.md) covers policy,
network/TLS, custody, and advanced recovery.

The `rc4` packages were a preliminary diagnostic baseline, not the final
documentation-aligned release. The final release requires new image digests,
package hashes, browser-download validation, and independent-host evidence.
