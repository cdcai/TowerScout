# Current Tasks - Final Candidate Build And Acceptance

**Sprint Period**: October 5-October 16, 2026
**Last Updated**: October 9, 2026
**Focus**: Qualify a dependable, downloadable Windows 11 application from
accepted `main` across Docker/Podman and CPU/NVIDIA profiles. Documentation
content is frozen and merged through PR #94, and the project-state
reconciliation is merged through PR #95. RC8 browser testing exposed a
pre-registration cancellation race; the bounded fix merged through PR #105.
PR #106 then added the owner-approved exact, expiring Debian Expat residual.
The same-source RC9 CPU/CUDA images pass the local and exact-published-digest
security gates, and their digest-pinned control ZIPs are published in the
non-Latest `v0.1.0-rc9` validation prerelease. Final browser-download and
independent-host acceptance now follow.
The Task-087 launcher
redesign remains preserved and deferred, not a release gate.

**Historical `rc4` Control-Package Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`

**Confirmed `rc4` Runtime Image Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`
**Accepted Documentation Content Source**: `fc97b3200785d307b39ef5a683979002a5f409e6`
**Preliminary Local RC5 Source**: `a24d369668d27240ed0baa184d071395455b9c95`
**Accepted RC9 Replacement Source**:
`b3431cf86d8a000462df487685104558ac7becd3`
**Frozen Publishable Candidate Source**:
`b3431cf86d8a000462df487685104558ac7becd3`. The same-source
`v0.1.0-rc9` CPU and CUDA 12.8 images passed local and exact-published-digest
security qualification with `push_latest=false`. The locally verified control
packages bind only those exact pinned manifest digests. The owner-authorized
non-Latest RC9 prerelease is published; every `latest` promotion and any
stable/general release remain separately owner-gated.
**Authoritative Branch**: `main`
**Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
**RC5 Security Boundary**: [ADR-024](./decisions/024-rc5-security-gate-and-residual-boundary.md)
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

### **TASK-103: CUDA 12.8 Blackwell ML Runtime**

**Status**: IN_PROGRESS - local `rc4` images/packages pass G10, exact-digest
W05, four-profile W09, and all first-host provider/recovery/review-export/
controlled-error/reboot cells. ADR-023 resolves the unsigned support boundary,
the bounded `rc4` browser-download Docker CPU diagnostic passed without a
larger blocker, and its documentation findings are merged through PR #94.
PR #95 then reconciled the accepted project state, and PR #96 merged the
application urllib3 correction. RC8 Podman CPU exposed a reproducible
pre-registration cancel-then-retry race. The bounded correction and five-key
security policy are now merged through PRs #105/#106, and the same-source RC9
CPU/CUDA exact-digest registry gates pass. Digest-pinned RC9 control ZIPs pass
local integrity validation and are published in the non-Latest RC9 validation
prerelease. Resume final browser-download plus independent-host evidence using
only those exact public bytes
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md`

Current scope:

- Adopt torch 2.10.0/torchvision 0.25.0 with distinct `cpu` and `cuda128`
  image/package identities under ADR-022.
- Complete gates-v3, RGB input, recovery-message, source-build, CI/security,
  documentation, governance, Podman, rollback, and compliance work.
- Qualify rebased CPU/CUDA images with real models and preserve every run;
  missing external cells remain blocked rather than inferred.
- Preserve the accepted-baseline scan gate, comparator hardening, sanitized
  evidence, and code-scanning disposition merged through PR #86.
- Keep the confirmed `rc4` CPU/CUDA runtime evidence. The `rc4` images and
  control ZIPs remain the regression baseline but are not the final
  documentation-aligned distribution: repository `docs/` is copied into both
  surfaces. The same-source RC9 image and package rebuild is complete. Do not
  promote `latest` or publish a stable/general release without separate owner
  authorization; the RC8 validation prerelease was separately authorized.

### **TASK-104: RC5 Security Gate And Residual Disposition**

**Status**: IN_PROGRESS - ADR-024 implementation and local CPU/CUDA security,
identity, Fiona/ZCTA, real-model/device, and live Azure/Google ZCTA-provider
proof pass. PR #106 merged the exact five-key policy. Same-source RC9 CPU and
CUDA 12.8 registry digests pass the strict local and exact-digest gates with no
`latest` promotion, and their digest-pinned control ZIPs pass local integrity
validation. The non-Latest RC9 package prerelease is published; final browser-
download and independent-host acceptance remain
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-104-rc5-security-gate-and-residual-disposition.md`

Current scope:

- Keep the 396-key accepted baseline unchanged.
- Pin candidate bases/pip, remove Debian GDAL and its unused transitive tree,
  and prove Fiona/ZCTA behavior through the bundled library.
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

**Status**: AT_RISK - historical `rc4` qualification and the preliminary
browser-download diagnostic pass. RC8 browser acceptance then exposed the
Podman cancellation race, so RC8 is superseded for final acceptance. The
reviewed correction and exact security amendment are included in the locally
verified RC9 image/package pair, and the non-Latest RC9 prerelease is
published. Exact browser-download testing, affected-profile repetition, and
independent-host evidence remain
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md`

Current scope:

- Record accepted source, host/runtime availability, candidate/package/assets,
  ADR-023 policy inputs, fixtures, and provider-account prerequisites.
- Attempt an extracted real control-package setup immediately when verified
  package and asset ZIPs are available; do not substitute a source build.
- Preserve `rc4` as the clearly labeled, non-qualifying browser-download
  diagnostic and RC8 as defect-reproduction evidence. Run final acceptance
  only against the exact browser-downloaded RC9 image/package identities.
- Extend truthful external combined-model qualification under W05, then bind
  W09/W10 evidence to exact ZIP hashes and image digests.
- Report `pass`, `fail`, `blocked`, `not_run`, or justified `not_applicable`;
  never infer readiness from an absent prerequisite.

### **TASK-097: Podman CPU/GPU Final Path Qualification**

**Status**: AT_RISK - the approved relative package-local provider passes from
spaced paths on rootless Podman 6.0.2. Exact `rc4` CPU/CUDA startup, live
Google/Azure workflows, cancellation/error recovery, review/export, restart,
volume retention, and CUDA `sm_120` execution pass on the first host; the
documented Python 3.12 prerequisite and independent-host proof remain
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-097-podman-final-path-qualification.md`

Current scope:

- Qualify Podman without Docker Desktop using the approved Compose provider and
  documented Python prerequisite.
- Bind operations to the intended machine/connection and fail before mutation
  on a target mismatch.
- Require CPU inference and NVIDIA CDI CUDA inference with no silent fallback.

### **TASK-092: Documentation Currentness And Information Architecture**

**Status**: IN_PROGRESS - `rc4` and five review rounds are dispositioned;
the frozen documentation is merged through PR #94. RC8 documentation-bearing
packages were published, but RC8 is superseded for final acceptance by the
Podman cancellation defect. The corrected same-source RC9 images pass exact-
digest qualification and their published control ZIPs preserve the frozen
documentation. Complete live permission verification, exact-browser-
downloaded-package/running-image
Help validation, screenshots/video, and the final W09/W10 gates
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

**Status**: IN_PROGRESS - exact `rc4` first-host cancellation/error recovery,
review/export, volume-preserving stop/relaunch, and reboot persistence pass in
all four profiles; independent-host repetition remains
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

### **TASK-089: cdcai Adoption Preparation And Deferred Ownership Transfer**

**Status**: BLOCKED / OWNER-GATED - local preparation only
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
12. [ ] Complete W10 four-profile and independent-host reproduction; otherwise
   report only the exact qualified subset.

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
