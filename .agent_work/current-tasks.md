# Current Tasks - Official Adoption And Handoff

**Delivery Period**: October 20-October 30, 2026
**Last Updated**: October 21, 2026
**Closeout Target**: October 30, 2026
**Delivery target**: October 27; support October 28-30.
**Current focus**: Complete reviewed adoption into cdcai, official artifact
qualification, wiki/video and owner delivery. Chris accepted ownership,
Administrative access, delivery direction and the proposed v0.1.3 release
name on October 20. Package permissions and actual delivery remain pending.
See [handoff navigation](context/status/Handoff-Planning/README.md).

**October 20 update:** Fork wiki rehearsal completed (14 pages plus sidebar).
Tuesday is substantially complete with documented follow-ups; official cdcai
publication and delivery remain pending. See the
[rehearsal and plan review](context/status/Handoff-Planning/2026-10-20-WIKI-REHEARSAL-AND-PLAN-REVIEW.md).

**October 21 update:** Tuesday preparation is documented, with detailed owner
backlog and security discussion materials. Read-only cdcai checks confirm
ancestry/admin/Actions allowlist. Chris subsequently approved enabling Issues;
that setting change is applied and verified. Package publication is not yet
proven. Wednesday PR/build review drafts are ready locally; no source adoption
or official acceptance. See the
[readiness review](context/status/Handoff-Planning/2026-10-21-READINESS-AND-ADOPTION-REVIEW.md).

**Final local source review:** 63 focused checks passed; archive links and
current Issues/CI wording corrected. See the
[review record](context/status/Handoff-Planning/2026-10-21-FINAL-ADOPTION-SOURCE-REVIEW.md).
Remote final-head checks, cdcai adoption and official-byte qualification remain open.

**Dependency follow-up:** PR #113 now includes aiohttp and Pillow security
corrections. Blocking CI passes; review approval, fork merge and actual
adoption integration remain pending. The local integration rehearsal
passed 144 checks on repeat; its initial Windows loopback failure is
retained in the [updated review](context/status/Handoff-Planning/2026-10-21-PR113-DEPENDENCY-AND-ADOPTION-REVIEW.md).

## Qualification history through October 19

The following narrative retains the candidate progression; older pending
statements describe that sequence. Current task summaries below control
remaining work, subject to the accepted decisions.

**Historical focus**: Qualify a dependable, downloadable Windows 11 application from
accepted `main` across Docker/Podman and CPU/NVIDIA profiles. Documentation
content is frozen and merged through PR #94, and the project-state
reconciliation is merged through PR #95. RC8 browser testing exposed a
pre-registration cancellation race; the bounded fix merged through PR #105.
PR #106 then added the owner-approved exact, expiring Debian Expat residual.
The same-source RC9 CPU/CUDA images pass the local and exact-published-digest
security gates, and their digest-pinned control ZIPs are published in the
non-Latest `v0.1.0-rc9` validation prerelease. Exact browser-downloaded RC9
Docker CPU/CUDA and Podman CPU/CUDA first-host acceptance passed on October
13, including the affected cancel-then-immediate-retry path. Docker and Podman
reboot persistence now pass. One independent NVIDIA host also passed all four
profiles, but exposed beginner-path runtime/documentation/export findings and
did not satisfy the original CPU-only/Podman-without-Docker allocation.
ADR-025 now selects a corrected-candidate four-profile run on this machine
and that independent NVIDIA host. TASK-105 corrections merged through PRs
#109/#110 at accepted `main` `835cbb9`. The same-source `v0.1.3-rc5` CPU/CUDA
images passed strict local and exact-digest gates, and the six-file GitHub
prerelease is immutable and non-Latest. Browser-downloaded bytes and sidecars
match all six published hashes; File Explorer extraction retained Mark of the
Web and internal checksums passed. The owner freed disk space. Exact-package
Docker CPU and CUDA setup, asset import, device selection, managed TLS repair,
and fixed combined-model probes now pass on this host. The owner reports live
Google/Azure detection on both Docker profiles; CSV, KML, and dataset downloads
were independently found and parsed. The owner reports CUDA cancel/retry and
browser ZIP lookup succeeded. Both Docker profiles passed shipped stop/relaunch
with all eight named volumes, both provider configured states, assets, device
policy, and managed TLS retained. The owner refreshed both browser sessions,
downloaded and restored a dataset in each, and reported usable review state.
Both Podman profiles passed exact-package setup, intended devices, real
combined-model probes, provider setup, browser workflows, exports, and shipped
stop/relaunch. The bidirectional engine switch preserved both RC5 Docker and
Podman installations; dataset restore and review controls worked after each
switch. After the Windows reboot, all four profiles retained their original
volumes, configured providers, assets, correct devices and digests, and normal
TLS. The owner restored datasets, used review controls, and downloaded new
files in each; the new dataset ZIPs parsed cleanly. The Podman Windows client
socket required one volume-preserving machine stop/start to recover. The
owner subsequently confirmed CPU browser cancel/retry and public ZIP lookup
on both engines, closing the remaining first-host browser cells. The
independent four-profile RC5 operational report and extracts have now been
reviewed: all 108 extract hashes/sizes and 61 JSON files verified. The owner
confirms independent-host dataset download/restore passed and that model
comparisons used the same public NYC area. Credit these functional results;
the accepted finding dispositions and evidence-method reconciliation are
recorded in the
[RC5 intake](./tasks/active/TASK-105/RC5-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-16.md).
The owner approved bounded candidate acceptance on October 19 for reviewed
commit `33bd3a3`: the
[accepted decision](./decisions/026-rc5-bounded-candidate-acceptance.md),
[qualification matrix](./tasks/active/TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md),
[operations addendum](../docs/release/rc5-operations-addendum.md), and
[cdcai handoff](../docs/release/task105-cdcai-handoff.md) credit the two-host
functional results and document accepted short-path/Python/test-method
exceptions. PR #111 merged this acceptance and handoff documentation into
`main` as `2c86c12` on October 19; official adoption remains pending. All six
original browser assets, tag/source, immutable status, and
release attestation were reverified unchanged on October 19. No new runtime
test, image build, release-asset edit, or official publication follows from this closeout.
The Task-087 launcher
redesign remains preserved and deferred, not a release gate.

**Historical `rc4` Control-Package Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`

**Confirmed `rc4` Runtime Image Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`
**Accepted Documentation Content Source**: `fc97b3200785d307b39ef5a683979002a5f409e6`
**Preliminary Local RC5 Source**: `a24d369668d27240ed0baa184d071395455b9c95`
**Accepted RC9 Replacement Source**:
`b3431cf86d8a000462df487685104558ac7becd3`
**Historical RC9 Publishable Candidate Source**:
`b3431cf86d8a000462df487685104558ac7becd3`. The same-source
`v0.1.0-rc9` CPU and CUDA 12.8 images passed local and exact-published-digest
security qualification with `push_latest=false`. The locally verified control
packages bind only those exact pinned manifest digests. The owner-authorized
non-Latest RC9 prerelease is published; every `latest` promotion and any
stable/general release remain separately owner-gated.
**Current RC5 Candidate Source**:
`835cbb910573a931350c5b704d14496952d7ef87`, published as immutable non-Latest
`v0.1.3-rc5`. The closeout review branch contains supplemental documentation
and evidence, not an implicitly selected official release source.
**Authoritative Branch**: `main`
**Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
**RC5 Security Boundary**: [ADR-024](./decisions/024-rc5-security-gate-and-residual-boundary.md)
**Final-Candidate Host Allocation**: [ADR-025](./decisions/025-two-host-final-candidate-qualification.md)
**Exact RC5 Bounded Acceptance**: [ADR-026](./decisions/026-rc5-bounded-candidate-acceptance.md)
**Acceptance**: [Windows deployment prioritization v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
**Work Plan**: [Windows deployment hardening v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)

## Current Release State

- The published `v0.1.2` pilot remains immutable.
- New work starts from accepted `main`; PRs #64/#67 were not merged or
  reconciled and their exact heads are preserved by archive tags.
- The Task-103 `rc4` CPU and CUDA 12.8 (`cuda128`) images have distinct
  confirmed digests. W09 control packages are assembled and locally qualified
  from accepted source. Because `docs/` is also baked into the images and
  served in-app, the ADR-023/Task-092 documentation refresh requires new
  documentation-aligned image and control-package identities before final
  distribution. Package publication and `latest` remain owner-gated.
- `J-Schulein` approved the documentation content freeze at `524ba37`. The
  bounded post-freeze reproducibility corrections landed at `f8e191d`, PR #94
  merged as `fc97b32`, and post-merge CI passed. No documentation review
  blocker remained for the now-completed clean-source RC8 rebuild.
- PR #95 merged the bounded project-state reconciliation as `a24d369`. PR #96
  then merged the application `urllib3==2.8.0` correction as `b0725e7`; all
  applicable post-merge checks passed. Retained Trivy evidence shows that ten
  of the 14 new HIGH keys come from unused Debian packages pulled in by
  `gdal-bin`; the other four are pip-private urllib3 and Bookworm OpenSSL
  records. ADR-024 originally authorized removing `gdal-bin` and accepting
  only those four exact records through October 31, 2026 using a fail-closed
  residual file.
  TASK-104 implements that boundary and the scan-before-push workflow. The
  396-key baseline remains unchanged.
- PRs #97-#100 merged the ADR-024 implementation, shell-quoting correction,
  transport-safe config-identity rule, read-only exact-digest recovery, and
  immutable-tag overwrite/race protection. Owner-authorized CPU and CUDA 12.8
  dispatches for `v0.1.0-rc5` with `push_latest=false` then passed. CPU
  verification run `37663225514` qualified exact registry manifest
  `sha256:8e624a332a0b70ce70a6d29625d8482bb04651767d38d21e46cac16932b65bee`
  without replacing its tag. CUDA publish run `37663527863` qualified exact
  registry manifest
  `sha256:e50a43293d07c6904b103201f65b142cc38267d4d263be67e702c672628dbfec`.
  Each exact-digest comparison reported baseline 396, candidate 78, accepted
  baseline 74, accepted temporary residuals 4, blocking 0, severity
  escalations 0, and resolved 322. No `latest` promotion step ran and no
  package was published. The individually qualified images have different
  source labels, so final paired-package identity remains intentionally
  unfrozen pending an owner traceability decision.
- PR #101 recorded the RC5 evidence and merged as
  `7827c2af8ecb7d8b21d246b69e135807fa497fd2` after exact-head and
  post-merge checks passed. Historical `v0.1.0-rc6-cpu` and
  `v0.1.0-rc7-cpu` tags already existed from June source and were preserved;
  `v0.1.0-rc8` was the first unused CPU/CUDA pair. Owner-authorized CPU run
  `37674158762` and CUDA run `37674161407` both passed build/load, the local
  dependency/Fiona and Trivy gates, immutable-tag absence, push/config
  identity, exact-published-digest Trivy/SBOM, and final comparison. The frozen
  manifests are CPU
  `sha256:2e040c3b09d1aa493b205ec2100c112a839ab7a9bfc90a639f73918e06135412`
  and CUDA 12.8
  `sha256:712beb4e143495ba72705cc56b89a939c5bebfdc47dc2f6d0694c81e9e60ca57`.
  Both carry the exact `7827c2a` source label and passed with baseline 396,
  candidate 78, accepted baseline 74, accepted residual 4, blocking 0,
  severity escalations 0, and resolved 322. Both `latest` steps were skipped;
  no control package or release was published. A clean detached checkout of
  `7827c2a` then produced local control ZIPs with SHA-256
  `8fd46711b57a25dd71cd879a06fe519674596ee9a71fa66b2347204fe8bc74f0`
  (CPU) and
  `463d3f2348e369ed647bb8ed66c15588fc4051197e49ac90441552b8318bdada`
  (CUDA 12.8). Both manifests, outer sidecars, all 73 internal checksums, and
  the focused `7/7` package tests passed. The retained browser-downloaded asset
  ZIP remains byte-identical to the required RC8 asset at SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`;
  it was not duplicated locally merely to rename it.
- First-host RC8 Docker CPU/CUDA browser acceptance passed the exercised
  provider, TLS-repair, model, and cancellation paths. RC8 Podman CPU passed
  setup, Azure/provider persistence, real CPU detection, ZIP lookup,
  controlled-error recovery, review/export, and relaunch, but immediate
  cancel-then-retry reproduced a request-ordering race four times, including
  after a reboot with Docker Desktop closed. The cancelled browser request
  reached `/getobjects` after `/abort` had returned idle/ready, so the retry
  received `DETECTION_BUSY`. Correct Podman target selection, container health,
  and available memory were confirmed; RC8 is therefore not the final
  candidate. A request-correlated cancellation tombstone fix now passes
  focused source tests and an isolated Podman CPU Azure cancel-then-retry
  runtime smoke layered on the exact RC8 image with its preserved named
  volumes. The cancelled run returned zero detections and the immediate retry
  completed with 14 real detections. The reviewed RC9 image/package now
  supplies the required replacement; affected-profile repetition from exact
  browser-downloaded RC9 bytes remains required. The overlay itself was not a
  release candidate.
- PR #105 merged the request-correlated cancellation correction as accepted
  source `004631754be343a1a9c0a7e0777dfc39e689c9f3`; its required post-merge
  checks passed. Owner-authorized RC9 CPU run `37935858689` then found new
  HIGH key `CVE-2026-77214 / libexpat1@2.5.0-1+deb12u4` and failed closed at
  the local comparator before GHCR login/push. CUDA run `37935867972` was
  cancelled before any publication step. No RC9 image or `latest` tag was
  published. Reachability review found no supported TowerScout call to the
  affected `XML_ParseBuffer` API, and Debian Bookworm had no fixed package.
  `J-Schulein` approved adding this one exact CPU/CUDA residual under the same
  October 31 expiry. The baseline remains 396 keys; every other new or changed
  HIGH/CRITICAL finding remains blocking.
- PR #106 merged the five-key residual-policy amendment as accepted source
  `b3431cf86d8a000462df487685104558ac7becd3`; required post-merge checks
  passed. Owner-authorized RC9 CPU run `37942033212` and CUDA 12.8 run
  `37942073914` both passed build/load, dependency/Fiona verification, local
  Trivy comparison before login, immutable-tag absence, push/config identity,
  exact-published-digest Trivy/SBOM, and the final comparison. The immutable
  manifests are CPU
  `sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`
  and CUDA 12.8
  `sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
  Both comparisons reported baseline 396, candidate 79, accepted baseline 74,
  accepted residual 5, blocking 0, severity escalations 0, and resolved 322.
  Both `latest` steps were skipped. A clean detached checkout of `b3431cf`
  then produced control ZIPs with SHA-256
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`
  (CPU) and
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`
  (CUDA 12.8). Both manifests, outer sidecars, all 73 internal checksums, and
  the focused `7/7` package tests passed. The shared asset bytes were
  reverified at SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Owner-authorized GitHub release `v0.1.0-rc9` (release ID `408047593`) was
  published at `2026-10-09T15:26:48Z` as a non-draft, non-Latest prerelease
  targeting exact source `b3431cf86d8a000462df487685104558ac7becd3`.
  GitHub reports all six assets uploaded with the approved byte sizes and
  SHA-256 digests; all six unauthenticated browser-download URLs returned HTTP
  200. Stable `v0.1.2` remains Latest, and no GHCR `latest` tag was promoted.
- Independent host `INDEP-HOST-01` used the exact RC9 public bytes and passed
  Docker CPU/CUDA and Podman CPU/CUDA setup, real model/device execution, both
  providers, detection parity, cancellation/retry, controlled recovery,
  exports, stop/relaunch, and reboot. Sanitized extracts are retained outside
  the repository at ZIP SHA-256
  `39a4052a5ac2bb99ba994453b39980b5688ecb0d8586e1827e811fb92c588145`;
  all 42 JSON files parse and all 78 internal manifest rows match. The run also
  confirms the fresh Podman GPU pull timeout, mixed Docker/Podman startup race,
  PowerShell 7 provider-install/hash failure and partial-retry defect,
  misleading provider check, browser export gap, and smaller documentation/
  reproducibility findings. Only Docker CPU received the complete click-by-
  click UI workflow; the original CPU-only and Podman-without-Docker host
  allocation had not been completed. RC9 therefore remains a
  validation prerelease and must not be promoted.
- Exact browser-downloaded RC9 Podman CPU first-host acceptance passed from the
  CPU control ZIP at SHA-256
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`,
  the shared asset ZIP at
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`,
  and exact image digest
  `sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`.
  The rootless Podman 6.0.2/package-local Compose path passed setup on the
  supported alternate port 5235 with Docker Desktop closed, real Azure and
  Google CPU detection, Google TLS repair, ZIP lookup, cancellation with zero
  results followed by an immediate 14-detection retry, controlled HTTP 400 to
  HTTP 200 recovery, Review navigation, nonempty CSV/KML and valid dataset ZIP
  export, eight-volume stop/relaunch persistence, exact running Help content,
  and loopback-only healthy runtime. No provider key, certificate identity,
  raw browser trace, screenshot, or AOI is retained in repository evidence.
- Exact browser-downloaded RC9 Podman CUDA first-host acceptance passed from
  the CUDA control ZIP at SHA-256
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`
  and exact image digest
  `sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
  The package-local Compose and NVIDIA CDI path passed real Azure cancellation
  with immediate 14-detection retry, managed Google TLS repair and required
  relaunch, real Google detection, ZIP lookup, controlled-error recovery,
  Review and CSV/KML/dataset exports, byte-identical Help, eight-volume
  persistence, and post-relaunch detection. Both models ran on CUDA 12.8 for
  the `sm_120` NVIDIA device with no CPU fallback.
- Exact browser-downloaded RC9 Docker CPU first-host acceptance passed from the
  same CPU control ZIP, shared asset ZIP, and exact CPU image digest. Docker
  Desktop passed real Azure cancellation with immediate 14-detection retry,
  managed Google TLS repair and required relaunch, real Google detection, ZIP
  lookup, controlled-error recovery, Review and CSV/KML/dataset exports,
  byte-identical Help, eight-volume persistence, and post-relaunch detection.
  Both models remained on CPU with no CUDA-selection marker.
- Exact browser-downloaded RC9 Docker CUDA first-host acceptance passed from
  the published CUDA control ZIP, shared asset ZIP, and exact CUDA image
  digest. Docker Desktop passed CUDA 12.8/`sm_120` device and kernel checks,
  real Azure cancellation with immediate 14-detection retry, managed Google
  TLS repair and required relaunch, real Google detection, ZIP lookup,
  controlled-error recovery, Review and CSV/KML/dataset exports,
  byte-identical Help, eight-volume persistence, and post-relaunch detection.
  Both models ran on CUDA with no CPU fallback.
- Full readiness requires actual YOLO and EfficientNet work on the required
  device in all four profiles plus independent-computer reproduction.
- Static checks, health/readiness, mocked tests, or CPU fallback are not
  substitutes for the required runtime evidence.
- ADR-023 resolves the signing/policy choice: the standard Windows package is
  unsigned and supports only users/sites that permit its supplied wrappers.
  Signature-enforcing managed endpoints are outside the standard claim.
- Missing machines, assets, provider accounts, authoritative download hashes,
  or failed tests are blockers and must remain visible in the forecast.
- cdcai adoption and external publication remain owner-authorized actions.

---

## Active Delivery Work

### **TASK-105: Final Release Correction And Qualification**

**Status**: IN_PROGRESS - corrections merged through PRs #109/#110, and the
same-source `v0.1.3-rc5` image/security and immutable publication gates passed.
Two-host functional qualification is accepted under ADR-026, and PR #111
merged the acceptance and handoff documentation as `2c86c12`. Official cdcai
adoption, official-byte qualification, and verified material receipt remain
pending.

**First-host checkpoint (October 14, before independent-host closeout)**:
Exact browser-downloaded Docker CPU/CUDA installs, combined-model device probes,
and owner-observed Google/Azure detection pass on this host. Export files were
found and parsed; CUDA browser cancel/retry and ZIP lookup were owner-observed.
Both Docker profiles passed shipped stop/relaunch and retained provider/asset/
device/TLS state; the owner refreshed both and restored exported datasets.
Exact browser-extracted Podman CPU/CUDA packages passed internal integrity,
first image pulls, asset import, selected package-local Compose provider,
guided normal-TLS repair, intended CPU/CUDA readiness, and fixed combined-model
probes. Both Podman apps show Google/Azure configured and selected-provider
geocoding works. The owner reports Google/Azure browser detection, result views,
and CSV/KML/dataset controls work on both; three new export sets parsed cleanly.
The owner also confirmed Podman CUDA cancel/retry and browser ZIP navigation.
Both Podman profiles passed shipped stop/relaunch with their original eight
volumes, provider settings, assets, device, and normal TLS retained. After
refresh, the owner reported in-memory results cleared and previously downloaded
datasets restored correctly. Two new post-restart export sets parsed cleanly.
The shipped Podman stops, machine stop, Docker Desktop start, and shipped Docker
starts then passed; both Docker profiles retained original volumes, configured
providers, assets, devices, digests, and normal TLS. The owner confirmed Docker
browser dataset restore, review, and new downloads; new exports parsed cleanly.
The return switch to Podman passed runtime checks for both RC5 profiles and
their original volumes. Older RC9 containers needed an explicit start after
the Podman machine restart and are healthy again. The owner confirmed dataset
restore and review controls work on both Podman profiles after the return
switch. After a Windows reboot, both Docker profiles passed shipped startup,
readiness, original eight volumes each, both providers, assets, device, exact
digest, and normal TLS. The owner restored a dataset, used review controls, and
downloaded new files in each; two dataset ZIPs parsed with clean CRCs. Docker
Desktop then quit. The Podman machine reported running but its Windows client
socket was unavailable; a normal machine stop/start restored the connection
without changing containers or volumes. Both RC5 Podman profiles passed shipped
startup, original eight volumes each, both providers, assets, device, exact
digest, and normal TLS. The owner restored a dataset, used review controls, and
downloaded new files in each; two dataset ZIPs parsed with clean CRCs. The two
retained RC9 containers needed explicit start and returned healthy. This host's
four-profile reboot-persistence gate passed. Independent-host evidence was
subsequently reviewed and accepted in the October 19 closeout below.
The owner subsequently confirmed Podman CPU and Docker CPU browser
cancel/retry excluded cancelled results, succeeded on retry, and navigated from
a public ZIP lookup. Docker CPU/CUDA were restored through the shipped scripts
after that check and are ready, healthy, with both providers configured,
correct devices and digests, and eight named volumes each. The Podman machine
is stopped for Docker coexistence.
This host's default Python 3.14 caused the pinned provider install to fail;
selecting installed Python 3.12 through the shipped
helper succeeded on ordinary retry. This tested-prerequisite deviation is
recorded in the task; the guide's default-`python` example remains a docs gap.
**October 19 closeout**: Two-host functional evidence and accepted finding
dispositions are consolidated in the RC5 closeout matrix. The owner-approved
ADR-026 and operations/handoff supplements merged through PR #111 as
`2c86c12`. Official cdcai adoption, official-byte qualification, and named
maintenance custody remain pending.

**October 19 post-merge verification**: Main CI run `39290490547` passed.
Controller workflow `39290490621` initially stopped at an npm `ECONNRESET`
during test-utility installation, before controller tests ran; its failed-job
rerun passed, and all three controller/helper jobs are successful. The two
PR #111 bot findings identify acceptance-guidance inconsistencies. The bounded
follow-up adds ADR-026 to root guidance and replaces the stale independent-host
status with the accepted closeout. The strict agent-work validator, 34 local
document targets, acceptance/status consistency checks, and `git diff --check`
passed for the two-file documentation correction.
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-105-final-release-correction-and-qualification.md`

Current scope:

- Preserve the RC9 finding dispositions and exact RC5 acceptance under ADR-026.
- Review the official source/artifact delta, incorporate accepted operating
  restrictions into packaged and served documentation, and freeze official identities.
- Pass fresh security and actual-download integrity checks and qualify affected
  real-package, model, provider, persistence and recovery paths before recommendation.
- Record official delivery and Chris's receipt with TASK-089.

ADR-026's approved evidence substitutions apply to exact `v0.1.3-rc5` only.
Do not automatically carry acceptance to changed official bytes. CPU-only
hardware and Podman-without-Docker remain unqualified under ADR-025; preserve
the supported-host and unsigned-package boundaries.


### **TASK-103: CUDA 12.8 Blackwell ML Runtime**

**Status**: IN_PROGRESS - the CPU/CUDA 12.8 bridge is included in exact RC5's
bounded two-host acceptance under ADR-026. Preserve earlier runtime evidence;
official changed-artifact qualification and the ADR-022 maintenance obligation
remain. The bridge review is due January 31, 2027 or an earlier ADR-022 trigger.
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md`

Current scope:

- Preserve distinct CPU/CUDA identities, real-model/device results, accepted
  security controls and historical qualification evidence.
- Review and qualify affected runtime behavior in the official build; source
  checks and healthy endpoints alone do not establish model/device readiness.
- Hand off the ADR-022 bridge review and replacement decision to Chris with
  the required real-model/device regression evidence.
- Keep older rc4/RC8/RC9 records historical; exact RC5 acceptance does not
  authorize stable publication or qualify a changed official artifact.


### **TASK-104: RC5 Security Gate And Residual Disposition**

**Status**: IN_PROGRESS - accepted RC5 has dated October 14 security results.
Official cdcai builds require fresh local scan-before-push and exact-published-
digest verification. Preserve the 396-key baseline and exact five residuals;
their acceptance expires October 31, 2026 at 23:59:59 UTC. Prepare the security
follow-up for Chris before closeout; no exception is extended by handoff.
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-104-rc5-security-gate-and-residual-disposition.md`

Current scope:

- Keep the 396-key accepted baseline unchanged.
- Preserve merged base/pip pins and Debian GDAL removal; verify the official
  build retains these controls and affected Fiona/ZCTA behavior.
- Review the reconciled security-review custody note and its remaining identity
  question; do not treat an old review as a fresh scan result.
- Match only the exact pip-private urllib3, Bookworm OpenSSL, and Debian Expat
  records in the owner-approved, expiring residual file.
- Build/load/scan locally before any push; verify registry config identity and
  exact-digest scan/SBOM evidence before any `latest` promotion.

### **TASK-095: Governance And AI-Ready Handoff Foundation**

**Status**: IN_PROGRESS - W00 alignment complete; Phase B handoff governance continues
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md`

Current scope:

- Make the v2 main-based plan discoverable from active entrypoints.
- Remove PR #67/Task-087 resume gates from current execution direction while
  preserving their history.
- Correct misleading release-critical skill commands and evidence guidance.
- Keep the active board, backlog, requirements, design, and handoff consistent.

### **TASK-091: Owner-Runnable Release Qualification**

**Status**: IN_PROGRESS - exact fork `v0.1.3-rc5` has bounded two-host acceptance
under ADR-026. Preserve the RC9 first-host and independent-intake history.
Official cdcai source/artifact delta review, fresh security/integrity checks,
affected real-package/profile qualification, and owner receipt remain.
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md`

Current scope:

- Record accepted source, host/runtime availability, candidate/package/assets,
  ADR-023 policy inputs, fixtures, and provider-account prerequisites.
- Attempt an extracted real control-package setup immediately when verified
  package and asset ZIPs are available; do not substitute a source build.
- Preserve `rc4` as the clearly labeled, non-qualifying browser-download
  diagnostic and RC8/RC9 as historical evidence. Bind official qualification
  to exact browser-downloaded official packages and published image identities;
  use ADR-026 only within its explicit RC5 boundary.
- Extend truthful external combined-model qualification under W05, then bind
  W09/W10 evidence to exact ZIP hashes and image digests.
- Report `pass`, `fail`, `blocked`, `not_run`, or justified `not_applicable`;
  never infer readiness from an absent prerequisite.

### **TASK-097: Podman CPU/GPU Final Path Qualification**

**Status**: IN_PROGRESS - exact RC5 Podman CPU/CUDA evidence is accepted within
ADR-026's two-host boundary and method exceptions. Preserve earlier defect and
recovery records. Official changed-artifact checks and packaged short-path/
Python guidance remain; Podman-without-Docker and rootful operation are unqualified.
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-097-podman-final-path-qualification.md`

Current scope:

- Qualify Podman on both available hosts with Docker Desktop closed, the
  approved Compose provider, and documented Python prerequisite. Do not claim
  Podman-without-Docker installation coverage.
- Bind operations to the intended machine/connection and fail before mutation
  on a target mismatch.
- Require CPU inference and NVIDIA CDI CUDA inference with no silent fallback.

### **TASK-092: Documentation Currentness And Information Architecture**

**Status**: IN_PROGRESS - RC5 supplemental operating restrictions are accepted.
Short-path/Python guidance is now integrated into maintained manual and HTML
sources ([October 20 verification](context/status/Handoff-Planning/2026-10-20-PODMAN-MANUAL-INTEGRATION.md)).
Verify inclusion in official packages and served Help, official links, official cdcai wiki publication (fork rehearsal complete),
final screenshots/video, and owner receipt. The supplement is not in immutable
RC5 downloads. Chris confirmed ownership and access on October 20.
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-092-documentation-currentness.md`

Current scope:

- Keep active agent/task directions aligned with the main-based delivery.
- Update public and in-app instructions only against observed package behavior
  and exact accepted artifact identities.
- Execute the detailed child plan at
  `.agent_work/tasks/active/TASK-092/wiki-information-architecture.md`; keep
  exact release instructions available offline and avoid independently
  maintained Wiki/package duplication.
- Account for `docs/` in both control ZIPs and OCI images; verify running-app
  Help against the documentation-aligned image before final acceptance.
- Preserve historical pilot documentation as clearly historical.

### **TASK-093: Persistent Data Lifecycle And Recovery Rehearsal**

**Status**: IN_PROGRESS - RC5 recovery, lifecycle, and restore evidence is credited
within ADR-026's explicit method exceptions. Preserve historical RC9 reboot
and recovery records. Review the official artifact delta, rerun affected
recovery/persistence paths, and hand off tested dataset/volume/rollback
boundaries without claiming an untested cross-version volume downgrade.
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-093-persistent-data-recovery.md`

Current scope:

- Preserve all eight named volumes and successful review/export inputs.
- Prove stop/relaunch, reboot, cancellation/error recovery, and a successful
  next request on the exact candidate.
- Rehearse rollback/recovery without destructive volume cleanup.

---

## Preserved, Completed, Deferred, Or Owner-Gated Work

### **TASK-087: Host-Side TLS Repair Control Plane**

**Status**: ARCHIVED / DEFERRED - PRs #64/#67 closed without merge; future work
requires a new task and branch from then-current `main`
**Task File**: `.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md`

The exact PR heads, launcher code, and review/evidence history are preserved by
archive tags and the
[final disposition record](./context/archive/2026-09/TASK-087-PR64-PR67-FINAL-DISPOSITION-2026-09-24.md).
Do not merge, reconcile, extend, resume, or repeatedly review those branches as
a deployment prerequisite. The existing command-based lifecycle and TLS paths
remain the release path; only bounded defects reproduced there are in scope.

### **TASK-089: cdcai Adoption Preparation And Ownership Transfer**

**Status**: IN_PROGRESS - ownership, Administrative access, delivery direction
and proposed official release name confirmed October 20. Local preparation
is underway; reviewed adoption and official qualification/publication remain.
**Task File**: `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`

No cdcai mutation or external publication occurs without owner qualification
and explicit authorization.

---

## Delivery Sequence And Checkpoints

1. [x] Complete W00 entrypoint, decision, task, and release-critical skill
   alignment; pass the strict `.agent_work` validator and contradiction review.
2. [x] Complete W01 inventory and attempt a real downloaded/extracted package
   install as soon as verified control and asset ZIPs are available.
3. [x] Record the Day-1 forecast as `go`, `at_risk`, or `blocked`, with each
   blocker, owner, and next check named.
4. [x] Select, review, and merge the evidence-required W02-W08 fixes and W05
   harness through PRs #77-#83; runtime acceptance proof remains.
5. [x] By Day 3, require a corrected Docker/Podman rehearsal plus real combined
   inference or revise the forecast.
6. [x] Freeze exact W09 source/images/ZIPs/assets/fixtures/tools before final
   distribution.
7. [x] Run the preserved `rc4` browser-download shakedown as preliminary
   diagnostic evidence, then incorporate applicable findings into Task-092.
8. [x] Freeze Task-092 content, merge the accepted documentation through PR
   #94, and confirm post-merge CI.
9. [x] Complete ADR-024/TASK-104, merge the bounded security correction and
   its exact Expat amendment, freeze the reconciled accepted-main source, and
   qualify same-source RC9 CPU/CUDA images.
10. [x] Assemble and locally verify digest-pinned RC9 CPU/CUDA control ZIPs
    and the six-asset publication set.
11. [x] After owner authorization, publish the exact RC9 assets and
    authoritative hashes before final browser-download extraction testing or
    tester distribution.
12. [x] Complete RC9 first-host and one independent-NVIDIA-host four-profile
    reproduction; preserve the reported deviations and findings rather than
    treating them as a final-release pass.
13. [x] TASK-105 corrections merged through PRs #109/#110 at `835cbb9`.
14. [x] Exact `v0.1.3-rc5` was published as an immutable non-Latest fork candidate after its dated security gates.
15. [x] Two-host RC5 functional evidence received bounded acceptance under ADR-026 on October 19, with explicit method exceptions and installation restrictions.
16. [x] Chris confirmed ownership, access, delivery direction and proposed official release name on October 20.
17. [ ] Finish adoption review and permission checks, then execute the authorized cdcai PR/merge sequence.
18. [ ] Freeze official identities, pass fresh security and official-byte/affected runtime qualification, and authorize public recommendation.
19. [ ] Deliver wiki/video, owner guidance, backlog and private-material index to Chris; verify receipt by October 27. Deliver the leadership report separately to the outgoing lead's manager.
20. [ ] Complete support and handoff closeout October 28-30 without silently extending security exceptions.

## Runtime Coordination

State the engine/profile before runtime work and verify it is available. When
the current session grants W00-W10 implementation scope, routine validation may
continue without repeated approval for every command. If Docker Desktop,
Podman, a restart, or another external prerequisite is unavailable, record the
blocker and continue safe non-runtime work. Never delete named volumes or mutate
an unverified Compose/Podman target.

## Related Sources

- [Prioritization v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
- [Implementation plan v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)
- [Static verification boundary](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2-verification.md)
- [Post-Day-7 suggestions](./context/status/Reprioritization%20Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md)
- [Task Backlog](./task-backlog.md)
- [Requirements](./requirements.md)
- [Design](./design.md)
- [Completed Tasks](./completed-tasks.md)
