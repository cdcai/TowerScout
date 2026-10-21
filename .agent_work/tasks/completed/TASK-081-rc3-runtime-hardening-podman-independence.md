# TASK-081: RC3 Runtime Hardening And Podman Independence

**Status**: COMPLETED - runtime hardening and CPU validation completed; live GPU evidence continued through TASK-083 and package delivery through TASK-084
**Priority**: HIGH  
**Type**: C (Runtime Hardening / Podman Support / Release Validation)  
**Estimated Effort**: 2-4 days (16-32 hours), split between CPU-dev-able fixes and hardware-dependent GPU validation  
**Target Sprint**: Sprint 06 V1 RC1 / post-rc3 hardening  

## Objective

Implement the actionable recommendations from the June 11, 2026 RC3
GPU/Podman analysis and reviewer audit while preserving the validated
CPU-default UAT package path.

This task deliberately separates runtime hardening from `TASK-075` GPU package
implementation and `TASK-080` UAT guide work. The work crosses launcher
behavior, Compose/runtime defaults, Podman independence, CI coverage, docs, and
small release-safety fixes, so it needs one owner task with explicit support
boundaries.

## Background

The empirical replay document supersedes the earlier static GPU issue analysis.
On the controlled 25-tile fixture, Docker GPU, Docker CPU, and Podman CPU
produced matching detection outputs. That result makes a model/precision change,
including a TF32-focused fix, the wrong release response for the reported T1000
concern unless later evidence proves a new failure mode.

The remaining recommendations are operational and supportability issues:

- default image references can fall back to a bare `latest` tag outside the
  pinned release-package path
- engine auto-selection currently depends too much on executable presence rather
  than daemon liveness
- Podman asset import needs a direct copy fallback when the Compose provider
  cannot perform `cp`
- launcher/import flows can accidentally preserve an existing container with a
  different CPU/GPU mode
- Podman CPU independence needs an explicit Compose-provider strategy instead
  of accidental delegation to Docker tooling
- Podman GPU remains plausible, but only after WSL2/CDI/preflight and hardware
  evidence
- reviewer-audit items identify low-risk release hardening around uploads,
  debug routes, and pilot-scale detection limits

## Requirements (EARS Notation)

**R-081-001**: WHEN a user starts TowerScout from the release package or source
checkout, THE SYSTEM SHALL use an explicit image flavor or pinned package image
reference instead of falling through to an ambiguous bare `latest` tag.

**R-081-002**: WHEN Compose service restart policy is evaluated for the package
path, THE SYSTEM SHALL use a release-supportable restart behavior that survives
normal host/runtime restarts unless explicitly stopped by support scripts.

**R-081-003**: WHEN runtime engine auto-selection is requested, THE SYSTEM SHALL
prefer a detected healthy/livable engine over an installed but unavailable
engine and SHALL report the selected engine and reason.

**R-081-004**: WHEN Podman asset import cannot use the selected Compose
provider's copy command, THE SYSTEM SHALL fall back to direct `podman cp`
without requiring Docker Desktop.

**R-081-005**: WHEN GPU mode changes between launches or import/setup
operations, THE SYSTEM SHALL detect stale container/device mismatch and SHALL
recreate or stop with clear guidance rather than silently reusing the wrong
device mode.

**R-081-006**: WHEN `-Gpu on` launch completes, THE SYSTEM SHALL verify
readiness reports a CUDA selected device or SHALL fail closed with support-safe
diagnostics.

**R-081-007**: WHEN support output, status output, or readiness output reports
runtime state, THE SYSTEM SHALL identify the engine, Compose provider, image
reference/flavor, GPU mode, and selected ML device without exposing secrets.

**R-081-008**: WHEN users upload image or model files, THE SYSTEM SHALL persist
them with sanitized filenames and SHALL prevent path traversal or unsafe name
reuse.

**R-081-009**: WHEN non-production debug routes are present, THE SYSTEM SHALL
remove or gate them before external UAT unless they are explicitly required and
support-safe.

**R-081-010**: WHEN pilot/UAT detection area size exceeds the configured pilot
tile cap, THE SYSTEM SHALL stop before a large detection run and SHALL return a
clear user-facing message.

**R-081-011**: WHERE Podman CPU support is productized, THE SYSTEM SHALL define
the approved Compose-provider strategy, version reporting, installation
expectations, and CI/test evidence separately from Docker Desktop validation.

**R-081-012**: WHERE Podman GPU support is implemented, THE SYSTEM SHALL gate it
behind WSL2/CDI/preflight checks and SHALL not document it as supported until
fixed-fixture parity, timing, and hardware evidence pass.

## Acceptance Criteria

- [x] No task implementation treats TF32 or model precision changes as the RC3
      T1000 fix unless new empirical evidence is added to this task.
- [x] Runtime image defaults avoid bare `latest` in package and source-adjacent
      defaults, with docs updated for the selected CPU/CUDA flavor strategy.
- [x] Compose restart policy is updated and covered by focused tests or package
      inspection.
- [x] Engine auto-selection probes daemon liveness and reports why Docker or
      Podman was selected.
- [x] Podman asset import has a direct `podman cp` fallback based on the
      existing TLS helper pattern.
- [x] Launcher/import flows preserve or recreate containers based on engine,
      port, project, image, and GPU mode rather than health alone.
- [x] `-Gpu on` readiness validation fails closed if `ml_runtime.selected_device`
      is not CUDA.
- [x] Support/status output includes active engine, Compose provider, image
      reference or flavor, GPU mode, and selected device in safe form.
- [x] Upload filename sanitization is implemented and covered by route/unit
      tests.
- [x] The debug Azure route is removed or explicitly gated with tests proving it
      is not exposed in the external UAT path.
- [x] A pilot tile cap is configurable, documented, and tested.
- [x] Podman CPU independence docs distinguish package-runtime support,
      Compose-provider requirements, and source-build/TLS caveats.
- [x] Podman GPU docs remain "not validated / support-assigned only" until
      hardware evidence is captured.
- [ ] `.agent_work` validation passes after task and implementation updates.

## Dependencies

- `TASK-066`: release-candidate validation evidence and package/runtime support
  caveats.
- `TASK-073`: UAT execution plan and support-safe evidence boundaries.
- `TASK-074`: bootstrap/preflight, engine reporting, and package setup behavior.
- `TASK-075`: GPU launch overlay, readiness diagnostics, and GPU support claim
  boundaries.
- `TASK-080`: first-cohort UAT guide and rc3 package publication context.
- Owner-provided RC3 review documents dated 2026-06-11:
  - `rc3-gpu-and-podman-issue-analysis-2026-06-11.md`
  - `rc3-gpu-and-podman-issue-analysis-2026-06-11-v2-empirical.md`
  - `rc3-podman-independence-gpu-roadmap-2026-06-11.md`
  - `rc3-podman-independence-gpu-roadmap-2026-06-11-v2.md`
  - `rc3-reviewer-audit-2026-06-11.md`

## Implementation Plan

1. **Phase 0 - Scope Lock And Baseline Checks**
   - Record that the empirical replay controls the GPU issue interpretation.
   - Inventory current defaults in `compose.yaml`, `.env.example`, launcher,
     import, docs, and release-package generation.
   - Decide whether the immediate default should be `latest-cpu`, a CPU digest,
     or package-only digest injection.

2. **Phase 1 - Pre-UAT Runtime Fixes**
   - Replace ambiguous image defaults and update docs.
   - Adjust restart policy and package inspection tests.
   - Change engine auto-selection to liveness-based detection.
   - Add Podman direct-copy fallback to asset import.

3. **Phase 2 - Launcher And Device Integrity**
   - Add mode-mismatch detection for stale containers.
   - Preserve GPU state through setup/import flows.
   - Validate `-Gpu on` against readiness `ml_runtime.selected_device`.
   - Improve support-safe runtime/device summaries.

4. **Phase 3 - Reviewer-Audit Quick Fixes**
   - Sanitize uploaded filenames.
   - Remove or gate the debug Azure route.
   - Add a configurable pilot tile cap and route tests.

5. **Phase 4 - Podman CPU Productization**
   - Define the Compose-provider approach.
   - Add version/provider reporting and tests.
   - Update Podman package docs and support boundaries.
   - Add CI or local validation hooks that do not depend on Docker Desktop.

6. **Phase 5 - Podman GPU Gated Track**
   - Add Podman GPU preflight only behind explicit support-assigned flags.
   - Validate CDI/WSL2 behavior on suitable hardware before changing support
     language.
   - Capture parity/timing evidence in task-local support docs if validation
     becomes available.

7. **Phase 6 - Documentation And Handoff**
   - Update package guide, quick start, runtime contract, and UAT support notes.
   - Run focused tests and `.agent_work` validation.
   - Record remaining support boundaries before external tester handoff.

## Validation Strategy

- `python .agent_work/scripts/validate_agent_work.py`
- Focused unit tests for release package/image defaults, launcher engine/device
  decisions, import-assets behavior, and route hardening.
- Focused PowerShell parser and helper tests for changed launcher/import
  scripts.
- Package/docs command checks when package-facing docs change.
- Docker CPU package smoke when local runtime is available.
- Podman CPU package smoke when a running Podman machine and approved Compose
  provider are available.
- GPU validation only on suitable NVIDIA Docker/Podman GPU hosts; record
  hardware, engine, provider, readiness `ml_runtime`, timing, and fixed-fixture
  output parity.

## Non-Goals

- Do not claim Podman GPU support before hardware validation passes.
- Do not make broad model, TF32, or precision changes as a substitute for
  launcher/runtime fixes.
- Do not redesign the frontend or split the monolith unless a listed acceptance
  criterion requires a localized route change.
- Do not implement offline RPM bundles, Quadlet/kiosk deployment, native
  Windows installer behavior, or Apache-only runtime migration in this task.
- Do not expand external UAT scope without owner approval.

## Risks And Open Questions

- Vendoring or blessing a standalone Compose provider creates update,
  checksum, and CVE-response obligations.
- CPU/CUDA image tag strategy needs to avoid breaking the validated digest
  package path while still making source-adjacent defaults safe.
- Podman GPU behavior depends on WSL2, NVIDIA driver, Podman machine version,
  CDI device exposure, and Compose provider support.
- CI can cover parsing and decision logic, but meaningful Podman/GPU support
  claims require host evidence.
- Changing stale-container behavior must preserve named volumes by default so
  setup, imported assets, and support logs are not lost.

## Evidence Handling

Keep raw logs, screenshots, provider responses, `.env` files, private AOIs, and
unredacted browser/network traces out of project-wide status/context files.
Place task-local proof notes or sanitized summaries under this task's support
area if needed, and redact provider keys, map URLs, tile URLs, private
coordinates, and user-identifying paths.

---

## Implementation Log

### 2026-07-02 - Sprint 6 Closeout
**Objective**: Close Task-081 as the RC3 runtime-hardening baseline.
**Context**: Task-081 delivered runtime defaults, launcher/import hardening, route safety fixes, live Podman CPU validation, and live Docker Desktop CPU validation. Its remaining GPU validation gate was later handled by `TASK-083`, while package delivery was carried by `TASK-084`.
**Decision**: Mark Task-081 complete at Sprint 6 closeout and preserve later GPU/package evidence in the owning follow-on tasks.
**Execution**: Updated task status and moved this task file to `.agent_work/tasks/completed/`.
**Validation**: Closeout is documentation-only. Original automated, Podman CPU, and Docker Desktop CPU validation evidence remains below.
**Next**: Keep future runtime hardening under new tasks or `TASK-087` where it directly affects host-side TLS repair.

### 2026-06-12 - Task Documentation Created
**Objective**: Create active task documentation for the RC3 runtime hardening and Podman independence implementation plan.  
**Context**: The owner asked for `TASK-081` documentation after reviewing the June 11 RC3 GPU/Podman analysis packet and reviewer audit. The recommendations cut across runtime defaults, launcher behavior, Podman support, GPU validation, CI, docs, and small release hardening items.  
**Decision**: Create a new active Type C task rather than fold the work into `TASK-075` or `TASK-080`. `TASK-075` remains the single GPU-capable package implementation, and `TASK-080` remains the UAT guide/process task.  
**Execution**: Added `TASK-081` to `.agent_work/current-tasks.md` and created this detailed task file with EARS requirements, acceptance criteria, phased implementation plan, validation strategy, non-goals, risks, and evidence handling rules.  
**Output**: `TASK-081` is ready for implementation planning and owner review.  
**Validation**: `python .agent_work/scripts/validate_agent_work.py` passed.  
**Next**: Start Phase 0 baseline checks when implementation is approved.

### 2026-06-12 - Runtime Hardening Implementation Slice
**Objective**: Implement the CPU-safe RC3 hardening items that can be validated without live GPU hardware.  
**Context**: The task requirements prioritized unambiguous image defaults, restart behavior, liveness-based engine selection, Podman asset import fallback, stale CPU/GPU mode detection, `-Gpu on` readiness verification, upload/debug-route safety, and a pilot tile cap.  
**Decision**: Keep Podman GPU as a gated validation track and avoid model/precision changes. Implement the low-risk runtime and route safety fixes with focused tests before attempting live Docker/Podman smoke validation.  
**Execution**: Updated `compose.yaml`, `.env.example`, `scripts/package-release.ps1`, `scripts/lib/TowerScoutCompose.ps1`, `scripts/import-assets.ps1`, `scripts/launch.ps1`, `webapp/towerscout.py`, `webapp/ts_validation.py`, package/runtime docs, and focused Task-081 tests.  
**Output**: Runtime defaults now use `latest-cpu` instead of bare `latest`; Compose restart policy is `always`; engine auto-selection probes liveness; Podman asset import can fall back to direct `podman cp`; stale containers are restarted when GPU mode or ML device policy mismatches the requested launch; `-Gpu on` fails unless readiness reports CUDA; upload filenames are sanitized; `/debug-azure-maps` is disabled by default; UAT defaults include a `100` tile cap.  
**Validation**: Focused and broader automated validation passed: Task-081 runtime/route tests, import-assets, Task-074/075 launcher tests, route/runtime/package/config/error-sanitization tests, PowerShell parser checks, docs command scan, `.agent_work` validation, agent-work quick check, `py_compile`, and `git diff --check`. Full-tree secret scan surfaced pre-existing sensitive-term findings and an output-encoding crash, but a direct diff scan found no new secret-like additions in this change set.  
**Next**: Perform live Docker/Podman package smoke validation if runtime access is available; keep Podman GPU support unclaimed until hardware evidence exists.

### 2026-06-12 - Draft PR And Live Podman Validation
**Objective**: Publish Task-081 as a focused review branch/PR and run the available live runtime validation.
**Context**: The owner requested a focused branch/PR and live validation before pointing a reviewer at the implementation. Docker Desktop, Podman, asset import, and GPU were the requested review/validation surfaces.
**Decision**: Open the PR first with the automated validation and reviewer focus areas, then record live host evidence as a follow-up commit. Treat Docker Desktop/GPU as blocked if the host cannot expose those runtimes, while still validating Podman CPU behavior.
**Execution**: Created branch `feature/task-081-rc3-runtime-hardening`, committed `feat(task-081): harden runtime launch paths`, pushed to `origin`, and opened draft PR `#31`. Started the local Podman machine, ran Podman launch, fixed live-smoke defects in Compose stderr handling and strict-safe readiness summary output, ran Podman launch again, ran Podman asset import from `webapp/` with hash verification, collected status/logs, and stopped the validation container.
**Output**: Podman CPU package-runtime launch passed on port `5006`; readiness reached `state=ready`, `asset_status=ok`, `config_status=ok`, writable persistence paths were reported, and final runtime metadata reported `container_engine=podman`. Podman asset import with `-Source webapp -VerifyHashes` passed with `post_import_health=ok`, `state=ready`, `asset_status=ok`, `verify_hashes=True`, no missing assets, and no corrupt assets. Docker Desktop validation is blocked on this host because the `desktop-linux` context cannot connect to `npipe:////./pipe/dockerDesktopLinuxEngine`; GPU validation is blocked because `nvidia-smi` is unavailable and Docker GPU runtime is not reachable.
**Validation**: Focused Task-081 runtime tests and Task-075 launcher GPU tests passed after the live-smoke fixes. PowerShell parser checks for changed launcher/helper scripts passed.
**Next**: Push the validation/fix follow-up commit to PR `#31`; request reviewer attention on the areas listed in the PR body, especially the live-smoke fixes and Docker/GPU host blockers.

### 2026-06-12 - Live Docker Desktop CPU Validation
**Objective**: Complete the Docker Desktop CPU-default runtime validation after the host runtime became reachable.
**Context**: Earlier Docker Desktop validation was blocked because the `desktop-linux` context could not connect to the Docker Desktop Linux engine socket. After host restart/recovery, Docker Desktop reported server version `29.5.3` and Compose version `v5.1.4`. A stale rc2 CUDA container was still running on port `5015`.
**Decision**: Stop only the stale rc2 container by name, preserving named volumes, then run the Task-081 Docker CPU launch/import/status path on port `5005`.
**Execution**: Stopped `towerscout-google-firstlaunch-towerscout-1`, ran `.\start.bat -Engine docker -Port 5005 -Gpu off -NoBrowser -TimeoutSeconds 180`, ran `.\scripts\import-assets.cmd -Engine docker -Source webapp -Port 5005 -VerifyHashes -RestartWaitSeconds 120`, collected Docker status and bounded logs, and stopped the validation container.
**Output**: Docker Desktop CPU launch passed. Readiness reached `state=ready`; asset and config status were `ok`; runtime metadata reported `container_engine=docker`, `device_policy=cpu`, `selected_device=cpu`, and `pytorch_flavor=cpu`; persistence paths were writable. Asset import passed with `post_import_health=ok`, `state=ready`, `asset_status=ok`, `verify_hashes=True`, no missing assets, and no corrupt assets.
**Validation**: Docker status reported `towerscout-towerscout-1` healthy on port `5005`; bounded logs showed normal startup, configured Google/Azure keys, CPU runtime, lazy classifier initialization, persistent secret loading, and Waitress startup. `scripts\stop.cmd -Engine docker -Port 5005` stopped the validation container after the smoke.
**Next**: Keep GPU validation pending until a suitable NVIDIA Docker Desktop or Podman GPU runtime is visible; update PR evidence with the Docker Desktop CPU pass.

---

## Validation Results

### Initial Documentation Validation
**Test Date**: 2026-06-12  
**Test Environment**: Local TowerScout workspace on Windows  
**Test Status**: SUPERSEDED BY IMPLEMENTATION VALIDATION  

### Acceptance Criteria Validation

- [x] **Task tracker synchronization**: `current-tasks.md` includes `TASK-081`
      and points to this active task file.
- [x] **Agent-work structure validation**: `python .agent_work/scripts/validate_agent_work.py`
      passes after the task file is created.
- [x] **Implementation criteria**: CPU-safe implementation slice completed with
      focused automated validation.
- [x] **Podman CPU runtime validation**: live Podman package-runtime launch and
      asset import passed on the local Windows/WSL2 host.
- [x] **Docker Desktop runtime validation**: live Docker Desktop CPU launch,
      asset import, readiness/status, bounded logs, and cleanup passed on port
      `5005`.
- [ ] **GPU runtime validation**: blocked on this host because NVIDIA runtime
      evidence is unavailable.

### Implementation Slice Validation
**Test Date**: 2026-06-12  
**Test Environment**: Local TowerScout workspace on Windows  
**Test Status**: PASS FOR AUTOMATED VALIDATION; PODMAN CPU LIVE VALIDATION PASS; DOCKER DESKTOP CPU LIVE VALIDATION PASS; GPU BLOCKED BY HOST

### Test Results

- [x] `python -m py_compile webapp\towerscout.py webapp\ts_validation.py` - PASS with system Python.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_081_route_hardening.py tests\unit\test_import_assets_script.py tests\unit\test_task_074_bootstrap.py tests\unit\test_task_075_launcher_gpu.py -q -p no:cacheprovider` - PASS, 29 tests.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py tests\unit\test_release_package_script.py tests\unit\test_container_publish_workflow.py tests\unit\test_config.py tests\unit\test_error_sanitization.py -q -p no:cacheprovider` - PASS, 61 tests.
- [x] `powershell` parser check for changed PowerShell scripts - PASS.
- [x] `python .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` - PASS with existing `127.0.0.1` warning in `docs\oci-quick-start.md`.
- [x] `python .agent_work\scripts\validate_agent_work.py` - PASS.
- [x] `python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` - PASS.
- [x] `git diff --check` - PASS.
- [x] Direct diff scan for new secret-like additions - PASS, no matches in changed/untracked Task-081 files.
- [ ] Full-tree secret scan - NOT CLEAN: surfaced pre-existing sensitive-term findings in older docs/artifacts and hit a console encoding error; not introduced by this change set.
- [x] Draft PR opened: `https://github.com/J-Schulein/TowerScout/pull/31`.
- [x] `podman machine start` - PASS; Podman 5.8.2 rootless WSL2 machine started successfully.
- [x] `.\start.bat -Engine podman -Port 5006 -Gpu off -NoBrowser -TimeoutSeconds 180` - PASS after remediation; readiness reached `state=ready`, assets/config reported ok, and launcher summary reported `Runtime: engine=podman`.
- [x] `.\scripts\import-assets.cmd -Engine podman -Source webapp -Port 5006 -VerifyHashes -RestartWaitSeconds 120` - PASS; `post_import_health=ok`, `state=ready`, `asset_status=ok`, `verify_hashes=True`, `missing=`, and `corrupt=`.
- [x] `scripts\status.cmd -Engine podman -Port 5006` - PASS; final readiness reported `state=ready`, `container_engine=podman`, required assets ok, config ok, and named persistence paths writable.
- [x] `scripts\logs.cmd -Engine podman -Tail 80` - PASS; bounded logs showed normal startup, configured Google/Azure keys, CPU runtime, lazy classifier initialization, and Waitress startup.
- [x] `scripts\stop.cmd -Engine podman -Port 5006` - PASS; validation container stopped.
- [x] `docker version` / `docker info --format '{{json .ServerVersion}}'` - PASS after host runtime recovery; Docker Desktop `4.77.0`, Engine `29.5.3`, Linux/amd64.
- [x] `docker compose version` - PASS; Docker Compose `v5.1.4`.
- [x] `docker stop towerscout-google-firstlaunch-towerscout-1` - PASS; stopped stale rc2 CUDA container on port `5015` without deleting named volumes.
- [x] `.\start.bat -Engine docker -Port 5005 -Gpu off -NoBrowser -TimeoutSeconds 180` - PASS; readiness reached `state=ready`, assets/config reported ok, and launcher summary reported `Runtime: engine=docker device_policy=cpu selected_device=cpu pytorch_flavor=cpu`.
- [x] `.\scripts\import-assets.cmd -Engine docker -Source webapp -Port 5005 -VerifyHashes -RestartWaitSeconds 120` - PASS; `post_import_health=ok`, `state=ready`, `asset_status=ok`, `verify_hashes=True`, `missing=`, and `corrupt=`.
- [x] `scripts\status.cmd -Engine docker -Port 5005` - PASS; final readiness reported `state=ready`, `container_engine=docker`, required assets ok, config ok, and named persistence paths writable.
- [x] `docker logs --tail 80 towerscout-towerscout-1` - PASS; bounded logs showed normal startup, configured Google/Azure keys, CPU runtime, lazy classifier initialization, persistent secret loading, and Waitress startup.
- [x] `scripts\stop.cmd -Engine docker -Port 5005` - PASS; validation container stopped.
- [ ] GPU smoke - BLOCKED: `nvidia-smi` is not available on this host and no NVIDIA runtime evidence has been captured.

### Issues Identified

- Full-tree secret scan reports pre-existing sensitive artifacts and environment-variable references outside this Task-081 change set, including old browser-run summaries under `.agent_work/context/archive/2026-07/analysis/browser-runs/`. This should be handled as separate evidence hygiene, not as part of the runtime-code implementation.
- Live Podman launch initially exposed that Podman Compose provider banners on stderr could abort PowerShell under `$ErrorActionPreference = "Stop"` during both stale-session `compose ps` inspection and main Compose invocation.
- Live Podman launch initially exposed that `Write-TowerScoutReadinessSummary` assumed optional readiness `runtime.device_policy` fields were always present under strict mode.
- Live Podman import/status initially exposed stale local `.env` engine metadata: `TOWERSCOUT_CONTAINER_ENGINE=docker` could leak into a Podman-launched container unless the selected engine overrides shell env before Compose runs.
- Docker Desktop was initially blocked by host runtime state, then passed after Docker Desktop became reachable outside the sandbox. Sandboxed Docker CLI access still reports named-pipe permission denial, so local validation commands that talk to Docker Desktop require approved elevated execution.
- GPU validation remains blocked by missing NVIDIA runtime evidence.

### Remediation Actions

- No remediation needed for changed files based on direct diff scan.
- Updated `Invoke-TowerScoutCompose` and `Get-TowerScoutComposeServiceContainerIds` to temporarily set `$ErrorActionPreference = "Continue"` around native Compose calls, preserving exit-code handling while tolerating successful providers that write banners to stderr.
- Updated `Write-TowerScoutReadinessSummary` and `Test-TowerScoutCudaSelected` to use strict-safe optional property reads for partial readiness payloads.
- Updated shared Compose invocation to set `$env:TOWERSCOUT_CONTAINER_ENGINE` to the selected engine and added stale-session detection for container-engine mismatches.
- Added/extended Task-081 regression tests for successful provider stderr banners, engine metadata propagation, and container-engine mismatch restarts.
- Defer pre-existing evidence cleanup to a separate task or owner-approved hygiene pass to avoid altering unrelated historical artifacts during this runtime implementation.

### Sign-off

Automated implementation validation, live Podman CPU package-runtime validation,
and live Docker Desktop CPU runtime validation passed. The remaining GPU support
evidence was carried forward to `TASK-083`, and CPU/CUDA package delivery was
carried forward to `TASK-084`; Task-081 is closed at Sprint 6 closeout.
