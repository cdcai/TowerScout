# Current Tasks - Windows Deployment Delivery Week

**Sprint Period**: September 22-September 28, 2026
**Last Updated**: October 5, 2026
**Focus**: Qualify a dependable, downloadable Windows 11 application from
accepted `main` across Docker/Podman and CPU/NVIDIA profiles. Day 2 has moved
the evidence-selected W03-W08 corrections through focused review and merge.
The Task-087 launcher redesign is preserved in immutable archive tags and a
final disposition record, but PRs #64/#67 are closed without merge and are not
release gates.

**Accepted Control-Package Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`

**Confirmed `rc4` Runtime Image Source**: `541622556fb7999ee4e88fb1e44f7797b9da34f5`
**Next Documentation-Aligned Candidate Source**: Not frozen; pending Task-092
content completion and clean-source rebuild
**Authoritative Branch**: `main`
**Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
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
and the bounded `rc4` browser-download Docker CPU diagnostic passed without a
larger blocker. Incorporate its findings, then freeze documentation-aligned
image/control-ZIP identities and complete final browser-download plus
independent-host evidence
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
  surfaces. Rebuild under new identities after Task-092 content freeze and do
  not publish packages or promote `latest` without owner authorization.

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

**Status**: AT_RISK - local `rc4` W05/W09 and four-profile first-host
provider, cancellation/error recovery, review/export, and stop/relaunch cells
pass, including exact-`rc4` reboot persistence. ADR-023 resolves policy/signing
by narrowing the supported environment. The preliminary `rc4` browser-download
Docker CPU diagnostic passed and now informs Task-092; it does not replace the
final exact-candidate browser-download and independent-host evidence
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md`

Current scope:

- Record accepted source, host/runtime availability, candidate/package/assets,
  ADR-023 policy inputs, fixtures, and provider-account prerequisites.
- Attempt an extracted real control-package setup immediately when verified
  package and asset ZIPs are available; do not substitute a source build.
- Use `rc4` first for a clearly labeled, non-qualifying browser-download
  diagnostic; preserve findings, then repeat final acceptance against the
  documentation-aligned image/package identities.
- Extend truthful external combined-model qualification under W05, then bind
  W09/W10 evidence to exact ZIP hashes and image digests.
- Report `pass`, `fail`, `blocked`, `not_run`, or justified `not_applicable`;
  never infer readiness from an absent prerequisite.

### **TASK-068: Windows Test Portability And Script Validation**

**Status**: COMPLETED - W02 merged as `8976222`; final `rc4` exact-package
Docker/Podman setup, start, stop, relaunch, and eight-volume preservation pass
on the first host
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-068-windows-script-validation.md`

Current scope:

- Keep normal helper-disabled launch and stop independent of the dormant
  helper module, profile writes, and ACL operations.
- Preserve the explicitly enabled review path without reactivating it for the
  release.
- Prove Windows PowerShell 5.1 preflight failure, scalar Compose failure,
  packaged setup/start/stop/relaunch, and named-volume preservation.

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

**Status**: IN_PROGRESS - `rc4` findings are dispositioned; Round 2 and Round 3
findings are implemented. Round 4 confirmed those corrections and found one
residual packaged OCI port instruction; R4-01 is implemented locally with
regression coverage. Draft PR #94 remains open; complete final focused
confirmation, live permission verification, final release wording, content
freeze, new artifact identities, and running-image validation
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

### **TASK-101: extract-zip Advisory Assessment And Release-Gate Disposition**

**Status**: COMPLETED - security remediation passed on accepted `main`; the
former PR #67 integration condition is superseded by ADR-021, not passed
**Task File**: `.agent_work/tasks/active/TASK-101-extract-zip-advisory-release-gate.md`

The Node/Puppeteer remediation, exact-main checks, and alert closure remain
valid completed evidence. No PR #67 reconciliation is required for this
delivery.

### **TASK-099: August Dependency Advisory Follow-Up**

**Status**: COMPLETED - retained in the active directory until sprint closeout
**Task File**: `.agent_work/tasks/active/TASK-099-august-dependency-advisory-follow-up.md`

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
8. [ ] Freeze Task-092 content and rebuild documentation-aligned CPU/CUDA
   images and control ZIPs under new identities; publish authoritative hashes
   before final extraction testing or tester distribution.
9. [ ] Complete W10 four-profile and independent-host reproduction; otherwise
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
