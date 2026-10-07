# TASK-104: RC5 Security Gate And Residual Disposition

**Status**: IN_PROGRESS - implementation is complete on
`fix/rc5-fast-safe-security-gate`; local CPU proof passed and CUDA proof is
paused for a Windows/WSL host restart after Docker Desktop failed while loading
the large CUDA image
**Priority**: CRITICAL
**Type**: C (Release Security / Container Publication)
**Owner**: `J-Schulein` until handoff; `cdcai` thereafter
**Decision**: [ADR-024](../../decisions/024-rc5-security-gate-and-residual-boundary.md)
**Depends on**: TASK-103, PR #96 merge `b0725e750c1541e7cb60df881d3906f761657089`

## Objective

Remove the unused Debian GDAL dependency, enforce exact time-bounded residual
matching, and prevent an unqualified image from being pushed before the local
security gate passes. Preserve the accepted 396-key baseline unchanged.

## Required Outcome

- CPU and CUDA 12.8 images contain neither Debian GDAL/libheif nor the
  transitively installed Debian Python packages.
- Fiona loads the packaged ZCTA shapefile through its bundled GDAL library.
- The application imports `urllib3==2.8.0`; only pip's private 2.7.0 inventory
  may match the two approved urllib3 residuals.
- Only the exact two urllib3 and two OpenSSL package keys in the residual file
  may pass, and only through October 31, 2026.
- Missing/empty scans, wrong image/source/flavor identity, severity escalation,
  unknown fields, expiry, duplicates, mismatches, and unused exceptions fail
  closed.
- The workflow scans locally before GHCR login/push, proves registry config
  identity after the immutable push, rescans the exact digest, and promotes
  `latest` only after confirmation.

## Execution Checklist

- [x] Record ADR-024 and the exact residual schema/entries.
- [x] Pin base-image indexes and pip; remove `gdal-bin`.
- [x] Implement the fail-closed comparator and regression coverage.
- [x] Reorder the publish workflow and add parsed workflow ratchets.
- [ ] Pass focused tests, full required CI, `git diff --check`, and strict
  `.agent_work` validation.
- [ ] Build local CPU and CUDA 12.8 images from one exact source revision.
- [ ] Verify package inventory, Fiona linkage, ZCTA lookup, real model/device
  work, and retained scan/SBOM evidence for both flavors.
- [ ] Obtain reviewed merge and green exact-head/post-merge CI.
- [ ] After separate owner dispatch authorization, publish immutable versioned
  images with `push_latest=false` and confirm exact-digest G10 evidence.
- [ ] Assemble digest-pinned packages and complete the final browser-download
  and independent-host four-profile matrix under Tasks 091/092/093/097/103.

## Local Validation Record - October 7, 2026

Exact implementation revision:
`6d3abf2ed51d1e3ef2493b27d10adc4e7f0e4540`.

### Repository gates

- Focused security/workflow/runtime suite: `55 passed`.
- Broader focused release/security suite completed earlier in this branch:
  `139 passed`.
- Frontend build and setup-wizard, detection-cancel, and provider-state
  contracts passed.
- `npm audit --audit-level=high` reported zero vulnerabilities.
- Quick and strict `.agent_work` validators and `git diff --check` passed.
- The Windows full unit run completed with 643 passed, 74 skipped, and 20
  host-environment failures: 19 deferred Task-087 helper tests were blocked by
  endpoint antivirus policy, and one unrelated loopback reset passed on an
  immediate isolated rerun. No Task-104 test failed.

### CPU image proof

- Local image:
  `towerscout:v0.1.3-rc5-fastsafe-6d3abf2-cpu-local`.
- OCI manifest/image ID:
  `sha256:7e325c27290eb1a247db4fb84b2d1ddc420dcce3a7f6eb31ec45d4040c27b6b5`.
- OCI config digest:
  `sha256:e8523a828378ffce7831fd882a6b8c5574df173910175ee2b78b51be4a064f8e`.
- Source and flavor labels matched the exact revision and `cpu`.
- Package proof passed: pip `26.2.1`, application urllib3 `2.8.0`, pip-private
  urllib3 `2.7.0`, and no Debian GDAL, libheif, or Debian Python packages.
- Fiona `1.10.1` resolved GDAL from `site-packages/fiona.libs`, not from a
  Debian system GDAL package.
- Trivy `0.69.3` strict comparison passed: baseline 396, candidate 78,
  accepted baseline 74, accepted temporary residuals 4, blocking 0, severity
  escalations 0, and resolved 322.
- Retained local evidence SHA-256 values:
  - Trivy JSON: `07c30e067e0199212fe2ad1862bb6fd4a702de043938226e3d4162eaf79ee6ef`.
  - Delta JSON: `d8f3fb7a11fc2dd2178567fb9e02b02b81d50ed4f630cb1ea01d96a81faa067c`.
  - CycloneDX SBOM: `d46594a48510b3e279bf844f08b4846c17dae43e901464d46095afbfaa39c6a7`.
  - Build metadata: `bdfea7531c0a46401d1f7e0ec6031772f06438bdfa9b7ade3547c269d0db72c4`.

### CUDA host stop and resume point

- The pinned CUDA 12.8 dependency build completed after using the previously
  approved managed-network CA bundle as an ephemeral BuildKit secret. The
  bundle was not copied into the image or repository.
- Docker completed the CUDA layers and emitted manifest
  `sha256:eb8362d01263b6382d0f6320b3d4fca21ad53275c68be8bcc1505f49249166d1`
  and config
  `sha256:159b6b50020f111a58c2018e361398c35227b7af9fc0bdf015f6dc23aedebd04`,
  but Docker Desktop returned EOF while unpacking the final local image.
- The C: drive had fallen to about 137 MB free. Only the disposable Trivy DB
  cache was removed (1.341 GB); reports, SBOMs, packages, assets, and prior
  evidence were retained.
- Before the required restart, 18.891 GiB of verified ignored duplicates were
  removed: superseded RC1-RC4 `dist` package/qualification trees, duplicate RC4
  extracted asset trees and asset ZIP, three detached temporary package-source
  worktrees, and an unused root-level copy of `newest.pt`. Free space increased
  from 4.673 GiB to 22.834 GiB. The current RC5 validation tree and CPU security
  evidence, the authoritative `webapp/model_params` assets, the exact RC4
  browser-download evidence and downloaded asset ZIP, and the dirty
  `task103-source-revert` recovery worktree were explicitly retained.
- Docker's VHD then remained attached. A clean WSL shutdown detached it, but
  Windows subsequently refused WSL VM creation with `0x80070569` (requested
  logon type not granted). No Windows security policy was weakened or changed.
- Resume after a Windows restart: confirm Docker Desktop and the Task-103
  Podman machine start normally, verify adequate free space, retry the cached
  CUDA build/load, then complete CUDA inventory, Fiona/ZCTA, real GPU model,
  Trivy, and SBOM proof. Repeat the remaining CPU ZCTA/real-model checks before
  any push.
- Nothing from this branch has been pushed or published. This preserves the
  required local-scan-before-push order.

## Stop Conditions

- Any new unaccepted HIGH/CRITICAL key or severity escalation.
- A residual package/version/identity mismatch or expired/unused entry.
- Fiona resolves to system GDAL, ZCTA lookup fails, or model/device behavior
  changes.
- A local scan and registry config/image identity cannot be reconciled.
- A required host, provider account, frozen asset, or exact artifact identity
  is unavailable; record `blocked`, never `pass`.

## Publication Boundary

Implementation, local builds, and local validation are authorized. GHCR
dispatch, package/release publication, and `latest` promotion remain separate
owner actions. The full support claim still requires all four profiles and
independent-host reproduction.
