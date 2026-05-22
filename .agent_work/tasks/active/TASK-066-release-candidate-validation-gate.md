# TASK-066: Release Candidate Validation Gate

**Status**: IN_PROGRESS
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

### 2026-05-22 - Validation Started From Merged PR16
**Objective**: Start the internal V1 RC1 release-candidate validation gate from the merged PR16 documentation baseline.
**Context**: PR16 was squash-merged into `main`, adding package-local docs, Settings Resource Links, route hardening, package staging updates, and PR16 reviewer follow-up fixes. `TASK-066` is now the next Sprint 06 gate before external UAT planning.
**Decision**: Run the gate from a fresh `docs/task-066-release-candidate-validation` branch based on updated `main`. Start with package/static validation and package assembly before attempting runtime launch or bounded detection.
**Execution**: Updated local `main` to the merged PR16 commit and created the TASK-066 validation branch.
**Output**: `TASK-066` is now in progress.
**Validation**: Pending package/static validation.
**Next**: Inspect release package inputs, run focused release tests, generate a current package staging directory, summarize package contents, and then proceed to runtime validation if prerequisites are available.

### 2026-05-22 - Local Package Path Validated And Release Blockers Fixed
**Objective**: Execute the package, asset import, provider setup, restart persistence, and bounded detection smoke against a local RC-style package.
**Context**: Validation used Docker Desktop on Windows with the app already occupying port `5000`, so local packages were launched on alternate ports with `-Gpu off`. Generated packages used local mutable image tags and dirty-tree allowances for validation only; they are not release artifacts.
**Findings**:
- `scripts/import-assets.ps1` did not propagate a non-default `-Port`, so importing assets while another TowerScout instance used port `5000` recreated the package service with the wrong port binding and failed. Fixed by adding a `-Port` parameter and setting `TOWERSCOUT_PORT` before Compose calls.
- `scripts/import-assets.ps1` copied assets into named volumes while the Flask process had already initialized without model files, so readiness could report assets `ok` while `/getengines` still lacked `newest`. Fixed by restarting TowerScout after model/data copy and before manifest verification.
- First EfficientNet use in a clean container downloaded the ImageNet base checkpoint into `/root/.cache/torch` even though the TowerScout project checkpoint was present. Fixed by changing `webapp/ts_en.py` to build the EfficientNet-B5 architecture locally with `EfficientNet.from_name(...)` and then load the packaged TowerScout state dict.
- Podman image build on this host failed before application build because Docker Hub base-image pull hit a TLS certificate verification error. Docker Desktop build and runtime validation succeeded.
**Validation Evidence**:
- Static/focused release tests passed before runtime validation: `45 passed` across release package, manifest, Flask route, license notice, and container publish tests.
- Local package `dist/towerscout-v0.1.0-rc1-runtime-local-offlinecheck2` imported 9 manifest assets with `-VerifyHashes`, reached readiness `ready`, persisted Azure provider setup, and exposed `newest` through `/getengines` after import without a manual restart.
- Health/docs/license routes returned `200`: `/api/health`, `/docs/`, and `/license`.
- Bounded Azure smoke on the public local fixture returned HTTP `200` in `20.15s`: 1 tile record, 14 detection records, 14 selected detections, and 14 detections with address text/provider metadata.
- Clean-container first detection produced no `/root/.cache/torch` checkpoint cache after the EfficientNet fix; logs show `EfficientNet base architecture initialized` and `EfficientNet weights loaded on CPU`, with no pretrained checkpoint download.
- Performance log for the first patched container detection: 1 tile, total workflow `20.12s`, model time `11.62s`, model initialization `7.01s`, secondary classifier load `3.18s`, geocoding provider request `0.28s`.
- Post-fix focused validation passed: `git diff --check`, `.agent_work` validation, PowerShell syntax parse for `scripts/import-assets.ps1`, `py_compile` for ML modules, and `55 passed` across focused release/package/route/license/container/ML unit tests.
**Output**: Local package path is now viable after the script/runtime fixes. The real RC artifact still needs a digest-pinned image/package run before sign-off.
**Next**: Run focused validation on the changed scripts/runtime/docs, record CI/static-analysis and Markdown-to-HTML recommendations, then decide whether TASK-066 can move to final RC artifact validation or should route additional hardening to TASK-067/TASK-068.

### 2026-05-22 - PR17 Reviewer Follow-Up Hardening
**Objective**: Address reviewer feedback before merging PR17.
**Context**: The reviewer agreed with the direction but identified three changes that should be tightened before merge: post-import service usability, the Windows-skipped import helper test, and safer checkpoint loading.
**Decision**: Add a bounded post-restart wait that accepts the normal pre-provider setup state. The helper should require `/api/health` to respond, `/api/readiness` assets to be `ok`, and `/getengines` to return at least one engine; it should not require the full readiness state to be `ready` because provider setup can happen after asset import.
**Execution**:
- Added a post-restart poll to `scripts/import-assets.ps1` with `-RestartWaitSeconds`.
- Moved import-helper static regression coverage into a cross-platform test file and added ordering checks for port propagation, copy, restart, wait, and verification.
- Changed EfficientNet checkpoint loading to prefer `torch.load(..., weights_only=True)` with a compatibility fallback for older Torch behavior.
**Validation**:
- `git diff --check`, `.agent_work` validation, PowerShell parser validation, and ML `py_compile` passed.
- Focused unit suite passed with `55 passed` and the existing `datetime.utcnow()` warnings.
- Clean local EfficientNet initialization with a temporary `TORCH_HOME` succeeded with no Torch checkpoint cache populated.
- Fresh local package import smoke on port `5006` passed after the post-restart wait: `health=ok`, readiness `state=setup_required`, `asset_status=ok`, `engine_count=1`, and `-VerifyHashes` returned `asset_status=ok`.
**Next**: Re-run focused tests, update PR17, then proceed to final digest-pinned package validation after merge.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-22
**Test Environment**: Windows 11 AMD64 workstation, Docker Desktop engine, local Docker image `towerscout:task066-local`, CPU launch via `-Gpu off`, Azure provider configured from local ignored development config for validation only.
**Test Status**: PARTIAL_PASS_AFTER_FIXES - local RC-style package path passed; final digest-pinned RC artifact still pending.

### Acceptance Criteria Validation
- [x] Package generated or obtained - local validation packages generated with dirty-tree/mutable-image warnings; release artifact with immutable digest still required.
- [x] Asset bundle validated - manifest assets staged/imported and `-VerifyHashes` returned `asset_status=ok`.
- [x] Docs used as instructions - package quick start/package guide steps exercised; docs updated for non-default port import and post-import restart behavior.
- [x] Launch path verified - Docker launch on alternate ports reached expected first-run states and final `ready`.
- [x] Provider setup verified - Azure provider setup saved through API and persisted across restart in the package config volume.
- [x] Detection smoke verified - bounded Azure fixture returned HTTP `200`, 14 detection records, selected detections, and address fields.
- [x] Status/log support commands produce useful evidence - `status.cmd`, `/api/readiness`, Docker logs, and `performance.log` exposed actionable evidence.
- [x] CPU-safe default launch verified - validation launched with `-Gpu off`; runtime readiness selected CPU with `torch 2.2.1+cpu`.
- [ ] Immutable image digest release package verified - PENDING final RC package/image digest.
- [ ] NVIDIA Docker Desktop WSL2 GPU evidence - PENDING separate GPU host validation before any broad GPU support claim.
- [x] CI/static-analysis expansion recommendation recorded - see recommendations below.
- [x] Markdown-to-HTML generation/parity recommendation recorded - see recommendations below.
- [ ] V1 RC1 recommendation produced - PENDING final digest-pinned artifact validation.

### Issues Identified

1. **Fixed - non-default port asset import failure**: `import-assets.ps1` previously did not set `TOWERSCOUT_PORT`, causing `5000` bind conflicts when the app was already running elsewhere.
2. **Fixed - imported models not discovered until restart**: asset import copied model files after app startup, leaving the in-memory engine registry stale.
3. **Fixed - hidden EfficientNet first-use download**: `EfficientNet.from_pretrained(...)` downloaded a 117 MB base checkpoint on clean first detection.
4. **Environment blocker for Podman on this host**: Podman build failed on Docker Hub base-image TLS verification before TowerScout code ran. Docker Desktop remains the validated engine for this local run.
5. **Final RC blocker still open**: this evidence used local mutable images and dirty-tree validation packages. A final digest-pinned release package run remains required.

### Remediation Actions

- Added `-Port` support to `scripts/import-assets.ps1` and documented non-default port use in Markdown and Settings-linked HTML quick-start docs.
- Restarted TowerScout inside `scripts/import-assets.ps1` after copying assets so model discovery matches readiness state.
- Changed EfficientNet initialization to use local architecture construction plus packaged TowerScout checkpoint loading.
- Added unit coverage proving EfficientNet initialization does not call `from_pretrained()` and static regression coverage for import helper port/restart behavior.
- Validated the patched package path with a fresh package/project name and clean runtime cache.

### Automation Recommendations

- Move package-script checks for `import-assets.ps1 -Port` behavior and post-copy restart behavior into `TASK-067` or `TASK-068`; this is Windows-first behavior that would have caught both script issues before manual RC validation.
- Add a release/package smoke that stages a local package, imports assets into a clean Compose project, asserts `/getengines` includes `newest`, and checks `/api/readiness` after import. Keep this advisory at first because it requires container runtime availability and large assets.
- Add an ML runtime guard test that fails if EfficientNet initialization reintroduces `from_pretrained()` or creates a Torch checkpoint cache during clean local initialization.
- Add a route/static check that package-local `/docs/`, `/license`, `/license.txt`, and Settings-linked HTML docs are present in both source and staged packages.
- Treat Markdown as the source of truth for end-user docs and either generate Settings-linked HTML from Markdown during package assembly or add a CI parity check that fails when Markdown sections change without the corresponding HTML update. Generation is preferable after RC1 if there is time; parity checking is the minimum RC-safe gate.

### Sign-off

Not ready for external UAT sign-off yet. Local package-path validation passed after fixes, but final sign-off requires a clean digest-pinned RC package run and a decision on whether Docker-only validation is sufficient for RC1 or whether Podman/TLS remediation must be completed first.
