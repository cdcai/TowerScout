# TASK-073: Clean-Machine Pilot / UAT Execution Plan

**Status**: NOT_STARTED  
**Priority**: HIGH  
**Type**: B/C (User Testing / Release Validation)  
**Estimated Effort**: 0.5-1 day (4-8 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Define the controlled external pilot / UAT workflow for TowerScout V1 RC1 after the internal clean-machine release-candidate gate has passed or produced owner-accepted residual risks.

This task should make external testing repeatable, bounded, and evidence-producing.

## Requirements (EARS Notation)

**R-073-001**: WHEN external pilot/UAT begins, THE PROJECT SHALL provide tester instructions that match the validated V1 RC1 package/docs/assets path.

**R-073-002**: WHEN testers report results, THE PROJECT SHALL capture environment details, package version, asset bundle version, runtime engine, Compose provider, provider used, network/TLS context, and test flow outcome.

**R-073-003**: WHEN testers hit a problem, THE PROJECT SHALL route the report through `.agent_work/user-testing/` using the established issue and artifact workflow.

**R-073-004**: WHEN a pilot test is considered successful, THE PROJECT SHALL have evidence that install, launch, provider setup, bounded detection, and issue reporting are usable under the supported V1 RC1 environment.

**R-073-005**: IF external testers find blockers in install, launch, setup, detection, export, assets, or documentation, THEN THE PROJECT SHALL classify those blockers as V1 fix work unless explicitly owner-accepted.

**R-073-006**: WHEN pilot/UAT completes, THE PROJECT SHALL decide whether V1 is complete, needs V1 patch work, or requires another release candidate.

## Acceptance Criteria

- [ ] Pilot/UAT start criteria are documented.
- [ ] Pilot/UAT stop criteria are documented.
- [ ] Tester instructions are aligned with `TASK-071` docs and `TASK-066` findings.
- [ ] Acceptance checklist covers package extraction, launch, asset import, provider setup, bounded detection, status/log collection, and issue reporting.
- [ ] Environment capture checklist is ready.
- [ ] Issue-reporting workflow links to `.agent_work/user-testing/`.
- [ ] Support escalation path is documented.
- [ ] Blocker triage rules distinguish V1 blockers, V1 patch candidates, and V2 backlog items.
- [ ] V1 completion gate after pilot/UAT is documented.

## Dependencies

- `TASK-066`: release candidate validation gate.
- `TASK-071`: end-user release package documentation.
- `TASK-072`: release asset bundle contract.
- `.agent_work/user-testing/README.md`: existing user-testing workspace rules.
- `.agent_work/user-testing/issue-tracker.md`: issue tracking surface.
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`: existing tester issue report checklist.

## Implementation Plan

1. Review the user-testing workspace and existing tester report checklist.
2. Pull relevant clean-machine findings from `TASK-066`.
3. Define pilot start criteria and stop criteria.
4. Draft a bounded acceptance checklist for testers.
5. Draft environment capture and support evidence collection instructions.
6. Define issue triage rules for V1 blockers, V1 patch candidates, and V2 backlog items.
7. Link the UAT plan to the Sprint 06 plan and user-testing workspace.
8. Prepare handoff guidance for pilot testers and first-line support.

---

## Implementation Log

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for clean-machine pilot / UAT execution planning.  
**Context**: Sprint 06 planning separates internal release-candidate validation from external pilot/UAT. External testing should start only after `TASK-066` validates or dispositiones the package/docs/assets path.  
**Decision**: Keep this task focused on UAT planning and evidence workflow, not on fixing release-candidate defects. Defects found by `TASK-066` should be routed before pilot start.  
**Execution**: Created `.agent_work/tasks/active/TASK-073-clean-machine-uat-plan.md` and synchronized the task with `current-tasks.md`.  
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Wait for `TASK-066` findings, then build the pilot/UAT checklist and handoff flow.

---

## Validation Results

### Test Summary
**Test Date**: Pending  
**Test Environment**: Pending  
**Test Status**: NOT_STARTED

### Acceptance Criteria Validation
- [ ] Start/stop criteria documented - PENDING
- [ ] Tester acceptance checklist ready - PENDING
- [ ] Environment capture checklist ready - PENDING
- [ ] Issue-report workflow linked - PENDING
- [ ] V1 completion gate documented - PENDING

### Issues Identified

None yet.

### Remediation Actions

None yet.

### Sign-off

Pending implementation and validation.
