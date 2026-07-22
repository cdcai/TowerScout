# Current Tasks - Active Sprint

**Sprint Period**: Sprint 07 begins July 2, 2026
**Last Updated**: July 22, 2026
**Focus**: Close the completed `v0.1.2` pilot-launch lane, preserve the feedback-gated cdcai adoption boundary, and rebaseline the handoff schedule to the hard 2026-10-31 project end date without selecting the next implementation work yet.
**Status**: The validated fork-side `v0.1.2` pilot email has been sent. Feedback is captured by the project lead in a fillable Word document outside the repository, and the confirmed primary and backup support owners have appropriate access. `TASK-088` is complete. `cdcai/TowerScout` remains intentionally unchanged until feedback review and explicit owner approval under `TASK-089`.

---

## Sprint 06 Closeout Summary

Sprint 06 produced the V1 RC / pilot-ready Windows package path and carried it from RC1 package validation through RC7.1 tester-facing release validation. Final V1 completion is still separate: it depends on pilot/UAT feedback, blocker triage, and explicit disposition of remaining support or V1 patch work.

Completed Sprint 06 task artifacts moved from `.agent_work/tasks/active/` to `.agent_work/tasks/completed/`:

- `TASK-065`: release packaging and runtime support follow-through
- `TASK-066`: release candidate validation gate
- `TASK-067`: CI release gate tightening
- `TASK-069`: license and release policy review
- `TASK-071`: end-user release package documentation
- `TASK-072`: release asset bundle contract
- `TASK-073`: clean-machine pilot / UAT execution plan
- `TASK-074`: runtime prerequisite preflight
- `TASK-075`: single GPU-capable package implementation
- `TASK-079`: RC1 reliability fixes and performance instrumentation
- `TASK-080`: UAT user guide and setup process simplification
- `TASK-081`: RC3 runtime hardening and Podman independence
- `TASK-082`: RC4 documentation and package organization
- `TASK-083`: RC5 Podman independence, GPU CDI, and release validation
- `TASK-084`: GA packaging hardening and Podman provider onboarding
- `TASK-085`: dataset ZIP restore path traversal hardening
- `TASK-086`: provider TLS auto-repair and setup triage

Sprint 06 closeout records:

- Retrospective: [SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md](./context/analysis/SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md)
- Archived Sprint 06 plan: [SPRINT-06-PLAN.md](./context/archive/2026-07/status/SPRINT-06-PLAN.md)
- Completed task record: [completed-tasks.md](./completed-tasks.md)

---

## Sprint 07 Transition State

The pilot-transition lane is complete through distribution. The project is
extended through 2026-10-31, with 2026-10-30 treated as the operational
closeout date because October 31 falls on a Saturday.

This Phase 1 update intentionally does not select the next implementation
tasks. `TASK-087` retains its merged non-mutating proof but later enablement is
paused pending a future planning decision. `TASK-089` remains owner-gated until
pilot feedback is reviewed and an adoption baseline is explicitly approved.

---

## Sprint 07 Task State

### **TASK-087: Host-Side TLS Repair Control Plane**
**Status**: PAUSED / DEFERRED - Gate 3 non-mutating proof merged on `main`; later helper enablement and managed-network validation require a future planning decision
**Type**: B/C (Runtime Support / Setup UX / TLS Trust)
**Priority**: MEDIUM-HIGH
**Estimated Effort**: 4-7 days (32-56 hours), plus managed-network package validation
**Target Sprint**: Sprint 07
**Task File**: `.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md`

**Objective**: Design and implement a support-safe host-side repair control plane that lets TowerScout present a guided "repair TLS trust and restart" action when provider setup detects a managed-network TLS certificate trust failure, while reusing the validated `TASK-086` repair flow.

**Sprint 07 Entry Conditions**:
- `TASK-086` remains the validated command-based repair baseline and fallback.
- RC7.1 tester-facing package validation has passed.
- The helper must be package-local, loopback-only, token-protected, allowlisted, and support-safe before it reaches product UI.

**Current Sprint 07 Work Sequence**:
1. Gate 1 / Gate 2 helper proof: merged in PR #45 with controlled Docker CPU/off live-wrapper evidence and helper security constraints.
2. Gate 3 non-mutating proof: merged through PR #46 on `main`, including the reviewed CI/gate hardening.
3. Gate 3 follow-up: add visible fallback/repair UI only after release work allows the later helper-availability and browser-mutation enablement slice to begin.
4. Gate 4 managed-network package validation: blocked until the later helper enablement slice passes and the release owner approves user-facing package inclusion.

**Evidence Handling**:
Do not record provider keys, helper tokens, certificate subjects, raw thumbprints, raw provider responses, `.env` files, raw logs, browser network traces, screenshots, private AOIs, or local environment dumps in task evidence. Use sanitized operation states and public-safe summaries only.

### **TASK-088: Stable Release And Handoff Closeout**
**Status**: COMPLETED - pilot distributed, support coverage confirmed, and release/evidence custody recorded
**Type**: C (Release Engineering / Documentation / Handoff)
**Priority**: HIGH
**Estimated Effort**: 2-4 days (16-32 hours), excluding owner-gated migration follow-through
**Target Sprint**: Sprint 07
**Task File**: `.agent_work/tasks/active/TASK-088-stable-release-and-handoff-closeout.md`

**Objective**: Close out the validated fork-side pilot release and leave a durable handoff record for the confirmed project extension through October 31.

**Completed Scope**:
1. Formalized the reviewed handoff plan into task-tracked execution.
2. Recorded the merged PR #46 baseline and completed the pre-tag source pass.
3. Validated and published the stable `v0.1.2` package set.
4. Sent pilot-facing guidance that distinguishes the fork download from the
   unchanged official cdcai repository.
5. Confirmed the external Word feedback method, support coverage, and durable
   release/evidence custody without changing cdcai.

**Important Boundaries**:
- Keep the fork release self-consistent even if cdcai release recreation happens later.
- Resolve the namespace/download-home sequencing explicitly before the first public stable package is published.
- Do not publish final GitHub Release assets under the current `v0.1.0` or `v0.1.1` identities; the active path is the `v0.1.2` release line built from the post-PR-48 frozen main baseline.
- Treat any `rc7.1` promotion fallback as an explicit release-identity decision, not as an implicit rename.
- Do not rebuild or replace the validated `v0.1.2` pilot assets; fixes require a new version.
- Do not present `cdcai/TowerScout` as the pilot download or modify it during the owner-approved feedback hold.

### **TASK-089: cdcai Adoption Preparation And Deferred Ownership Transfer**
**Status**: DEFERRED / OWNER-GATED - prepare the handoff now, but do not change cdcai until pilot feedback is reviewed and the owner approves an adoption baseline
**Type**: C (Repository Migration / Release Ownership / Handoff)
**Priority**: HIGH
**Estimated Effort**: 1-2 days (8-16 hours) once prerequisites are satisfied
**Target Sprint**: Sprint 07
**Task File**: `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`

**Objective**: Prepare a safe, reviewable cdcai adoption package while keeping the official repository unchanged during the pilot, then transfer the owner-approved baseline only after feedback review.

**Execution Gates**:
1. Pilot feedback is collected and triaged.
2. The cdcai owner explicitly approves the version to adopt.
3. cdcai collaborator write, Actions, and package-publish ownership are confirmed.
4. A durable backlog/feedback destination is approved; it need not be cdcai Issues during the hold.
5. The image-copy-versus-rebuild and validation path is approved for the selected baseline.

---

## Backlog Selection Hold

No new backlog task is selected by this Phase 1 update. The ordered inventory
remains in `task-backlog.md` for the next planning iteration.

---

## Sprint 07 Guardrails

- Do not weaken the manual `repair-provider-tls.cmd` fallback while building the guided helper.
- Do not mount Docker or Podman control sockets into the container for this feature.
- Do not let browser input become shell command text.
- Do not expose helper tokens or raw certificate/provider details through readiness, status, logs, DOM attributes, console output, task files, or support evidence.
- Do not start unrelated V2 architecture work while the host-side TLS repair proof is active unless the team intentionally pauses Sprint 07.

---

## Related Documentation

- [Current Pilot And Adoption Plan](./context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
- [Task Backlog](./task-backlog.md)
- [Completed Tasks](./completed-tasks.md)
- [Sprint 06 Retrospective](./context/analysis/SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md)
