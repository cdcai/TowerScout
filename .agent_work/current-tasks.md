# Current Tasks - Sprint 08

**Sprint Period**: July 23-August 7, 2026
**Last Updated**: July 27, 2026
**Focus**: Preserve the completed dependency-security gate and resume the
authorized universal provider TLS repair without changing the frozen pilot or
cdcai.

**Current Release State**:

- Fork-side `v0.1.2` is the immutable pilot package.
- New development uses immutable `v0.1.3-rc.N` candidate identities.
- `cdcai/TowerScout` remains unchanged until final owner qualification and
  explicit adoption approval.
- October 30 is operational closeout; October 31 is the hard project end.

---

## Sprint 07 Closeout

Sprint 07 completed Task-088 pilot distribution and custody. Task-088 moved to
`tasks/completed/`. Task-087 carries forward under the owner-approved fix-first
plan. Task-089 remains a standing owner-gated handoff lane.

Retrospective:
[`SPRINT-07-RETROSPECTIVE-ANALYSIS-2026-07-23.md`](./context/analysis/SPRINT-07-RETROSPECTIVE-ANALYSIS-2026-07-23.md)

---

## Sprint 08 Task State

### **TASK-095: Governance And AI-Ready Handoff Foundation**

**Status**: IN_PROGRESS - Phase A roadmap/workspace rebaseline is complete;
Phase B governance and final handoff maintenance continue through closeout
**Type**: C (Governance / Documentation / Handoff)
**Priority**: HIGH
**Estimated Effort**: Phase A 1-2 days; Phase B 2-4 distributed days
**Task File**:
`.agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md`

**Phase A Outcome**:

- One canonical fix-first roadmap controls forward execution.
- Tasks 090-097 have unique, stable rebaseline definitions; Task-098 is the
  unique follow-on security-remediation lane added by the July 23 live alert
  review.
- Sprint, backlog, requirements, design, pilot, handoff, and agent guidance are
  aligned.
- Superseded planning/review material is archived rather than left in active
  status.
- Completed PR status packets, the superseded RC1 intake workflow, stale
  Sprint/source-install guides, and one exact duplicate archive file were
  removed from the current information surface.

**Remaining Scope**: Keep task disposition, navigation, tool-neutral
maintenance instructions, backlog, release evidence, and owner handoff current
through October 30.

### **TASK-090: Runtime, Custom-Image, And Dependency Security Investigation**

**Status**: COMPLETED - investigation and approved Task-098 scope complete
**Type**: C (Security Investigation)
**Priority**: HIGH
**Estimated Effort**: 1-3 days for investigation and classification only
**Task File**:
`.agent_work/tasks/active/TASK-090-runtime-custom-image-dependency-security.md`

**Historical Objective**: Determine whether local-only runtime reachability
and custom-image behavior created an actionable release risk, and classify the
62-alert Trivy dependency baseline reported on `main` on July 23. Separate
evidence, classification, and remediation estimates; do not hide remediation
inside the investigation.

**Exit Gate**:

- Every code-scanning alert has a package/call-path disposition and is
  classified as release-blocking, required hardening, accepted risk, not
  reachable, or scanner/version false positive.
- Any remediation receives a separate Task-098 scope, estimate, and approval.
- No release-blocking critical/high finding remains unresolved; any residual
  critical/high risk requires written project-lead/cdcai-owner acceptance.
- No later runtime work begins with an unresolved mandatory finding.

**Assessment**:
[`GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`](./context/analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md)

**Investigation Outcome**:

- The July 23 live GitHub inventory reconciled exactly to 62 alerts with no
  missing or extra alert numbers.
- Five alerts are release-blocking, one requires hardening, and 56 are not
  reachable on the supported call paths.
- At investigation time, the normal Compose port was published on all host
  interfaces, contradicting the local-only assumption and making loopback
  binding a mandatory Task-098 control.
- The Task-090 proposal estimated Task-098 at 4-8 days for mandatory slices,
  or 6-11 days for the full coordinated dependency hardening, plus required
  GPU/runtime host availability.
- No dependency pin, alert state, runtime, release asset, or external
  repository was changed.

### **TASK-098: Dependency Security Remediation And Release Gate**

**Status**: COMPLETED - PR #51 merged as `e499b50`; main CI passed; Dependabot
reconciled to eight documented non-blocking torch advisories
**Type**: C (Security Remediation / Runtime Qualification)
**Priority**: HIGH
**Estimated Effort**: Mandatory slices 4-8 days; full coordinated hardening
6-11 days, plus required GPU/runtime host availability
**Task File**:
`.agent_work/tasks/active/TASK-098-dependency-security-remediation.md`

**Objective**: Implement only the approved Task-090 remediation slices,
qualify the affected dependency and runtime paths, and close the security
release gate before Task-087 resumes.

**Closeout Outcome**:

- The external Docker CUDA qualification passed on exact source commit
  `675bd8fabc27765522906957524d2027d931f6a1`.
- Live Google/Azure estimate, detect, cancel, and recovery smokes passed
  against the Task-098 candidate image.
- PR #51 was squash-merged as `e499b50d285b775047fb6efadcec512f7753c859`,
  and post-merge workflow run `30284846056` passed every job.
- Dependabot reconciled to eight open torch alerts: three medium and five low.
  No critical/high alert remains, and no alert was manually dismissed.
- Incompatible standalone torch PR #60 was closed with a future coordinated
  torch/torchvision requalification disposition.
- Task-097/Task-091 retain Podman CPU/GPU and the final four-profile
  operational package matrix.

**Start Gate**:

- The Task-090 classification and target matrix are final.
- Project-lead approval and its non-regression caveat are recorded. No
  cdcai-owner confirmation is required for fork-side remediation.
- Fixed patch targets, the ML candidate set and selection criteria, regression
  scope, and any residual-risk decision path are agreed. The final ML pair and
  wheel flavors are selected during the approved compatibility spike.
- A reproducible pre-change functional, detection-output, and performance
  baseline is captured before the first dependency or runtime change.
- No dependency pin, alert state, release asset, or external repository change
  occurs before this gate passes.

### **TASK-087: Host-Side TLS Repair Control Plane**

**Status**: READY TO RESUME - Tasks 090/098 and the mandatory security gate
are complete; begin from current `main` after the Task-098 closeout merges
**Type**: B/C (Runtime Support / Setup UX / TLS Trust)
**Priority**: HIGH
**Estimated Effort**: 4-7 days plus managed-network package validation
**Task File**:
`.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md`

**Rebased Scope**:

- Finish the existing gated helper rather than restart the design.
- Support Google Maps and Azure Maps.
- Support Docker and Podman application-provider TLS repair.
- Keep Podman Compose-provider installation and Podman-machine trust separate.
- Pass managed-network validation before candidate inclusion.

### **TASK-089: cdcai Adoption Preparation And Deferred Ownership Transfer**

**Status**: BLOCKED / OWNER-GATED - preparation only; no cdcai mutation
**Type**: C (Repository Migration / Release Ownership / Handoff)
**Priority**: HIGH
**Estimated Effort**: 1-2 days after qualification and authorization
**Task File**:
`.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`

**Current Boundary**:

- The final cdcai tag and release title are selected before the official build.
- `v0.1.3-rc.N` candidate names do not dictate the final cdcai identity.
- Execution waits for owner qualification, explicit adoption approval, and an
  approved release/package/backlog transfer plan.

---

## Sprint 08 Sequence

1. Task-095 Phase A rebaseline and readiness cleanup: complete.
2. Task-090 62-alert investigation and disposition: complete.
3. Task-098 approved remediation and qualification: complete.
4. Release-blocking findings resolved and residual torch alerts explicitly
   dispositioned: complete.
5. Resume Task-087 from current `main` after the Task-098 closeout merges.
6. Re-plan the next sprint using actual security and Task-087 outcomes.

Task-096 and Task-097 are mandatory roadmap work but are not pulled into this
sprint yet. Task-098 remains in the current-sprint record as a completed task
until Sprint 08 closeout. Task-058 and Task-059 remain conditional stretch
work.

---

## Runtime Coordination

Before any Docker- or Podman-dependent work:

1. Tell the user which runtime profile is required.
2. Ask the user to start Docker Desktop and/or the Podman machine.
3. Wait for confirmation before beginning runtime-dependent validation.
4. Allow time for a workstation restart when Docker Desktop requires it.

Planning, documentation, and static source review do not require a runtime
startup request.

---

## Related Sources

- [Canonical October Fix-First Roadmap](./context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
- [Pilot And Adoption Track](./context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
- [Task Backlog](./task-backlog.md)
- [Requirements](./requirements.md)
- [Design](./design.md)
- [Completed Tasks](./completed-tasks.md)
