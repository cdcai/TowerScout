# TASK-071: End-User Release Package Documentation

**Status**: NOT_STARTED  
**Priority**: CRITICAL  
**Type**: B/C (Documentation / User Enablement)  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Produce package-based end-user documentation for TowerScout V1 RC1 so a non-technical Windows pilot user can download the release package, place/import required assets, start TowerScout, complete first-run setup, validate success, and report problems without project tribal knowledge.

This task should replace or clearly distinguish older source/Conda tester guidance from the V1 RC1 package path.

## Requirements (EARS Notation)

**R-071-001**: WHEN a pilot user receives the V1 RC1 release package, THE DOCUMENTATION SHALL explain what files to download and where to extract them.

**R-071-002**: WHEN required assets are supplied separately, THE DOCUMENTATION SHALL explain the asset bundle layout, placement, import command, and verification expectations defined by `TASK-072`.

**R-071-003**: WHEN a user starts TowerScout for the first time, THE DOCUMENTATION SHALL explain how to run `start.bat`, what readiness states mean, and when the browser should open.

**R-071-004**: WHEN no provider key is configured, THE DOCUMENTATION SHALL explain how to use Setup Wizard or Settings to configure at least one supported map provider.

**R-071-005**: WHEN launch or setup fails, THE DOCUMENTATION SHALL tell users what status/log/preflight evidence to collect and what information not to share.

**R-071-006**: WHEN a user's environment includes Docker, Podman, Compose provider, TLS inspection, restricted network, or asset issues, THE DOCUMENTATION SHALL route the user to the appropriate supported V1 RC1 guidance or clearly state the limitation.

**R-071-007**: WHEN older source-install tester guides remain in the repo, THE DOCUMENTATION SHALL make clear whether they are legacy/source-install guidance and not the preferred V1 RC1 pilot package path.

## Acceptance Criteria

- [ ] A one-page V1 RC1 quick start exists for Windows 11 AMD64 pilot users.
- [ ] A fuller V1 RC1 package guide exists for first-line support and testers.
- [ ] The docs explain release package download/extraction, asset placement/import, launch, first-run setup, validation, stop/restart, troubleshooting, and issue reporting.
- [ ] The docs include sensitive-data handling guidance for `.env`, provider keys, logs, cached provider responses, uploaded files, and exported datasets.
- [ ] The docs reflect the `TASK-072` asset bundle contract.
- [ ] The docs reflect current Podman/Docker support language from `TASK-065`.
- [ ] The docs state the V1 RC1 support boundary, including CPU baseline and supported Windows target.
- [ ] Older source/Conda testing guides are marked or linked in a way that avoids confusing pilot package users.
- [ ] `TASK-066` can use these docs as the only user-facing instructions for clean-machine validation.

## Dependencies

- `TASK-072`: release asset bundle contract.
- `TASK-065`: release support language and runtime support caveats.
- `docs/oci-quick-start.md`: current OCI quick-start baseline.
- `docs/oci-runtime-contract.md`: current runtime contract.
- `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`: older source/venv tester guide to reconcile or label.
- `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`: older source/Conda tester guide to reconcile or label.

## Implementation Plan

1. Review existing OCI docs and older user-testing guides.
2. Decide where V1 RC1 package docs should live, favoring `docs/` for release-package docs and `.agent_work/context/guides/` for internal tester/support handoff if needed.
3. Draft a one-page quick start for pilot users.
4. Draft a full package guide for support/testers.
5. Integrate the `TASK-072` asset bundle contract.
6. Add troubleshooting and issue-report guidance aligned with `.agent_work/user-testing/`.
7. Mark older source/Conda tester guides as legacy/source-install guidance if they remain.
8. Hand off the docs to `TASK-066` for clean-machine validation.

---

## Implementation Log

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for end-user release package documentation.  
**Context**: Sprint 06 planning identified that broad end-user testing should wait until package docs and asset instructions are clear. Existing tester guides target source/Conda flows and do not represent the V1 RC1 release package path.  
**Decision**: Keep this task focused on package-based user documentation, with source-install guidance treated as legacy/support material unless explicitly needed.  
**Execution**: Created `.agent_work/tasks/active/TASK-071-end-user-release-docs.md` and synchronized the task with `current-tasks.md`.  
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Start documentation inventory and draft the V1 RC1 quick start once `TASK-072` provides the asset contract.

---

## Validation Results

### Test Summary
**Test Date**: Pending  
**Test Environment**: Pending  
**Test Status**: NOT_STARTED

### Acceptance Criteria Validation
- [ ] Quick start created - PENDING
- [ ] Full package guide created - PENDING
- [ ] Asset contract integrated - PENDING
- [ ] Troubleshooting guidance included - PENDING
- [ ] Older guides reconciled or labeled - PENDING

### Issues Identified

None yet.

### Remediation Actions

None yet.

### Sign-off

Pending implementation and validation.
