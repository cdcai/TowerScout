# TASK-084 Final Package Gate Checklist

**Date**: 2026-06-16
**Source baseline**: `main` at `be67e67382e437b36fd1851fb89bc44e6f590200`
**Scope**: Remaining gates before final GA/pilot package publication after
PR #34 (`TASK-084` implementation), PR #35 (`TASK-085` security gate), and
PR #37 (`TASK-084` user/support docs and asset lookup remediation) merged.

## Gate Status

- [x] `TASK-084` implementation slice merged: runtime cleanup, package
      guardrails, shared asset identity, and Podman provider onboarding.
- [x] `TASK-085` dataset ZIP restore traversal hardening merged and validated.
- [x] `TASK-084` user/support docs and shared asset lookup remediation merged
      through PR #37.
- [x] Final release version/name selected: `v0.1.0-rc6`.
- [x] Shared Model & Data Package ZIP filename selected:
      `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`.
- [x] Shared Model & Data Package ZIP SHA-256 captured:
      `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- [x] CPU image published and immutable digest captured:
      `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- [x] CUDA 12.1 image published or selected and immutable digest captured:
      `sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41`.
- [x] CPU control ZIP generated from `be67e67382e437b36fd1851fb89bc44e6f590200` or a later documented
      release source ref.
- [x] CUDA control ZIP generated from the same release source ref.
- [x] CPU and CUDA package manifests point to the same shared asset bundle
      filename and SHA-256.
- [x] CPU and CUDA package runtime paths use digest-pinned image references
      without mutable tags.
- [x] `IMAGE.txt`, `.env.example`, `release-manifest.v1.json`, checksum
      sidecars, `SOURCE.txt`, image digest, package checksum, SBOM/provenance
      reference, and asset checksum agree for each control ZIP.
- [x] CPU package validation passes on Docker CPU.
- [ ] CPU package validation passes on Podman CPU with approved provider
      against rebuilt publishable ZIPs. Locally patched generated package
      validation passed after the source fix described below.
- [ ] CUDA package validation passes on Docker GPU with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [ ] CUDA package validation passes on Podman GPU CDI with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [x] CPU package rejects `-Gpu on` with package-aware guidance.
- [x] CUDA package remains fail-closed for `-Gpu on` unless readiness reports
      `selected_device=cuda`.
- [x] Podman provider helper path is documented and verified against the final
      package layout. Re-run after the publishable ZIP rebuild as part of the
      final CPU Podman smoke.
- [x] User/support docs explain CPU vs CUDA package selection in plain
      language.
- [x] User/support docs explain the Podman approved-provider path and connected
      helper usage.
- [ ] Public evidence packet is sanitized for provider-key previews, raw local
      AOIs, personal paths, and host-specific secrets.
- [ ] Final evidence summary records source ref, package checksums, image
      digests, asset checksum, manifest validation, SBOM/provenance references,
      and runtime validation outcomes.

## Inputs To Collect Next

| Input | Status | Notes |
|---|---|---|
| Release version/name | Selected | `v0.1.0-rc6`. |
| Release source ref | Source fix pending | Current pre-fix candidate baseline is `be67e67382e437b36fd1851fb89bc44e6f590200`; update to the Podman source-fix commit before rebuilding publishable ZIPs. |
| Shared asset ZIP filename | Captured | `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`. |
| Shared asset ZIP SHA-256 | Captured | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`. |
| CPU image digest | Captured | `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`. |
| CUDA image digest | Captured | `sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41`. |
| CUDA publication decision | Pending runtime evidence | Final only after Docker GPU and Podman GPU CDI evidence; otherwise hold/label. |
| SBOM/provenance references | Pending | Record artifact locations or release references for both images. |

## Generated RC6 Artifacts

These artifacts are now validation artifacts, not final publishable artifacts:
the ZIPs were cut before the Podman release-package project-name fix. Rebuild
the CPU and CUDA control ZIPs from the fixed source ref and replace the ZIP
checksums below before publication.

| Artifact | Path / reference | SHA-256 or digest |
|---|---|---|
| Shared Model & Data Package ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip` | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu` | `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a` |
| CUDA image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121` | `sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41` |
| CPU control ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu.zip` | `65b0595de84934347ccec7e156da7e2e101f6588d4fa18cca45424dce3caae5e` |
| CUDA control ZIP | `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cuda121.zip` | `99af4a53f2044a96715a2def10ac11407ad4eef9ce550b66c9e007bed1faacd0` |

## Local Package-Cut Validation

- `git diff --check` passed before package generation.
- Static release manifest checks passed for both generated package directories.
- Package summaries for both ZIPs found expected top-level runtime files,
  compliance notices, docs, scripts, `release-manifest.v1.json`, and
  `webapp/asset_manifest.v1.json`.
- Focused package/bootstrap tests passed:
  `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py tests\unit\test_task_074_bootstrap.py -q -p no:cacheprovider`
  with `27 passed`.
- CPU and CUDA `setup-towerscout.cmd -VerifyOnly` validated package ZIP and
  shared asset ZIP checksum discovery before engine preflight.
- CPU `start.bat -Gpu on` failed closed with package-aware CUDA-package
  guidance before container startup.

## Docker Runtime Validation

- CPU package Docker smoke passed on port `5015`:
  `setup-towerscout.cmd -Engine docker -Port 5015 -Gpu off -NoBrowser
  -TimeoutSeconds 240 -RestartWaitSeconds 240`.
- CPU package imported staged assets with hash verification, reached
  readiness `setup_required`, reported `asset_status=ok`, and reported
  `runtime.container_engine=docker`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cpu`, and image digest
  `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- CPU status snapshot showed Docker Compose v5.1.4, a healthy container, all
  nine asset entries `ok`, `torch_version=2.2.1+cpu`, and
  `torch_cuda_available=false`.
- CUDA package Docker GPU launch was attempted on port `5016` with
  `-Gpu on`; the CUDA image pulled successfully, but Docker failed before app
  startup with NVIDIA runtime error `WSL environment detected but no adapters
  were found`.
- That GPU attempt is a fail-closed host validation failure, not a package
  manifest/image mismatch. Docker GPU release evidence remains open until a
  WSL-visible NVIDIA adapter is available, or the CUDA artifact is held/labeled
  support-candidate.
- CUDA package CPU-fallback smoke passed on port `5016`:
  `setup-towerscout.cmd -Engine docker -Port 5016 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- CUDA package imported staged assets with hash verification, reached
  readiness `setup_required`, reported `asset_status=ok`, and reported
  `runtime.container_engine=docker`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cuda121`, and image digest
  `sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41`.
- CUDA status snapshot showed Docker Compose v5.1.4, a healthy container, all
  nine asset entries `ok`, `torch_version=2.2.1+cu121`,
  `torch_cuda_build=12.1`, and `torch_cuda_available=false` while GPU mode was
  off.
- RC6 CPU and CUDA Docker package containers were stopped and removed after
  status capture. A separate pre-existing `towerscout-towerscout-1` container
  still owns host port `5005`.

## Podman Runtime Validation

- Post-restart Podman engine checks passed with Podman `5.8.2`; `podman info`
  was reachable.
- The default `podman compose version` path still reported a stale machine
  connection URI, so the package-local approved-provider helper was used.
- `scripts\install-podman-compose-provider.cmd -Apply -Force` passed from the
  CPU package layout after connected download: it fetched the approved PyPI
  `podman-compose` 1.5.0 wheel, verified SHA-256, created the package-local
  `.venv`, installed pinned `python-dotenv==1.1.1` and `PyYAML==6.0.2`, backed
  up `.env`, and updated only `PODMAN_COMPOSE_PROVIDER`.
- Initial CPU Podman setup on port `5017` started the service but failed during
  asset import because the direct-copy fallback searched for the raw package
  folder project name `towerscout-v0.1.0-rc6-cpu` while `podman-compose`
  labeled the project as `towerscout-v010-rc6-cpu`.
- Source fix: inferred Compose project names now remove characters outside
  `[a-z0-9_-]`, while explicit `COMPOSE_PROJECT_NAME` still wins.
- Source cleanup: Podman asset import now uses provider `compose ps` for
  service container identity, then direct `podman cp`, instead of first
  invoking unsupported provider `cp`; label lookup remains as a fallback and
  honors `COMPOSE_PROJECT_NAME` from package `.env`.
- Locally patched CPU package smoke then passed on port `5017` with readiness
  `setup_required`, `asset_status=ok`, `runtime.container_engine=podman`,
  `device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cpu`, and image
  digest
  `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- Status snapshot showed a healthy Podman container and all nine asset entries
  `ok`.
- The RC6 Podman validation container was stopped and removed after evidence
  capture.
- Source tests passed after the fix:
  `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py -q -p no:cacheprovider`
  with `42 passed`.
- Publication note: the current RC6 ZIP checksums above are for packages cut
  before this source fix. Rebuild the CPU and CUDA control ZIPs from the fixed
  source ref before final publication, then rerun CPU Podman validation against
  the rebuilt CPU ZIP.

## Remaining Runtime Blockers

- Docker GPU validation is blocked on this local host because Docker's NVIDIA
  prestart hook reports no WSL-visible NVIDIA adapters.
- Final publishable CPU Podman validation is blocked until the source fix is
  committed and the RC6 control ZIPs are rebuilt.
- Podman GPU CDI validation remains blocked until a WSL-visible NVIDIA Podman
  host is available, or the CUDA package is explicitly held/labeled
  support-candidate.

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
