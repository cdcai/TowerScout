# TASK-084 Final Package Gate Checklist

**Date**: 2026-06-16
**Source baseline**: `main` at `ff01c10f6b45`
**Scope**: Remaining gates before final GA/pilot package publication after
PR #34 (`TASK-084`) and PR #35 (`TASK-085`) merged.

## Gate Status

- [x] `TASK-084` implementation slice merged: runtime cleanup, package
      guardrails, shared asset identity, and Podman provider onboarding.
- [x] `TASK-085` dataset ZIP restore traversal hardening merged and validated.
- [ ] Final release version/name selected.
- [ ] Shared Model & Data Package ZIP filename selected.
- [ ] Shared Model & Data Package ZIP SHA-256 captured.
- [ ] CPU image published and immutable digest captured.
- [ ] CUDA 12.1 image published or selected and immutable digest captured.
- [ ] CPU control ZIP generated from `ff01c10f6b45` or a later documented
      release source ref.
- [ ] CUDA control ZIP generated from the same release source ref.
- [ ] CPU and CUDA package manifests point to the same shared asset bundle
      filename and SHA-256.
- [ ] CPU and CUDA package runtime paths use digest-pinned image references
      without mutable tags.
- [ ] `IMAGE.txt`, `.env.example`, `release-manifest.v1.json`, checksum
      sidecars, `SOURCE.txt`, image digest, package checksum, SBOM/provenance
      reference, and asset checksum agree for each control ZIP.
- [ ] CPU package validation passes on Docker CPU.
- [ ] CPU package validation passes on Podman CPU with approved provider.
- [ ] CUDA package validation passes on Docker GPU with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [ ] CUDA package validation passes on Podman GPU CDI with readiness
      `selected_device=cuda`, or CUDA final publication is held.
- [ ] CPU package rejects `-Gpu on` with package-aware guidance.
- [ ] CUDA package remains fail-closed for `-Gpu on` unless readiness reports
      `selected_device=cuda`.
- [ ] Podman provider helper path is documented and verified against the final
      package layout.
- [ ] User/support docs explain CPU vs CUDA package selection in plain
      language.
- [ ] User/support docs explain the Podman approved-provider path and connected
      helper usage.
- [ ] Public evidence packet is sanitized for provider-key previews, raw local
      AOIs, personal paths, and host-specific secrets.
- [ ] Final evidence summary records source ref, package checksums, image
      digests, asset checksum, manifest validation, SBOM/provenance references,
      and runtime validation outcomes.

## Inputs To Collect Next

| Input | Status | Notes |
|---|---|---|
| Release version/name | Pending | Needed before naming package ZIPs and evidence folders. |
| Release source ref | Drafted | Current candidate baseline is `ff01c10f6b45`; update if more commits land. |
| Shared asset ZIP filename | Pending | Must be identical in CPU and CUDA manifests. |
| Shared asset ZIP SHA-256 | Pending | Must match package sidecars and release evidence. |
| CPU image digest | Pending | Required before CPU control ZIP can be final. |
| CUDA image digest | Pending | Required before CUDA control ZIP can be final or support-held. |
| CUDA publication decision | Pending | Final only after Docker GPU and Podman GPU CDI evidence; otherwise hold/label. |
| SBOM/provenance references | Pending | Record artifact locations or release references for both images. |

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
- CPU package Podman launch/readiness smoke with approved provider.
- CUDA package Docker GPU launch/readiness smoke on the support GPU host.
- CUDA package Podman GPU CDI launch/readiness smoke on the support GPU host.
- Secret/provider-key safety scan over any public evidence folder before
  attachment or publication.

## Hold Rules

- Do not publish a final CPU package until the CPU image digest, shared asset
  checksum, manifest consistency, and Docker/Podman CPU validation are
  complete.
- Do not publish a final CUDA package until the CUDA image digest, shared asset
  checksum, manifest consistency, Docker GPU validation, and Podman GPU CDI
  validation are complete.
- If the GPU host is unavailable, hold the CUDA package or label it as a
  pre-release/support candidate rather than final GA.
- Do not attach evidence publicly until provider-key previews and local
  host/user-specific details have been removed.
