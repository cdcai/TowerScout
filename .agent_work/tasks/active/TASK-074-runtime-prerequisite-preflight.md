# TASK-074: Runtime Prerequisite Preflight

**Status**: IN_PROGRESS - reviewer hardening underway after Docker Desktop and qualified Podman bootstrap smokes passed
**Priority**: HIGH  
**Type**: B/C (Launcher / Supportability / Release UX)  
**Estimated Effort**: 1-2 days (8-16 hours) for RC1 MVP; additional polish can follow after pilot feedback  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Implement a Windows package bootstrap/preflight layer that reduces first-launch friction for V1 RC1 users while preserving the validated release package boundaries.

The RC1 MVP should make the current package path easier to run without turning TowerScout into a native installer. Docker Desktop remains the primary pilot path. Podman remains a qualified support-directed path when the workstation already has a running Podman machine and approved Compose provider.

## Requirements (EARS Notation)

**R-074-001**: WHEN a user runs the package bootstrap entry point, THE SYSTEM SHALL check the selected runtime engine prerequisites before starting TowerScout.

**R-074-002**: WHEN Docker is selected, THE SYSTEM SHALL check Docker CLI availability, Docker daemon readiness, Docker Compose availability, WSL 2/virtualization hints where available, local port availability, and minimum free disk space.

**R-074-003**: WHEN Podman is selected, THE SYSTEM SHALL check Podman CLI availability, Podman machine state, Podman Compose provider availability, local port availability, and minimum free disk space without requiring Docker Desktop.

**R-074-004**: WHEN both Docker and Podman are installed and automatic engine selection is used, THE SYSTEM SHALL report which engine was selected and remind the user that assets/provider setup are engine-specific named volumes.

**R-074-005**: WHEN release files are provided, THE SYSTEM SHALL verify Application Package and Model & Data Package checksums before extraction or import.

**R-074-006**: WHEN a Model & Data Package ZIP is provided, THE SYSTEM SHALL reject unsafe ZIP entries, reject ambiguous nested asset layouts, extract into a temporary staging folder, and promote only the expected `model_params/`, `data/`, and `asset_manifest.v1.json` entries after validation.

**R-074-007**: WHEN release metadata is available, THE SYSTEM SHALL verify that the Application Package, Model & Data Package, `release-manifest.v1.json`, `IMAGE.txt`, and `webapp/asset_manifest.v1.json` describe the same release handoff before importing assets.

**R-074-008**: WHEN assets are imported, THE SYSTEM SHALL call the existing asset import path with hash verification enabled and report plain-English success or failure.

**R-074-009**: WHEN TowerScout starts, THE SYSTEM SHALL warn that the first GHCR image pull can take several minutes and SHALL keep polling readiness until success, timeout, or a clear failure.

**R-074-010**: WHEN readiness is `setup_required`, `degraded`, `ready`, or `fatal`, THE SYSTEM SHALL explain the state in user-facing language and identify the next safe action.

**R-074-011**: WHEN TLS/provider validation fails because of certificate inspection or network restrictions, THE SYSTEM SHALL point support to the existing TLS CA import flow without asking the user to send provider keys or raw network traces.

**R-074-012**: WHEN GPU options are exposed, THE SYSTEM SHALL keep the default CPU-safe and SHALL not claim GPU support unless workstation-specific NVIDIA Docker validation has passed.

**R-074-013**: IF bootstrap/preflight cannot make a safe decision, THEN THE SYSTEM SHALL stop with a clear support message rather than mutating assets, changing engines, or continuing with a mismatched release.

## Acceptance Criteria

- [x] A top-level `bootstrap.cmd` or equivalent RC1 package entry point is implemented and documented.
- [x] The bootstrap path has a PowerShell implementation with `-Engine docker|podman|auto`, `-Port`, `-Gpu off|auto|on`, `-NoBrowser`, and dry-run/verify-only behavior where useful.
- [x] Docker preflight reports Docker CLI, daemon, Compose, WSL 2 hint, port, disk-space, and image-pull readiness in plain English.
- [x] Podman preflight reports Podman CLI, machine state, Compose provider, port, and disk-space readiness in plain English without requiring Docker Desktop.
- [x] Asset ZIP verification rejects missing checksums, mismatched hashes, mismatched release versions, unsafe ZIP paths, and nested `assets\assets\...` layouts; ZIP extraction uses temporary staging and cleanup so failed manifest/release validation does not leave final asset entries behind.
- [x] Asset import uses the existing validated named-volume importer and `-VerifyHashes`.
- [x] Readiness output maps `setup_required`, `degraded`, `ready`, and `fatal` to clear next actions.
- [x] User-facing docs and Settings-linked HTML are updated only after the implemented behavior exists.
- [x] Focused tests cover engine selection/preflight parsing, checksum comparison, safe ZIP extraction/layout validation, release/version matching, and readiness message mapping.
- [x] Manual validation covers Docker Desktop CPU-default launch. Podman validation is recorded if the host has a working Podman machine and approved Compose provider.

## Dependencies

- `TASK-071`: end-user package documentation and Settings-linked docs.
- `TASK-073`: pilot/UAT checklist and first-launch friction findings.
- `TASK-066`: validated package image/assets/readiness baseline.
- `TASK-075`: GPU launch boundary and CPU-safe default behavior.
- `scripts/launch.ps1`, `scripts/import-assets.ps1`, `scripts/lib/TowerScoutCompose.ps1`, and existing `.cmd` wrappers.

## Non-Goals For RC1 MVP

- Native Windows installer behavior.
- Start menu shortcuts or registered Windows applications.
- Hosted automatic asset download unless release-owner distribution authorization and network behavior are explicitly approved.
- Bundled OCI image archive support.
- Source checkout, Python, Conda, or Node.js environment setup for pilot users.
- Claiming broad Docker-Desktop-free Podman support beyond the validated Podman machine plus Compose-provider path.
- Claiming GPU acceleration before NVIDIA Docker Desktop WSL2 validation, fixed-fixture parity, and timing evidence pass.

## Implementation Plan

1. Inventory current launch/import/status scripts and identify reusable helpers versus new bootstrap-only logic.
2. Define the RC1 bootstrap command surface and keep `start.bat` as a direct supported path.
3. Add a PowerShell preflight implementation with structured result objects and plain-English summaries.
4. Add safe ZIP/checksum/release matching helpers for local release artifacts.
5. Add asset staging validation that rejects unsafe or ambiguous layouts before named-volume import and uses temporary extraction staging before final asset promotion.
6. Wire bootstrap to existing launch/import/status behavior instead of duplicating Compose logic.
7. Add focused unit tests for parser/helpers and lightweight script syntax validation.
8. Update `docs/v1-rc1-quick-start.md`, `docs/v1-rc1-quick-start.html`, `docs/v1-rc1-package-guide.md`, and UAT instructions to describe the new bootstrap flow only after implementation passes.
9. Validate Docker Desktop CPU-default path and record Podman validation boundaries if Podman is available.

---

## Implementation Log

### 2026-05-27 - Task Created From Install-UX Review
**Objective**: Create detailed task documentation for the runtime prerequisite preflight/bootstrap work selected after `TASK-073` documentation hardening.  
**Context**: The RC1 install-UX review recommended a more guided first-launch experience, including a top-level bootstrap entry point, automatic prerequisite checks, checksum verification, asset ZIP handling, clearer engine status, and plain-English recovery messages. The owner agreed with the direction but asked to preserve Podman support language rather than diminishing it.  
**Decision**: Split the work into low-risk documentation hardening now and implementation under `TASK-074` next. Keep Docker Desktop as the primary RC1 pilot path while retaining Podman as a qualified support-directed path with explicit prerequisites and validation boundaries.  
**Execution**: Created this task file with EARS requirements, acceptance criteria, non-goals, and an implementation plan that reuses existing launch/import/status scripts instead of replacing the validated package path.  
**Output**: `TASK-074` is ready for planning/implementation after the current documentation hardening commit.  
**Validation**: Task trackers were synchronized and `.agent_work` validation passed in the documentation hardening PR.  
**Next**: Start implementation planning after the documentation hardening commit is reviewed/merged.

### 2026-05-27 - Bootstrap/Preflight MVP Implemented
**Objective**: Implement the RC1 first-setup bootstrap layer without replacing the validated launch/import path.
**Context**: PR #20 merged the documentation hardening and selected this task. The next implementation step was to automate the common first-launch checks while preserving Docker Desktop as the primary pilot path and Podman as a qualified support-directed path.
**Decision**: Add a top-level `bootstrap.cmd` that delegates to `scripts/bootstrap.ps1`; keep reusable, testable helper functions in `scripts/lib/TowerScoutBootstrap.ps1`; keep `start.bat` as the direct launch path after setup.
**Execution**: Implemented disk, port, Docker, Podman, Compose, WSL hint, checksum sidecar, release handoff, image-pull readiness, asset ZIP safety/layout, manifest matching, and readiness-guidance helpers. Bootstrap can run `-VerifyOnly`, optionally verify `-PackageZip`, stage `-AssetZip`, import staged assets through `scripts/import-assets.ps1 -VerifyHashes`, and then call `scripts/launch.ps1`. Updated `scripts/package-release.ps1` to include the new bootstrap entry point and helper library. Updated `scripts/launch.ps1` readiness output with plain-English next actions.
**Output**: The package now has a guided first-setup path while preserving the existing manual `start.bat` and `scripts/import-assets.cmd` fallback paths.
**Validation**: Focused tests passed with `.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_import_assets_script.py tests\unit\test_release_package_script.py tests\unit\test_flask_routes.py::test_docs_routes_expose_package_local_docs -q -p no:cacheprovider`; PowerShell parser validation passed for bootstrap, launcher, and package scripts; `.agent_work` validation passed; doc-command validation passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed. A local `.\bootstrap.cmd -Engine docker -Gpu off -VerifyOnly -NoBrowser -MinimumFreeGB 1` smoke correctly stopped before mutation because Docker Desktop was not reachable on the host.
**Next**: Run broader focused validation, perform Docker Desktop bootstrap smoke if feasible, and record any Podman boundary evidence if available.

### 2026-05-28 - Docker Desktop Bootstrap Smoke Passed
**Objective**: Validate the Task-074 bootstrap path against a running Docker Desktop engine.
**Context**: Docker Desktop was started after the initial verify-only smoke had correctly stopped on daemon unavailability. The first elevated Docker preflight showed a source-checkout `.env` image of `towerscout:local`, which exposed two implementation issues before release package validation: image-readiness wording assumed GHCR, and `docker image inspect` used full JSON output that could block with redirected stdout.
**Decision**: Keep the image-readiness check but inspect only `{{.Id}}`, and make non-GHCR image wording generic. Fix the final bootstrap handoff to `launch.ps1` by passing explicit named parameters rather than array-splatting script arguments.
**Execution**: Updated `scripts/lib/TowerScoutBootstrap.ps1`, `scripts/bootstrap.ps1`, and Task-074 tests. Reran `.\bootstrap.cmd -Engine docker -Gpu off -VerifyOnly -NoBrowser -MinimumFreeGB 1`; it passed, reported Docker daemon/Compose/WSL checks, and correctly detected the local image. Reran `.\bootstrap.cmd -Engine docker -Gpu off -NoBrowser -TimeoutSeconds 180 -MinimumFreeGB 1`; it passed and reached readiness `ready`.
**Output**: Docker Desktop CPU-default bootstrap path is validated on this host from the source checkout with `towerscout:local`.
**Validation**: Bootstrap launch output reported `Starting TowerScout with docker`, Docker Compose `v5.1.3`, GPU mode `off`, readiness `ready`, asset status `ok`, config status `ok`, and browser launch skipped by request.
**Next**: Rerun focused automated validation and decide whether to move to review/PR.

### 2026-05-28 - Podman Boundary Validation Recorded
**Objective**: Validate the qualified Podman path with Docker Desktop stopped and Podman running.
**Context**: The owner stopped Docker Desktop and started Podman to avoid accidentally validating against the Docker daemon. The host had Podman machine `podman-machine-default` running, `podman compose` available, and the source-checkout `towerscout:local` image present in the Podman image store.
**Decision**: Treat this as qualified Podman boundary evidence, not a broad Podman claim. Keep Docker Desktop as the primary pilot path and keep Podman support-directed with explicit machine/Compose-provider requirements.
**Execution**: Ran `.\bootstrap.cmd -Engine podman -Gpu off -VerifyOnly -NoBrowser -MinimumFreeGB 1`; preflight passed. A default-port launch on `5000` failed because Podman/rootless port forwarding reported `bind: address already in use` even though the Windows port check was free. Hardened preflight to detect stopped/created engine containers that reserve a host port before Compose mutates state. Removed the stale failed validation container and reran on `-Port 5009`; bootstrap launched successfully and reached readiness `ready`.
**Output**: Qualified Podman launch path passed on a non-default port. Default `5000` remains a host-specific Podman/rootless-port caveat on this workstation and should be handled by choosing a non-default `-Port` or clearing the local Podman port state.
**Validation**: `.\scripts\status.cmd -Engine podman -Port 5009` reported container `towerscout-towerscout-1`, image `docker.io/library/towerscout:local`, `0.0.0.0:5009->5000/tcp`, readiness `ready`, assets `ok`, config `ok`, and runtime `container_engine: podman`. The validation container was removed afterward to avoid leaving a stale port mapping.
**Next**: Rerun focused automated validation after the stale-container preflight hardening and prepare the PR for review.

### 2026-05-28 - Reviewer Hardening Applied
**Objective**: Address the Task-074 reviewer findings before PR merge.
**Context**: The reviewer agreed the bootstrap architecture was sound, but recommended fixing direct asset ZIP extraction before merge and tightening Podman Compose-provider and checksum-verification wording.
**Decision**: Implement lightweight staged extraction rather than a native-installer-style rollback system. Keep Docker Desktop as the primary path, keep Podman qualified and support-directed, and do not change the default package port.
**Execution**: Updated `Expand-TowerScoutAssetZip` to extract into `assets\.staging-<guid>`, validate the staged asset manifest/release match before final promotion, move only `model_params`, `data`, and `asset_manifest.v1.json` into final `assets\`, remove temporary staging on success/failure, and remove any promoted entries if final promotion fails. Updated Quick Start Markdown/HTML to clarify that checksum verification happens only for ZIP paths explicitly passed with `-PackageZip` and/or `-AssetZip`. Updated the Package Guide Podman section to clarify that the selected Compose provider must be validated in the target environment, especially when Docker Desktop is uninstalled and `PODMAN_COMPOSE_PROVIDER` is needed to force an approved provider.
**Output**: The reviewer’s required pre-merge hardening is implemented without changing package boundaries, default CPU behavior, or Podman support framing.
**Validation**: Focused Task-074 bootstrap tests passed with `8 passed`; expanded focused validation passed with `14 passed` across Task-074 bootstrap, import-assets script, release-package script, and package-local docs route coverage. PowerShell parser validation passed for bootstrap, helper, launch, and package scripts. `.agent_work` validation passed. Docs command check passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`. `git diff --check` passed.
**Next**: Review final diff and prepare PR update.

---

## Validation Results

### Test Summary
**Test Date**: May 27, 2026
**Test Environment**: Windows local repo; PowerShell helper/unit validation
**Test Status**: IN_PROGRESS

### Acceptance Criteria Validation
- [x] Bootstrap entry point implemented - PASS - `bootstrap.cmd` delegates to `scripts/bootstrap.ps1`.
- [x] Engine-aware preflight implemented - PASS - Docker and Podman checks are implemented with bounded command timeouts and plain-English failures; image-pull readiness is reported after the selected engine passes preflight.
- [x] Safe checksum/ZIP/asset validation implemented - PASS - checksum sidecars, safe ZIP root/layout checks, temporary extraction staging, cleanup on failure, release filename matching, and control/asset manifest matching are covered.
- [x] Existing launch/import paths reused - PASS - bootstrap calls `scripts/import-assets.ps1 -VerifyHashes` and `scripts/launch.ps1`.
- [x] Docs synced after implementation - PASS - Quick Start Markdown/HTML, Package Guide, OCI docs, Project Overview, asset contract, and UAT checklist were updated after the implementation existed.
- [x] Focused automated tests added - PASS - `tests/unit/test_task_074_bootstrap.py`.
- [x] Docker Desktop validation recorded - PASS - `.\bootstrap.cmd -Engine docker -Gpu off -NoBrowser -TimeoutSeconds 180 -MinimumFreeGB 1` reached readiness `ready`.
- [x] Podman validation boundary recorded - PASS_WITH_NOTES - Docker-stopped Podman preflight passed; Podman launch reached readiness `ready` on `-Port 5009`; default `5000` hit a host-specific Podman/rootless bind caveat.

### Issues Identified

- Reviewer identified direct asset ZIP extraction into final `assets\` as a first-launch reliability risk because interrupted extraction or post-extraction validation failure could leave partial final assets behind.
- Reviewer identified minor wording ambiguity around Podman Compose-provider validation and when checksum verification occurs.

### Remediation Actions

- Added temporary asset ZIP extraction staging and cleanup before final asset promotion.
- Tightened Podman Compose-provider documentation without diminishing qualified Podman support.
- Clarified that checksum verification runs only for ZIP paths explicitly passed to bootstrap.

### Sign-off

Not started. Task is selected as the next high-leverage RC1 install-support improvement after documentation hardening.
