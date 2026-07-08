# Current Tasks - Active Sprint

**Sprint Period**: Sprint 07 begins July 2, 2026
**Last Updated**: July 8, 2026
**Focus**: Execute the TASK-088 pre-tag stable-release closeout from merged `main` while keeping Task-087 helper enablement dark and explicitly deferred.
**Status**: Sprint 06 is closed. The release path is validated through `v0.1.0-rc7.1`, completed Sprint 06 task files have moved to `.agent_work/tasks/completed/`, and PR #46 is now merged on `main` as the baseline for stable-release closeout.

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

## Sprint 07 Goal

Deliver a proof-backed, support-safe host-side control plane that can guide managed-network TLS repair and restart from the TowerScout setup experience without exposing arbitrary host-command execution or leaking certificate/provider details.

Sprint 07 starts with helper transport and security proof. Product UI integration and package inclusion are gated until the helper can prove loopback binding, token/origin controls, allowlisted script invocation, sanitized progress states, and correct runtime-profile targeting.

Because the project end date is now close, Sprint 07 also carries a bounded release-transition lane for stable `v0.1.0` closeout and cdcai handoff. That work must preserve the `TASK-086` fallback and must not weaken the dark-control-plane guardrails while release and migration steps proceed.

---

## Active Sprint 07 Tasks

### **TASK-087: Host-Side TLS Repair Control Plane**
**Status**: IN_PROGRESS - Gate 3 non-mutating proof merged on `main`; later helper enablement and managed-network validation remain deferred
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

### **TASK-088: Stable v0.1.0 Release And Handoff Closeout**
**Status**: IN_PROGRESS - PR #46 merged; pre-merge gate closed; pre-tag source pass now active
**Type**: C (Release Engineering / Documentation / Handoff)
**Priority**: HIGH
**Estimated Effort**: 2-4 days (16-32 hours), excluding owner-gated migration follow-through
**Target Sprint**: Sprint 07
**Task File**: `.agent_work/tasks/active/TASK-088-stable-release-and-handoff-closeout.md`

**Objective**: Execute the bounded pre-handoff work needed to cut stable `v0.1.0` from the fork, validate it, finalize user/support guidance, and leave a clean, reviewable release package plus handoff record for cdcai.

**Current Scope**:
1. Formalize the reviewed handoff plan into task-tracked execution rather than leaving it only in status analysis.
2. Record the merged PR #46 baseline and execute the pre-tag source pass required for a trustworthy stable release.
3. Validate the rebuilt stable package set and publish the fork-side stable release.
4. Finalize the handoff notes, guides, and operator-facing documentation needed before migration execution begins.

**Important Boundaries**:
- Keep the fork release self-consistent even if cdcai release recreation happens later.
- Resolve the namespace/download-home sequencing explicitly before the first public stable package is published.
- Treat any `rc7.1` promotion fallback as an explicit release-identity decision, not as an implicit rename.

### **TASK-089: cdcai Migration Execution And Ownership Transfer**
**Status**: BLOCKED - awaiting owner-side access, Issues enablement, and package-publish confirmation
**Type**: C (Repository Migration / Release Ownership / Handoff)
**Priority**: HIGH
**Estimated Effort**: 1-2 days (8-16 hours) once prerequisites are satisfied
**Target Sprint**: Sprint 07
**Task File**: `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`

**Objective**: Transfer the validated stable release line, selected tags, image ownership, release assets, and durable task/backlog context from the fork back to `cdcai/TowerScout` without breaking source provenance or digest-pinned package behavior.

**Blocked By**:
1. cdcai collaborator write for the execution owner.
2. cdcai confirmation for Actions and `packages:write` behavior.
3. cdcai GHCR publish ownership and visibility flip.
4. cdcai Issues enablement or an explicitly approved alternate backlog destination.

---

## Near-Term Backlog Watch

These are not active Sprint 07 work unless explicitly selected:

| Task | Reason To Pull Forward |
|---|---|
| `TASK-076` Provider API Key Exposure And Restriction Policy | Needed before broader distribution if provider-key ownership/restriction policy is still informal. |
| `TASK-068` Windows Test Portability And Script Validation | Useful if Sprint 07 helper work exposes PowerShell or runtime-script gaps that should be covered outside manual validation. |
| `TASK-077` Public Release Manifest And Asset Import Hardening | Remaining staged/allowlist asset-activation hardening if release feedback shows import risk. |
| `TASK-070` Restricted-Network Package Enhancements | Pull forward only if restricted-network/offline support becomes a launch requirement. |

---

## Sprint 07 Guardrails

- Do not weaken the manual `repair-provider-tls.cmd` fallback while building the guided helper.
- Do not mount Docker or Podman control sockets into the container for this feature.
- Do not let browser input become shell command text.
- Do not expose helper tokens or raw certificate/provider details through readiness, status, logs, DOM attributes, console output, task files, or support evidence.
- Do not start unrelated V2 architecture work while the host-side TLS repair proof is active unless the team intentionally pauses Sprint 07.

---

## Related Documentation

- [Task Backlog](./task-backlog.md)
- [Completed Tasks](./completed-tasks.md)
- [Sprint 06 Retrospective](./context/analysis/SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md)
