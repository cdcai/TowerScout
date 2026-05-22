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

**R-066-009**: WHEN the RC package includes the optional GPU path, THE VALIDATION SHALL prove the default CPU launch first and SHALL treat NVIDIA Docker Desktop WSL2 GPU validation as a separate evidence item before any GPU support claim.

**R-066-010**: WHEN release-candidate validation identifies manual package, docs, or quality checks that should become repeatable gates, THE TASK SHALL produce a CI/static-analysis expansion recommendation with the intended blocking/advisory policy.

**R-066-011**: WHEN user-facing docs are validated, THE TASK SHALL evaluate a Markdown-to-HTML generation or parity-check strategy so package-local Markdown docs and Settings-linked HTML docs do not drift over time.

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
- [ ] CPU-safe default launch is verified with `-Gpu off` or equivalent default launcher behavior.
- [ ] If GPU support is claimed for the RC, `-Gpu auto` and `-Gpu on` are validated on an NVIDIA Docker Desktop WSL2 host with readiness diagnostics, fixed-fixture CPU/GPU output parity, and timing evidence.
- [ ] CI/static-analysis expansion recommendation recorded, including visible route/package-staging checks, Windows package-script coverage, warning debt, and advisory-to-blocking gate candidates.
- [ ] Markdown-to-HTML generation or parity-check recommendation recorded, including source-of-truth policy, package staging impact, and test coverage impact.
- [ ] Time-to-first-run, manual interventions, confusing steps, and defects are recorded.
- [ ] V1 RC1 pass/fail recommendation produced.

## Dependencies

- `TASK-065`: release packaging and runtime support follow-through.
- `TASK-072`: release asset bundle contract.
- `TASK-071`: end-user release package documentation.
- `scripts/package-release.cmd` / `scripts/package-release.ps1`: package generation.
- `scripts/import-assets.cmd` / `scripts/import-assets.ps1`: asset import.
- `start.bat` and launcher scripts.
- `TASK-075`: CPU-safe default launch, optional Docker GPU overlay, and GPU validation boundaries.
- `.github/workflows/ci.yml`: current automated CI/static-analysis baseline.
- `TASK-067`: follow-up home for CI release-gate tightening if `TASK-066` recommends implementation beyond the RC validation task.
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
10. Identify which manual RC validation checks should become visible CI/static-analysis gates and route implementation to `TASK-067` if needed.
11. Evaluate whether Markdown docs should generate Settings-linked HTML docs, whether a parity test is enough for RC1, and what package-staging changes would be required.
12. Produce a V1 RC1 pass/fail recommendation and hand off to `TASK-073`.

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

### 2026-05-20 - Task-075 GPU Validation Handoff
**Objective**: Add GPU/CUDA validation expectations from `TASK-075`.
**Context**: `TASK-075` proved CUDA-wheel CPU fallback locally and implemented optional Docker GPU overlay/launcher behavior. A running local Compose service prevented launcher smoke without disturbing the active app, and this host does not provide NVIDIA GPU validation.
**Decision**: `TASK-066` should validate CPU launch as the default release path. GPU support remains a separate evidence item requiring an NVIDIA Docker Desktop WSL2 host and fixed-fixture parity/timing evidence.
**Execution**: Added `R-066-009`, GPU-specific acceptance criteria, and a dependency on `TASK-075`.
**Output**: The RC validation gate now has explicit CPU-default and GPU-claim boundaries.
**Validation**: Pending Task-066 execution.
**Next**: Include `-Gpu off`, `-Gpu auto`, and `-Gpu on` branches in the validation checklist, but only mark GPU support claimable after NVIDIA host evidence exists.

### 2026-05-22 - PR16 Review Follow-Up Scope Added
**Objective**: Add deferred documentation-maintenance and CI-quality recommendations from the PR16 readiness review to the release-candidate gate.
**Context**: PR16 user documentation is close to merge-ready after targeted documentation fixes, but the review identified two broader follow-ups: visible CI/static-analysis expansion for package/docs validation and a durable Markdown-to-HTML generation or parity strategy for Settings-linked docs.
**Decision**: Track the investigation and recommendation work in `TASK-066` because the release-candidate gate is where manual package validation, docs drift risk, and CI coverage gaps can be evaluated against the actual RC package path. Implementation of new CI gates can be routed to `TASK-067` if the validation evidence justifies it.
**Execution**: Added `R-066-010`, `R-066-011`, acceptance criteria, dependencies, and implementation-plan steps for CI/static-analysis expansion and Markdown-to-HTML generation/parity evaluation.
**Output**: `TASK-066` now explicitly includes the deferred PR16 readiness recommendations without blocking the narrow PR16 documentation patch.
**Validation**: Pending `.agent_work` validation after the PR16 documentation updates.
**Next**: During `TASK-066`, validate the package path first, then decide which checks should become automated gates before external UAT.

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
