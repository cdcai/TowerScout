# Current Tasks - Sprint 09

**Sprint Period**: August 8-August 21, 2026
**Last Updated**: August 20, 2026
**Focus**: Reconcile the accepted Task-101 dependency-security change into
Draft PR #67 and validate that branch's new exact head before Task-087 resumes.
PR #72 and the default-branch alert gate have passed; new Task-087
implementation and package work remain paused through the downstream branch
gate.

**Current Release State**:

- Fork-side `v0.1.2` is the immutable pilot package.
- New development uses immutable `v0.1.3-rc.N` candidate identities.
- Dependabot alert `#76` closed as fixed, without dismissal, after PR #72
  squash-merged as `0cc189c`. Task-101 remains active only for PR #67 semantic
  integration and exact-head validation; Task-087 remains paused through that
  downstream gate.
- `cdcai/TowerScout` remains unchanged until final owner qualification and
  explicit adoption approval.
- October 30 is operational closeout; October 31 is the hard project end.

---

## Sprint 08 Closeout

Sprint 08 completed Tasks 090 and 098 within the July 23-August 7 period and
cleared the original dependency-security gate. Task-099 began during Sprint 08
but completed on August 11 after the declared period, so its completion belongs
to Sprint 09. Tasks 087, 089, and 095 carry forward.

Retrospective:
[`SPRINT-08-RETROSPECTIVE-ANALYSIS-2026-08-11.md`](./context/analysis/SPRINT-08-RETROSPECTIVE-ANALYSIS-2026-08-11.md)

---

## Sprint 09 Task State

### **TASK-095: Governance And AI-Ready Handoff Foundation**

**Status**: IN_PROGRESS - Phase A roadmap/workspace rebaseline is complete;
Phase B governance and final handoff maintenance continue through closeout
**Type**: C (Governance / Documentation / Handoff)
**Priority**: HIGH
**Estimated Effort**: Phase A 1-2 days; Phase B 2-4 distributed days
**Task File**:
`.agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md`

**Current Scope**:

- Keep task disposition, navigation, backlog, release evidence, and owner
  handoff sources current through October 30.
- Preserve one canonical fix-first roadmap and the immutable pilot/adoption
  boundary.
- Close sprint and task-state drift when live evidence changes the plan.

### **TASK-099: August Dependency Advisory Follow-Up**

**Status**: COMPLETED - PR #68 merged the narrow dependency fixes as
`f460445`; PR #69 merged the root-manifest refresh as `0133b50`. Dynamic graph
run `31510493332` replaced the stale snapshot, alert `#74` closed without
dismissal, the SBOM contains only `aiohttp==3.14.3`, and the August 11 closeout
inventory was exactly the eight documented torch residuals
**Completed**: August 11, 2026
**Type**: C (Security Remediation / Release Gate)
**Priority**: HIGH
**Task File**:
`.agent_work/tasks/active/TASK-099-august-dependency-advisory-follow-up.md`

**Release Boundary**: Task-099 cleared its scoped dependency-security gate on
August 11. Alert `#76` opened afterward and belongs to separately activated
Task-101 rather than rewriting Task-099. PR #72 restored the blocking frontend
gate and alert `#76` closed as fixed; Task-087 resumption, PR #67 merge, and
candidate publication remain paused through Task-101's downstream
reconciliation gate. Reviewer input may continue.

### **TASK-101: extract-zip Advisory Assessment And Release-Gate Disposition**

**Status**: IN_PROGRESS - PR #72 squash-merged as `0cc189c`, alert `#76` closed
as fixed without dismissal, and exact-main CI passed August 19; PR #67 semantic
integration and exact-head validation remain open
**Type**: C (Security Remediation / CI And Release Gate)
**Priority**: HIGH
**Estimated Effort**: 1-2 days plus CI rerun timing
**Task File**:
`.agent_work/tasks/active/TASK-101-extract-zip-advisory-release-gate.md`

**Current Scope And Gates**:

- Preserve Task-099 as the dated August 11 closeout. Task-101 uniquely owns
  alert `#76`, the current npm lock graph, and restoration of the blocking
  frontend dependency-security gate.
- Treat the finding as a CI/developer-browser-install risk, not a shipped
  TowerScout runtime dependency. Do not claim exploitation or end-user runtime
  exposure without new evidence.
- Preserve the locally validated Node `>=22.12.0` / Puppeteer `25.8.0` path,
  whose locked browser tooling removes vulnerable `extract-zip`; do not use
  `npm audit fix --force`, weaken the high-severity gate, or dismiss the alert.
- Preserve the green final PR #72 evidence at `820b649`: CI/CD run
  `32308971393` and Task-087 run `32308971392`. Preserve the exact-main
  post-merge evidence at squash commit `0cc189c`: CI/CD run `32310281115` and
  Task-087 run `32310281051` passed, and alert `#76` closed as fixed without
  dismissal.
- Align the maintained Node baseline across CI, `package.json`, and the Docker
  frontend stage, and remove the redundant Puppeteer browser-download path
  from Task-087 workflows that already install a pinned browser separately.
- Keep the Docker frontend-stage build blocking on pull requests; the full
  runtime-image build remains the separately documented main-branch advisory
  check.
- Treat those narrowly scoped Task-101 security-workflow edits as gate work;
  they do not resume broader Task-087 implementation.
- Require clean install/audit/lock-graph, frontend bundle/contracts, Task-087
  browser/Windows-helper, and Docker build validation before acceptance.
- Bring current `main` into PR #67 through semantic reconciliation while
  preserving ADR-019 and the branch's review evidence. New Task-087
  implementation, merge, and candidate-package work remain paused until the
  reconciled branch's required exact-head matrix passes.

### **TASK-087: Host-Side TLS Repair Control Plane**

**Status**: PAUSED / RECONCILIATION-GATED - PR #72 and alert `#76` default-branch
reconciliation passed. Draft PR #67 and its recorded Task-087 evidence remain
preserved and reviewable; no new launcher or package implementation,
merge, or publication proceeds until current `main` is semantically integrated
there and the branch's required exact-head matrix passes.
**Type**: B/C (Runtime Support / Setup UX / TLS Trust)
**Priority**: HIGH
**Remaining Estimate**: 1-2 days after PR #67 reconciliation from the
preserved PR #67 checkpoint
**Task File**:
`.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md`

**Current Scope And Gates**:

- Preserve the visible Python/Tkinter launcher, bounded native transaction,
  existing evidence, and reviewer context through the PR #67 reconciliation
  gate.
- Queue implementation-producing review changes until Task-087 resumes;
  clarification and documentation review may continue.
- Generate the full-runnable validation package from the accepted
  post-reconciliation commit in an approved environment; local PowerShell
  policy blocks the normal base-package generator on this workstation.
- Run UI-driven Docker Google Maps, Azure Maps, and controlled
  recovery/rollback validation while preserving named volumes.
- Configure an approved non-Docker-Desktop Podman Compose provider separately
  before any Podman mutation; do not silently install or select a provider.
- Keep signing, representative managed-endpoint validation, candidate
  inclusion, and merge as separate later gates.
- Preserve PR #67's August 19 proceed disposition under ADR-019 for semantic
  reconciliation after Task-101; do not restate it as a new decision here.
- Keep Task-086 as the supported command-based fallback until every Task-087
  gate passes.

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

## Sprint 09 Sequence

1. [x] Preserve the completed Task-099 evidence and activate Task-101 for the
   newly disclosed alert `#76`.
2. [x] Complete Task-101's supported Node/Puppeteer remediation and required
   clean-install, audit, lock-graph, frontend, browser, Windows-helper, and
   Docker-build validation.
3. [x] Merge PR #72 after its final exact-head checks pass, then confirm alert
   `#76` closes without dismissal on the default branch.
4. [ ] Bring the accepted Task-101 change into Draft PR #67 and preserve its
   recorded ADR-019 proceed disposition during semantic reconciliation.
5. [ ] Require green checks at the new exact PR #67 head.
6. [ ] Explicitly resume Task-087 only after steps 4-5 pass.
7. [ ] Generate and verify the exact-source full-runnable Task-087 package in an
   approved environment.
8. [ ] Complete the Docker Google/Azure and controlled recovery validation, then
   the approved-provider Podman coverage.
9. [ ] Complete technical/security review, signing-path coordination, and
   representative managed-endpoint validation as applicable.
10. [ ] If Task-087 proceeds, select Task-096 next, followed by Task-097. Keep Tasks
   091-093 behind the stable candidate/runtime boundary.

Task-058 and Task-059 remain conditional stretch work. Task-094 remains
evidence-gated. Task-101 is active for downstream PR #67 reconciliation;
Task-087 remains active in tracking but paused on that gate. Task-099 stays in
`tasks/active/` until Sprint 09 closeout.

---

## Runtime Coordination

Before any Docker- or Podman-dependent work:

1. Tell the user which runtime profile is required.
2. Ask the user to start Docker Desktop and/or the Podman machine.
3. Wait for confirmation before beginning runtime-dependent validation.
4. Allow time for a workstation restart when Docker Desktop requires it.

Planning, documentation, static source review, and branch reconciliation do
not require a runtime startup request.

---

## Related Sources

- [Canonical October Fix-First Roadmap](./context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
- [Pilot And Adoption Track](./context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
- [Task Backlog](./task-backlog.md)
- [Requirements](./requirements.md)
- [Design](./design.md)
- [Completed Tasks](./completed-tasks.md)
