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
- Tasks 090-097 as formalized by Phase A and Task-098 added by the July 23
  code-scanning readiness review
- Final candidate and handoff evidence

## Implementation Log

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
