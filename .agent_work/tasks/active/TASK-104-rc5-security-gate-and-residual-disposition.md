# TASK-104: RC5 Security Gate And Residual Disposition

**Status**: IN_PROGRESS - implementation merged through PR #98 as `30d5585`;
local CPU/CUDA identity, dependency, Fiona/ZCTA, real-model/device, Trivy, and
SBOM proof passed after the required Windows/WSL restart. The isolated CUDA
provider-backed detection-over-ZCTA cell also passed for Azure and Google
after the known Google TLS repair. The first owner-authorized registry attempt
failed closed before login/push on a workflow shell-quoting defect. Its PR #98
correction passed, but the CPU retry stopped after immutable push because a
transport-sensitive manifest equality check rejected matching config identity.
That bounded correction, successful exact-digest dispatch evidence, and final
package acceptance remain
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
- [x] Pass focused tests, full required CI, `git diff --check`, and strict
  `.agent_work` validation.
- [x] Build local CPU and CUDA 12.8 images from one exact source revision.
- [x] Verify package inventory, Fiona linkage, ZCTA lookup, real model/device
  work, and retained scan/SBOM evidence for both flavors.
- [x] Obtain reviewed merge and green exact-head/post-merge CI.
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

### Post-restart CPU/CUDA proof

- The restart cleared the WSL host failure. Docker Desktop 4.86.0 and its
  Linux engine started normally, the retained Task-103 Podman machine was
  running, and the CUDA image completed its previously interrupted local load.
- CUDA image identity matched the pre-restart build exactly: manifest/image ID
  `sha256:eb8362d01263b6382d0f6320b3d4fca21ad53275c68be8bcc1505f49249166d1`,
  config digest
  `sha256:159b6b50020f111a58c2018e361398c35227b7af9fc0bdf015f6dc23aedebd04`,
  source label `6d3abf2ed51d1e3ef2493b27d10adc4e7f0e4540`, and flavor
  `cuda128`.
- CUDA inventory and linkage passed: Python 3.11.17, pip 26.2.1, application
  urllib3 2.8.0, pip-private urllib3 2.7.0, torch 2.10.0+cu128,
  torchvision 0.25.0+cu128, Fiona 1.10.1/GDAL 3.9.2 from
  `site-packages/fiona.libs`, and no Debian GDAL/libheif/Python packages.
- A direct CUDA matrix kernel executed on the NVIDIA RTX PRO 500 Blackwell
  Laptop GPU with capability `sm_120`; the torch architecture list contained
  `sm_120`.
- The RC5 asset ZIP and retained browser-downloaded RC4 asset ZIP were
  byte-identical at SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  Every extracted asset matched its manifest byte count and SHA-256. Both
  images loaded the real 2025 ZCTA shapefile through Fiona and returned one
  Polygon feature for ZIP code 20001 through the actual `/getzipcode` route.
- The frozen RGB fixture manifest SHA-256 was
  `c72b65cca35b10ed96a45b1c609f184ce3a2df93a9a100855bc9745abb2c9447`.
  CPU and CUDA identity/startup/combined phases passed. Both combined runs
  produced 13 positive secondary candidates, six EfficientNet batches, 54
  accepted detections, and zero secondary errors. CPU observed both models on
  CPU; CUDA observed both on `cuda:0` with no fallback. Host-neutral combined
  evidence identifiers and hashes:
  - CPU `20261007T153056Z_FIRST-HOST-LOCAL_docker_C_cpu_6d3abf2_combined`:
    combined JSON
    `40b4a4a9b2dc2a7df72510cd096599585e39b76ca86f5e784676bc0a82b4480a`,
    run JSON
    `6996908d02a5228e888587481aa7c6b803c19be6313d1c9d6e2faaac003740a2`.
  - CUDA `20261007T153542Z_FIRST-HOST-LOCAL_docker_C_cuda128_6d3abf2_combined`:
    combined JSON
    `4133ce2636f5000eead77df8d0bf3cc5f36c18241e5ad3065657b9b80802d9a6`,
    run JSON
    `d94628509c80caf3104fddd44d55eb4021698f686e69516e5a68475c67062bd0`.
- Trivy 0.69.3 strict CUDA comparison passed: baseline 396, candidate 78,
  accepted baseline 74, accepted temporary residuals 4, blocking 0, severity
  escalations 0, and resolved 322. Retained CUDA evidence SHA-256 values:
  - Trivy JSON: `3c2d70526c13c37837f12d01764dbd94fb85ad1b715eff10886388e77b6a861b`.
  - Delta JSON: `f7d3866c492d14cf9197edadf5c3d97406a3f9397df4d9264c4c5041361f7858`.
  - CycloneDX SBOM: `ff243dafa75c7fa19a2a3e1df8d3dd72f3fefb3a574c469b54d4791a2c1ddc8a`.
- The approved managed-network CA bundle was mounted read-only only for the
  Trivy database download; it was not copied into the image, repository, or
  evidence. The 1.340 GiB disposable Trivy cache was removed after the reports
  were retained. No image, tag, registry, package, or named volume was removed.
- The post-restart focused comparator/workflow/package/runtime suite passed
  33/33 tests using an explicit permitted pytest scratch directory. The strict
  `.agent_work` validator and `git diff --check` also passed. Two earlier test
  attempts were blocked during pytest temporary-directory setup by host ACLs;
  no comparator test body failed, and their generated scratch was removed.
- An isolated Docker CUDA session used the exact validated image on loopback
  port 5235, fresh Task-104 config/session volumes, and the already
  hash-verified assets mounted read-only. Readiness remained `ready`, asset
  status remained `ok`, and the selected device remained `cuda` on the
  Blackwell `sm_120` host.
- Setup saved Azure successfully. Google first reproduced the known
  `tls_ca_untrusted` boundary. The packaged repair dry run found exactly one
  safe CA candidate with no ambiguity; certificate identities were suppressed.
  The selected CA was applied only to the isolated Task-104 config volume, and
  the exact container was recreated with the combined bundle. Azure config,
  image identity, assets, and CUDA selection persisted, and Google then
  reported `tls_ok` before its key was saved through the `localhost:5235` UI.
- The actual `/getzipcode` route returned one 114-point Polygon for ZCTA
  `20004`. Both providers completed a real `newest`-model detection over that
  complete returned polygon:
  - Azure estimated and returned 46 tile records in 35.0 seconds, producing
    219 detections, 120 inside-boundary detections, and 217 selected/secondary-
    positive detections.
  - Google estimated and returned 46 tile records in 32.4 seconds, producing
    225 detections, 123 inside-boundary detections, and 224 selected/secondary-
    positive detections.
- No provider key, provider URL, request payload, certificate identity, raw
  network trace, or screenshot was written to repository evidence or terminal
  output. The keys remain only in the isolated active test config volume until
  its separately verified cleanup. No image, tag, package, or release has been
  pushed or published.

### PR #97 review correction

- The first exact-head CI run passed all required checks. Automated review then
  identified two fail-closed gaps before merge.
- Local config-digest resolution now prefers Buildx metadata and supports both
  Docker's containerd image store and classic image store. Local image ID,
  manifest digest, and config digest are validated separately. Registry
  identity is established by matching the published config digest to the
  locally scanned config digest; local and published manifest digests are
  retained separately because push can translate OCI media types to Docker
  schema 2.
- Accepted-residual duplicate detection now covers the complete file before
  flavor filtering, so duplicate CPU/CUDA-split entries cannot evade the
  one-key rule.
- Regression coverage was added for both corrections. The focused comparator,
  workflow, CI-ratchet, and runtime-contract suite passed 56/56 tests. The
  sandboxed test attempts could not create pytest scratch directories; the
  same suite passed outside that filesystem restriction. No image or package
  was built, pushed, tagged, or published during this correction.

### First authorized registry attempt

- `J-Schulein` authorized `v0.1.0-rc5` CPU and CUDA 12.8 workflow dispatches
  with `push_latest=false` from accepted `main` at `d0c36be`.
- CPU run `37655436322` built its local image, then failed in `Verify local
  dependency and geospatial boundary`. The outer GitHub-host shell interpreted
  the nested `awk '{print $3}'` while `set -u` was active, producing an unbound
  positional-parameter error. Local Trivy comparison, GHCR login/push,
  published-digest confirmation, SBOM, and `latest` were skipped.
- CUDA run `37655478076` was still in the local build/load step when the shared
  defect was confirmed. Normal and force-cancel requests returned GitHub API
  errors, but the unchanged workflow subsequently failed closed at the same
  dependency/Fiona boundary. Scanning, GHCR login/push, published-digest
  confirmation, SBOM, and `latest` were skipped for both flavors.
- The correction sends the container shell body through a quoted heredoc so
  host expansion cannot consume container-only variables. Parsed-workflow
  regression coverage requires that boundary and rejects the former outer
  single-quoted `sh -c` form. No RC5 image or package was published by either
  failed attempt.

### CPU retry after PR #98

- PR #98 merged as `30d5585d522d58e2ab2a2609d62055b31420dd91`;
  exact-head and post-merge CI passed.
- CPU run `37657322565` passed build/load, dependency/Fiona verification, the
  local Trivy scan, and the prepublication comparator before GHCR login.
- The immutable `v0.1.0-rc5-cpu` push completed. Its registry manifest digest
  is `sha256:8e624a332a0b70ce70a6d29625d8482bb04651767d38d21e46cac16932b65bee`,
  and its config digest exactly matches the locally scanned config digest
  `sha256:6d1603fedb56a87095e5cc3d77cab80c243331274e12d4668065096726cd466e`.
- Docker translated the local OCI manifest into Docker schema 2 during push,
  changing the manifest digest without changing image config identity. The
  workflow's extra local-versus-registry manifest equality assertion therefore
  failed before exact-digest Trivy/SBOM generation. No `latest` tag or package
  was published, and CUDA was held pending the bounded correction.
- The correction removes only that invalid equality assertion. It retains both
  manifest digests as evidence and continues to require the exact published
  digest's config identity to equal the locally scanned image config.

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
