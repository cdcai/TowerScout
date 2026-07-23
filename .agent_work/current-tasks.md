# Current Tasks - Sprint 08

**Sprint Period**: July 23-August 7, 2026
**Last Updated**: July 23, 2026
**Focus**: Start the bounded runtime, custom-image, and dependency-security
investigation; define any required remediation; and prepare the authorized
universal provider TLS repair without changing the frozen pilot or cdcai.

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

**Status**: READY / NEXT - Task-095 Phase A is complete
**Type**: C (Security Investigation)
**Priority**: HIGH
**Estimated Effort**: 1-3 days for investigation and classification only
**Task File**: Create in `tasks/active/` when implementation begins

**Objective**: Determine whether local-only runtime reachability and
custom-image behavior create an actionable release risk, and classify all 62
open Trivy dependency alerts currently reported on `main`. Separate evidence,
classification, and remediation estimates; do not hide remediation inside the
investigation.

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

### **TASK-087: Host-Side TLS Repair Control Plane**

**Status**: PLANNED / RESELECTED - resume after Tasks 090/098 and the mandatory
security gate
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
2. Start Task-090 with the 62-alert inventory as a required workstream.
3. Scope and approve Task-098 for mandatory dependency remediation.
4. Resolve release-blocking findings and explicitly disposition the remainder.
5. Resume Task-087 only after the Tasks 090/098 security gate passes.
6. Re-plan the next sprint using actual security and Task-087 outcomes.

Task-096 and Task-097 are mandatory roadmap work but are not pulled into this
sprint yet. Task-098 enters this sprint only to the extent Task-090 identifies
mandatory remediation. Task-058 and Task-059 remain conditional stretch work.

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
