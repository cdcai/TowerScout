# TASK-084 Final Package Gate Checklist

**Date**: 2026-06-16
**Last updated**: 2026-06-17 after remote GPU evidence review.
**Source baseline**: `main` at `12daa5536f580f76d063559e86b9a474451bc54b`
**Scope**: Remaining gates before final GA/pilot package publication after
PR #34 (`TASK-084` implementation), PR #35 (`TASK-085` security gate), and
PR #37 (`TASK-084` user/support docs and asset lookup remediation), and PR #38
(`TASK-084` Podman package asset import stabilization) merged.

## Gate Status

- [x] `TASK-084` implementation slice merged: runtime cleanup, package
      guardrails, shared asset identity, and Podman provider onboarding.
- [x] `TASK-085` dataset ZIP restore traversal hardening merged and validated.
- [x] `TASK-084` user/support docs and shared asset lookup remediation merged
      through PR #37.
- [x] `TASK-084` Podman release-package asset import stabilization merged
      through PR #38.
- [x] Final release version/name selected: `v0.1.0-rc6`.
- [x] Shared Model & Data Package ZIP filename selected:
      `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`.
- [x] Shared Model & Data Package ZIP SHA-256 captured:
      `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- [x] CPU image published and immutable digest captured:
      `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`.
- [x] CUDA 12.1 image published or selected and immutable digest captured:
      `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`.
- [x] CPU control ZIP generated from
      `12daa5536f580f76d063559e86b9a474451bc54b`.
- [x] CUDA control ZIP generated from the same release source ref.
- [x] CPU and CUDA package manifests point to the same shared asset bundle
      filename and SHA-256.
- [x] CPU and CUDA package runtime paths use digest-pinned image references
      without mutable tags.
- [x] `IMAGE.txt`, `.env.example`, `release-manifest.v1.json`, checksum
      sidecars, `SOURCE.txt`, image digest, package checksum, SBOM/provenance
      reference, and asset checksum agree for each control ZIP.
- [x] CPU package validation passes on Docker CPU.
- [x] CPU package validation passes on Podman CPU with approved provider
      against rebuilt publishable ZIPs.
- [x] CUDA package validation passes on Docker GPU with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [x] CUDA package validation passes on Podman GPU CDI with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [x] CPU package rejects `-Gpu on` with package-aware guidance.
- [x] CUDA package remains fail-closed for `-Gpu on` unless readiness reports
      `selected_device=cuda`.
- [x] Podman provider helper path is documented and verified against the final
      rebuilt package layout.
- [x] User/support docs explain CPU vs CUDA package selection in plain
      language.
- [x] User/support docs explain the Podman approved-provider path and connected
      helper usage.
- [x] Unofficial GPU-validation prerelease published for remote GPU-machine
      testing without consuming the official `v0.1.0-rc6` release tag.
- [x] Public evidence packet is sanitized for provider-key previews, raw local
      AOIs, personal paths, and host-specific secrets.
- [x] Final evidence summary records source ref, package checksums, image
      digests, asset checksum, manifest validation, SBOM/provenance references,
      and runtime validation outcomes.

## Inputs To Collect Next

| Input | Status | Notes |
|---|---|---|
| Release version/name | Selected | `v0.1.0-rc6`. |
| Release source ref | Captured | `12daa5536f580f76d063559e86b9a474451bc54b`. |
| Shared asset ZIP filename | Captured | `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`. |
| Shared asset ZIP SHA-256 | Captured | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`. |
| CPU image digest | Captured | `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`. |
| CUDA image digest | Captured | `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`. |
| CUDA publication decision | Runtime evidence accepted | Docker GPU and Podman GPU CDI evidence passed on the support GPU host; proceed as support-validated CUDA path after official release handoff/publication approval. |
| SBOM/provenance references | Captured in package manifests/image metadata and standalone evidence provenance | `ARTIFACT-PROVENANCE.md` records the source ref, checksums, image digests, and runtime evidence index; `PUBLIC-SUMMARY.md` is the public-safe attachment. |

## Generated RC6 Artifacts

These artifacts were rebuilt after PR #38 from source ref
`12daa5536f580f76d063559e86b9a474451bc54b`.

Unofficial GPU-validation prerelease:
`https://github.com/J-Schulein/TowerScout/releases/tag/gpu-validation-2026-06-16`.
The prerelease is marked as a prerelease, targets
`12daa5536f580f76d063559e86b9a474451bc54b`, and does not use the official
`v0.1.0-rc6` release tag.

| Artifact | Path / reference | SHA-256 or digest |
|---|---|---|
| Shared Model & Data Package ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip` | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu` | `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd` |
| CUDA image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121` | `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0` |
| CPU control ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip` | `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d` |
| CUDA control ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip` | `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603` |
| GPU validation README | `dist\v0.1.0-rc6\README-GPU-VALIDATION.md` | Uploaded as release asset and used as release notes |

## Local Package-Cut Validation

- `git diff --check` passed after rebuilding the CPU and CUDA control ZIPs.
- Package summaries for both rebuilt ZIPs found expected top-level runtime files,
  compliance notices, docs, scripts, `release-manifest.v1.json`, and
  `webapp/asset_manifest.v1.json`.
- Focused package/bootstrap tests passed:
  `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py tests\unit\test_task_074_bootstrap.py -q -p no:cacheprovider`
  with `27 passed`.
- Rebuilt CPU package SHA-256 sidecar:
  `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d`.
- Rebuilt CUDA package SHA-256 sidecar:
  `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603`.
- Rebuilt CPU `start.bat -Gpu on` failed closed with package-aware
  CUDA-package guidance before container startup.

## Docker Runtime Validation

- CPU package Docker smoke passed on port `5015`:
  `setup-towerscout.cmd -Engine docker -Port 5015 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- CPU package imported staged assets with hash verification, reached
  readiness `setup_required`, reported `asset_status=ok`, and reported
  `runtime.container_engine=docker`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cpu`, and image digest
  `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`.
- CPU status snapshot showed Docker Compose v5.1.4, a healthy container, all
  nine asset entries `ok`, `torch_version=2.2.1+cpu`, and
  `torch_cuda_available=false`.
- CUDA package Docker GPU launch was attempted on port `5016` with
  `-Gpu on` before the PR #38 package rebuild; the CUDA image pulled
  successfully, but Docker failed before app startup with NVIDIA runtime error
  `WSL environment detected but no adapters were found`.
- That GPU attempt is a fail-closed host validation failure, not a package
  manifest/image mismatch. Docker GPU release evidence remains open until a
  WSL-visible NVIDIA adapter is available, or the CUDA artifact is held/labeled
  support-candidate.
- Rebuilt CUDA package CPU-fallback smoke passed on port `5016`:
  `setup-towerscout.cmd -Engine docker -Port 5016 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- CUDA package imported staged assets with hash verification, reached
  readiness `setup_required`, reported `asset_status=ok`, and reported
  `runtime.container_engine=docker`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cuda121`, and image digest
  `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`.
- CUDA status snapshot showed Docker Compose v5.1.4, a healthy container, all
  nine asset entries `ok`, `torch_version=2.2.1+cu121`,
  `torch_cuda_build=12.1`, and `torch_cuda_available=false` while GPU mode was
  off.
- RC6 CPU and CUDA Docker package containers were stopped and removed after
  status capture. A separate pre-existing `towerscout-towerscout-1` container
  still owns host port `5005`.

## Podman Runtime Validation

- Podman engine checks passed with Podman `5.8.2`; `podman info` was
  reachable.
- The package-local approved-provider helper was used from the rebuilt CPU
  control ZIP layout.
- `scripts\install-podman-compose-provider.cmd -Apply -Force` passed from the
  rebuilt CPU package layout after connected download: it fetched the approved
  PyPI `podman-compose` 1.5.0 wheel, verified SHA-256, created the
  package-local `.venv`, installed pinned `python-dotenv==1.1.1` and
  `PyYAML==6.0.2`, backed up `.env`, and updated only
  `PODMAN_COMPOSE_PROVIDER`.
- Rebuilt CPU Podman setup passed on port `5017`:
  `setup-towerscout.cmd -Engine podman -Port 5017 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- The setup path discovered the shared Model & Data Package ZIP from the parent
  folder, verified both checksum sidecars, imported staged assets with hash
  verification, used provider-backed `compose ps` plus direct `podman cp`, and
  reached readiness `setup_required`.
- Status snapshot showed the approved package-local provider path,
  `podman-compose version 1.5.0`, a healthy Podman container, all nine asset
  entries `ok`, `runtime.container_engine=podman`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cpu`, and image digest
  `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`.
- The RC6 Podman validation container was stopped and removed after evidence
  capture.

## Remote GPU Host Validation

- Evidence folder:
  `.agent_work/tasks/completed/TASK-084/evidence/TowerScout-rc6-gpu-validation-evidence-emailsafe/TowerScout-rc6-gpu-validation-evidence/`.
- Docker GPU and Podman GPU CDI both reached readiness `ready` with
  `device_policy=cuda`, `selected_device=cuda`, `pytorch_flavor=cuda121`,
  `torch_cuda_available=true`, `cuda_device_name="NVIDIA T1000 8GB"`,
  `asset_status=ok`, and the final CUDA image digest
  `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`.
- Google and Azure provider paths both live-validated through the setup wizard
  and completed end-to-end detection on CUDA for Docker GPU and Podman GPU CDI.
- Included detection artifacts report CUDA model execution for YOLOv5 primary
  inference and EfficientNet secondary classification.
- Docker/Azure and Podman/Azure repeated logs captured matching selected-count
  distributions of `50` high-mode and `22` low-mode detections. Docker/Google
  repeated logs captured `49` high-mode and `26` low-mode detections; the
  included Podman/Google log captures the matching `49` high-mode run.
- CPU package `-Gpu on` guardrail returned exit code `1` and refused before
  container startup with package-aware guidance to use the CUDA package.
- The local internal evidence summary remains ignored because it contains
  email-safe but non-public validation context; `ARTIFACT-PROVENANCE.md` makes
  the packet standalone, and `PUBLIC-SUMMARY.md` is the public-safe attachment.
- Evidence hardening checks passed:
  `python .agent_work\scripts\validate_agent_work.py`, `git diff --check`,
  the TowerScout secret/provider-key scan over `ARTIFACT-PROVENANCE.md` and
  `PUBLIC-SUMMARY.md`, and a targeted grep over the public-safe files for the
  raw AOI, local paths, key-preview terms, and common provider-key patterns.

## Closed Runtime Blockers

- Local Docker GPU validation remained blocked on this workstation because
  Docker's NVIDIA prestart hook reported no WSL-visible NVIDIA adapters.
- The support GPU host resolved that local limitation and closed both final CUDA
  runtime gates: Docker GPU and Podman GPU CDI.

## Command Templates

Publish image flavors from GitHub Actions, using the same base release tag for
both runs:

```powershell
gh workflow run container-publish.yml --repo J-Schulein/TowerScout --ref main -f tag=<release-version> -f pytorch_flavor=cpu -f push_latest=false
gh workflow run container-publish.yml --repo J-Schulein/TowerScout --ref main -f tag=<release-version> -f pytorch_flavor=cuda121 -f push_latest=false
```

Expected published image tags:

```text
ghcr.io/j-schulein/towerscout:<release-version>-cpu
ghcr.io/j-schulein/towerscout:<release-version>-cuda121
```

Capture each immutable digest from the workflow summary or uploaded
`image-metadata-<tag>.json` artifact before generating packages.

Generate the CPU control package:

```powershell
.\scripts\package-release.cmd `
  -Version <release-version>-cpu `
  -Image ghcr.io/j-schulein/towerscout:<release-version>-cpu `
  -ImageDigest sha256:<cpu-image-digest> `
  -PytorchFlavor cpu `
  -AssetBundleVersion <release-version> `
  -AssetBundleSha256 <asset-zip-sha256> `
  -OutputDir dist\<release-version> `
  -Force
```

Generate the CUDA control package:

```powershell
.\scripts\package-release.cmd `
  -Version <release-version>-cuda121 `
  -Image ghcr.io/j-schulein/towerscout:<release-version>-cuda121 `
  -ImageDigest sha256:<cuda121-image-digest> `
  -PytorchFlavor cuda121 `
  -AssetBundleVersion <release-version> `
  -AssetBundleSha256 <asset-zip-sha256> `
  -OutputDir dist\<release-version> `
  -Force
```

The shared asset ZIP expected by both generated manifests is:

```text
towerscout-<release-version>-assets-towerscout-v1-assets-2026-05-05.zip
```

## Validation Commands To Re-run During Package Cut

- `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`
- `git diff --check`
- Focused package tests for `scripts/package-release.*` and
  `release-manifest.v1.json`.
- CPU package Docker launch/readiness smoke.
- CPU package Podman launch/readiness smoke with approved provider, rerun
  after rebuilding the control ZIPs from the fixed source ref.
- CUDA package Docker GPU launch/readiness smoke on the support GPU host.
- CUDA package Podman GPU CDI launch/readiness smoke on the support GPU host.
- Secret/provider-key safety scan over any public evidence folder before
  attachment or publication.

## Hold Rules

- Do not publish a final CPU package until the CPU image digest, shared asset
  checksum, manifest consistency, source project-name fix, rebuilt control ZIP,
  and Docker/Podman CPU validation are complete.
- Do not publish a final CUDA package until the CUDA image digest, shared asset
  checksum, manifest consistency, Docker GPU validation, and Podman GPU CDI
  validation are complete.
- If the GPU host is unavailable, hold the CUDA package or label it as a
  pre-release/support candidate rather than final GA.
- Do not attach evidence publicly until provider-key previews and local
  host/user-specific details have been removed.
