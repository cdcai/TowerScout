# TASK-103: CUDA 12.8 Blackwell ML Runtime

**Status**: IN_PROGRESS - local `rc4` CPU/CUDA images and control ZIPs pass
G10, W05, four-profile W09 setup/device/lifecycle, and the complete local W10
provider/cancel/error/review-export/relaunch/reboot matrix. ADR-023 resolves
the unsigned support boundary. The preliminary `rc4` browser-download Docker
CPU diagnostic passed, its findings are incorporated, and the documentation
content plus project-state reconciliation are merged through PRs #94/#95. A
local documentation-aligned `rc5` rehearsal from `a24d369` passed build,
health, device, package-integrity, and documentation-parity checks. ADR-024
then resolved the bounded security delta. First-host RC8 Podman CPU testing
exposed a pre-registration cancel-then-retry race. The bounded request-
correlation fix and exact Expat residual amendment are merged through PRs
#105/#106. Same-source RC9 CPU/CUDA registry images now pass local and exact-
published-digest security qualification, and their digest-pinned control ZIPs
pass local integrity validation. RC9 prerelease publication remains owner-
gated before final browser-download validation and independent-host evidence
can resume
**Priority**: CRITICAL
**Type**: C (ML Runtime Migration / Release Qualification)
**Owner**: Release owner; active agent executes the authorized implementation
and qualification brief
**Decision**: [ADR-022](../../decisions/022-cuda128-blackwell-ml-runtime.md)
**Implementation Brief**:
[TASK103-IMPLEMENTATION-BRIEF-V3-2026-09-24.md](./TASK-103/TASK103-IMPLEMENTATION-BRIEF-V3-2026-09-24.md)

## Objective

Replace the accepted torch 2.6.0/cu126 runtime with the qualified
torch 2.10.0/torchvision 0.25.0 pair and distinct `cpu`/`cuda128` artifacts,
then qualify the rebased Windows Docker/Podman CPU/NVIDIA release without
weakening model correctness, device, security, persistence, or recovery gates.

## Requirements

- WHEN a GPU profile is qualified, THE PROJECT SHALL prove both YOLO and
  EfficientNet execute on CUDA; CPU fallback is not a GPU pass.
- WHEN relative G8/G9 results are reported under gates v3, THE PROJECT SHALL
  use same-host interleaved runs, at least three run directories per side, and
  no overlapping scans or builds.
- WHEN a CUDA build cannot serve the detected GPU, THE APPLICATION SHALL emit
  the matching newer-GPU, older-GPU, CPU-only, driver/container, or precision
  recovery message without implying a fallback occurred when none did.
- WHEN publishing images, THE WORKFLOW SHALL scan and generate an SBOM for the
  exact published digest and preserve written finding dispositions.
- BEFORE publication, THE PROJECT SHALL inventory the shipped NVIDIA runtime
  components for compliance review without making a legal determination.
- AFTER Checkpoint 2, THE PROJECT SHALL land the required pre-publication
  corrections before dispatching images; package/release publication and
  `latest` remain gated on owner confirmation of the exact digests.

## Execution Record

### Phase 0 / Phase 1 - Completed 2026-09-24

- Package hashes and reconstructed pilot tree verified.
- Track L CUDA verdict: PASS on `sm_120`; both models observed on `cuda:0`;
  torch `2.10.0+cu128`; torchvision `0.25.0+cu128`; CUDA build `12.8`;
  minimum free VRAM 2.89 GiB.
- Explicit CPU profile of the `cuda128` image: PASS after correcting the
  qualification identity contract.
- Negative controls N2/N3: PASS. The old cu126 runtime failed the decisive
  Blackwell kernel path as expected; the cuda128 runtime passed.
- Checkpoint 1 acknowledged by the owner with Track L PASS confirmed.

### Phase 2 - Completed 2026-09-28

- [x] Rebased the nine pilot commits onto accepted `main` (`10cd13a`) after
  confirming PRs #77-#84 merged.
- [x] Predeclared gates v3 and implemented fail-closed total-footprint and
  interleaved-run comparison rules before Phase 2 measurement.
- [x] Complete RGB crop conversion, runtime messages, source-build hardening,
  CI/security evidence, documentation, governance, and validation.
- [x] Qualify a new Podman CPU/GPU machine or record unavailable cells as
  `blocked`, never `pass`.
- [x] Rehearse source, artifact/volume, and `-Gpu off` recovery paths without
  deleting the eight named volumes.
- [x] Run rebased final CPU/CUDA qualification with gates v3; preserve every
  run and verdict, including failures.
- [x] Push `feature/task-103-cuda128-ml-runtime` and open
  [Task-103 PR #86](https://github.com/J-Schulein/TowerScout/pull/86) with links to
  ADR-022 and the Track L verdict.
- [x] Land the accepted-baseline Trivy delta gate, fail-closed comparator
  context validation, corrected/sanitized evidence, and alert #215 disposition
  with green CI before H9 dispatch.
- [x] Dispatch CPU and CUDA 12.8 images with `push_latest=false`, then report
  exact digests and scan/SBOM artifacts before any package publication.

### W09 Package Assembly And First-Host Qualification - Completed 2026-09-28

- [x] Merge package-only Podman spaced-path correction in
  [PR #87](https://github.com/J-Schulein/TowerScout/pull/87) with green CI.
- [x] Build final CPU and CUDA 12.8 control ZIPs from accepted package source
  `99de5595b0d98b67c24909c1f2712f72d8714ab3` and bind them to the
  owner-confirmed image digests and shared asset ZIP.
- [x] Verify outer sidecars, all internal checksums, manifest identities,
  compliance inventory, forbidden-file inventory, and package secret hygiene.
- [x] Run exact-package setup on Docker CPU, Docker CUDA, rootless Podman CPU,
  and rootless Podman CUDA; preserve all eight named volumes for each package.
- [x] Reconfirm real-model and memory gates against the exact image digests and
  run an exact-package CUDA `sm_120` kernel probe.
- [x] Complete the first-host per-profile provider/recovery/review-export and
  controlled-error W10 acceptance cells on the exact `rc4` packages.
- [x] Complete exact-`rc4` first-host reboot persistence on all four profiles.
- [x] Resolve policy/signing through ADR-023's unsigned standard-package
  support boundary; signature-enforcing managed endpoints remain out of scope.
- [x] Run the preserved `rc4` package as a preliminary browser-download
  diagnostic and disposition its findings for Task-092.
- [x] Rebuild the updated manuals into same-source RC8 CPU/CUDA image and
  digest-pinned control-ZIP identities because `docs/` is present in both
  surfaces.
- [ ] Publish the owner-approved candidate assets, then complete final
  browser-download and independent-host W10 acceptance cells before claiming
  release readiness.

### W10 Local First-Host Rehearsal - Started 2026-09-28

- [x] Run an exact-package fresh Docker CPU install from a spaced path with new
  volumes, the frozen CPU ZIP/digest, and the frozen asset ZIP.
- [x] Configure live Azure and Google providers without reading or recording
  credentials; pass normal positive detection on both providers.
- [x] Reproduce `tls_ca_untrusted`, run the packaged dry-run/apply repair with
  certificate identities suppressed, and verify repaired Google TLS.
- [x] Preserve provider config, repaired CA trust, assets, port, and image
  identity across a volume-preserving stop and fresh-shell relaunch.
- [x] Implement and locally validate the bounded TLS helper non-default-port
  preservation fix; replacement-package managed-network repetition remains.
- [x] Implement and locally validate cancel readiness against the shared
  detection slot; the real Google cancel-then-next overlay now passes.
- [x] Merge the lifecycle fixes through
  [PR #89](https://github.com/J-Schulein/TowerScout/pull/89) as `95a3ccc` with
  green exact-head CI.
- [x] Preserve the failed `v0.1.3-rc2` CPU/CUDA dispatches and security
  artifacts after G10 blocked two newly disclosed HIGH `linux-libc-dev`
  findings; neither digest is a replacement candidate.
- [x] Land the bounded removal of the unnecessary runtime development package
  through [PR #90](https://github.com/J-Schulein/TowerScout/pull/90), then
  publish new immutable `rc3` tags with `push_latest=false`; both G10 deltas
  passed with zero new findings.
- [x] Assemble replacement CPU/CUDA control ZIPs from `7a5eedd` and repeat
  exact-package setup plus stop/relaunch across Docker/Podman CPU/CUDA without
  deleting any of the eight named volumes per profile.
- [x] Repeat the managed-TLS cell on the fresh `rc3` Docker CPU package,
  including the non-default-port repair lifecycle and persistent trusted bundle.
- [x] Repeat Google normal, Google cancel-then-next, and Azure normal live-
  provider cells on the fresh `rc3` Docker CPU package without retaining
  credentials, request payloads, provider URLs, or screenshots.
- [x] Reboot the first host and verify exact digests, loopback ports, all eight
  named volumes per profile, health/readiness, persistent Docker CPU provider
  configuration and repaired CA trust, post-reboot Google/Azure requests, and
  real Docker/Podman CUDA `sm_120` kernels. Docker restored automatically;
  Podman required a documented manual start of the retained containers.
- [x] Merge the Podman TLS repair lifecycle fix through
  [PR #92](https://github.com/J-Schulein/TowerScout/pull/92) as `cbb574f` and
  the cancellation retry-readiness fix through
  [PR #93](https://github.com/J-Schulein/TowerScout/pull/93) as `fba9dcb`.
- [x] Dispatch new immutable `rc4` CPU/CUDA images from accepted `main`,
  assemble replacement control ZIPs, and repeat affected W09/W10 cells.
- [x] Complete Docker CPU/CUDA and Podman CPU/CUDA provider/recovery/
  review-export workflows plus controlled-error checks in every profile.
- [x] Complete an exact-`rc4` reboot with provider/TLS/device persistence and
  post-reboot Google/Azure workflow checks in every profile.
- [x] Resolve policy/signing scope through ADR-023.
- [x] Complete the preliminary `rc4` browser-download Docker CPU shakedown and
  disposition its findings for Task-092.
- [x] Complete the documentation-aligned RC8 image/package rebuild and local
  integrity validation.
- [ ] Publish the owner-approved exact RC8 assets, then complete final
  exact-candidate browser-download and independent-host cells.

## Acceptance Boundary

Unit/static checks and health/readiness are necessary but do not establish
release readiness. Final claims require exact image/package identity, real
models on the required device, providers, persistence/recovery, and the
independent-host evidence required by Task-091. Missing external prerequisites
remain explicit blockers.

## Evidence

- [Track L evidence index](./TASK-103/TRACK-L-EVIDENCE-INDEX.md)
- [T1000 pilot evidence pointer](./TASK-103/T1000-EVIDENCE-POINTER.md)
- [Gates v3](./TASK-103/task103_gates.v3.json)
- [Phase 2 evidence index](./TASK-103/PHASE2-EVIDENCE-INDEX.md)
- [W09 candidate evidence index](./TASK-103/W09-EVIDENCE-INDEX.md)
- [W10 local first-host evidence index](./TASK-103/W10-LOCAL-FIRST-HOST-EVIDENCE-INDEX.md)

## Publication Boundary

Checkpoint 2 and the replacement H9 dispatch are authorized and recorded. W09
replacement assembly and local qualification are authorized. Package
publication, `latest` promotion, and closeout remain explicitly owner-gated.

## 2026-10-06 Documentation Merge Checkpoint

The owner approved the Task-092 content freeze at `524ba37`; bounded
reproducibility corrections landed at `f8e191d`; and PR #94 merged as
`fc97b32` with green post-merge CI. The next candidate must be rebuilt from the
exact accepted-main commit after the project-state reconciliation. This
checkpoint does not authorize package publication or `latest` promotion and
does not replace the final browser-download or independent-host gates.

## 2026-10-06 Reconciled Source And RC5 Security Checkpoint

PR #95 merged as `a24d369668d27240ed0baa184d071395455b9c95`; both post-merge
workflows passed. Local CPU and CUDA 12.8 images built from that exact source.
Both images passed label/runtime checks, CPU health/readiness, in-image
documentation parity, CUDA 12.8 `sm_120` execution on the RTX PRO 500, local
control-ZIP integrity, and package `-VerifyOnly` checks. These local packages
are non-publishable because they intentionally use mutable local image tags.

Fresh Trivy `0.69.3` scans produced identical CPU/CUDA results and blocked on
14 new HIGH keys. PR #96 merged the application `urllib3==2.8.0` correction as
`b0725e750c1541e7cb60df881d3906f761657089`; its required post-merge checks
passed. The retained scan evidence and second-opinion investigation then
established that ten keys belong to unused Debian Python/libheif packages
pulled in by `gdal-bin`, while the remaining four identify pip's private
`urllib3==2.7.0` and Bookworm OpenSSL. ADR-024 authorizes TASK-104 to remove
only that unused Debian dependency and enforce the exact four-key exception
through October 31, 2026. The 396-key baseline remains unchanged. Publication
remains stopped until TASK-104 passes review and exact local qualification;
GHCR dispatch remains a separate owner action. See
[the full security disposition](./TASK-103/RC5-PREPUBLICATION-SECURITY-DISPOSITION-2026-10-06.md).

## 2026-10-07 ADR-024 / TASK-104 Security Correction

The owner selected the fastest safe path: pin the base-image indexes and pip,
remove `gdal-bin`, fail closed on incomplete or identity-mismatched scans, and
scan locally before registry login or push. CPU and CUDA 12.8 candidates must
prove that Debian GDAL/libheif/Python packages are absent, Fiona still reads
the packaged ZCTA data through its bundled library, the application imports
`urllib3==2.8.0`, and only the exact unexpired residuals match. ADR-024
originally approved four records; the October 9 RC9 amendment adds only exact
`CVE-2026-77214 / libexpat1@2.5.0-1+deb12u4`, bringing the policy to five. A
new key, changed package/version, CRITICAL escalation, unused exception, or
expiry is a release blocker. Final browser-download and independent-host gates
are not reduced by this amendment.

## 2026-10-09 RC9 Expat Stop And Owner Disposition

PR #105 merged the cancellation-race correction as accepted source
`004631754be343a1a9c0a7e0777dfc39e689c9f3`, with green post-merge checks.
Owner-authorized RC9 CPU run `37935858689` stopped at its local security gate
before GHCR login or push on newly disclosed HIGH finding
`CVE-2026-77214 / libexpat1@2.5.0-1+deb12u4`. The paired CUDA run
`37935867972` was cancelled before any scan or publication step. No RC9 image
or `latest` tag was published.

The affected API is `XML_ParseBuffer`. Repository and runtime tracing found no
supported TowerScout caller: Python `pyexpat` was loaded indirectly through
`torchvision.datasets.voc`, but CPython's wrapper uses `XML_Parse`; the Debian
library is retained through the OpenGL/Mesa dependency chain for OpenCV.
Debian Bookworm had no fixed package. `J-Schulein` approved one exact
CPU/CUDA residual through October 31, 2026. The accepted baseline stays at
396 keys and every different or changed HIGH/CRITICAL record still blocks.

## 2026-10-09 Same-Source RC9 Registry And Package Qualification

PR #106 merged the exact Expat residual amendment as accepted-main source
`b3431cf86d8a000462df487685104558ac7becd3`; all required post-merge checks
passed. `J-Schulein` then authorized fresh CPU and CUDA 12.8 dispatches for
`v0.1.0-rc9` with `push_latest=false`.

- CPU run `37942033212` qualified
  `ghcr.io/j-schulein/towerscout@sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`.
  Its config digest is
  `sha256:3dd62907f9f6ab4d76b3ac9b8804a73e4b04f098aad22221f737cbfc595a170a`.
- CUDA run `37942073914` qualified
  `ghcr.io/j-schulein/towerscout@sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
  Its config digest is
  `sha256:aa397626a037531892eb8005004aaef33faaed0c29720444cbf73fe05d5f99ad`.
- Both images carry source label `b3431cf86d8a000462df487685104558ac7becd3`
  and their required `cpu` or `cuda128` flavor label. Both workflows passed
  dependency/Fiona verification, local Trivy comparison before registry
  login, immutable-tag absence, push/config identity, exact-digest Trivy/SBOM,
  and the final comparison. Each reported baseline 396, candidate 79,
  accepted baseline 74, accepted residual 5, blocking 0, severity escalations
  0, and resolved 322. Both `latest` steps were skipped.
- A clean detached checkout of the same source produced
  `towerscout-v0.1.0-rc9-cpu.zip` (199812 bytes, SHA-256
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`)
  and `towerscout-v0.1.0-rc9-cuda128.zip` (199840 bytes, SHA-256
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`).
  Both manifest checks, outer sidecars, all 73 internal checksums across 74
  files, the focused `7/7` package tests, `git diff --check`, and the strict
  `.agent_work` validator passed.
- The retained 800655295-byte browser-downloaded asset ZIP was reverified at
  SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  The RC9-named local staging entry is a same-volume hard link, not an 800 MB
  duplicate. Package-only sensitive-term scans found only expected docs that
  name the generated `FLASK_SECRET_KEY`; no credential values or runtime data
  were found.

No RC9 control package or GitHub release was published at this checkpoint.
Exact release-asset publication remains separately owner-authorized, and the
final support claim still requires browser-downloaded and independent-host
four-profile proof.

## 2026-10-07 Same-Source RC8 Package Assembly

A clean detached checkout of frozen image source
`7827c2af8ecb7d8b21d246b69e135807fa497fd2` produced the two local control
packages without mutable-image, missing-source, dirty-source, no-ZIP, or force
overrides:

- CPU: `towerscout-v0.1.0-rc8-cpu.zip`, 199842 bytes, SHA-256
  `8fd46711b57a25dd71cd879a06fe519674596ee9a71fa66b2347204fe8bc74f0`.
- CUDA 12.8: `towerscout-v0.1.0-rc8-cuda128.zip`, 199850 bytes, SHA-256
  `463d3f2348e369ed647bb8ed66c15588fc4051197e49ac90441552b8318bdada`.

The manifests bind the exact RC8 source, CPU/CUDA flavor, corresponding
registry manifest digest, RC8 asset filename, and authoritative asset SHA-256
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
Both outer sidecars and all 73 internal checksums across 74 ZIP entries passed.
The focused package/manifest regression suite passed `7/7`. The retained
browser-downloaded RC4 asset ZIP is 800655295 bytes and reverified at the same
authoritative content hash; it was not copied under the RC8 filename merely to
duplicate 800 MB before publication. Local packages are retained under the
ignored `dist/rc8-candidate/` directory. No release asset or `latest` tag was
published at that local-assembly checkpoint.

## 2026-10-07 RC8 Validation Prerelease Publication

After explicit owner authorization, the exact CPU package, CUDA 12.8 package,
shared asset archive, and their three SHA-256 sidecars were published in
[GitHub prerelease v0.1.0-rc8](https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc8).
GitHub release ID `406175444` is non-draft and prerelease; `v0.1.2` remains the
Latest release. The RC8 tag resolves to frozen source
`7827c2af8ecb7d8b21d246b69e135807fa497fd2`, and GitHub's recorded sizes and
digests match all six approved local inputs. No image `latest` tag was promoted.
Exact browser-downloaded bytes and independent-host proof remain required.

## 2026-10-08 RC8 Podman Cancellation Finding And Bounded Fix

**Objective**: Resolve the RC8 Podman CPU cancel-then-immediate-retry failure
without changing provider, model, package, volume, or public API behavior.

**Context**: The exact browser-downloaded RC8 Podman CPU package passed setup,
Azure configuration, real CPU detection, ZIP lookup, controlled-error
recovery, review/export, and volume-preserving relaunch. Immediate
cancel-then-retry failed four times, including after Windows reboot with
Docker Desktop closed and the intended rootless Podman machine selected. The
container remained ready, did not restart or exhaust memory, and saw about
16.5 GB of available memory.

**Decision**: Correlate each browser detection and abort request with the same
short-lived request identity. When abort arrives before the run is registered,
retain a 60-second cancellation tombstone for only that identity. A delayed
matching request returns a cancelled empty result before provider/model work;
a new retry identity remains independent. Preserve the existing legacy path
for clients that do not send correlation metadata.

**Execution**: Updated `webapp/js/src/ui/search.js`, the generated
`webapp/js/towerscout.js`, `webapp/towerscout.py`, and `webapp/ts_progress.py`.
Added backend tests for abort-before-admission, abort-during-admission, stale
request separation, and internal metadata hiding. Extended the frontend
cancellation contract to prove `/getobjects` and `/abort` send the same
identity.

**Output**: The exact reproduced ordering is now covered: an early abort is
remembered, the delayed original request performs no provider/model work, the
detection lock is released, and a differently identified retry remains
eligible. No credentials, private AOI coordinates, raw traces, or screenshots
were added to repository evidence.

**Validation**: `12/12` focused admission/progress tests pass; the broader
selected progress/admission/abort route set passes `15/15`; the frontend
cancellation recovery contract, ProviderStateManager contract, global
contract, debug logging contract, generated-bundle consistency check, and
`git diff --check` pass. A wider name-filtered cancellation run also confirmed
all 13 relevant TowerScout tests passed; its two additional selected tests
were blocked by local Defender and temporary-directory conditions unrelated
to this change. An isolated validation image layered only the corrected
runtime files onto the exact RC8 CPU digest and reused the eight preserved
RC8 Podman named volumes. Azure cancel-then-immediate-retry browser run
`20261008-171359-azure-cancel` passed: abort returned HTTP 200 in 51 ms with
zero detections after cancellation, and the immediate retry completed one
real tile with 14 detections in about 21.7 seconds. There were no page errors;
the only HTTP error was the nonfunctional `favicon.ico` 404. The temporary
container was removed without removing volumes, and the original RC8 Podman
CPU container was restored healthy on port 5000.

**Disposition**: PR #105 carried the bounded fix through review, and the
same-source RC9 image/package now supplies the replacement candidate. Repeat
the affected exact-package Podman acceptance cells from browser-downloaded RC9
bytes. The local validation overlay was not final release qualification.
