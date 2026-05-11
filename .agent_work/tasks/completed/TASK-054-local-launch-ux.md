# TASK-054: Local Launch UX

**Status**: COMPLETED - PHASE 1 MVP
**Priority**: MEDIUM  
**Type**: B (Deployment UX / Local Supportability)  
**Estimated Effort**: 1-2 days (8-12 hours)  
**Target Sprint**: Sprint 05 extension / Sprint 06 carry-forward after `TASK-025`

## Objective

Deliver a launcher-first local startup and support flow over the selected OCI/container runtime baseline so a supported Windows/AMD64 local user can start, stop, inspect status/logs, and open TowerScout without relying on raw container CLI workflows.

`TASK-054` is the local UX layer over the `TASK-025` runtime contract. It must not become container implementation, native installer work, cross-platform packaging, or background-job architecture.

After the `TASK-025` merge, this task should assume the normal user path is a GitHub Release ZIP package that wraps the merged OCI/runtime contract. Podman is the preferred open-source Windows runtime target after release-support gates; `TASK-025` validated the Windows WSL engine path, including while Docker Desktop's engine was unavailable, and `TASK-065` validated `podman-compose 1.5.0` as a Docker-Desktop-free Compose provider. Docker-compatible paths remain useful for developer/support fallback where licensing and endpoint policy allow.

## Requirements (EARS Notation)

**R-054-001**: WHEN a supported Windows local user launches TowerScout from a GitHub Release ZIP package, THE SYSTEM SHALL provide a host-side launcher path beginning with `start.bat` or equivalent release-package script.

**R-054-002**: WHEN the launcher starts TowerScout, THE SYSTEM SHALL wait for application shell readiness before opening the browser.

**R-054-003**: WHEN the selected container engine is running but the application is not ready, THE SYSTEM SHALL distinguish container startup from application readiness.

**R-054-004**: WHEN first-run asset bootstrap is still in progress or has failed, THE SYSTEM SHALL surface actionable status instead of hiding the delay behind a generic startup wait.

**R-054-005**: WHEN users need routine support actions, THE SYSTEM SHALL provide documented or scripted start, stop, logs, and status paths.

**R-054-006**: WHEN startup fails, THE SYSTEM SHALL provide troubleshooting guidance for selected engine not running, Podman machine/WSL2/Hyper-V failures where applicable, Docker Desktop licensing/endpoint issues where applicable, port conflicts, startup timeout, failed first-run asset bootstrap, restricted network behavior, and provider-key failures.

**R-054-007**: WHEN support information is requested, THE PROJECT SHALL document log locations and version/asset manifest collection steps.

**R-054-008**: WHEN unsupported environments are discussed, THE PROJECT SHALL state that Mac, ARM64, offline, air-gapped, shared deployment, and native installer behavior are not v1 support promises.

**R-054-009**: WHEN the launcher polls readiness, THE SYSTEM SHALL consume the `TASK-025` `/api/health` and structured `/api/readiness` contract, including `starting`, `setup_required`, `degraded`, `ready`, and `fatal` states.

## Acceptance Criteria

- [x] `start.bat` or equivalent Windows-first GitHub Release launcher exists.
- [x] Launcher waits for app readiness before opening the browser.
- [x] Stop/logs/status support exists as scripts or clear user-facing guidance.
- [x] First-run asset/bootstrap delay and failure handling is visible to users.
- [x] Troubleshooting docs cover selected engine, Podman machine/WSL2/Hyper-V where applicable, Docker Desktop licensing/endpoint where applicable, port, timeout, network, asset, and provider-key failures.
- [x] Log locations and version/asset manifest collection guidance are documented.
- [x] Unsupported v1 environments are documented without implying support.
- [x] Launcher consumes or documents `/api/health` and structured `/api/readiness` state handling.
- [x] Launcher behavior is validated against the selected runtime-host path from `TASK-025`.

## Dependencies

- `TASK-025`: Docker-compatible / OCI containerization baseline
- `TASK-063`: Pre-Docker release hardening and CI reproducibility gate
- `TASK-065`: Release packaging and runtime support follow-through for final Podman/Docker support language and remaining release-support gates

## Implementation Plan

1. Confirm the merged `TASK-025` scripts, Compose files, `/api/health`, and `/api/readiness` states that the launcher will wrap.
2. Implement Windows-first GitHub Release launcher script and companion stop/logs/status path.
3. Add browser-open behavior only after readiness succeeds.
4. Add first-run asset/bootstrap status and failure guidance.
5. Document routine startup, shutdown, support-log, and troubleshooting flows.
6. Validate clean first launch, repeat launch, startup timeout, and selected-engine-not-running behavior.
7. Coordinate with `TASK-065` so broad Podman support language names the validated Podman machine and Compose-provider prerequisites.

---

## Implementation Log

### 2026-04-28 - Task File Creation
**Objective**: Create task-specific documentation for the local launcher/support UX layer.  
**Context**: `TASK-054` existed in `current-tasks.md` as a post-Docker stretch task but did not have an individual active task file. The latest review emphasized support diagnostics and operational clarity as v1 success criteria.  
**Decision**: Keep `TASK-054` as the post-Docker local UX/support layer, with explicit boundaries against installer and architecture work.  
**Execution**: Created this task file with EARS requirements, acceptance criteria, dependencies, and implementation plan.  
**Output**: `TASK-054` now has task-specific active documentation.  
**Validation**: Pending `.agent_work` structure validation.  
**Next**: Start only after the selected container runtime baseline is stable enough to target.

### 2026-05-04 - Open-Source Release Package Direction Update
**Objective**: Align launcher scope with the newer GitHub-first, Podman-as-open-source-candidate deployment direction.
**Context**: Client feedback asked for an open-source-friendly path for sites to deploy from GitHub to laptops with clear folder and asset instructions. `TASK-025` now treats GitHub Releases as the normal user-facing release control plane and Podman as the preferred open-source runtime target pending validation.
**Decision**: Keep `TASK-054` as the UX/support layer over the selected runtime contract rather than a Docker-only launcher. The launcher should wrap the GitHub Release ZIP package path and report engine-specific failures without absorbing container implementation.
**Execution**: Updated objective, requirements, acceptance criteria, dependencies, and implementation plan to refer to the selected container engine, GitHub Release package scripts, Podman machine/WSL2/Hyper-V failure handling, and Docker Desktop licensing/endpoint caveats where applicable.
**Output**: `TASK-054` now matches the updated deployment strategy while preserving its boundary from `TASK-025`.
**Validation**: Documentation update only; implementation validation remains pending.
**Next**: Start only after `TASK-025` chooses and validates the runtime-host path that the launcher will wrap.

### 2026-05-05 - Finalized TASK-025 Decision Lock Intake
**Objective**: Align launcher assumptions with the finalized pre-`TASK-025` containerization decisions.
**Context**: The selected package direction is now a GitHub Release ZIP with a pinned GHCR image digest, optional OCI archive fallback, Podman-first target after validation, Docker-compatible fallback, manifest-managed assets, and structured readiness.
**Decision**: Keep `TASK-054` as the runtime UX wrapper. It should consume the structured `/api/health` and `/api/readiness` states from `TASK-025` rather than inventing separate readiness semantics.
**Execution**: Updated objective text, requirements, and acceptance criteria to reference the finalized package/runtime direction and readiness state contract.
**Output**: `TASK-054` now matches the locked `TASK-025` starting contract.
**Validation**: Documentation update only; implementation validation remains pending.
**Next**: Start only after `TASK-025` produces the selected runtime start command and readiness contract.

### 2026-05-07 - Post-TASK-025 Merge Reconciliation
**Objective**: Reconcile `TASK-054` with the merged `TASK-025` baseline without starting launcher implementation.
**Context**: PR #7 merged `TASK-025` into `main`, making the Docker-compatible / OCI runtime baseline available for the launcher task. Podman engine behavior passed on this host, including with Docker Desktop's engine unavailable; `TASK-065` later validated `podman-compose 1.5.0` as the Docker-Desktop-free Compose provider.
**Decision**: Mark this task ready for Phase 1 planning while keeping implementation unstarted. Keep the launcher scope pointed at the merged `TASK-025` scripts, Compose files, and readiness contract, and keep final Podman support language gated by `TASK-065`.
**Execution**: Updated task status, target sprint, objective context, dependencies, and implementation-plan wording.
**Output**: `TASK-054` is aligned to the post-merge runtime baseline and ready for a separate Phase 1 planning/implementation start.
**Validation**:
- `git diff --check -- .agent_work\design.md .agent_work\requirements.md .agent_work\current-tasks.md .agent_work\task-backlog.md .agent_work\tasks\active\TASK-054-local-launch-ux.md .github\copilot-instructions.md .github\instructions\github-repo-management.instructions.md` -> passed.
- `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` -> passed.
**Next**: Begin Phase 1 only after explicit go-ahead.

### 2026-05-07 - Phase 1 Launcher MVP Start
**Objective**: Start the Phase 1 launcher MVP and reconcile the remaining tracker cleanup before implementation.
**Context**: The owner approved starting `TASK-054` after the readiness check. `TASK-025` is merged, `TASK-052` is complete, the branch is already `feature/task-054-local-launch-ux`, and `.agent_work` validation passed. Two stale bookkeeping items remained: the `TASK-025` task-file status still referenced an open PR, and `current-tasks.md` still showed `TASK-052` with a pending marker in the `TASK-054` dependency list.
**Decision**: Keep the launcher MVP narrow: add a Windows-first host launcher over the existing Compose scripts and readiness contract, without changing container runtime behavior or broad Podman support claims.
**Execution**: Updated task status to `IN_PROGRESS - PHASE 1 LAUNCHER MVP`, corrected the stale `TASK-025` header, and updated the active tracker dependency marker for `TASK-052`.
**Output**: Phase 1 implementation is authorized and task tracking now reflects the current prerequisite state.
**Validation**: Pending focused script, documentation, and `.agent_work` validation after implementation.
**Next**: Implement the Windows launcher MVP and update release-package documentation.

### 2026-05-07 - Phase 1 Launcher MVP Implementation And Validation
**Objective**: Implement and validate the Windows-first launcher MVP.
**Context**: `TASK-025` already provided low-level `scripts/start.cmd`, `scripts/status.cmd`, `scripts/logs.cmd`, and `scripts/stop.cmd` helpers. `TASK-054` needed the user-facing host launcher layer that waits for application readiness and opens the browser only after the app shell is reachable.
**Decision**: Add a top-level `start.bat` that delegates to `scripts/launch.ps1`. Keep `scripts/start.cmd` as the low-level Compose command for support and automation. The launcher should create `.env` from `.env.example` when missing, set the selected engine and port for Compose, start the service, poll `/api/readiness`, print actionable readiness state, and skip browser launch when `-NoBrowser` is supplied.
**Execution**:
- Added `start.bat`.
- Added `scripts/launch.ps1` with `-Engine`, `-Port`, `-TimeoutSeconds`, `-Build`, and `-NoBrowser` options.
- Updated `scripts/package-release.ps1` so release packages include `start.bat` and `scripts/launch.ps1`.
- Updated `docs/oci-quick-start.md` with first-run launcher flow, support diagnostics, troubleshooting, and no-browser/timeout/port options.
- Updated `docs/oci-runtime-contract.md` to include the top-level launcher in the release package contract.
**Output**: Phase 1 now has a Windows-first launcher MVP over the existing OCI/Compose runtime contract.
**Validation**:
- PowerShell parser check passed for `scripts/launch.ps1`, `scripts/start.ps1`, `scripts/status.ps1`, `scripts/package-release.ps1`, and `scripts/lib/TowerScoutCompose.ps1`.
- `git diff --check` passed.
- `.\start.bat -NoBrowser -TimeoutSeconds 60` passed against the Docker runtime path after running with local engine access: readiness state `ready`, asset status `ok`, config status `ok`, and browser launch skipped.
- `.\scripts\package-release.cmd -Version task054-check2 -OutputDir .agent_work\pytest-temp\task054-package -NoZip` passed and staged `start.bat`, `scripts\launch.ps1`, and `SHA256SUMS.txt`.
- `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed.
**Next**: Keep broader Podman release-support language gated by `TASK-065`; use this Phase 1 MVP as the launcher baseline for any Phase 2 readiness UX follow-up.

### 2026-05-07 - Phase 1 UX And Failure-Path Closeout
**Objective**: Confirm the launcher MVP is understandable on the happy path and fails visibly on lightweight failure paths.
**Context**: The owner ran `.\start.bat` from the repo root. The launcher opened TowerScout in the browser, and the console messaging matched the intended healthy path. Additional failure-path checks were needed before marking Phase 1 complete.
**Decision**: Close Phase 1 as complete and defer additional readiness orchestration/polish to a later Phase 2 only if release-support work shows the MVP is insufficient.
**Execution**:
- Confirmed user-facing happy-path messaging looked good to the owner.
- Ran invalid engine selection through `.\start.bat -Engine invalid -NoBrowser`.
- Ran invalid timeout input through `.\start.bat -NoBrowser -TimeoutSeconds 1`.
- Ran unreachable-readiness support path through `.\scripts\status.cmd -Port 59999`.
**Output**: Phase 1 happy path and lightweight failure paths are validated. The launcher does not silently open the browser on these failure paths.
**Validation**:
- Invalid engine returned PowerShell `ValidateSet` guidance listing `auto,docker,podman`.
- Invalid timeout returned `TimeoutSeconds must be at least 5.`
- `.\scripts\status.cmd -Port 59999` returned Compose status plus `TowerScout readiness endpoint is not reachable at http://127.0.0.1:59999/api/readiness.`
**Next**: Commit the Phase 1 slice and move release-support follow-through to `TASK-065`.

### 2026-05-07 - Windows Host Diagnostics Follow-Up
**Objective**: Add WSL/virtualization diagnostics to startup failure output without making WSL a hard preflight gate.
**Context**: The owner asked whether the launcher should check for WSL because Docker and Podman commonly require WSL2 or a comparable virtualization backend on Windows. A hard WSL preflight could produce false negatives for Hyper-V, future remote-engine paths, or already-managed engine behavior.
**Decision**: Keep Docker/Podman as the runtime source of truth, and print Windows-only diagnostics only after Compose startup fails.
**Execution**:
- Added `Write-TowerScoutHostDiagnostics` to `scripts/launch.ps1`.
- The launcher now checks for `wsl.exe`, prints `wsl --status` when available, prints `podman machine list` for Podman failures, and mentions Docker Desktop WSL2/Hyper-V backend health for Docker failures.
- Updated `docs/oci-quick-start.md` to describe the diagnostic behavior as support hints rather than a support promise.
**Output**: Startup failures now include better Windows host context for WSL2/Hyper-V/virtualization and Podman machine issues.
**Validation**:
- PowerShell parser check passed for `scripts/launch.ps1`.
- `git diff --check` passed.
- Intentional invalid-image startup check printed Windows diagnostics: `wsl.exe` location, readable `wsl --status` output showing default WSL version `2`, Docker Desktop backend guidance, and local IT virtualization/endpoint/Compose-provider guidance.
**Next**: Commit the Phase 1 slice.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-07
**Test Environment**: Windows PowerShell, Docker Compose runtime on `http://127.0.0.1:5000`
**Test Status**: PASS for Phase 1 MVP

### Acceptance Criteria Validation
- [x] **Windows launcher**: `start.bat` delegates to `scripts/launch.ps1`.
- [x] **Readiness before browser**: launcher polls `/api/readiness` and opens the browser only after `setup_required`, `degraded`, or `ready`.
- [x] **Support commands**: existing start/stop/logs/status scripts remain available and documented.
- [x] **First-run status**: launcher prints readiness state, asset status, config status, and recovery guidance.
- [x] **Troubleshooting**: quick-start docs cover engine, Podman machine/WSL2/Hyper-V, Docker Desktop policy/licensing, port, timeout, network, asset, and provider-key failures.
- [x] **Diagnostics**: quick-start docs identify status/log commands, `IMAGE.txt`, `asset_manifest.v1.json`, `SHA256SUMS.txt`, log volume/path, and sensitive artifacts not to share.
- [x] **Unsupported environments**: v1 exclusions remain documented.
- [x] **Readiness contract**: launcher consumes `/api/readiness`; runtime docs cover `/api/health` and `/api/readiness`.
- [x] **Runtime validation**: no-browser launcher run passed against the Docker runtime path.
- [x] **Human UX pass**: owner confirmed the normal launcher command opened the app and the console messaging looked good.
- [x] **Failure-path validation**: invalid engine, invalid timeout, and unreachable-readiness support checks fail visibly with actionable output.
- [x] **Windows host diagnostics**: launcher startup failure path includes WSL/virtualization and Podman machine diagnostics as support hints.

### Issues Identified

- Launcher validation used Docker on this host. `TASK-065` now owns remaining release-support language and regression gates after validating the Docker-Desktop-free Podman Compose-provider path.
- Phase 2 readiness UX is cleanly deferred. The MVP already consumes structured readiness and opens the browser after shell availability; further polish should be driven by release-support findings rather than added speculatively.
