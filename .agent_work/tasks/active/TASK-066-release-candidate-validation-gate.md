# TASK-066: Release Candidate Validation Gate

**Status**: NOT_STARTED  
**Priority**: CRITICAL  
**Type**: C (Release Engineering / Validation)  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Internally validate the TowerScout V1 RC1 package/docs/assets path from a clean user-facing environment before external pilot/UAT begins.

This task is the bridge between engineered release readiness and real user testing. It should prove that a representative user can follow the documented package path without project tribal knowledge.

## Requirements (EARS Notation)

**R-066-001**: WHEN a V1 RC1 release candidate is validated, THE VALIDATION SHALL use the release package, asset bundle, and end-user docs intended for pilot users.

**R-066-002**: WHEN validation starts, THE VALIDATION SHALL begin from a clean or representative Windows 11 AMD64 environment with no reliance on local repo-specific tribal knowledge.

**R-066-003**: WHEN the package is launched, THE VALIDATION SHALL verify package extraction, `.env` creation, pinned image digest behavior, selected runtime engine startup, and readiness polling.

**R-066-004**: WHEN assets are imported, THE VALIDATION SHALL verify the documented asset bundle layout, import helper behavior, readiness asset status, and release-candidate checksum/hash expectations.

**R-066-005**: WHEN provider setup is performed, THE VALIDATION SHALL verify Setup Wizard or Settings persistence across restart for at least one supported provider.

**R-066-006**: WHEN the app reaches a usable state, THE VALIDATION SHALL run one bounded detection smoke that exercises the intended package path without creating a long or fragile test.

**R-066-007**: IF clean-machine validation exposes install, launch, setup, detection, documentation, asset, TLS, or runtime prerequisite blockers, THEN THE TASK SHALL record them as blockers and route them to the appropriate task before external UAT.

**R-066-008**: WHEN validation completes, THE TASK SHALL produce a pass/fail V1 RC1 recommendation and record remaining risks.

## Acceptance Criteria

- [ ] Release candidate package generated or obtained with immutable image digest.
- [ ] Asset bundle available in the `TASK-072` layout.
- [ ] `TASK-071` docs used as the validation instructions.
- [ ] Package extraction and `.env` initialization verified.
- [ ] Docker or Podman engine/Compose startup verified for the selected validation path.
- [ ] Readiness states verified before and after asset import and provider setup.
- [ ] Asset import and optional release-candidate hash verification verified.
- [ ] Provider setup and restart persistence verified.
- [ ] At least one bounded detection smoke passes or a blocker is recorded.
- [ ] Status/log support commands produce useful evidence.
- [ ] Time-to-first-run, manual interventions, confusing steps, and defects are recorded.
- [ ] V1 RC1 pass/fail recommendation produced.

## Dependencies

- `TASK-065`: release packaging and runtime support follow-through.
- `TASK-072`: release asset bundle contract.
- `TASK-071`: end-user release package documentation.
- `scripts/package-release.cmd` / `scripts/package-release.ps1`: package generation.
- `scripts/import-assets.cmd` / `scripts/import-assets.ps1`: asset import.
- `start.bat` and launcher scripts.
- Optional: `TASK-074` if prerequisite friction becomes severe.

## Implementation Plan

1. Confirm `TASK-065`, `TASK-071`, and `TASK-072` are ready enough for validation.
2. Generate or obtain the V1 RC1 package with an immutable image digest.
3. Prepare a clean or representative validation environment.
4. Execute the package docs step by step without using repo-local shortcuts.
5. Import and verify assets.
6. Configure at least one provider and verify persistence across restart.
7. Run a bounded detection smoke.
8. Capture logs/status/readiness outputs and user-friction notes.
9. Triage findings into blockers, follow-ups, or accepted risks.
10. Produce a V1 RC1 pass/fail recommendation and hand off to `TASK-073`.

---

## Implementation Log

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for release-candidate validation.  
**Context**: Sprint 06 planning intentionally places clean-machine validation after asset contract and package docs, so external user testing starts only after the known package/docs/assets path has been internally proven.  
**Decision**: Treat `TASK-066` as an internal release-candidate gate, not broad external UAT. External tester planning belongs to `TASK-073`.  
**Execution**: Created `.agent_work/tasks/active/TASK-066-release-candidate-validation-gate.md` and synchronized the task with `current-tasks.md`.  
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Wait for `TASK-072` and `TASK-071` deliverables, then build the validation checklist and execute the clean-machine gate.

---

## Validation Results

### Test Summary
**Test Date**: Pending  
**Test Environment**: Pending  
**Test Status**: NOT_STARTED

### Acceptance Criteria Validation
- [ ] Package generated or obtained - PENDING
- [ ] Asset bundle validated - PENDING
- [ ] Docs used as instructions - PENDING
- [ ] Launch path verified - PENDING
- [ ] Provider setup verified - PENDING
- [ ] Detection smoke verified - PENDING
- [ ] V1 RC1 recommendation produced - PENDING

### Issues Identified

None yet.

### Remediation Actions

None yet.

### Sign-off

Pending implementation and validation.
