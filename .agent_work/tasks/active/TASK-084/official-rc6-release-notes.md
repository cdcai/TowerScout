# TowerScout v0.1.0-rc6 Release Notes

TowerScout `v0.1.0-rc6` is a controlled release-candidate package for the
Windows package path. It provides separate digest-pinned Application Package
variants for normal CPU users and support-validated NVIDIA GPU workstations.

## Assets

Download one Application Package variant and the shared Model & Data Package
from this release's `Assets` section.

Normal/non-GPU users:

- `towerscout-v0.1.0-rc6-cpu.zip`
- `towerscout-v0.1.0-rc6-cpu.zip.sha256`
- `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

Support-assigned GPU users:

- `towerscout-v0.1.0-rc6-cuda121.zip`
- `towerscout-v0.1.0-rc6-cuda121.zip.sha256`
- `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

Do not use GitHub's automatic source-code ZIP/TAR.GZ downloads for the normal
package workflow.

## Artifact Identity

| Artifact | SHA-256 or digest |
|---|---|
| CPU Application Package ZIP | `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d` |
| CUDA 12.1 Application Package ZIP | `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603` |
| Shared Model & Data Package ZIP | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu@sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd` |
| CUDA image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121@sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0` |
| Source ref | `12daa5536f580f76d063559e86b9a474451bc54b` |

## Validation Summary

- CPU package Docker setup/readiness passed.
- CPU package Podman setup/readiness passed with an approved package-local
  `podman-compose` provider.
- CUDA package Docker CPU-fallback setup/readiness passed.
- CPU package `-Gpu on` refused before container startup with package-aware
  guidance to use the CUDA package.
- CUDA package Docker GPU validation passed on the support GPU host with
  `selected_device=cuda`.
- CUDA package Podman GPU CDI validation passed on the support GPU host with
  `selected_device=cuda`.
- Google and Azure provider detection both completed on CUDA during the support
  GPU validation pass.

## Support Boundaries

- The CPU package is the default for normal users.
- The CUDA package is only for support-validated NVIDIA GPU workstations.
- Podman remains support-assigned and requires a running Podman machine plus an
  approved non-Docker-Desktop Compose provider.
- Restricted-network/offline preload, source-build validation, and large-AOI
  performance are outside this release-candidate's default tester path.
- Testers and support should not share API keys, full `.env` files, private
  AOIs, raw logs, raw provider responses, browser network traces, tile/map
  URLs, or provider portal screenshots unless an approved handling procedure is
  in place.
