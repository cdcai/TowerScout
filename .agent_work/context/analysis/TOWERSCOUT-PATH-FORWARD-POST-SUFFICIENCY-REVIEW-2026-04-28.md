# TowerScout Path Forward After Plan Sufficiency Review

**Created**: April 28, 2026  
**Purpose**: Consolidate the senior engineering reviews, the April 28 sufficiency assessment, and the current Sprint 05 planning state into a single path-forward document for TowerScout local deployment, release readiness, and post-Docker architecture work.

---

## Executive Decision

TowerScout should move forward with the current staged plan. The plan is sufficient because v1 is now deliberately narrow:

- single-user local release
- Windows/AMD64 first
- normal outbound internet required
- CPU is the supported baseline
- GPU/CUDA is optional acceleration only
- Docker is the first runtime baseline, not the final end-user experience
- release engineering support is limited/manual for v1

The plan should not become a broad rewrite, shared-service redesign, native installer push, or multi-platform support program before the Docker baseline is stable.

The latest review does require tighter execution gates. The primary change is not a new roadmap direction. It is making the v1 operating contracts explicit before the project treats Docker output as releasable.

---

## Current State

TowerScout is no longer a loose research prototype. The repo now has:

- Setup Wizard and Settings for API key/configuration management
- disk-backed config persistence under `webapp/config/.env`
- filesystem-backed Flask sessions
- progress/cancel handling for detection
- a local-first YOLO runtime through `webapp/ts_yolov5_local.py`
- normalized runtime paths under `webapp/`
- current integration smoke coverage for the corrected route/runtime baseline
- Waitress in the application entrypoint for local non-dev serving

The repo is still not productized for local release because:

- Docker is not implemented yet
- first-run asset/bootstrap behavior is not fully operationalized
- dependency/build reproducibility still needs a committed policy
- CI still has advisory checks and floating third-party action references
- `.pt` model upload remains a high-risk product surface
- `performance.log` has conflicting format ownership
- ProviderStateManager responsiveness and inference-mode behavior still need targeted validation before Docker sign-off
- long-running detection still runs in the request path
- durable run/job state is not yet separated from sessions/local process state

---

## Path Forward

### Phase 0: Keep The Scope Narrow

V1 success is operational clarity, not architectural completeness.

Supported for v1:

- one local user
- Windows/AMD64
- Docker Desktop / WSL2 as the engineering baseline
- normal internet access
- CPU execution
- optional CUDA acceleration on compatible AMD64 hosts
- manual release/support workflow

Not supported for v1:

- shared multi-user deployment
- offline or air-gapped operation
- broad proxy/TLS-interception support
- Mac/ARM64 release promise
- native installer/auto-update promise
- crash-safe workflow continuity
- distributed queue or separate inference service

### Phase 1: Complete `TASK-063` Before Docker

`TASK-063` is the pre-Docker release-hardening gate. It should resolve or explicitly accept the findings that would otherwise become part of the Docker baseline.

Required outputs:

- dependency vulnerability patch/risk decision
- frontend lockfile/reproducibility decision
- dependency repeatability policy for Python dependencies, frontend dependencies, and runtime assets
- third-party GitHub Action pinning by immutable reference, with Trivy specifically removed from `@master`
- recurring review/update cadence for pinned third-party GitHub Actions
- minimal workflow permission review
- release-candidate blocking/advisory CI policy
- residual Torch Hub / legacy YOLO audit proving no active runtime falls back to nondeterministic bootstrap behavior
- `.pt` model upload support boundary
- aligned Flask upload limit, Waitress request-body limit, and `.pt` upload policy
- provider API key restriction guidance for Google and Azure, including browser/server key separation where applicable
- insecure TLS troubleshooting-only boundary
- single authoritative performance metrics/log file contract
- written v1 release boundary and security/support posture

Docker should not start until `TASK-063` is complete or any unresolved item has owner-approved explicit risk acceptance.

### Phase 2: Complete `TASK-064` Before Docker Sign-Off

`TASK-064` is a bounded final-review gate. It should not become broad frontend modernization or general CPU optimization.

Required outputs:

- ProviderStateManager busy-wait / main-thread locking behavior removed, replaced with a bounded event/state transition, or owner-approved
- provider switching behavior preserved after any frontend change
- narrow `torch.inference_mode()` benchmark against the active CPU inference path or an equivalent repeatable local fixture
- measured apply/defer/reject decision for `torch.inference_mode()` before Docker starts

This gives Docker a cleaner baseline and prevents targeted responsiveness/performance questions from being misdiagnosed as containerization failures.

### Risk Acceptance Rule

Any unresolved `TASK-063` or `TASK-064` finding requires owner approval before `TASK-025` starts. The approval note must document:

- issue being accepted
- why fixing it now is deferred
- expected user or release impact
- mitigation or workaround
- review timing
- follow-up owner and task

### Phase 3: Deliver `TASK-025` As The Docker Runtime Contract

`TASK-025` should stay focused on container build/run behavior and runtime persistence.

Required outputs:

- Dockerfile and Compose configuration
- Docker validation on the corrected smoke baseline
- versioned v1 Docker runtime/persistence contract
- stable `FLASK_SECRET_KEY` behavior
- explicit persistence map
- cache/geocode durability classification
- first-run asset manifest and recovery behavior
- setup/settings persistence validation
- detection workflow validation in container
- container health/readiness contract for `TASK-054`
- Docker runtime behavior that preserves the upload-limit/request-body policy decided in `TASK-063`

Docker should not absorb launcher UX, background jobs, filesystem-session redesign, native installer work, or backend decomposition.

### Phase 4: Deliver `TASK-054` As The Local Launch And Support UX

`TASK-054` is the user-facing bridge over the Docker baseline.

Required outputs:

- `start.bat` first
- stop/logs/status helper path
- readiness polling before browser open
- first-run asset/download delay and failure messaging
- log-location guidance
- version/asset manifest visibility or collection path
- troubleshooting guidance for Docker not running, port conflicts, startup timeout, failed bootstrap, restricted network, and provider-key failures

This task should not become native installer work or a cross-platform packaging promise.

### Phase 5: Move Long-Running Work Behind A Local Job Boundary

`TASK-058` is the next major architecture step after Docker and launcher work.

Recommended local job-runner contract:

- single-user local job runner
- one run/job ID per detection/export workflow
- progress state survives request boundaries
- cancellation is tied to run ID, not only request/session timing
- SQLite is the default planned local durable metadata store unless `TASK-058` design validation finds a blocker
- schema/versioning/recovery behavior covers job metadata, progress state, cancellation state, and asset/run manifest references
- active workflow continuity across app crash/restart is best-effort for v1 unless explicitly upgraded later
- no distributed queue, multi-tenant fairness, or separate inference service in the first implementation

The job boundary should improve responsiveness, timeout behavior, progress/cancel reliability, and future decomposition without turning TowerScout into a shared service.

### Phase 6: Decompose Backend Layers After The Job/State Boundary

`TASK-059` should follow `TASK-058`, not precede it.

The main decomposition seams should be:

- route modules or blueprints
- detection orchestration service
- provider/geocoding service boundaries
- export/restore service boundaries
- state/session/run metadata helpers
- logging/support diagnostics

This order avoids refactoring the wrong seams before execution/state ownership is clearer.

---

## V1 Runtime And Persistence Contract

`TASK-025` must make this concrete as a versioned v1 contract.

Restart/update durable:

- `webapp/config/`
- stable `FLASK_SECRET_KEY`
- downloaded model/data assets
- asset/version manifest
- user exports/imported datasets
- support-relevant logs

Writable during runtime:

- `webapp/flask_session/`
- `webapp/temp/`
- `webapp/uploads/`
- `webapp/cache/`

Cleanup-safe or best-effort:

- transient upload files
- partial failed first-run downloads after recovery is available
- temporary session children
- geocode/cache data when reset behavior is clear
- active workflow/session continuity across crash/restart for Docker v1

The first Docker milestone should contain filesystem-session behavior rather than redesign it. Cache and geocode data must be classified as durable, best-effort, or cleanup-safe during `TASK-025`. The state redesign belongs to `TASK-058`.

---

## Asset Contract

`TASK-025` must create an asset inventory before Docker validation is considered complete.

Required inventory:

- YOLO weights
- EfficientNet project weights
- EfficientNet base-model/bootstrap behavior
- ZIP-code boundary data and year/version

Required manifest fields:

- asset name
- expected path
- version or source reference
- source URL or distribution source
- checksum when available
- required/optional classification
- recovery behavior for missing or partial assets

Recommended strategy:

- first-run download plus persistent storage for large runtime assets
- image-baked assets only when intentionally justified
- manual model/data update path for v1
- visible failure/retry behavior rather than silent startup stalls

---

## CI And Release Gate Contract

`TASK-063` should define release-candidate interpretation. Suggested first pass:

Blocking before release packaging:

- unit tests
- current smoke baseline relevant to the release target
- Docker build/run validation once `TASK-025` exists
- dependency install/import smoke after dependency changes
- high-severity dependency/security findings unless owner-approved
- third-party GitHub Action pinning by immutable reviewed reference
- documented review/update cadence for pinned third-party GitHub Actions
- no `aquasecurity/trivy-action@master`
- workflow permission review documented
- dependency repeatability policy documented for Python dependencies, frontend dependencies, and runtime assets

Advisory until dedicated cleanup:

- repo-wide Black formatting drift
- mypy strictness
- broad Bandit cleanup below the agreed release severity
- broad coverage threshold enforcement
- full frontend build modernization

This keeps CI honest without blocking the release path on unrelated historical cleanup.

---

## Security And Support Posture

Security posture for v1:

- API keys remain local and masked in UI/logs
- provider-key restrictions should be documented for Google and Azure
- TLS verification remains on by default
- `TOWERSCOUT_ALLOW_INSECURE_TLS` remains troubleshooting-only
- `.pt` model upload is disabled, gated, or documented as trusted local-admin/developer behavior only
- Flask upload limits, Waitress request-body limits, and `.pt` upload policy are aligned
- imagery, locations, exports, uploaded datasets, API keys, and support logs are treated as sensitive local artifacts

Support posture for v1:

- support is manual
- logs must have documented locations
- startup failures must be distinguishable from Docker, network, provider-key, and asset-bootstrap failures
- support bundle automation is nice-to-have, but log/version/asset collection instructions are required
- unsupported environments must be named explicitly

---

## Updated Task Sequence

1. `TASK-063`: Pre-Docker release hardening and operational gate
2. `TASK-064`: Targeted runtime responsiveness and inference baseline
3. `TASK-025`: Docker containerization and runtime/persistence contract
4. `TASK-054`: Launcher and support UX over Docker
5. `TASK-058`: Local job runner and durable run state, using SQLite by default unless design validation finds a blocker
6. `TASK-059`: Backend layer decomposition and logging consolidation
7. `TASK-026`: CPU optimization, informed by real workload telemetry
8. `TASK-027`: Enhanced error handling, prioritized by release/support findings
9. `TASK-060`: Frontend build modernization
10. `TASK-061`: Coordinated NumPy 2 runtime migration
11. `TASK-029`: Multi-provider fallback, only after deployment baseline and support model are stable unless provider reliability becomes the dominant release blocker

---

## Go / No-Go Criteria For The Docker Baseline

Go:

- `TASK-063` is complete or has owner-approved explicit risk acceptances
- `TASK-064` is complete or has owner-approved explicit risk acceptances
- ProviderStateManager responsiveness risk is resolved or owner-approved with evidence
- `torch.inference_mode()` benchmark decision is recorded
- runtime/persistence map is written
- cache/geocode durability classification is written
- asset inventory/manifest strategy is written
- `FLASK_SECRET_KEY` continuity is validated
- Setup Wizard and Settings persist across container restart
- first-run asset failure is visible and recoverable
- detection smoke path runs in container
- log locations and support diagnostics are documented

No-go:

- CI still uses floating security actions without documented acceptance
- pinned third-party GitHub Actions have no documented review/update cadence
- frontend dependency reproducibility is ambiguous
- dependency repeatability beyond top-level pins is ambiguous
- upload-size/request-body limits are inconsistent with the `.pt` upload policy
- ProviderStateManager busy-wait or inference-mode findings remain unreviewed
- `.pt` upload is exposed without a trusted-user boundary
- `performance.log` still has conflicting formats
- Docker persistence behavior is only assumed, not tested
- unsupported environments are implied as supported

---

## Key Risks

### Scope Creep

Risk: v1 grows to include shared service, offline, Mac/ARM64, native installer, or GPU guarantees.

Mitigation: Keep unsupported environments named in docs and acceptance criteria.

### Fragile Docker Success

Risk: Docker builds, but first-run setup, state persistence, or asset recovery fails for real users.

Mitigation: Make the persistence map and asset manifest part of `TASK-025`, not follow-up documentation.

### Targeted Runtime Findings Become Docker Noise

Risk: ProviderStateManager responsiveness behavior or `torch.inference_mode()` uncertainty is discovered during Docker validation and incorrectly treated as a containerization failure.

Mitigation: Clear `TASK-064` before `TASK-025`, or record owner-approved explicit risk acceptance with evidence.

### CI Green But Not Releasable

Risk: advisory CI gives false confidence.

Mitigation: Define release-candidate blocking checks in `TASK-063`.

### Request-Bound Detection Persists Too Long

Risk: launcher polish hides the structural cost of long-running request work.

Mitigation: Keep `TASK-058` as the next major architecture step after Docker/launcher.

### Support Without Support Data

Risk: limited release engineering creates manual support burden without enough local diagnostics.

Mitigation: `TASK-054` must expose log/status/version/asset guidance.

---

## Recommendation

Proceed with the updated plan.

Do not redesign TowerScout now. Complete the pre-Docker hardening gate, clear the bounded `TASK-064` responsiveness/performance gate, ship a narrow Docker runtime baseline, add launcher/support UX, then move detection behind a local job boundary. Treat operational contracts as the definition of v1 success.

This path preserves the recent stabilization work, avoids premature multi-user architecture, and gives reviewers a concrete basis for deciding when the project is ready for a limited local release.
