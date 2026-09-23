# Current Tasks - Windows Deployment Delivery Week

**Sprint Period**: September 22-September 28, 2026
**Last Updated**: September 22, 2026
**Focus**: Qualify a dependable, downloadable Windows 11 application from
accepted `main` across Docker/Podman and CPU/NVIDIA profiles. Begin with W00
direction alignment and W01 early package installation. PR #67 and the
Task-087 launcher redesign are preserved but deferred and are not release
gates.

**Execution Baseline**: `9276084d91807906c53e00060670692b27e38483`
**Delivery Branch**: `delivery/windows-deployment-v2`
**Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**Acceptance**: [Windows deployment prioritization v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
**Work Plan**: [Windows deployment hardening v2](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)

## Current Release State

- The published `v0.1.2` pilot remains immutable.
- New work starts from accepted `main`; PR #67 is not merged or reconciled.
- The release contract requires CPU and CUDA 12.6 artifacts to have distinct
  identities and pinned digests.
- Full readiness requires actual YOLO and EfficientNet work on the required
  device in all four profiles plus independent-computer reproduction.
- Static checks, health/readiness, mocked tests, or CPU fallback are not
  substitutes for the required runtime evidence.
- Missing machines, assets, provider accounts, signing/policy decisions, or
  failed tests are blockers and must remain visible in the forecast.
- cdcai adoption and external publication remain owner-authorized actions.

---

## Active Delivery Work

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

**Status**: AT_RISK - first-host Docker CPU package and standalone real-model
proof pass; secure CUDA image/package assembly passes but this Blackwell host is
incompatible with the selected CUDA wheel; combined-flow fixture, provider,
rootless Podman, managed-endpoint, and independent-host evidence remain
**Priority**: CRITICAL
**Task File**: `.agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md`

Current scope:

- Record accepted source, host/runtime availability, candidate/package/assets,
  policy/signing inputs, fixtures, and provider-account prerequisites.
- Attempt an extracted real control-package setup immediately when verified
  package and asset ZIPs are available; do not substitute a source build.
- Extend truthful external combined-model qualification under W05, then bind
  W09/W10 evidence to exact ZIP hashes and image digests.
- Report `pass`, `fail`, `blocked`, `not_run`, or justified `not_applicable`;
  never infer readiness from an absent prerequisite.

### **TASK-068: Windows Test Portability And Script Validation**

**Status**: IN_PROGRESS - W01 reproduced the dormant-helper antivirus blocker;
bounded W02 fix is at `fa5ce83`, packaged Docker CPU proof and independent
review and exact-head CI pass; merge disposition and final W09 repetition remain
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

**Status**: AT_RISK - approved package-local provider passes with Python 3.12;
Python 3.14 dependency resolution fails, the running default connection is
rootful, and the existing rootless validation machine is stopped
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-097-podman-final-path-qualification.md`

Current scope:

- Qualify Podman without Docker Desktop using the approved Compose provider and
  documented Python prerequisite.
- Bind operations to the intended machine/connection and fail before mutation
  on a target mismatch.
- Require CPU inference and NVIDIA CDI CUDA inference with no silent fallback.

### **TASK-092: Documentation Currentness And Information Architecture**

**Status**: SELECTED - W00 entrypoints now; tested user/manual alignment in W09
**Priority**: HIGH
**Task File**: `.agent_work/tasks/active/TASK-092-documentation-currentness.md`

Current scope:

- Keep active agent/task directions aligned with the main-based delivery.
- Update public and in-app instructions only against observed package behavior
  and exact accepted artifact identities.
- Preserve historical pilot documentation as clearly historical.

### **TASK-093: Persistent Data Lifecycle And Recovery Rehearsal**

**Status**: SELECTED - acceptance design active; runtime evidence follows W07/W10
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

**Status**: DEFERRED - preserved outside the delivery window
**Task File**: `.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md`

Preserve PR #67, its launcher code, and its review/evidence history. Do not
merge, reconcile, extend, resume, or repeatedly review it as a deployment
prerequisite. The existing command-based lifecycle and TLS paths remain the
release path; only bounded defects reproduced there are in scope.

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
4. [ ] Select only evidence-required W02-W08 fixes and focused regressions.
5. [ ] By Day 3, require a corrected Docker/Podman rehearsal plus real combined
   inference or revise the forecast.
6. [ ] Freeze exact W09 source/images/ZIPs/assets/fixtures/tools before final
   distribution.
7. [ ] Complete W10 four-profile and independent-host reproduction; otherwise
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
