# TASK-074: Runtime Prerequisite Preflight

**Status**: NOT_STARTED - selected as next implementation candidate after `TASK-073` documentation hardening  
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

**R-074-006**: WHEN a Model & Data Package ZIP is provided, THE SYSTEM SHALL reject unsafe ZIP entries, reject ambiguous nested asset layouts, and stage only the expected `model_params/`, `data/`, and `asset_manifest.v1.json` entries.

**R-074-007**: WHEN release metadata is available, THE SYSTEM SHALL verify that the Application Package, Model & Data Package, `release-manifest.v1.json`, `IMAGE.txt`, and `webapp/asset_manifest.v1.json` describe the same release handoff before importing assets.

**R-074-008**: WHEN assets are imported, THE SYSTEM SHALL call the existing asset import path with hash verification enabled and report plain-English success or failure.

**R-074-009**: WHEN TowerScout starts, THE SYSTEM SHALL warn that the first GHCR image pull can take several minutes and SHALL keep polling readiness until success, timeout, or a clear failure.

**R-074-010**: WHEN readiness is `setup_required`, `degraded`, `ready`, or `fatal`, THE SYSTEM SHALL explain the state in user-facing language and identify the next safe action.

**R-074-011**: WHEN TLS/provider validation fails because of certificate inspection or network restrictions, THE SYSTEM SHALL point support to the existing TLS CA import flow without asking the user to send provider keys or raw network traces.

**R-074-012**: WHEN GPU options are exposed, THE SYSTEM SHALL keep the default CPU-safe and SHALL not claim GPU support unless workstation-specific NVIDIA Docker validation has passed.

**R-074-013**: IF bootstrap/preflight cannot make a safe decision, THEN THE SYSTEM SHALL stop with a clear support message rather than mutating assets, changing engines, or continuing with a mismatched release.

## Acceptance Criteria

- [ ] A top-level `bootstrap.cmd` or equivalent RC1 package entry point is implemented and documented.
- [ ] The bootstrap path has a PowerShell implementation with `-Engine docker|podman|auto`, `-Port`, `-Gpu off|auto|on`, `-NoBrowser`, and dry-run/verify-only behavior where useful.
- [ ] Docker preflight reports Docker CLI, daemon, Compose, WSL 2 hint, port, disk-space, and image-pull readiness in plain English.
- [ ] Podman preflight reports Podman CLI, machine state, Compose provider, port, and disk-space readiness in plain English without requiring Docker Desktop.
- [ ] Asset ZIP verification rejects missing checksums, mismatched hashes, mismatched release versions, unsafe ZIP paths, and nested `assets\assets\...` layouts.
- [ ] Asset import uses the existing validated named-volume importer and `-VerifyHashes`.
- [ ] Readiness output maps `setup_required`, `degraded`, `ready`, and `fatal` to clear next actions.
- [ ] User-facing docs and Settings-linked HTML are updated only after the implemented behavior exists.
- [ ] Focused tests cover engine selection/preflight parsing, checksum comparison, safe ZIP extraction/layout validation, release/version matching, and readiness message mapping.
- [ ] Manual validation covers Docker Desktop CPU-default launch. Podman validation is recorded if the host has a working Podman machine and approved Compose provider.

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
5. Add asset staging validation that rejects unsafe or ambiguous layouts before named-volume import.
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

---

## Validation Results

### Test Summary
**Test Date**: Pending  
**Test Environment**: Pending implementation  
**Test Status**: NOT_STARTED

### Acceptance Criteria Validation
- [ ] Bootstrap entry point implemented - PENDING.
- [ ] Engine-aware preflight implemented - PENDING.
- [ ] Safe checksum/ZIP/asset validation implemented - PENDING.
- [ ] Existing launch/import paths reused - PENDING.
- [ ] Docs synced after implementation - PENDING.
- [ ] Focused automated tests added - PENDING.
- [ ] Docker Desktop validation recorded - PENDING.
- [ ] Podman validation boundary recorded - PENDING.

### Issues Identified

- No implementation issues yet.

### Remediation Actions

- None yet.

### Sign-off

Not started. Task is selected as the next high-leverage RC1 install-support improvement after documentation hardening.
