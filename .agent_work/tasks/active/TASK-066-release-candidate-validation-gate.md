# TASK-066: Release Candidate Validation Gate

**Status**: IN_PROGRESS - post-PR28 final prerelease Docker Desktop package path and bounded provider smoke passed; Podman source-build TLS, Docker-Desktop-free Podman, and NVIDIA GPU evidence pending
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

- [x] Release candidate package generated or obtained with immutable image digest.
- [x] Asset bundle available in the `TASK-072` layout.
- [x] `TASK-071` docs used as the validation instructions.
- [x] Package extraction and `.env` initialization verified.
- [x] Docker or Podman engine/Compose startup verified for the selected validation path.
- [x] Readiness states verified before and after asset import and provider setup.
- [x] Asset import and optional release-candidate hash verification verified.
- [x] Provider setup and restart persistence verified.
- [x] At least one bounded detection smoke passes or a blocker is recorded.
- [x] Status/log support commands produce useful evidence.
- [x] CPU-safe default launch is verified with `-Gpu off` or equivalent default launcher behavior.
- [ ] If GPU support is claimed for the RC, `-Gpu auto` and `-Gpu on` are validated on an NVIDIA Docker Desktop WSL2 host with readiness diagnostics, fixed-fixture CPU/GPU output parity, and timing evidence.
- [x] CI/static-analysis expansion recommendation recorded, including visible route/package-staging checks, Windows package-script coverage, warning debt, and advisory-to-blocking gate candidates.
- [x] Markdown-to-HTML generation or parity-check recommendation recorded, including source-of-truth policy, package staging impact, and test coverage impact.
- [x] Time-to-first-run, manual interventions, confusing steps, and defects are recorded.
- [x] V1 RC1 pass/fail recommendation produced.

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
- `TASK-074`: selected follow-up for runtime prerequisite preflight/bootstrap after install-UX review confirmed enough first-launch friction to automate before broad external UAT.

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

### 2026-05-22 - Final Digest-Pinned Docker RC Package Validation
**Objective**: Validate the merged RC package path using the real GHCR digest-pinned image rather than a mutable local validation image.
**Context**: PR17 was merged to `main`. The user kept the existing local app on port `5000`, so the release package was validated as a separate Compose project on port `5007`. Docker Desktop was the selected validation engine for this run.
**Execution**:
- Published the RC image with GitHub Actions run `26312057748` from commit `1d8e472621ba5ea2a0f975b0cc749eea14c18f25`.
- Produced image `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121` with digest `sha256:55aabd73a0cbdb76a1d48f427e9fe74dcab63ed87f2a15d32d9709de3ce1a232`.
- Generated `dist/towerscout-v0.1.0-rc1.zip` and package directory `dist/towerscout-v0.1.0-rc1` pinned to that image digest.
- Staged the separate asset-bundle layout into the package `assets\` directory from the local release asset source for validation, then imported with `scripts\import-assets.cmd -Engine docker -Source assets -Port 5007 -VerifyHashes -RestartWaitSeconds 180`.
- Saved Azure provider setup through the package API and verified restart persistence with `start.bat -Engine docker -Port 5007 -Gpu off -NoBrowser -TimeoutSeconds 180`.
**Validation Evidence**:
- GitHub Actions publish run completed successfully and the GHCR tag/digest manifest was inspectable.
- Package ZIP SHA-256: `8D1E710681F856E6AAEB0B961FDA6934993FDA5CA3632D48A149ACFD2F1125D3`.
- Package manifest validation passed with non-blocking recommended-field warnings for future manifest enrichment (`checksums`, `releasePosture`, `releaseVersion`, `sourceRef`).
- First launch created `.env` and reached the expected pre-setup state: `setup_required`, `asset_status=degraded`, `config_status=setup_required`.
- Asset import passed: `post_import_health=ok`, `asset_status=ok`, `engine_count=1`, `verify_hashes=True`, and no missing/corrupt assets.
- Restarted package returned `ready` with `asset_status=ok`, `config_status=ok`, and persisted Azure provider setup.
- Readiness reported the pinned image digest, `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, `torch_cuda_build=12.1`, `configured_policy=cpu`, and `selected_device=cpu` under `-Gpu off`.
- `/api/health`, `/api/readiness`, `/docs/`, and `/license` returned HTTP `200`.
- Bounded Azure detection smoke passed on the public local fixture. Warm run returned HTTP `200` in `4.02s`: 1 tile record, 14 detection records, 14 selected detections, and 14 detections with address metadata (`azure_maps=9`, `outside_boundary=5`).
- Performance evidence showed the first digest-pinned run paid one-time initialization (`11.92s` total, `5.37s` model time), while the warm run completed in `4.00s` total with `3.15s` model time.
- Runtime cache check found no `/root/.cache/torch`; Ultralytics settings cache was `12K`, confirming the previous hidden EfficientNet checkpoint download did not return.
- Running container image size from Docker inspect was `7,106,386,204` bytes for the CUDA-capable single package image.
- Temporary RC validation stack was stopped after evidence capture; only the user's original `towerscout-towerscout-1` container remained running on port `5000`.
**Findings**:
- No Docker Desktop release blocker found for the CPU-default RC path.
- GPU support should not be broadly claimed until the NVIDIA Docker Desktop WSL2 validation item passes.
- Podman remains unvalidated on this host because the earlier base-image pull hit host TLS certificate verification before TowerScout code ran.
- The asset ZIP/checksum sidecar itself was not newly generated by this run; validation used the documented extracted asset layout and import hash verification.
**Recommendation**: Proceed toward Docker Desktop-based controlled RC1/UAT preparation, with explicit release notes that CPU-default Docker validation passed, GPU acceleration is pending NVIDIA-host evidence, and Podman remains a follow-up validation path unless it is required for the first external pilot cohort.
**Next**: Stop the validation stack, record cleanup evidence, then decide whether to run Podman/TLS remediation before `TASK-073` or start `TASK-073` with Docker Desktop as the supported pilot engine.

### 2026-05-26 - Podman Package Runtime And TLS Validation
**Objective**: Validate the Podman path before external pilot prep and separate normal package-runtime TLS risk from source-build/base-image TLS risk.
**Context**: Validation used the same digest-pinned RC image and a fresh extraction of `dist\towerscout-v0.1.0-rc1.zip` into `dist\towerscout-v0.1.0-rc1-podman-validation`. The existing Docker Desktop API was unavailable during this run, so the Podman evidence stands on the Podman machine and package route.
**Execution**:
- Confirmed Podman `5.8.2` and a running WSL Podman machine.
- Confirmed `podman compose` is available but delegates to external provider `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe` reporting Docker Compose `v5.1.3`.
- Pulled `ghcr.io/j-schulein/towerscout@sha256:55aabd73a0cbdb76a1d48f427e9fe74dcab63ed87f2a15d32d9709de3ce1a232` through Podman successfully, proving the GHCR digest/TLS path required by the package.
- Launched the clean package on port `5008` with `start.bat -Engine podman -Port 5008 -Gpu off -NoBrowser -TimeoutSeconds 180`.
- Imported the staged asset bundle with `scripts\import-assets.cmd -Engine podman -Source assets -Port 5008 -VerifyHashes -RestartWaitSeconds 180`.
- Saved Azure provider setup, verified restart persistence, route health, bounded detection, logs, and runtime cache behavior.
**Validation Evidence**:
- First launch reached the expected setup state: `setup_required`, `asset_status=degraded`, `config_status=setup_required`.
- Asset import passed: `post_import_health=ok`, `asset_status=ok`, `engine_count=1`, `verify_hashes=True`, and no missing/corrupt assets.
- Restarted Podman package returned `ready` with `asset_status=ok` and `config_status=ok`.
- Readiness reported `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, `torch_cuda_build=12.1`, `configured_policy=cpu`, and `selected_device=cpu` under `-Gpu off`.
- `/api/health`, `/api/readiness`, `/docs/`, and `/license` returned HTTP `200` on port `5008`.
- Bounded Azure detection smoke returned HTTP `200` in `13.05s`: 1 tile record, 14 detection records, 14 selected detections, and 14 detections with address metadata (`azure_maps=9`, `outside_boundary=5`).
- Performance evidence: 1 tile, total workflow `13.02s`, model time `6.21s`, model initialization `5.20s`, secondary classifier load `1.05s`, geocoding provider request `0.50s`.
- Runtime cache check found no `/root/.cache/torch`; Ultralytics settings cache was `12K`.
- Temporary Podman validation stack was stopped after evidence capture; `podman ps` returned no running containers.
**TLS Finding**:
- Podman successfully pulled the RC image from GHCR by digest, so normal package image retrieval is not blocked by TLS on this host.
- Podman still fails pulling `docker.io/library/python:3.11-slim-bookworm` because the Podman VM does not trust the Docker Hub/CloudFront TLS chain: `tls: failed to verify certificate: x509: certificate signed by unknown authority`.
- This Docker Hub TLS failure affects source builds and Docker-Hub-backed developer paths, not the normal digest-pinned GHCR package path validated for RC1.
**Recommendation**: Podman can be included as a validated package-runtime option for the controlled RC path only with the tested provider caveat: this host used `podman compose` delegating to Docker Compose v5.1.3. Do not claim Docker-Desktop-free Podman coverage from this run. Keep Podman VM CA import or clean-host Podman-only validation as a follow-up before promising source-build or Docker-Hub-backed workflows.
**Next**: Merge the evidence update, then proceed to `TASK-073` with Docker Desktop as the primary pilot engine and Podman package runtime as a supported-but-qualified path unless the pilot cohort requires Docker-Desktop-free Podman.

### 2026-05-27 - Route-Test Timeout And Isolation Gap Identified
**Objective**: Investigate repeated long-running validation commands before concluding the PR/code review.
**Context**: Broad focused pytest commands repeatedly stalled for 20-30 minutes until manually interrupted. Docker Desktop and Podman runtime engines were not required for those commands.
**Finding**: The stall isolated to `tests/unit/test_flask_routes.py`, which imports the full `towerscout` Flask module during pytest collection. That import executes production-style module bootstrap from `webapp/towerscout.py`, including `.env` discovery/loading, runtime logging/path setup, ML diagnostics, and other side effects before individual tests start. The timeout logs showed the test path loaded the real local `webapp/config/.env` instead of remaining fully isolated.
**Risk**: This does not invalidate the digest-pinned Docker/Podman package-runtime validation, but it weakens automated review confidence because one route-test module can hang before pytest produces normal progress output.
**Decision**: Do not expand the current validation-evidence PR into a broad Flask test refactor unless CI or reviewer feedback requires it. Record the issue as a pre-pilot follow-up and route implementation to `TASK-067` and/or `TASK-068`.
**Recommended Fix Scope**:
- Add timeout safeguards for local/CI pytest runs so collection-time hangs fail with diagnostics instead of waiting indefinitely.
- Isolate Flask route tests from real local config by setting test config/log/cache/upload/session paths before importing the app, or by refactoring toward an app factory/test bootstrap.
- Keep route/static docs/license checks in the release gate, but avoid importing production config and provider secrets during unit-test collection.
**Sequencing Recommendation**: Address the timeout safeguard and route-test isolation issue before starting broad `TASK-073` external pilot prep, unless the owner explicitly accepts it as a non-pilot-blocking internal test-harness risk.
**Next**: Update `current-tasks.md` and route the fix to `TASK-067`/`TASK-068` before or immediately after PR18 merge.

### 2026-05-27 - Route-Test Timeout And Isolation Gap Closed
**Objective**: Record the merged follow-up that closes the pre-pilot route-test validation caveat.
**Context**: `TASK-067` / PR #19 implemented pytest timeout safeguards, CI timeout limits, isolated route-test runtime paths, and legacy agent-guidance cleanup.
**Decision**: Treat the Flask route-test timeout/isolation finding as closed for `TASK-073` sequencing after PR #19 merge, while keeping broader package-runtime smoke automation as a later optional ratchet.
**Execution**: PR #19 was squash-merged into `main` as `dcf2322`.
**Output**: Broad pilot/UAT planning can proceed with the remaining `TASK-066` caveats limited to Podman source-build TLS, Docker-Desktop-free Podman support language, asset ZIP/checksum publication, and NVIDIA GPU support evidence.
**Validation**: PR #19 validation included pytest-timeout recognition (`timeout: 120.0s`, `timeout method: thread`) and `52 passed` across focused route/config/runtime tests.
**Next**: Begin `TASK-073` clean-machine pilot/UAT execution planning.

### 2026-05-27 - Install-UX Preflight Follow-Up Selected
**Objective**: Record the follow-up task selected after user-facing install documentation review.
**Context**: `TASK-073` and the install-UX review confirmed that current docs can be clarified, but users/support still have to manually reason through engine readiness, checksums, release-file matching, asset ZIP layout, first image pull timing, and readiness state interpretation.
**Decision**: Treat the low-risk documentation hardening as part of `TASK-073`, and route implementation-level bootstrap/preflight work to `TASK-074` before broad external UAT. Preserve Docker Desktop as the primary pilot engine and Podman as a qualified support-directed package-runtime path.
**Output**: `TASK-066` release validation remains passed with boundaries; `TASK-074` now owns automation that can reduce first-launch support risk before pilot expansion.
**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed; `python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `python .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Complete the docs/task hardening commit, then start `TASK-074` implementation planning.

### 2026-05-28 - Task-074 Post-Merge Package Bootstrap Validation Passed
**Objective**: Record completion of the selected bootstrap/preflight follow-through before returning to clean-machine UAT planning.
**Context**: `TASK-074` added a package bootstrap entry point, prerequisite checks, checksum and release matching, safe asset ZIP staging, readiness guidance, and package `.env` initialization across Compose entrypoints. PR #23 was squash-merged before this validation.
**Execution**: Generated a clean package from merged `main` without `-AllowDirtySource`, validated package shape and release manifest, ran `bootstrap.cmd -VerifyOnly -AssetZip ...`, confirmed verify-only left package assets untouched, ran full Docker bootstrap on isolated port `5010`, captured status/readiness evidence, and removed the isolated validation stack.
**Validation Evidence**:
- Clean package generated from commit `8e975e1` under `dist\task074-post-pr23-package\towerscout-v0.1.0-rc1`.
- Package summary found 45 files including `.env.example`, `IMAGE.txt`, `release-manifest.v1.json`, compliance notices, `compose.yaml`, `compose.gpu.yaml`, `bootstrap.cmd`, scripts, docs, and `webapp/asset_manifest.v1.json`.
- Manifest check passed with only the known recommended-field warnings for future enrichment (`checksums`, `releasePosture`, `releaseVersion`, `sourceRef`).
- Verify-only bootstrap passed, verified the asset ZIP checksum, confirmed Docker CLI/daemon/Compose/WSL checks, confirmed port `5010` availability, and did not stage final assets.
- Full bootstrap created `.env` from `.env.example`, imported assets with `verify_hashes=True`, reported no missing/corrupt assets, and reached readiness `setup_required` with assets `ok`.
- Runtime readiness reported `device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cuda121`, and image digest `sha256:55aabd73a0cbdb76a1d48f427e9fe74dcab63ed87f2a15d32d9709de3ce1a232`.
- The isolated validation project `towerscout-task074-postpr23` was stopped and volumes removed; the user's original Docker container on port `5000` remained healthy.
**Recommendation**: Treat `TASK-074` as complete for RC1 bootstrap/preflight scope. Proceed back to `TASK-073` clean-machine UAT preparation with Docker Desktop as the primary pilot path, qualified Podman language preserved, and GPU/Docker-Desktop-free Podman caveats unchanged.
**Next**: Update active task tracking, run `.agent_work` validation, and continue `TASK-073`.

### 2026-05-29 - Final Draft-Release Artifact Path Validated
**Objective**: Re-run the release package gate against the actual draft-release assets after PR27 merged.
**Context**: Earlier digest-pinned validation used image digest `sha256:55aabd73a0cbdb76a1d48f427e9fe74dcab63ed87f2a15d32d9709de3ce1a232`, which predated the final Task-073 handoff documentation updates. The final image needed to be rebuilt from the accepted source ref because the runtime image serves Settings-linked docs from `/app/docs`.
**Execution**:
- Synced `main` to accepted source ref `baa5ccc053184d4a24389a436f6d7c2168238c1e`.
- Quarantined old local `dist` artifacts under `dist/archive-pre-final-20260529`.
- Published `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121` from that source ref with GitHub Actions run `26631165695`.
- Generated `dist/towerscout-v0.1.0-rc1.zip` with the published digest and `pytorch_flavor=cuda121`.
- Created draft prerelease `v0.1.0-rc1` and uploaded the Application Package, Model & Data Package, and both checksum sidecars.
- Downloaded the draft-release assets into `dist/release-download-validation`, verified checksums, extracted the Application Package, and ran `bootstrap.cmd -Engine docker -Gpu off -PackageZip ..\towerscout-v0.1.0-rc1.zip -AssetZip ..\towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip -NoBrowser`.
**Validation Evidence**:
- Published image digest: `sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`.
- GitHub asset digest for `towerscout-v0.1.0-rc1.zip`: `sha256:ff7a2c997fe0678c1133847a56e1d2f21c7935732b1103841313a2b404cd3344`.
- GitHub asset digest for `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`: `sha256:00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Bootstrap verified both checksum sidecars, validated the asset ZIP layout, pulled the pinned image, initialized `.env`, imported assets with hash verification, and reached `setup_required` with `asset_status=ok`.
- `/api/health`, `/api/readiness`, `/docs/project-overview.html`, `/docs/towerscout-user-guide.html`, and `/license` returned HTTP `200`.
- `status.cmd` reported the running image `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`, Docker Compose `v5.1.3`, container health `healthy`, readiness `setup_required`, and all manifest assets `ok`.
- Runtime readiness confirmed CPU-safe launch from the CUDA-capable image: `configured_policy=cpu`, `selected_device=cpu`, `torch_version=2.2.1+cu121`, `torch_cuda_build=12.1`, and `torch_cuda_available=false`.
- The final validation stack was stopped after evidence capture.
**Findings**:
- No package/image/docs/assets mismatch remains for the draft-release artifact path.
- At this checkpoint, provider setup persistence and bounded detection smoke had not yet been rerun because no provider key or final public smoke fixture was selected for this handoff packet. That gap is superseded by the later final-digest provider smoke entry below.
**Recommendation**: Treat the final Docker Desktop bootstrap/readiness package path as passed for the draft-release assets. Do not mark external UAT approved until provider-key expectations, smoke fixture, support contact, and owner/reviewer acceptance are recorded in `TASK-073`.
**Next**: Fill the UAT handoff packet, decide whether to run provider setup plus bounded detection against the selected fixture, and then publish or owner-approve the draft prerelease for controlled testers.

### 2026-05-29 - Final-Digest Provider Smoke And Published Prerelease
**Objective**: Complete the owner-selected provider setup and bounded detection smoke on the final published digest before external UAT.
**Context**: The release owner selected Azure Maps, `200 west st, New York, NY 10282`, and a `150 meter` circle as the public RC1 smoke fixture. The owner also approved publishing the prerelease after internal validation.
**Execution**:
- Copied local ignored provider config into the downloaded validation container for this internal smoke only.
- Verified container readiness from inside the RC container with asset status `ok`, config status `ok`, default provider `azure`, CPU device selection, and image digest `sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`.
- Resolved the public fixture coordinates without recording the provider key.
- Ran the bounded detection smoke inside the RC container because this workstation had a conflicting host process on `localhost:5000`.
- Published the `v0.1.0-rc1` prerelease.
**Validation Evidence**:
- Published prerelease URL: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc1`.
- Smoke fixture: Azure Maps, `200 west st, New York, NY 10282`, `150 meter` circle, estimated `8` tiles and `48.23` seconds.
- Detection result: HTTP `200`, elapsed time about `43` seconds, `55` total records, `8` tile records, `47` cooling-tower records, and `47` records with address data.
- Release assets remained the same final files and checksums recorded above.
**Finding**: `/api/geocode/forward` returned HTTP `500` during fixture lookup because a successful Azure geocode result included a `GeocodingProvider` enum in the route-level `provider_used` field that Flask could not JSON serialize. The detection workflow itself completed with address data after the coordinates were resolved separately.
**Follow-Up Resolution**: PR #28 follow-up investigation confirmed the tester-visible Azure search path uses `/api/maps/azure/search`, not `/api/geocode/forward`. The backend route was still fixed by serializing `provider_used` from `GeocodingResult.to_dict()` output, and regression coverage now proves the route returns string provider fields for Azure forward-geocode results.
**Recommendation**: Docker Desktop CPU-default package validation can proceed to controlled external UAT after `TASK-073` tester/cohort selection and owner/reviewer packet approval. Keep GPU, Docker-Desktop-free Podman, and Podman source-build caveats bounded.
**Next**: Update `TASK-073` handoff state and request owner/reviewer approval for tester send.

### 2026-05-29 - Post-PR28 Final Artifact Refresh Validation
**Objective**: Re-run the release-candidate artifact gate after PR #28 merged runtime and package-doc changes.
**Context**: PR #28 fixed `/api/geocode/forward` serialization and updated package-included docs after the first published prerelease assets were generated. Because the image serves package-local docs and the release package pins a source ref plus image digest, the Application Package and GHCR image needed a final refresh from the merged source ref.
**Execution**:
- Published the `v0.1.0-rc1-cuda121` image from `main` source ref `e6495d14bd642eda81f7a70d6fe2e93d4b15097a` using GitHub Actions run `26641607377`.
- Downloaded the workflow image metadata artifact and extracted digest `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`.
- Regenerated `towerscout-v0.1.0-rc1.zip` with the refreshed digest and replaced the Application Package ZIP plus checksum on the published prerelease.
- Downloaded the refreshed app ZIP/checksum from the release into `dist\release-download-validation-final-e6495d1`, verified the app checksum, copied the unchanged Model & Data Package/checksum, verified the asset checksum, and extracted the downloaded app ZIP.
- Ran package bootstrap verify-only on port `5006`, explicitly pulled the pinned image after the first full bootstrap attempt exceeded the outer validation timeout during first image download, then validated the running package stack on port `5006`.
- Copied local ignored provider config into the validation container for internal smoke only and ran the public Azure fixture through search, estimate, and detection.
- Stopped the validation stack after evidence capture.
**Validation Evidence**:
- Published prerelease URL: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc1`.
- Accepted source ref: `e6495d14bd642eda81f7a70d6fe2e93d4b15097a`.
- Published image digest: `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`.
- Application Package SHA-256: `e071f1ac773f993b3a8636cab4be0e476ee95086dfec6ff24beda8b8a6fb3142`.
- Model & Data Package SHA-256: `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Package readiness reported `setup_required`, assets `ok`, CPU device selection, `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, and image digest `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158` under `-Gpu off`.
- In-container hash verification returned `asset_status=ok`, `verify_hashes=True`, no missing assets, no corrupt assets, and no optional missing assets.
- `/api/health`, `/api/readiness`, `/docs/project-overview.html`, `/docs/towerscout-user-guide.html`, `/docs/v1-rc1-quick-start.html`, and `/license` returned success.
- Azure search returned HTTP `200` with one result. Tile estimate returned HTTP `200`, `8` tiles, and `44.0` seconds. Detection returned HTTP `200`, `55` result records, `47` records with address data, and elapsed time about `59` seconds.
**Finding**: The first full bootstrap attempt exceeded the outer validation timeout while the new CUDA-capable image was not yet local. `bootstrap.cmd -VerifyOnly` had already passed and the explicit `docker pull` completed successfully. This is not a release blocker, but it reinforces the existing user-facing guidance that the first GHCR image pull can take several minutes and PowerShell should remain open.
**Recommendation**: Treat the post-PR28 Docker Desktop CPU-default package path as passed for controlled UAT, with the same bounded caveats around GPU, Docker-Desktop-free Podman, and Podman source-build validation.
**Next**: Update the UAT handoff packet and Task-073 evidence with the refreshed source ref, image digest, and checksum before owner/reviewer approval.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-22 through 2026-05-29
**Test Environment**: Windows 11 AMD64 workstation, Docker Desktop engine, Podman `5.8.2` WSL machine using `podman compose` with Docker Compose `v5.1.3` as external provider, final prerelease GHCR image `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`, CPU launch via `-Gpu off`, Azure provider configured from local ignored development config for validation only.
**Test Status**: PASS_WITH_BOUNDARIES - final prerelease Docker Desktop package path passed through bootstrap, asset import, readiness, Settings-linked docs, `/license`, provider setup, and bounded Azure detection smoke on the final digest. GPU, Docker-Desktop-free Podman, and Podman source-build TLS evidence remain bounded follow-ups.

### Acceptance Criteria Validation
- [x] Package generated or obtained - final RC control package generated with immutable GHCR image digest.
- [x] Asset bundle validated - manifest assets staged in the documented extracted layout, imported, and `-VerifyHashes` returned `asset_status=ok`.
- [x] Docs used as instructions - package quick start/package guide steps exercised; docs updated for non-default port import and post-import restart behavior.
- [x] Launch path verified - Docker launch on alternate ports reached expected first-run states and final `ready`.
- [x] Podman package runtime launch verified - Podman launch on port `5008` reached expected first-run states, asset import, restart persistence, and final `ready`.
- [x] Provider setup verified - Azure provider setup saved through API and persisted across restart in the package config volume.
- [x] Detection smoke verified - final-digest bounded Azure fixture returned HTTP `200`, `47` cooling-tower records, selected detections, and address fields.
- [x] Status/log support commands produce useful evidence - `status.cmd`, `/api/readiness`, Docker logs, and `performance.log` exposed actionable evidence.
- [x] CPU-safe default launch verified - validation launched with `-Gpu off`; runtime readiness selected CPU from the CUDA-capable image with `torch 2.2.1+cu121`.
- [x] Immutable image digest release package verified - post-PR28 final prerelease package pinned to GHCR digest `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`.
- [x] Bootstrap/preflight package path verified - post-PR23 clean package validation proved verify-only is non-mutating, asset ZIP staging/import succeeds, `.env` initializes from the pinned package template before Compose startup, and readiness reaches `setup_required` with assets `ok`.
- [ ] NVIDIA Docker Desktop WSL2 GPU evidence - PENDING separate GPU host validation before any broad GPU support claim.
- [ ] Docker-Desktop-free Podman evidence - PENDING clean-host validation with a provider that does not depend on Docker Desktop's external Compose binary.
- [x] CI/static-analysis expansion recommendation recorded - see recommendations below.
- [x] Markdown-to-HTML generation/parity recommendation recorded - see recommendations below.
- [x] V1 RC1 recommendation produced - Docker Desktop CPU-default RC path can proceed to controlled UAT, with GPU and Podman caveats.

### Issues Identified

1. **Fixed - non-default port asset import failure**: `import-assets.ps1` previously did not set `TOWERSCOUT_PORT`, causing `5000` bind conflicts when the app was already running elsewhere.
2. **Fixed - imported models not discovered until restart**: asset import copied model files after app startup, leaving the in-memory engine registry stale.
3. **Fixed - hidden EfficientNet first-use download**: `EfficientNet.from_pretrained(...)` downloaded a 117 MB base checkpoint on clean first detection.
4. **Open source-build caveat - Podman Docker Hub TLS**: Podman package runtime successfully pulled the RC image from GHCR, but Podman source-build/base-image pulls from Docker Hub still fail TLS certificate verification inside the Podman VM before TowerScout code runs.
5. **Open validation caveat - NVIDIA GPU host**: optional GPU acceleration needs NVIDIA Docker Desktop WSL2 validation before support claims.
6. **Open validation caveat - Docker-Desktop-free Podman**: this host's Podman Compose path delegates to Docker Desktop's Docker Compose binary, so it does not prove a Docker-Desktop-free Podman installation.
7. **Fixed - final release artifact publication**: final Application Package, Model & Data Package, and checksum sidecars were published under the `v0.1.0-rc1` prerelease and validated from downloaded GitHub assets.
8. **Fixed - route-test isolation and timeout safeguards**: `TASK-067` / PR #19 added pytest timeout safeguards and pre-import route-test runtime isolation so `tests/unit/test_flask_routes.py` no longer touches the developer's real local `.env` path during focused validation.
9. **Fixed - bootstrap/preflight package ordering and `.env` initialization**: `TASK-074` / PRs #22 and #23 ensured verify-only asset ZIP checks are non-mutating and packaged Compose entrypoints initialize `.env` from `.env.example` before starting the stack.
10. **Fixed - `/api/geocode/forward` serialization**: final smoke setup found this route returned HTTP `500` after Azure forward geocoding succeeded because the route-level `provider_used` field exposed a `GeocodingProvider` enum. PR #28 follow-up fixed the response serialization and added regression coverage. Tester-visible Azure search uses `/api/maps/azure/search`, so this defect did not block the selected external UAT fixture.

### Remediation Actions

- Added `-Port` support to `scripts/import-assets.ps1` and documented non-default port use in Markdown and Settings-linked HTML quick-start docs.
- Restarted TowerScout inside `scripts/import-assets.ps1` after copying assets so model discovery matches readiness state.
- Changed EfficientNet initialization to use local architecture construction plus packaged TowerScout checkpoint loading.
- Added unit coverage proving EfficientNet initialization does not call `from_pretrained()` and static regression coverage for import helper port/restart behavior.
- Validated the patched package path with a fresh package/project name and clean runtime cache.
- Published and validated the digest-pinned GHCR RC image and final control package.
- Validated the digest-pinned GHCR package runtime path under Podman on port `5008` and recorded the remaining Docker Hub TLS/source-build caveat.
- Validated the post-PR23 bootstrap/preflight path from a clean package generated from merged `main`, including non-mutating verify-only behavior, asset ZIP checksum verification, package `.env` initialization, asset import hash verification, and readiness with assets `ok`.

### Automation Recommendations

- Move package-script checks for `import-assets.ps1 -Port` behavior and post-copy restart behavior into `TASK-067` or `TASK-068`; this is Windows-first behavior that would have caught both script issues before manual RC validation.
- Add a release/package smoke that stages a local package, imports assets into a clean Compose project, asserts `/getengines` includes `newest`, and checks `/api/readiness` after import. Keep this advisory at first because it requires container runtime availability and large assets.
- Add an ML runtime guard test that fails if EfficientNet initialization reintroduces `from_pretrained()` or creates a Torch checkpoint cache during clean local initialization.
- Add a route/static check that package-local `/docs/`, `/license`, `/license.txt`, and Settings-linked HTML docs are present in both source and staged packages.
- `TASK-067` / PR #19 merged the route-test bootstrap fix: local/CI timeout safeguards, pre-import config/log/runtime path isolation, and fake provider keys are now available on `main`.
- Treat Markdown as the source of truth for end-user docs and either generate Settings-linked HTML from Markdown during package assembly or add a CI parity check that fails when Markdown sections change without the corresponding HTML update. Generation is preferable after RC1 if there is time; parity checking is the minimum RC-safe gate.

### Sign-off

Docker Desktop and Podman CPU-default RC1 package runtime validation passed against the digest-pinned GHCR image and can proceed to controlled UAT preparation if Docker Desktop remains the primary pilot engine and Podman is documented as a qualified package-runtime path. The route-test isolation/timeout gap is closed by `TASK-067` / PR #19. `TASK-074` bootstrap/preflight follow-through is complete and passed clean post-merge package validation. Do not claim GPU acceleration until NVIDIA Docker Desktop WSL2 evidence exists. Do not claim Docker-Desktop-free Podman or Podman source-build support until the external Compose-provider dependency and Docker Hub TLS/base-image pull blocker are resolved or tested on a clean Podman-only host.
