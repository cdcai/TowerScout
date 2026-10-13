# TASK-104: RC5 Security Gate And Residual Disposition

**Status**: IN_PROGRESS - implementation merged through PR #100 as `928a0f0`;
local CPU/CUDA identity, dependency, Fiona/ZCTA, real-model/device, Trivy, and
SBOM proof passed after the required Windows/WSL restart. The isolated CUDA
provider-backed detection-over-ZCTA cell also passed for Azure and Google
after the known Google TLS repair. The first owner-authorized registry attempt
failed closed before login/push on a workflow shell-quoting defect. Its PR #98
correction passed, but the CPU retry stopped after immutable push because a
transport-sensitive manifest equality check rejected matching config identity.
PR #99 corrected that assertion, and PR #100 added read-only exact-digest
recovery plus immutable-tag overwrite/race protection. PR #101 recorded the
RC5 evidence, then the same-source RC8 CPU and CUDA registry digests passed G10
with `push_latest=false`. RC9 CPU correctly stopped before publication on
newly disclosed `CVE-2026-77214`; the owner approved one exact October 31-
expiring residual, and PR #106 merged the bounded policy amendment. Fresh
same-source RC9 CPU/CUDA publications now pass both local and exact-digest
security gates with no `latest` promotion, and their digest-pinned packages
pass local integrity validation. The owner-authorized non-Latest RC9 package
prerelease is published; final browser-download and independent-host
acceptance remain
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
- Only the exact two urllib3, two OpenSSL, and one Debian libexpat package keys
  in the residual file may pass, and only through October 31, 2026.
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
- [x] After separate owner dispatch authorization, publish immutable versioned
  images with `push_latest=false` and confirm exact-digest G10 evidence.
- [x] Assemble and locally verify digest-pinned CPU and CUDA 12.8 packages.
- [x] After separate owner authorization, publish the historical RC8 package
  assets used to reproduce the Podman cancellation finding.
- [x] After separate owner authorization, publish the exact RC9 package assets.
- [ ] Complete the final browser-download and independent-host four-profile
  matrix under Tasks 091/092/093/097/103.

## RC9 Prepublication Stop And Bounded Expat Disposition - October 9, 2026

- `J-Schulein` authorized CPU and CUDA 12.8 `v0.1.0-rc9` dispatches from
  accepted `main` at `004631754be343a1a9c0a7e0777dfc39e689c9f3`, with
  `push_latest=false`.
- CPU run `37935858689` built and scanned locally, then failed closed before
  GHCR login or push on one new HIGH key:
  `CVE-2026-77214 / libexpat1@2.5.0-1+deb12u4 / Debian`.
- The comparison reported baseline 396, candidate 79, accepted baseline 74,
  accepted temporary residuals 4, blocking 1, severity escalations 0, and
  resolved 322. Its sanitized security artifact is
  `image-security-v0.1.0-rc9-cpu`, artifact ID `11618593527`.
- CUDA run `37935867972` was cancelled after the shared stop condition was
  known. Its build was cancelled and every scan, GHCR login/push,
  exact-digest, SBOM, and `latest` step was skipped. Neither dispatch
  published an RC9 image or changed a `latest` tag.
- Local reachability review found no direct XML parser import or call in the
  TowerScout Python source. CPython `pyexpat` is loaded indirectly by
  `torchvision.datasets.voc`, but its wrapper uses `XML_Parse`, not the
  affected `XML_ParseBuffer` API. Debian `libexpat1` is retained by the
  OpenGL/Mesa packages required by OpenCV, and the system library was not
  mapped into the observed steady-state RC8 process at startup.
- Debian Bookworm had no fixed package on October 9. `J-Schulein` approved one
  additional exact residual for this finding, for CPU and CUDA 12.8 only,
  under the existing October 31 expiry. Any identity, version, severity, or
  supported-path call-chain change remains blocking.
- Replaying the exact retained CPU report through the amended policy passed:
  baseline 396, candidate 79, accepted baseline 74, accepted residuals 5,
  blocking 0, severity escalations 0, and resolved 322. The amended residual
  file SHA-256 is
  `da207424b181c9f9df94bde02b6ca7665a8fea29f8ca7fee7a8184795d0db064`.
- The broader focused comparator, container-workflow, CI-ratchet, runtime, and
  ML-runtime contract suite passed `63/63`. The strict and quick
  `.agent_work` validators and `git diff --check` passed. The first sandboxed
  pytest attempts were blocked during temporary-directory setup by the known
  Windows ACL condition; the same tests passed outside that filesystem
  restriction with an explicit repository-local base directory.

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

### Immutable-tag recovery after PR #99

- PR #99 merged the transport-safe config-identity rule as
  `a886b8bb3011ff8be8764c4fa7d5f852d2636062`; exact-head and post-merge CI
  passed.
- Retrying the normal publish workflow would overwrite the already-created
  `v0.1.0-rc5-cpu` tag with a newly labeled image. That would violate the
  blocked-evidence and immutable-version boundary, even though the application
  build inputs did not change between `30d5585` and `a886b8b`.
- The recovery path is therefore read-only: verify the exact existing CPU
  digest and expected config/source/flavor identities, generate the missing
  exact-digest Trivy report and SBOM, enforce the same comparator, and upload
  evidence without any push or tag mutation.
- The normal publish workflow will also fail before push when a versioned tag
  already exists, or when registry inspection cannot prove that the requested
  tag is absent. This preserves immutable evidence and prevents accidental
  replacement during retries.

### Successful exact-digest registry qualification

- PR #100 merged the read-only exact-digest verifier and immutable-tag
  overwrite/race protection as
  `928a0f056d6fc004f1ce3f10ccbfb43d14076ea7`; exact-head and post-merge
  checks passed.
- CPU read-only verification run `37663225514` qualified the existing pinned
  image
  `ghcr.io/j-schulein/towerscout@sha256:8e624a332a0b70ce70a6d29625d8482bb04651767d38d21e46cac16932b65bee`.
  Its config/image ID is
  `sha256:6d1603fedb56a87095e5cc3d77cab80c243331274e12d4668065096726cd466e`,
  source label is `30d5585d522d58e2ab2a2609d62055b31420dd91`, and flavor is
  `cpu`. Artifact `image-security-verify-cpu-37663225514` has GitHub artifact
  ID `11500624238`. The exact-digest Trivy, delta, and SBOM SHA-256 values are
  `86bbfd1309b7c619230c72e4e31cd43a79c6d30f56617e0076a735ee145a1dfd`,
  `293e7fee14f0879a5f5eecb0710cfb1805d5093715983850f3941eecad31174e`,
  and `be214a5aa8509a4244217933c3599a6d43a39f1a1cae03affebcbac95e047ee2`.
- CUDA publish run `37663527863` qualified pinned image
  `ghcr.io/j-schulein/towerscout@sha256:e50a43293d07c6904b103201f65b142cc38267d4d263be67e702c672628dbfec`.
  Its config/image ID is
  `sha256:131908087d2efaf36c15de8eaa585e77843b0003736ce7b7be28256b7b3b7519`,
  source label is `928a0f056d6fc004f1ce3f10ccbfb43d14076ea7`, and flavor is
  `cuda128`. Artifact `image-security-v0.1.0-rc5-cuda128` has GitHub artifact
  ID `11503375308`. The exact-digest Trivy, delta, and SBOM SHA-256 values are
  `355506f49b92a4cd882ad09eefbac0685899099b756bb1c1a5185354d1bccbd9`,
  `634936a3ba5e28942ebd8532caf33be8baa470848f4c601afbad4b1483c177c0`,
  and `e3a8fd13185e1dad7a7e70abc0655692839a8575429ce1ada22967214f516a4b`.
- Both exact-digest comparisons passed with baseline 396, candidate 78,
  accepted baseline 74, accepted temporary residuals 4, blocking 0, severity
  escalations 0, and resolved 322. The baseline and residual-file hashes were
  identical across flavors. No `latest` promotion step ran, and neither run
  published a package.
- The source labels differ because the CPU tag was preserved rather than
  overwritten after the workflow corrections. A repository diff from
  `30d5585` through `928a0f0` contains only `.github`, `tests`, and
  `.agent_work` files, all excluded from the image build context. Runtime image
  inputs are therefore unchanged, but this is not an exact single-source
  release pair. Final package assembly remains stopped until the owner chooses
  a fresh same-source candidate tag or explicitly approves and records this
  traceability exception.

### Same-source RC8 registry qualification

- PR #101 merged the RC5 evidence record as
  `7827c2af8ecb7d8b21d246b69e135807fa497fd2`; exact-head review found no
  issues, and all exact-head and post-merge checks passed. Several GitHub-hosted
  jobs stalled during system-package installation and were canceled/retried;
  the targeted reruns passed without source changes.
- The initially proposed `v0.1.0-rc6-cpu` tag already identified historical
  June source `12daa5536f580f76d063559e86b9a474451bc54b`; `rc7-cpu` was
  also occupied. Both were preserved. `v0.1.0-rc8-cpu` and
  `v0.1.0-rc8-cuda128` were proven absent immediately before dispatch and were
  the first unused pair.
- CPU run `37674158762` qualified pinned image
  `ghcr.io/j-schulein/towerscout@sha256:2e040c3b09d1aa493b205ec2100c112a839ab7a9bfc90a639f73918e06135412`.
  Its config/image ID is
  `sha256:46ea8ce853eb621907e288595122312833019bb5a83f692c0f8c45ad2fae67da`,
  source label is `7827c2af8ecb7d8b21d246b69e135807fa497fd2`, and flavor is
  `cpu`. Evidence artifact `image-security-v0.1.0-rc8-cpu` has GitHub artifact
  ID `11506456463` and archive digest
  `sha256:258ec9c094f23d47f52a8b8dd1f0f4cbd20fcd05c279c606d86d8ef183441b76`.
  The exact-digest Trivy, delta, and SBOM SHA-256 values are
  `1668f2b2977233601cc0249f7f8202a9b013d1ff89192ea7086d235f1868bd2f`,
  `ff0decdf309c3fb13de2716f9f46ab11fe984b6999dbefe3985ee90f46373efc`,
  and `e1d3fdc52c7d71309f41ad4ed0d93e5fe393b8623d69e16402686fa6e29c22f2`.
- CUDA run `37674161407` qualified pinned image
  `ghcr.io/j-schulein/towerscout@sha256:712beb4e143495ba72705cc56b89a939c5bebfdc47dc2f6d0694c81e9e60ca57`.
  Its config/image ID is
  `sha256:9190dd3544d6f01a5e78fec094e0c8174703a93a0b4dbfd436f1b16866a8fc42`,
  source label is `7827c2af8ecb7d8b21d246b69e135807fa497fd2`, and flavor is
  `cuda128`. Evidence artifact `image-security-v0.1.0-rc8-cuda128` has GitHub
  artifact ID `11506538018` and archive digest
  `sha256:af5b62527d9c4f2f6c4fa8a5bd2fc9ff5d4700aadc150b82953c268d6164679f`.
  The exact-digest Trivy, delta, and SBOM SHA-256 values are
  `c3251bc71c28e95ed6de6f6c7b5dccbc483bf8cbc3af465708cc458751b08e14`,
  `09bd844229dd8d4ffa4a9956e3b9ef255c0cb088dee25215791d2271f49b001f`,
  and `fb4fa817071f1214e765855fa2d2a991f03d64ad1286eb9970261b47904158e7`.
- Both comparisons passed with baseline 396, candidate 78, accepted baseline
  74, accepted temporary residuals 4, blocking 0, severity escalations 0, and
  resolved 322. Baseline SHA-256
  `f18a4f2037573bb6f3280778fb694a8c1beb5e8c1313c47f10ac9cf507d31928`
  and residual-file SHA-256
  `7f2c261ede971d581f581857d11d8e1eafffef1b1390408dcd7b6865b05d55b2`
  matched across flavors. Both `latest` promotion steps were skipped. No
  control package or release asset was published.

### Same-source RC8 local control packages

- A clean detached checkout of frozen source
  `7827c2af8ecb7d8b21d246b69e135807fa497fd2` assembled the CPU and CUDA 12.8
  control ZIPs using only the exact RC8 registry manifest digests above.
- CPU ZIP SHA-256:
  `8fd46711b57a25dd71cd879a06fe519674596ee9a71fa66b2347204fe8bc74f0`.
- CUDA 12.8 ZIP SHA-256:
  `463d3f2348e369ed647bb8ed66c15588fc4051197e49ac90441552b8318bdada`.
- Both manifest checks, outer sidecars, all 73 internal checksums, and the
  focused `7/7` package/manifest regression suite passed.
- The retained 800655295-byte browser-downloaded asset ZIP was reverified at
  authoritative SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  It was not duplicated solely to stage the RC8 filename.
- That local checkpoint published no package/release asset or `latest` tag.

### Owner-authorized RC8 prerelease publication

- GitHub release ID `406175444` was published at `2026-10-07T21:23:59Z` as
  non-draft prerelease `v0.1.0-rc8` targeting exact source
  `7827c2af8ecb7d8b21d246b69e135807fa497fd2`.
- All six assets report state `uploaded`; GitHub's byte sizes and SHA-256
  digests match the approved CPU, CUDA 12.8, and asset ZIPs and sidecars.
- Unauthenticated checks returned HTTP 200 for the release page and all six
  browser-download URLs; temporary signed redirect URLs were not retained.
- Existing stable release `v0.1.2` remains Latest. No image `latest` tag was
  promoted, and no final release-readiness claim was made.
- Exact browser-download and independent-host acceptance remain open under the
  release-qualification tasks.

### Same-source RC9 exact-digest and local package qualification

- PR #106 merged the five-key residual-policy amendment as
  `b3431cf86d8a000462df487685104558ac7becd3`; exact-head and post-merge checks
  passed. The accepted baseline remains 396 keys, and the residual file hash
  is `da207424b181c9f9df94bde02b6ca7665a8fea29f8ca7fee7a8184795d0db064`.
- Owner-authorized CPU run `37942033212` qualified pinned image
  `ghcr.io/j-schulein/towerscout@sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`.
  Its config digest is
  `sha256:3dd62907f9f6ab4d76b3ac9b8804a73e4b04f098aad22221f737cbfc595a170a`.
  Evidence artifact `image-security-v0.1.0-rc9-cpu` has ID `11623080423`,
  archive digest
  `sha256:777ad260f1c0dc4c6d7f085968207f5f081c1d6245ea63371fe941d7697380cc`,
  and retention through January 7, 2027. Exact-digest Trivy, delta, and SBOM
  SHA-256 values are
  `b1ad39ee77dac8d2b86faa0c637109c5b197f728c7bb83d9af308f5fd182e526`,
  `1f23e23843d68f47c79ef57418973ff388af7c8d91a9034aa31c85c86d7d8f11`,
  and `d148374a12f0c328c1f84e335272e993279bcafadd29355e19b027629100b879`.
- Owner-authorized CUDA run `37942073914` qualified pinned image
  `ghcr.io/j-schulein/towerscout@sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
  Its config digest is
  `sha256:aa397626a037531892eb8005004aaef33faaed0c29720444cbf73fe05d5f99ad`.
  Evidence artifact `image-security-v0.1.0-rc9-cuda128` has ID `11623017469`,
  archive digest
  `sha256:a408049de93922aa4065b3c4ff9314750817766c0661865de91430f1d4f489b4`,
  and retention through January 7, 2027. Exact-digest Trivy, delta, and SBOM
  SHA-256 values are
  `c46f529c40a8a3d5d8e24758e24267bb4fd6cfa0635280625f43d7e165f9ae86`,
  `08002381af49fb4faa107892721925c2fb7e73f0905b3ffa21a6d66e86348ac3`,
  and `b448b72efc9ec54b42d0b8f7271abdc5c31bb2f8974ac98702a3942dbe059e44`.
- Both workflows passed the local comparison before GHCR login and the exact-
  published-digest comparison afterward: baseline 396, candidate 79, accepted
  baseline 74, accepted residual 5, blocking 0, severity escalations 0, and
  resolved 322. Both `latest` promotion steps were skipped.
- A clean detached checkout of `b3431cf` assembled the exact digest-pinned
  packages. CPU ZIP SHA-256 is
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`;
  CUDA 12.8 ZIP SHA-256 is
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`.
  Both manifests, outer sidecars, all 73 internal checksums, and the focused
  `7/7` package/manifest suite passed. The shared asset ZIP was reverified at
  SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

### Owner-authorized RC9 prerelease publication

- GitHub release ID `408047593` was published at `2026-10-09T15:26:48Z` as
  non-draft prerelease `v0.1.0-rc9` targeting exact source
  `b3431cf86d8a000462df487685104558ac7becd3`.
- All six approved assets report state `uploaded`; GitHub's byte sizes and
  SHA-256 digests match the verified CPU, CUDA 12.8, and shared asset ZIPs and
  their sidecars.
- Unauthenticated checks returned HTTP 200 for all six browser-download URLs;
  temporary signed redirect URLs were not retained.
- Existing stable release `v0.1.2` remains Latest. No GHCR `latest` tag was
  promoted and no final release-readiness claim was made.
- Exact browser-download and independent-host acceptance remain open under the
  release-qualification tasks.

## Stop Conditions

- Any new unaccepted HIGH/CRITICAL key or severity escalation.
- A residual package/version/identity mismatch or expired/unused entry.
- Fiona resolves to system GDAL, ZCTA lookup fails, or model/device behavior
  changes.
- A local scan and registry config/image identity cannot be reconciled.
- A required host, provider account, frozen asset, or exact artifact identity
  is unavailable; record `blocked`, never `pass`.

## Publication Boundary

Implementation, local builds, local validation, RC8/RC9 prerelease
publication, and RC9 GHCR dispatch were separately authorized and completed.
Any `latest` promotion and any stable/general release remain separate owner
actions. The full support claim still requires exact browser-downloaded bytes,
all four profiles, and independent-host reproduction.
