# TowerScout v0.1.0-rc7 Release Notes Draft

**Draft status**: Pre-build review draft. Artifact hashes, image digests, source
ref, and validation run identifiers are intentionally marked `TBD` until the
rc7 images and packages are built and validated.

TowerScout `v0.1.0-rc7` is a controlled release-candidate package for the
Windows package path. It keeps the rc6 CPU/CUDA package model and adds the
validated provider TLS repair baseline for managed-network users.

## Assets

Download one Application Package variant and the shared Model & Data Package
from this release's `Assets` section.

Normal/non-GPU users:

- `towerscout-v0.1.0-rc7-cpu.zip`
- `towerscout-v0.1.0-rc7-cpu.zip.sha256`
- `towerscout-v0.1.0-rc7-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-v0.1.0-rc7-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

Support-assigned GPU users:

- `towerscout-v0.1.0-rc7-cuda121.zip`
- `towerscout-v0.1.0-rc7-cuda121.zip.sha256`
- `towerscout-v0.1.0-rc7-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-v0.1.0-rc7-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

Do not use GitHub's automatic source-code ZIP/TAR.GZ downloads for the normal
package workflow.

## What Changed Since rc6

- Added the `TASK-086` managed-network provider TLS repair baseline.
- Added `scripts\repair-provider-tls.cmd` as the preferred support entry point
  for Google Maps or Azure Maps TLS trust failures inside the container.
- Centralized provider HTTP/TLS handling so validation, geocoding, imagery, map
  proxy, and no-key TLS checks classify and redact provider failures
  consistently.
- Improved Setup Wizard and Settings behavior so repairable provider TLS trust
  failures are not treated as invalid keys, and Azure can still be saved when
  Google needs TLS repair but Azure is selected and valid.
- Corrected the Setup Wizard repair guidance so the suggested TLS repair command
  preserves the active container engine and GPU mode instead of defaulting CUDA
  or Podman users to the Docker CPU command.
- Hardened provider URL redaction so successful detections, sessions, exports,
  support artifacts, and UI-facing tile records do not expose credential-bearing
  provider URLs.
- Replaced the validation package's inline provider verifier with an
  in-container temporary verifier script, avoiding Compose quote-stripping
  issues seen during internal TLS validation.

The one-click browser repair/restart helper is not part of rc7. That concept is
tracked separately as `TASK-087` and remains a follow-on plan gated behind host
helper transport, security, product-integration, and managed-network validation
proofs.

## Managed-Network TLS Repair

On managed networks, Google Maps or Azure Maps validation can fail even when a
provider key is correct because the Linux container does not automatically
inherit the Windows organization/root TLS inspection CA.

The rc7 repair baseline is the support-guided command path:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

Use the same engine and GPU mode the tester selected for setup. For Azure
validation failures, support can use `-Provider azure`. For CUDA package
validation, support should preserve the assigned GPU mode, such as `-Gpu auto`
or `-Gpu on`.

When the Setup Wizard or Settings surface provider TLS repair guidance, the
suggested dry-run command should already use the active runtime engine and GPU
mode. Support should still review the dry-run output before running the matching
`-Apply` command.

The dry-run output may include local certificate subjects and thumbprints. Treat
that output as support-sensitive. Do not paste certificate subjects,
thumbprints, provider keys, full `.env` files, raw logs, provider responses,
browser network traces, screenshots, or sensitive AOIs into public issue
comments or release evidence.

## Artifact Identity

| Artifact | SHA-256 or digest |
|---|---|
| CPU Application Package ZIP | `TBD after rc7 package build` |
| CUDA 12.1 Application Package ZIP | `TBD after rc7 package build` |
| Shared Model & Data Package ZIP | `TBD after rc7 package build` |
| CPU image | `TBD after rc7 image publish` |
| CUDA image | `TBD after rc7 image publish` |
| Source ref | `TBD after release commit/tag selection` |

## Validation Summary

Pre-build validation target:

- Task-086 source tests and focused package/config/route tests pass.
- CPU and CUDA rc7 images publish successfully from the selected source ref.
- CPU and CUDA Application Package ZIPs are digest-pinned to the published
  images.
- Package manifests, checksum sidecars, and `SHA256SUMS.txt` verification pass.
- Package hygiene checks confirm no local `.env`, logs, sessions, temp files,
  uploads, caches, screenshots, helper tokens, raw certificate material, or raw
  support artifacts are included.
- Downloaded CPU package validation passes setup, asset import, readiness, and
  provider setup path.
- Downloaded CUDA package validation passes assigned CPU-fallback or GPU path
  validation according to the selected support host.
- Managed-network TLS repair has passed CPU validation and is owner-confirmed
  for the CUDA package path from the internal V3 validation package.

Final rc7 release notes should replace this section with the actual validation
results and command evidence summary after package build and downloaded-release
validation.

## Support Boundaries

- The CPU package is the default for normal users.
- The CUDA package is only for support-validated NVIDIA GPU workstations.
- Podman remains support-assigned and requires a running Podman machine plus an
  approved non-Docker-Desktop Compose provider.
- Provider TLS repair remains a support-guided script path in rc7; there is no
  one-click browser repair button in this release.
- Restricted-network/offline preload, source-build validation, and large-AOI
  performance are outside this release-candidate's default tester path.
- Testers and support should not share API keys, full `.env` files, private
  AOIs, raw logs, raw provider responses, browser network traces, tile/map
  URLs, certificate subjects, certificate thumbprints, provider portal
  screenshots, or unreviewed support artifacts unless an approved handling
  procedure is in place.
