# TASK-095: Governance And AI-Ready Handoff Foundation

**Status**: IN_PROGRESS - Phase A complete; Phase B continues through handoff
**Priority**: HIGH
**Type**: C (Governance / Documentation / Handoff)
**Estimated Effort**: Phase A 1-2 days; Phase B 2-4 distributed days
**Target**: Phase A July 23, 2026; Phase B complete by October 30, 2026
**Owner**: Project lead with cdcai owner participation
**Created**: July 23, 2026

## Objective

Maintain one accurate, low-noise project control plane and leave the cdcai
owner a tool-neutral foundation for future maintenance, backlog work, and
optional AI-assisted development.

## Requirements

- WHEN the roadmap changes, THE PROJECT SHALL update one canonical roadmap and
  archive superseded drafts.
- WHEN task work is selected, THE PROJECT SHALL keep current, backlog,
  completed, and individual task records synchronized.
- WHEN ownership transfers, THE PROJECT SHALL provide repository-native,
  tool-neutral maintenance instructions and backlog context.
- WHEN old context remains useful only as history, THE PROJECT SHALL archive it
  rather than leave it in active status.
- BEFORE runtime-dependent validation, THE ACTIVE AGENT SHALL ask the user to
  start the required Docker Desktop and/or Podman runtime.

## Phase A - Roadmap And Workspace Rebaseline

### Acceptance Criteria

- [x] Establish one canonical October fix-first roadmap.
- [x] Record the fix-first/repository/release-naming decision in an ADR.
- [x] Confirm unique definitions for Tasks 090-097.
- [x] Close Sprint 07 and open Sprint 08.
- [x] Move completed Task-088 to `tasks/completed/`.
- [x] Reconcile `current-tasks.md`, `task-backlog.md`, and
  `completed-tasks.md`.
- [x] Replace obsolete current requirements/design with concise current
  sources and preserve their previous versions in the archive.
- [x] Archive superseded planning drafts, reviews, release checklists, and
  historical implementation strategies.
- [x] Keep the `v0.1.2` Pilot plan current for the pilot track while marking the
  new roadmap as the forward-development source.
- [x] Update `.agent_work` navigation, `HANDOFF.md`, and primary agent guidance.
- [x] Record the runtime-startup coordination preference.
- [x] Pass the quick workspace check, canonical validator, link/reference
  review, and `git diff --check`.

## Phase B - Ongoing Governance And Final Handoff

### Acceptance Criteria

- [ ] Keep task disposition and milestone status current through freeze.
- [ ] Maintain a prioritized, owner-readable Markdown backlog.
- [ ] Document tool-neutral task planning, implementation, validation, release,
  rollback, and maintenance procedures.
- [ ] Record optional AI-assisted workflows without requiring a particular
  vendor or tool.
- [ ] Decide whether GitHub Issues supplement the Markdown backlog.
- [ ] Verify repository access, release/package custody, and external guide/
  video custody.
- [ ] Ensure final documentation identifies current, historical, and archived
  sources unambiguously.
- [ ] Complete owner review and final sign-off by October 30.

## Dependencies

- Project lead and cdcai owner roadmap decisions
- Tasks 087 and 089
- Tasks 090-097 as formalized by Phase A, Task-098 added by the July 23
  code-scanning readiness review, and active Task-101
- Final candidate and handoff evidence

## Implementation Log

### 2026-08-20 - Task-101 Post-Merge Governance Checkpoint

**Objective**: Reconcile the current control-plane sources after the accepted
Task-101 remediation reached the default branch.

**Context**: PR #72 final head `820b649` passed CI/CD run `32308971393` and
Task-087 run `32308971392`, then squash-merged as `0cc189c`. Exact-main CI/CD
run `32310281115` and Task-087 run `32310281051` passed. Alert `#76` is fixed
through dependency reconciliation and has no dismissal metadata.

**Decision**: Mark the PR #72 and default-branch alert gates complete without
marking Task-101 complete or resuming Task-087. Task-101 remains active for PR
#67 semantic integration and exact-head validation; Task-087 remains paused /
reconciliation-gated through that checkpoint.

**Execution**: Updated the current task, backlog, requirement, design, roadmap,
pilot, handoff, task, decision, and agent-guidance sources. Historical task
logs, completed-task records, pilot assets, and the cdcai hold remain unchanged.

**Validation**: PASS. The quick workspace checker, canonical `.agent_work`
validator, and `git diff --check` passed on August 20. The checkpoint records
only sanitized GitHub identifiers and state.

**Next**: Merge current `main` normally into Draft PR #67, resolve the shared
governance sources semantically while preserving ADR-019 and branch evidence,
and require the reconciled exact-head matrix before closing Task-101 or
resuming Task-087.

### 2026-08-19 - Task-101 Activated And Task-087 Paused

**Objective**: Reflect the project lead's decision to resolve the blocking
dependency-security gate before continuing Task-087 implementation.

**Context**: Alert `#76` is a development/browser-install exposure rather than
an end-user runtime dependency. The frontend audit is intentionally blocking,
and a supported upstream removal path requires a tested Node/Puppeteer change.

**Decision**: Select Task-101 directly into the active Sprint 09 lane and
pause, rather than discard, Task-087. Keep PR #67 open for reviewer input and
preserve its evidence. Resume implementation, merge, and package work only
after Task-101 passes.

**Execution**: Created the active Type C Task-101 record, marked Task-087
dependency-gated, and reconciled current roadmap, requirement, design, handoff,
and agent-guidance sources. Completed Task-099 history remained unchanged.

**Output**: One immediate implementation lane, an explicit paused-but-
reviewable Task-087 state, and a testable security-gate path back to candidate
package work.

**Validation**: PASS for the lifecycle transition on August 19, 2026. The
TowerScout quick workspace checker and canonical `.agent_work` validator
passed, `git diff --check` found no whitespace errors, and current relative
Markdown links resolved across the changed files.

**Next**: Implement and validate Task-101 from current `main`, reconcile alert
`#76`, bring the accepted result into PR #67, and then resume Task-087 from its
preserved checkpoint.

### 2026-08-19 - Task-101 Quality Review Gate Reconciled

**Objective**: Keep the Task-101 evidence and Task-087 resume boundary
unambiguous after PR #72's independent quality review.

**Context**: The implementation head passed its main CI and all three Task-087
compatibility jobs. The review found the committed evidence state lagged those
runs and several current sources could be read as resuming Task-087 before PR
#67's new exact-head validation.

**Decision**: Record implementation head `a87ab53`, CI/CD run `32300398378`,
and Task-087 run `32300398377`. Standardize the downstream order as PR #72
merge, alert `#76` closure without dismissal, PR #67 semantic integration,
green PR #67 exact-head checks, and only then Task-087 resumption. Keep final
PR #72 check evidence in the PR description so an evidence-only commit does
not invalidate its own claim.

**Execution**: Reconciled the current task, backlog, requirement, design, ADR,
roadmap, Task-087, handoff, and Copilot sources. The CI quality ratchet also
adds a blocking Docker frontend-stage PR job and focused semantic contract.

**Validation**: The focused suite passed `12` tests; the uncached Docker
frontend-stage build, CI workflow summary, both agent-work validators, and
`git diff --check` passed. No raw log, provider data, certificate detail, or
local path was added to repository evidence.

**Next**: Require the review-remediation commit's exact-head PR checks, then
preserve the ordered post-merge gates without resuming Task-087 early.

### 2026-07-23 - Phase A Rebaseline

**Objective**: Replace the pre-decision planning state with one executable
fix-first roadmap before Task-090 begins.

**Context**: Sprint 07 still stated that no implementation task had been
selected. Active Handoff-Planning contained multiple drafts/reviews, while
prototype-era requirements/design text contradicted the current release and
runtime model.

**Decision**: Use the July 23 fix-first roadmap as the current execution source;
retain the Pilot plan for the unchanged `v0.1.2` track; archive superseded
material; keep Task-095 active through final handoff.

**Execution**:

- Closed Sprint 07 and created a concise recent completion record.
- Opened Sprint 08 with Tasks 095, 090, 087, and owner-gated 089.
- Formalized roadmap definitions for Tasks 090-097.
- Rebuilt current requirements/design around the October plan.
- Archived older planning, review, and prototype-era source files.
- Updated navigation, handoff, pilot, and agent guidance.
- Added the Docker/Podman startup coordination rule.
- Archived three completed Task-087/PR #46 status packets, the superseded RC1
  repository intake workflow, and stale Sprint/source-install guides.
- Removed one byte-identical duplicate archive snapshot and replaced the
  status/guide placeholders with current navigation.
- Recorded the 62-alert GitHub code-scanning baseline and inserted Tasks
  090/098 into the security gate.

**Output**: One current roadmap plus separated pilot, historical, active-task,
and archive sources.

**Validation**: PASS on July 23, 2026:

- `check_agent_work_quick.py`: passed
- `validate_agent_work.py`: passed
- current-source Markdown link check: passed
- contradiction phrase audit: no active stale-plan match
- `git diff --check`: passed

**Next**: Start Task-090 only after explicit implementation approval. Use its
classification to approve the separate Task-098 remediation scope before
Task-087 resumes.

## Validation Results

### Phase A - July 23, 2026

**Test Status**: PASS

- [x] Active task membership matches `current-tasks.md`.
- [x] No loose task Markdown files exist in `tasks/`.
- [x] Active status contains the current roadmap, Pilot plan, Pilot custody
  record, and active Pilot validation evidence.
- [x] Superseded roadmap/review material is under the July archive.
- [x] Current-source Markdown links resolve.
- [x] No secret-bearing or raw runtime evidence was added.
- [x] Workspace validator and diff checks pass.
- [x] Completed loose status packets and superseded RC1/stale-guide workflows
  are archived outside the current information surface.
- [x] GitHub code-scanning findings are durably inventoried and connected to a
  separate remediation gate.

Phase A is complete. Task-095 remains active for Phase B governance and final
handoff maintenance.
