# TASK-084 Official RC6 Release Handoff

**Date**: 2026-06-17  
**Status**: PUBLISHED_AND_POST_VALIDATED - official GitHub release publication
and downloaded-release verification passed on 2026-06-17.
**Target release tag**: `v0.1.0-rc6`  
**Target source ref**: `12daa5536f580f76d063559e86b9a474451bc54b`
**Published release URL**:
`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc6`

## Publication Boundary

The repository is public. Do not publish or commit raw GPU evidence files that
contain the fixed test AOI, local validation paths, or host-specific context.
Use only the public-safe evidence summary:

` .agent_work/context/analysis/TowerScout-rc6-gpu-validation-evidence-emailsafe/TowerScout-rc6-gpu-validation-evidence/PUBLIC-SUMMARY.md`

The local raw evidence packet remains internal/email-safe only.

## Required Release Assets

Upload these six files to the official `v0.1.0-rc6` GitHub release:

| Asset | Local path | SHA-256 |
|---|---|---|
| CPU Application Package | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip` | `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d` |
| CPU checksum sidecar | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip.sha256` | sidecar contains the CPU package SHA-256 |
| CUDA Application Package | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip` | `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603` |
| CUDA checksum sidecar | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip.sha256` | sidecar contains the CUDA package SHA-256 |
| Shared Model & Data Package | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip` | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| Shared Model & Data checksum sidecar | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip.sha256` | sidecar contains the asset package SHA-256 |

The optional public validation evidence attachment is
`PUBLIC-SUMMARY.md`; do not attach the raw email-safe evidence folder.

## Image Identity

| Package | Pinned image |
|---|---|
| CPU | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu@sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd` |
| CUDA 12.1 | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121@sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0` |

## Local Validation Already Complete

- Package summaries passed for both control ZIPs; each contains the expected
  scripts, docs, Compose files, compliance notices, `release-manifest.v1.json`,
  and `webapp/asset_manifest.v1.json`.
- Manifest checks passed for the expanded CPU and CUDA package directories.
- Agent-work validation passed.
- `git diff --check` passed.
- Secret/provider-key scan over public evidence summaries returned
  `matches: 0`.
- Targeted public-summary grep found no raw AOI, local user path, key-preview
  string, or common provider-key pattern.

## Recommended Release Settings

- Tag: `v0.1.0-rc6`
- Title: `TowerScout v0.1.0-rc6`
- Target: `12daa5536f580f76d063559e86b9a474451bc54b`
- Mark as prerelease: yes
- Mark as latest: no
- Release notes source:
  `.agent_work/tasks/active/TASK-084/official-rc6-release-notes.md`

## Publication Command Template

Executed after owner/reviewer approval:

```powershell
gh release create v0.1.0-rc6 `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip.sha256 `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip.sha256 `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip `
  dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip.sha256 `
  --repo J-Schulein/TowerScout `
  --target 12daa5536f580f76d063559e86b9a474451bc54b `
  --title "TowerScout v0.1.0-rc6" `
  --notes-file .agent_work\tasks\active\TASK-084\official-rc6-release-notes.md `
  --prerelease `
  --latest=false
```

After publication, download the uploaded `v0.1.0-rc6` assets into a fresh
validation folder and verify both checksum sidecars before approving tester
send.

## Publication Result

- Official GitHub release published:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc6`.
- GitHub release metadata verified after publication:
  - tag: `v0.1.0-rc6`
  - title: `TowerScout v0.1.0-rc6`
  - prerelease: `true`
  - target: `12daa5536f580f76d063559e86b9a474451bc54b`
  - published timestamp: `2026-06-17T16:15:03Z`
- All six required assets were uploaded to the official release.

## Post-Publication Checks

- [x] `gh release view v0.1.0-rc6 --repo J-Schulein/TowerScout` verified the
      tag, title, prerelease flag, target commit, publish timestamp, URL, and
      six uploaded assets.
- [x] Downloaded only `towerscout-v0.1.0-rc6*` release assets into a clean
      validation folder:
      `.agent_work/tmp/rc6-post-publication-20260617-121723`.
- [x] Verified CPU package, CUDA package, and shared asset ZIP SHA-256 values
      against both the expected values above and their downloaded sidecars:
  - CPU package:
    `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d`
  - CUDA package:
    `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603`
  - Shared Model & Data Package:
    `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- [x] Ran a downloaded-release CPU package setup/readiness smoke with Docker
      Desktop on port `5006` from the extracted downloaded CPU package.
- [x] Downloaded CPU package setup verified the CPU package sidecar, verified
      the shared Model & Data Package sidecar, staged assets, imported assets
      with hash verification, and started TowerScout successfully.
- [x] Downloaded CPU package readiness returned `state=setup_required`,
      `components.assets.status=ok`, `components.config.status=setup_required`,
      `runtime.container_engine=docker`, `runtime.device_policy=cpu`,
      `runtime.selected_device=cpu`, and `runtime.pytorch_flavor=cpu`; the app
      root returned HTTP `200`.
- [x] Stopped and removed the temporary downloaded-package validation
      container after evidence capture.
- [x] Existing support GPU evidence remains the CUDA runtime authority for
      Docker GPU and Podman GPU CDI because it was captured on the assigned
      WSL-visible NVIDIA host against the accepted RC6 artifacts.
- [x] Updated `RC1-PILOT-HANDOFF-PACKET.md` with the final release URL and
      downloaded-release verification state while keeping tester-send approval
      gated on tester/cohort selection and owner/reviewer packet approval.
- [x] `TASK-084` can now be marked complete; remaining external tester launch
      gates belong to `TASK-073` / UAT handoff approval.
