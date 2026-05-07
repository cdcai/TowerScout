# TASK-025: Docker / OCI Containerization

**Status**: COMPLETED - PR #7 OPEN
**Priority**: HIGH
**Type**: C (Infrastructure / Deployment Readiness)
**Estimated Effort**: 1-2 days (8-16 hours)
**Target Sprint**: Sprint 05 extension after `TASK-063` and `TASK-064`

## Objective

Create the Docker-compatible / OCI runtime baseline for TowerScout's supported v1 local deployment path on top of the corrected Sprint 05 runtime, smoke-test baseline, pre-Docker release-hardening gate, and targeted responsiveness/performance gate.

`TASK-025` is the container build/run and persistence task. It must not absorb launcher UX, background jobs, native installer work, broad backend decomposition, or release-hardening items owned by `TASK-063`.

After the May 4 Docker Desktop licensing and Podman reviews, this task should be implemented as an engine-aware OCI-compatible baseline rather than a Docker Desktop-specific product path. Docker Desktop, Podman Desktop, Linux Docker, Linux Podman, or a remote managed container host may be valid runtime hosts only after the relevant licensing, installation, virtualization, networking, Compose/provider, and support prerequisites are validated for the intended user environment.

After the May 4 open-source deployment review, client feedback, and follow-up decision review, the pre-task direction is now locked: use GitHub Releases as the default user-facing release control plane, publish/pin the application image through a registry-backed OCI path where possible, treat Podman as the preferred open-source Windows runtime target with a release-gated compatibility spike, keep Docker compatibility for licensed/approved and support/developer environments, and avoid making raw source clone/build the default end-user path.

## Finalized Pre-Task-025 Decisions

These decisions are accepted as the starting contract for `TASK-025`. The only adjustment mark is that **Podman-first is a selected target, not an already-proven release promise**; the Windows Podman Desktop / Podman machine compatibility spike remains a release gate before end-user support language can promise Podman.

- **Supported v1 user environment**: Windows 11/AMD64, single-user local use, CPU-first. NVIDIA/CUDA remains optional on compatible AMD64 hosts only after validation. Mac, ARM64, offline, air-gapped, VDI, shared multi-user deployment, native installer behavior, and managed/remote hosting are not v1 promises.
- **Runtime host position**: Podman Desktop plus WSL2/Hyper-V is the preferred open-source Windows runtime target after the spike passes. Docker Desktop remains a compatible secondary path only where licensing, procurement, endpoint policy, and installation prerequisites are approved. Linux Docker/Podman may be used as reference/developer/CI paths where practical.
- **Distribution strategy**: Use a GitHub Release ZIP as the normal user-facing package. The package should include quick-start docs, `compose.yaml`, `.env` template, start/stop/logs/status scripts, asset manifest, checksums, troubleshooting guidance, and a pinned GHCR image reference by digest. Optional OCI image archives are restricted-network fallbacks, not the default path.
- **Source clone/build boundary**: Clone/download source remains a developer/support workflow. Normal users should not need host Python, Node, GDAL, PyTorch, or local build steps.
- **Large asset strategy**: Large model/data assets stay out of git and out of the default source checkout. They should be managed by a versioned manifest, downloaded/imported into durable storage, staged before activation, verified with SHA-256, rechecked on startup/update, and recoverable through a manual/restricted-network import path.
- **Asset hosting/source**: GitHub Releases should host release metadata, manifests, checksums, and package files. Large binaries may live in governed object storage or an internal mirror when size, bandwidth, policy, or access control makes direct GitHub asset hosting unsuitable.
- **Persistence profile**: Named volumes are the default supported persistence profile. A host-visible data-directory profile may be offered only as an explicitly documented optional profile after validation.
- **Health/readiness contract**: `TASK-025` should provide `/api/health` for basic liveness and `/api/readiness` for structured startup state. Readiness states should include `starting`, `setup_required`, `degraded`, `ready`, and `fatal`, with redacted details for config, assets, provider setup, version, and recovery guidance.
- **Validation strategy**: Baseline CI should build the image and prove health/readiness without requiring private or heavyweight assets. Release-candidate/local validation should run the real asset bootstrap and detection smoke path.
- **Documentation strategy**: Ship two documentation layers: a GitHub-first end-user/operator guide and a technical OCI runtime contract. Both must state prerequisites, unsupported environments, asset handling, persistence, reset/update, troubleshooting, support diagnostics, and sensitive local data handling.
- **Open-source clarification**: The runtime/tooling path is open-source-friendly through Podman. TowerScout's application license/open-source suitability remains a separate product/legal clarification and is not solved by selecting Podman.

## V1 Scope Assumptions

- Single-user local deployment only.
- Windows/AMD64 is the first supported user target.
- Normal outbound internet access is required.
- CPU execution is the supported baseline.
- NVIDIA/CUDA is optional acceleration on compatible AMD64 hosts.
- Docker-compatible / OCI containerization is the first runtime baseline, not the final managed installer.
- Docker Desktop must not be assumed available for government users unless licensing, procurement, and endpoint prerequisites are approved for the intended user group.
- Podman may reduce Docker Desktop product/licensing dependency, but Windows Podman still depends on a Linux VM path such as WSL2 or Hyper-V plus engine, machine, Compose, proxy/certificate, and support validation.
- Podman should be treated as the preferred open-source runtime target, not as a promised supported user runtime until the Windows Podman Desktop/Podman machine compatibility spike passes or is explicitly risk-accepted.
- `TASK-025` should avoid Docker Desktop-only implementation assumptions and keep commands, validation, and future launcher hooks engine-aware where practical.
- GitHub Releases should be the default user-facing delivery path for release notes, quick-start docs, scripts, Compose-compatible config, asset manifests, checksums, troubleshooting, and a pinned GHCR image reference by digest. Optional OCI image archives are restricted-network fallbacks.
- Local clone-and-build from GitHub is a developer/support path, not the preferred v1 path for normal end users.
- Large model/data assets should not be committed to the git repository; they require a checksummed manifest/bootstrap path and a manual or restricted-network fallback bundle.
- A host-visible data-directory profile may be offered for sites that need inspectable local folders, but named volumes remain the safer default supported persistence mechanism unless validation proves otherwise.
- The client's "open source" requirement may refer to runtime tooling, application licensing, or both; TowerScout's `CC-BY-NC-SA-4.0` license should be clarified as a separate product/legal decision before release promises are made.
- Mac, ARM64, offline, air-gapped, VDI, shared multi-user, and native installer promises are out of scope for this task.

## Requirements (EARS Notation)

**R-025-001**: WHEN containerization work begins, THE PROJECT SHALL have completed `TASK-063` and `TASK-064` or recorded owner-approved risk acceptance for any unresolved pre-container gate item.

**R-025-002**: WHEN TowerScout is built as a container, THE SYSTEM SHALL provide a Docker-compatible/OCI image definition and Compose-compatible configuration that run the corrected Flask/Waitress application baseline.

**R-025-003**: WHEN the container is restarted or replaced, THE SYSTEM SHALL preserve required durable state including `webapp/config/`, stable `FLASK_SECRET_KEY`, downloaded runtime assets, user exports/imported datasets, and support-relevant logs.

**R-025-004**: WHEN runtime directories are mounted, THE SYSTEM SHALL classify each path as restart/update-durable, writable runtime state, or cleanup-safe/best-effort state in a versioned v1 runtime/persistence contract.

**R-025-005**: WHEN first-run runtime assets are missing, THE SYSTEM SHALL either bootstrap them into persistent storage or fail with actionable recovery guidance.

**R-025-006**: WHEN container validation runs, THE SYSTEM SHALL reuse the `TASK-052` smoke contract against the containerized app rather than creating an unrelated engine-specific validation path.

**R-025-007**: WHEN Setup Wizard or Settings saves configuration in the container runtime, THE SYSTEM SHALL persist the saved configuration across container restarts.

**R-025-008**: WHEN the launcher task consumes the selected container runtime baseline, THE SYSTEM SHALL expose a clear health/readiness contract suitable for host-side polling.

**R-025-009**: WHEN release documentation describes supported hosts, THE PROJECT SHALL state Windows/AMD64 CPU baseline support and label GPU, Mac, ARM64, offline, and shared-deployment behavior accurately.

**R-025-010**: WHEN cache and geocode data are mapped in the container runtime, THE PROJECT SHALL explicitly decide whether each cache class is durable, best-effort, or cleanup-safe for v1.

**R-025-011**: WHEN container config exposes request-body or upload-size behavior, THE SYSTEM SHALL preserve the upload-limit policy decided in `TASK-063`.

**R-025-012**: WHEN the container runtime starts without `FLASK_SECRET_KEY` in the persistent config file, THE SYSTEM SHALL generate a secure secret key, write it to `webapp/config/.env`, and reuse that same value across container restarts without exposing it in the UI.

**R-025-013**: WHEN container runtime guidance is documented, THE PROJECT SHALL distinguish the engine-neutral TowerScout container contract from host-specific Docker Desktop, Podman Desktop, Linux Docker, Linux Podman, or remote-host prerequisites.

**R-025-014**: WHEN validation scripts or launcher-facing contracts are designed, THE SYSTEM SHALL avoid hard-coding Docker Desktop-specific checks and SHALL leave room for a supported container-engine selection such as Docker or Podman.

**R-025-015**: WHEN end-user release packaging is designed, THE PROJECT SHALL make GitHub Releases the default user-facing control plane for release notes, setup instructions, scripts, Compose-compatible configuration, asset manifest metadata, checksums, troubleshooting guidance, and a pinned registry image reference by digest, with optional OCI image archives reserved for restricted-network fallback.

**R-025-016**: WHEN release guidance describes source checkout, THE PROJECT SHALL distinguish the normal end-user GitHub Release path from the developer/support clone-and-build path.

**R-025-017**: WHEN persistence options are documented, THE PROJECT SHALL define the default named-volume profile and decide whether to provide an optional host-visible data-directory profile for sites that need inspectable folders.

**R-025-018**: WHEN open-source deployment requirements are discussed, THE PROJECT SHALL separately track open-source runtime/tooling selection and TowerScout application licensing suitability.

**R-025-019**: WHEN release-candidate validation is designed, THE PROJECT SHALL split baseline CI validation from full asset-backed release validation so routine CI can prove image startup and readiness without requiring private or heavyweight assets.

**R-025-020**: WHEN readiness behavior is implemented, THE SYSTEM SHALL expose structured readiness states including `starting`, `setup_required`, `degraded`, `ready`, and `fatal` with redacted component details and actionable recovery guidance.

## Acceptance Criteria

- [x] `TASK-063` and `TASK-064` completed, or unresolved items documented as owner-approved risk acceptances before Docker implementation starts.
- [x] Docker-compatible/OCI image definition exists and builds from a clean checkout with documented prerequisites.
- [x] Compose-compatible configuration exists for supported local deployment.
- [x] Docker Desktop licensing/endpoint approval and Podman Desktop/Podman machine feasibility are documented as host-runtime gates, not hidden application assumptions.
- [x] Validation and launcher-facing status language is engine-aware enough to support Docker or Podman without rewriting the application runtime contract.
- [x] Podman compatibility spike is completed for this host before Podman is treated as the preferred open-source local runtime target; Docker-Desktop-free Compose-provider validation remains a support caveat before promising Podman broadly on hosts without Docker Desktop installed.
- [x] GitHub Release package contract is documented, including release notes, quick start, scripts, Compose-compatible config, pinned GHCR image reference by digest, optional OCI archive fallback, asset manifest, checksums, troubleshooting, and recovery guidance.
- [x] Local clone-and-build is documented as a developer/support path rather than the default normal-user deployment path.
- [x] Versioned v1 runtime/persistence contract exists and covers config, secret key, assets, exports/imports, logs, sessions, temp, uploads, cache, and geocode data.
- [x] Persistence contract distinguishes default named-volume behavior from any optional host-visible data-directory profile.
- [x] Cache and geocode data are classified as durable, best-effort, or cleanup-safe for v1.
- [x] Stable `FLASK_SECRET_KEY` behavior is documented and validated across restart.
- [x] Empty first-run container config generates and persists `FLASK_SECRET_KEY` into `webapp/config/.env` without requiring end-user manual setup.
- [x] Setup Wizard works in the container.
- [x] Settings save/load persists across container restart.
- [x] First-run asset inventory and bootstrap/recovery behavior are documented.
- [x] Asset manifest includes checksums and restricted-network/manual bundle recovery guidance.
- [x] Detection workflow smoke path runs in the container.
- [x] Container health/readiness behavior is available for `TASK-054`, including `/api/health` and structured `/api/readiness` states for `starting`, `setup_required`, `degraded`, `ready`, and `fatal`.
- [x] Baseline CI and release-candidate validation responsibilities are split and documented, including asset-aware skip/degraded behavior for routine CI and real-asset detection smoke for release candidates.
- [x] Unsupported v1 environments are documented and not implied as supported.
- [x] TowerScout application license/open-source suitability is recorded as a separate product/legal clarification item and not treated as solved by choosing Podman.
- [x] Container runtime configuration preserves the upload-limit/request-body policy decided in `TASK-063`.

## Dependencies

- `TASK-052`: Current integration smoke-test baseline
- `TASK-056`: First-run reliability and runtime determinism hardening
- `TASK-057`: Local YOLO runtime ownership and Torch Hub independence
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening
- `TASK-063`: Pre-Docker release hardening and CI reproducibility gate
- `TASK-064`: Targeted runtime responsiveness and inference baseline

## Implementation Plan

1. Confirm `TASK-063` and `TASK-064` completion/risk-acceptance status, including owner approval for any accepted unresolved item.
2. Write the versioned container runtime contract: supported host/runtime options, persistence map, first-run `FLASK_SECRET_KEY` generation/persistence behavior, cache/geocode durability decision, asset strategy, structured health/readiness behavior, upload-limit behavior, GitHub Release ZIP plus GHCR-by-digest package contract, optional host-visible data profile, and engine-aware validation path.
3. Implement the Docker-compatible/OCI image definition and Compose-compatible configuration using the normalized `webapp/` runtime contract.
4. Validate Setup Wizard, Settings persistence, empty-config secret-key generation, stable secret-key behavior across restart, first-run asset behavior, and detection smoke.
5. Document user-facing GitHub Release run/recovery guidance, including Docker Desktop, Podman Desktop, Linux engine, restricted-network asset, and source-build caveats, and hand off launcher requirements to `TASK-054`.
6. Run a short Podman compatibility spike or explicitly record owner-approved risk acceptance before making Podman a supported end-user runtime path.
7. Record the TowerScout application license/open-source suitability clarification as a product/legal follow-up if it cannot be resolved within `TASK-025`.

---

## Implementation Log

### 2026-04-28 - Task File Creation
**Objective**: Create task-specific documentation for the Docker baseline after the plan sufficiency review.  
**Context**: `TASK-025` existed in `current-tasks.md` but did not have an individual active task file. The latest review confirmed Docker-first sequencing while requiring clearer v1 runtime, persistence, asset, and support contracts.  
**Decision**: Keep `TASK-025` focused on container build/run behavior and require the v1 runtime contract before implementation is considered complete.  
**Execution**: Created this task file with EARS requirements, acceptance criteria, dependencies, and implementation plan.  
**Output**: `TASK-025` now has task-specific active documentation.  
**Validation**: Pending `.agent_work` structure validation.  
**Next**: Start only after `TASK-063` clears or records owner-approved explicit risk acceptance.

### 2026-04-28 - Final Path-Forward Review Expansion
**Objective**: Tighten the Docker runtime contract around persistence versioning, cache/geocode state, and upload limits.  
**Context**: The final path-forward review agreed with Docker sequencing but recommended making the persistence map a formally versioned v1 contract and aligning Docker runtime behavior with upload-limit decisions.  
**Decision**: Keep these requirements in `TASK-025` because they define container runtime behavior after `TASK-063` sets policy.  
**Execution**: Added EARS requirements and acceptance criteria for versioned persistence, cache/geocode classification, and upload-limit preservation.  
**Output**: `TASK-025` now requires Docker to implement the v1 runtime contract explicitly.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Start only after `TASK-063` and `TASK-064` clear or record owner-approved explicit risk acceptance.

### 2026-04-28 - Owner Approval Rule
**Objective**: Prevent Docker work from starting on implicit risk acceptance.  
**Context**: The project owner confirmed they will approve risk acceptances when given enough context to understand the decision and consequences.  
**Decision**: Treat owner-approved risk notes as required evidence for any unresolved `TASK-063` or `TASK-064` item before `TASK-025` starts.  
**Execution**: Updated requirements, acceptance criteria, dependencies, and implementation plan to require owner-approved risk acceptance before Docker implementation begins.  
**Output**: Docker start criteria now require either cleared pre-Docker gates or documented owner approval for accepted residual risk.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Confirm gate status before starting Docker implementation.

### 2026-04-30 - PR 6 Readiness Follow-Up Intake
**Objective**: Record the remaining follow-up items from the final `TASK-064` PR-readiness review before Docker work starts.
**Context**: PR #6 addressed the direct `TASK-064` review findings by adding PR-time frontend CI coverage and a provider-switch queue-recovery test. The remaining reviewer concerns are Docker/startup documentation and local Windows `test:stage-0` portability.
**Decision**: Treat Docker documentation, persistence/run guidance, and container validation as `TASK-025` implementation work. Treat the Windows/Bash `test:stage-0` issue as a tooling portability follow-up unless it blocks Docker validation.
**Execution**: Added this intake note rather than expanding PR #6 into Docker implementation or frontend build modernization.
**Output**:
- `TASK-025` should include explicit Docker user/support documentation for persistence mounts, supported hosts, first-run assets, diagnostics, and recovery paths.
- `TASK-025` should not rely on `npm run test:stage-0` as the only frontend validation path on Windows unless the Bash dependency is replaced or a portable equivalent is provided.
- Azure browser smoke remains an accepted local-provider-readiness caveat for `TASK-064`; Docker validation should still exercise configured provider readiness and report failures as provider/environment issues rather than container regressions when appropriate.
**Validation**: This is a planning intake note; implementation validation remains pending under `TASK-025`.
**Next**: Start `TASK-025` from latest `main` after PR #6 lands and verify these notes during the initial Docker audit/validation pass.

### 2026-04-30 - First-Run Secret-Key Persistence Clarification
**Objective**: Ensure Docker first-run behavior does not require end users to manually understand or create a Flask secret key.
**Context**: The current host runtime generates a temporary in-memory secret when `FLASK_SECRET_KEY` is absent, but it does not write that generated value back to `.env`. For Docker v1, replacing or restarting the container must not silently rotate session-signing state when the persistent config file is empty.
**Decision**: Require `TASK-025` to generate a secure `FLASK_SECRET_KEY` on first Docker startup when missing, persist it to `webapp/config/.env`, reuse it across restarts, and avoid exposing it in UI/status surfaces.
**Execution**: Added `R-025-012`, an acceptance criterion, and implementation-plan validation coverage for empty-config secret-key generation and restart persistence.
**Output**: `TASK-025` now explicitly tracks automatic first-run `FLASK_SECRET_KEY` generation and persistence as part of Docker completion.
**Validation**: Documentation update only; implementation validation remains pending under `TASK-025`.
**Next**: During Docker implementation, test with an empty persistent config volume, verify `.env` receives `FLASK_SECRET_KEY`, restart/recreate the container, and confirm the value is unchanged.

### 2026-05-01 - Containerization Decision Analysis
**Objective**: Create a comprehensive decision-support analysis before Docker implementation starts.
**Context**: `TASK-025` still needs final decisions around the container roadmap, v1 scope, asset strategy, persistence map, startup behavior, health/readiness, validation, support diagnostics, and future launcher/native-packaging direction.
**Decision**: Keep the detailed decision analysis with the owning task support artifacts and use it as the Phase 1 decision register for `TASK-025`.
**Execution**: Created `.agent_work/tasks/active/TASK-025/TASK-025-CONTAINERIZATION-DECISION-ANALYSIS-2026-05-01.md`.
**Output**: The project now has a self-contained roadmap/context/decision document covering remaining Docker strategy options, pros/cons, recommendations, second-review findings, and a proposed `TASK-025` phase breakdown.
**Validation**: Documentation update only; structure validation should be run after this documentation change.
**Next**: Review the decision register with the owner, record accepted/modified decisions, then begin Docker implementation from the locked runtime contract.

### 2026-05-04 - Docker Desktop Licensing And Podman Review Intake
**Objective**: Record reviewer feedback and runtime-host implications discovered after the May 4 Docker Desktop licensing and Podman analyses.
**Context**: The Docker Desktop licensing review concluded that government use of Docker Desktop creates a concrete licensing/procurement and managed-endpoint gate, but does not invalidate TowerScout's generic containerization work. The Podman review concluded that Podman can reduce Docker Desktop product dependency and fits the OCI/container contract, but Windows Podman still requires a Linux VM path such as WSL2 or Hyper-V and has Compose/provider, proxy/certificate, and support nuances.
**Decision**: Reframe `TASK-025` as a Docker-compatible / OCI container runtime baseline rather than a Docker Desktop-specific product path. Preserve the current container build/run/persistence strategy while making validation, launcher handoff, and documentation engine-aware enough to support Docker or Podman after host-runtime feasibility is validated.
**Execution**: Updated the objective, scope assumptions, requirements, acceptance criteria, and implementation plan to capture Docker Desktop licensing/endpoint gates, Podman feasibility gates, engine-aware validation, and the need for a Podman compatibility spike before promising Podman as an end-user runtime.
**Output**: `TASK-025` now distinguishes the application container contract from host-specific Docker Desktop, Podman Desktop, Linux engine, or remote-host delivery choices.
**Validation**: Documentation update only; implementation validation remains pending under `TASK-025`.
**Next**: Update the decision analysis addendum/status table, validate `.agent_work` structure, and then review the remaining decision items with the owner before implementation starts.

### 2026-05-04 - Decision Register Status Update
**Objective**: Confirm which `TASK-025` decision items still need answers after the Docker Desktop licensing and Podman review findings.
**Context**: The May 1 decision analysis listed 40 decision items. The later reviews did not invalidate the recommendations, but they changed the runtime-host decision from a Docker Desktop assumption into an engine-aware container host choice.
**Decision**: Keep the full decision register active, but classify the remaining decisions into two groups: items needing explicit owner/product sign-off before release, and items with strong recommendations that mainly need acceptance and implementation validation.
**Execution**: Added a "Decision Status After May 4 Reviews" section to the decision analysis, updated runtime validation and managed-machine risk items, and revised the ideal user flow to say users install the supported container runtime rather than assuming Docker Desktop.
**Output**: The decision analysis now states that `D-001`, `D-002`, `D-014`, `D-016`, `D-020`, `D-030`, `D-031`, `D-038`, and `D-040` remain the highest-priority explicit sign-off items. The remaining decisions have strong recommendations but still need owner acceptance or implementation lock-in.
**Validation**: `.agent_work` structure validation passed with `python .agent_work\scripts\validate_agent_work.py`.
**Next**: Review the sign-off items with the owner, choose the primary supported runtime-host path before release, and run or defer the Podman compatibility spike before promising Podman support.

### 2026-05-04 - Open-Source GitHub Release Direction Update
**Objective**: Incorporate client feedback requesting an open-source-friendly way for sites to deploy TowerScout from GitHub to local laptops with clear folder and asset guidance.
**Context**: The client feedback changes the preferred release packaging and runtime-host bias, but does not change the underlying need for an OCI-compatible container contract. Reviewer follow-up concluded that Podman is the leading open-source runtime candidate, GitHub Releases should be the user-facing release control plane, and raw source clone/build should remain a developer/support path because TowerScout still depends on large external model and ZIP-code assets.
**Decision**: Keep `TASK-025` OCI-first and engine-aware, make GitHub Releases the preferred end-user delivery path, treat Podman as the leading open-source runtime candidate pending validation, preserve Docker compatibility, and separately track TowerScout application license suitability because selecting Podman does not resolve application licensing questions.
**Execution**: Updated scope assumptions, requirements, acceptance criteria, and implementation plan to cover GitHub Release packaging, Podman validation, source-build boundaries, named-volume versus host-visible data profiles, checksummed asset/manual bundle handling, and open-source licensing clarification.
**Output**: `TASK-025` now reflects the newer product direction: GitHub-first release package for normal users, Podman-first candidate after validation, Docker-compatible OCI contract, and deliberate asset/persistence/licensing decisions before release.
**Validation**: Documentation update only; `.agent_work` validation should be rerun after synchronized planning updates.
**Next**: Update synchronized planning surfaces (`current-tasks.md`, `task-backlog.md`, `TASK-054`, and current Sprint 05 status docs), then validate `.agent_work` structure.

### 2026-05-05 - Finalized Pre-Task Decision Lock
**Objective**: Convert the remaining pre-task containerization decision items into an accepted starting contract for `TASK-025`.
**Context**: A follow-up reviewer agreed with the GitHub-first, OCI-compatible approach and recommended a more precise final shape: Podman-first target on Windows after validation, Docker-compatible fallback, GHCR image by digest, GitHub Release ZIP bundle, manifest-managed assets, split CI/release validation, and structured readiness.
**Decision**: Accept the reviewer direction with one adjustment mark: Podman-first is the selected target but remains a release-gated claim until the Windows Podman Desktop / Podman machine compatibility spike passes or is explicitly risk-accepted. This means `TASK-025` can start from an engine-neutral OCI contract, but release docs cannot promise Podman support until validation evidence exists.
**Execution**: Added the finalized pre-task decision set, tightened release-package, readiness, asset, validation, and Podman acceptance language, and kept the application license question separate from runtime/tooling choice.
**Output**: `TASK-025` now has a locked pre-task decision baseline and no longer treats the major decision items as open-ended research questions.
**Validation**: Documentation update only; `.agent_work` validation should be rerun after synchronized planning updates.
**Next**: Update the decision analysis and cross-reference planning docs, then run `.agent_work` structure validation.

### 2026-05-05 - Phase 1 Start
**Objective**: Move `TASK-025` from pre-task decision lock into Phase 1 runtime-contract execution.
**Context**: `TASK-063` is complete with no unresolved risk acceptance required. `TASK-064` is complete and explicitly hands off Docker documentation, container validation, and Windows `test:stage-0` portability follow-up to `TASK-025` or later tooling work. The May 5 decision lock finalized the GitHub-first, OCI-compatible baseline while preserving Podman as a release-gated supported-runtime claim.
**Decision**: Start `TASK-025` Phase 1 by documenting and reconciling the versioned v1 runtime/persistence, asset, health/readiness, release-package, and engine-aware validation contracts before image-definition implementation begins.
**Execution**: Updated the active task status to `IN_PROGRESS - PHASE 1 RUNTIME CONTRACT` and synchronized tracker surfaces to show that pre-container gates are cleared.
**Output**: `TASK-025` is now active in Phase 1. The immediate work is runtime contract inventory and documentation, not yet container file implementation.
**Validation**: Pending `.agent_work` structure validation after tracker updates.
**Next**: Audit runtime paths, assets, config/secret behavior, sessions, logs, uploads, cache/geocode storage, upload limits, and smoke-validation hooks; then write the v1 runtime/persistence contract and container validation checklist.

### 2026-05-05 - Phase 1 Runtime Contract Draft
**Objective**: Convert the initial code audit into a concrete v1 runtime, persistence, asset, readiness, release-package, and validation contract for container implementation.
**Context**: The container task must preserve normalized `webapp/` runtime paths, filesystem sessions, setup/settings config persistence, current upload-limit policy, and the `TASK-052` smoke contract while handling gitignored model/data assets explicitly.
**Decision**: Treat named volumes as the default v1 persistence profile; classify map/geocoding cache as best-effort persisted cache; keep clone/build as developer/support only; split routine CI health/readiness from release-candidate real-asset validation; and require health/readiness plus first-run secret persistence before launcher handoff.
**Execution**:
- Audited `webapp/ts_paths.py`, `webapp/ts_config.py`, `webapp/towerscout.py`, `webapp/ts_yolov5.py`, `webapp/ts_yolov5_local.py`, `webapp/ts_en.py`, `webapp/ts_zipcode.py`, `webapp/ts_geocache.py`, `webapp/ts_logging.py`, `webapp/ts_performance.py`, `webapp/ts_validation.py`, `.gitignore`, `webapp/requirements.txt`, `package.json`, `.github/workflows/ci.yml`, and `TASK-052` smoke tests.
- Captured local SHA-256 evidence for the current YOLO, EfficientNet, and ZIP-code assets.
- Created `.agent_work/tasks/active/TASK-025/TASK-025-V1-RUNTIME-CONTRACT-2026-05-05.md`.
**Output**: Phase 1 now has a concrete contract artifact covering support boundary, runtime path classification, asset inventory/checksum evidence, config/secret-key behavior, readiness states, upload/request-body behavior, cache/geocode durability, release package contents, and CI versus release-candidate validation.
**Validation**: Pending `.agent_work` structure validation after this task-log update.
**Next**: Use the contract to start Phase 2 implementation planning around first-run secret persistence, `/api/health`, `/api/readiness`, asset manifest/preflight, ZIP-code path handling, image definition, and Compose-compatible named volumes.

### 2026-05-05 - App Runtime Contract Implementation Slice
**Objective**: Implement the app-side runtime hooks required before Docker/OCI image and Compose work can rely on stable health, readiness, secret, and data-path behavior.
**Context**: The Phase 1 runtime contract identified four app blockers for containerization: process-local secret-key fallback, missing health/readiness routes, relative ZIP-code data path handling, and lack of focused tests for the new launcher/container status contract.
**Decision**: Implement a small reusable runtime helper module and keep container readiness checks redacted and lightweight. Preserve the `TASK-052` smoke baseline instead of replacing it with a Docker-specific test path.
**Execution**:
- Added `ts_config.ensure_persistent_flask_secret_key()` to create or reuse a stable `FLASK_SECRET_KEY` in `webapp/config/.env`.
- Updated Flask startup to use persistent secret handling outside testing or explicit `TOWERSCOUT_DISABLE_SECRET_PERSISTENCE`.
- Added `webapp/ts_runtime.py` with health/readiness payload helpers, runtime path writability checks, asset presence checks, support metadata, and redacted recovery guidance.
- Added `GET /api/health` and `GET /api/readiness` routes.
- Updated `ts_zipcode.py` to resolve ZIP-code shapefile data from the app base directory instead of relying on process cwd.
- Added focused tests for secret persistence, health/readiness route semantics, readiness redaction/setup-required behavior, and ZIP-code app-anchored path resolution.
**Output**:
- App now exposes cheap liveness and structured readiness for container engines and future launcher polling.
- Empty persistent config can receive a generated secret key before filesystem sessions depend on it.
- ZIP-code data lookup is no longer dependent on launching from `webapp/` as cwd.
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_config.py tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py -q -p no:cacheprovider` -> `27 passed, 8 warnings`
- `.\.venv\Scripts\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `172 tests collected`
- `.\.venv\Scripts\python.exe -m pytest tests\integration\test_end_to_end.py -q -p no:cacheprovider` -> `2 passed, 2 warnings`
- `python .agent_work\scripts\validate_agent_work.py` -> passed
**Next**: Add asset manifest/preflight structure and then start the Docker-compatible image definition plus Compose-compatible named-volume profile.

### 2026-05-05 - Asset Manifest And Preflight Slice
**Objective**: Add the manifest-managed asset contract required for container readiness, release packaging, and routine-CI degraded-mode startup.
**Context**: Large model and ZIP-code assets are gitignored and cannot be assumed present in a clean checkout or routine CI image. `TASK-025` needs a tracked manifest plus runtime preflight reporting before Docker/Compose validation can distinguish missing assets from container regressions.
**Decision**: Track the v1 manifest at `webapp/asset_manifest.v1.json`, allow override through `TOWERSCOUT_ASSET_MANIFEST`, check file presence and expected byte sizes during readiness, and reserve SHA-256 verification for explicit validation through `TOWERSCOUT_VERIFY_ASSET_HASHES=1` or release-candidate tooling so launcher polling does not hash large assets repeatedly.
**Execution**:
- Added `webapp/asset_manifest.v1.json` with YOLO, EfficientNet project weights, and ZIP-code shapefile component entries, expected byte sizes, SHA-256 values, source labels, and recovery guidance.
- Added `webapp/ts_assets.py` to load/validate the manifest and report `ok`, `degraded`, or `error` asset state with missing, corrupt, and optional-missing asset lists.
- Updated `webapp/ts_runtime.py` readiness to consume `ts_assets.build_asset_status()`, expose manifest version in readiness, treat manifest errors as `fatal`, and treat missing/corrupt required assets as `degraded`.
- Added `tests/unit/test_assets.py` plus readiness coverage for manifest-error fatal state.
**Output**:
- Routine CI can start without heavyweight assets and receive explicit degraded readiness instead of ambiguous pass/fail behavior.
- Release-candidate validation can enable hash verification against the same manifest.
- Readiness now reports asset manifest version and redacted asset state for launcher/support use.
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_assets.py tests\unit\test_runtime_contract.py tests\unit\test_flask_routes.py -q -p no:cacheprovider` -> `21 passed`
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_assets.py tests\unit\test_config.py tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py -q -p no:cacheprovider` -> `33 passed, 8 warnings`
- `.\.venv\Scripts\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `178 tests collected`
- `.\.venv\Scripts\python.exe -m pytest tests\integration\test_end_to_end.py -q -p no:cacheprovider` -> `2 passed, 2 warnings`
- `python .agent_work\scripts\validate_agent_work.py` -> passed
**Next**: Start Docker-compatible image and Compose-compatible named-volume implementation using the established secret, readiness, and asset manifest contracts.

### 2026-05-05 - OCI Image And Compose Baseline Slice
**Objective**: Add the first Docker-compatible / OCI image definition and Compose-compatible named-volume runtime profile on top of the established app runtime contracts.
**Context**: The app now has persistent secret-key handling, health/readiness routes, app-anchored ZIP-code data lookup, and manifest-backed asset preflight. Routine container CI still needs to start without large assets, so container startup must avoid eager ZIP-code/YOLO loading while readiness reports the missing assets as degraded.
**Decision**: Use a multi-stage image with a Node frontend build stage and Python 3.11 slim runtime stage, install CPU PyTorch wheels by default, exclude model/data assets from the image context, and use named volumes for config, assets, logs, sessions/temp/uploads, and cache. Add `TOWERSCOUT_STARTUP_PRELOAD=0` as an explicit container-mode startup switch rather than using the existing `dev` CLI path.
**Execution**:
- Added `Dockerfile` with frontend build, Python runtime dependency install, Waitress app command, healthcheck, and declared runtime volumes.
- Added `.dockerignore` to keep secrets, local runtime state, tests/dev artifacts, and large model/data assets out of image build context.
- Added `compose.yaml` for release-style image runs with named volumes and healthcheck.
- Added `compose.build.yaml` as a developer/support override for local image builds without changing the release-style Compose file.
- Added root `.env.example` for Compose runtime knobs without provider secrets.
- Added `towerscout.should_preload_startup_assets()` and `towerscout.load_model_catalog()` so missing model assets no longer crash asset-light startup when preload is disabled.
- Added focused unit coverage for the startup preload switch and empty model asset volume behavior.
**Output**:
- TowerScout now has an engine-neutral Compose runtime profile with named volumes matching the v1 persistence contract.
- Local developer/support builds can use `docker compose -f compose.yaml -f compose.build.yaml up --build`.
- Release packages can use `compose.yaml` with `TOWERSCOUT_IMAGE` set to a pinned GHCR image reference by digest.
- Container startup can serve health/readiness before large assets are present, while readiness remains responsible for reporting degraded asset state.
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py tests\unit\test_assets.py tests\unit\test_config.py -q -p no:cacheprovider` -> `35 passed, 8 warnings`
- `.\.venv\Scripts\python.exe -m py_compile webapp\towerscout.py webapp\ts_runtime.py webapp\ts_assets.py webapp\ts_config.py` -> passed
- `.\.venv\Scripts\python.exe -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(p).read_text()) for p in ['compose.yaml','compose.build.yaml']] ; print('compose yaml parsed')"` -> `compose yaml parsed`
- `docker compose -f compose.yaml config` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml config` -> passed
- `git diff --check -- Dockerfile .dockerignore compose.yaml compose.build.yaml .env.example webapp\towerscout.py tests\unit\test_flask_routes.py` -> passed
- `docker build --check -f Dockerfile .` could not be completed locally because Docker Desktop's Linux engine is not running: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
**Next**: Validate a real image build/run when a container engine is available, then prove health/readiness, generated secret persistence, setup/settings persistence, and asset-degraded/real-asset readiness through the container.

### 2026-05-05 - Engine-Aware Release Script Slice
**Objective**: Add the Windows-first helper scripts expected in the GitHub Release ZIP package without hard-coding TowerScout to Docker Desktop.
**Context**: The finalized `TASK-025` direction requires start, stop, logs, and status scripts that can work with Docker or Podman after runtime-host validation. The Compose files now define the common runtime contract, so scripts should be thin wrappers over Compose rather than a separate launcher implementation.
**Decision**: Add PowerShell scripts as the first supported helper surface because v1 targets Windows 11/AMD64. Default engine selection prefers Docker when both commands are present, but each script accepts `-Engine docker` or `-Engine podman` so the Podman spike can validate the same package shape.
**Execution**:
- Added `scripts/lib/TowerScoutCompose.ps1` with shared repo-root, engine discovery, and Compose invocation helpers.
- Added `scripts/start.ps1` with optional `-Build` support for developer/support local builds.
- Added `scripts/stop.ps1`, `scripts/logs.ps1`, and `scripts/status.ps1`.
- Made `status.ps1` call Compose `ps` and then poll `/api/readiness`, returning nonzero for fatal or unreachable readiness.
**Output**:
- The release-package baseline now has Windows-first start/stop/logs/status commands.
- The scripts use the same `compose.yaml` named-volume runtime profile as release runs and can opt into `compose.build.yaml` for local builds.
- The scripts remain engine-aware while Podman remains a release-gated compatibility claim.
**Validation**:
- PowerShell AST parse of `scripts/lib/TowerScoutCompose.ps1`, `scripts/start.ps1`, `scripts/stop.ps1`, `scripts/logs.ps1`, and `scripts/status.ps1` -> passed
- `git diff --check -- scripts Dockerfile .dockerignore compose.yaml compose.build.yaml .env.example webapp\towerscout.py tests\unit\test_flask_routes.py .agent_work\tasks\active\TASK-025-docker-containerization.md .agent_work\current-tasks.md` -> passed
**Next**: Add user-facing quick-start/runtime documentation and then validate a real container build/run when a Docker or Podman engine is available.

### 2026-05-05 - OCI Quick-Start Documentation Slice
**Objective**: Add release-package documentation outside `.agent_work` so the Compose files and scripts have a user/support-facing operating guide.
**Context**: The GitHub Release ZIP contract requires quick-start guidance, technical runtime-contract documentation, persistence notes, asset handling, engine caveats, and sensitive local data warnings. The task-local runtime contract is useful for implementation evidence, but release packages need concise root-level docs.
**Decision**: Add `docs/oci-quick-start.md` for normal/support operation and `docs/oci-runtime-contract.md` for the technical runtime summary. Keep Podman language release-gated and avoid promising unsupported v1 environments.
**Execution**:
- Created `docs/oci-quick-start.md` covering supported target, package contents, first run, developer build, engine selection, status/logs, named volumes, asset handling, and stop behavior.
- Created `docs/oci-runtime-contract.md` covering startup, health/readiness, writable paths, secret-key persistence, asset checks, upload limit, and CI versus release-candidate validation split.
**Output**:
- Release-package docs now match the engine-aware OCI contract and named-volume Compose profile.
- Sensitive local data surfaces are called out in the user-facing quick start.
**Validation**:
- `python .agent_work\scripts\validate_agent_work.py` -> passed
- `git diff --check -- docs scripts Dockerfile .dockerignore compose.yaml compose.build.yaml .env.example webapp\towerscout.py tests\unit\test_flask_routes.py .agent_work\tasks\active\TASK-025-docker-containerization.md .agent_work\current-tasks.md` -> passed
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py tests\unit\test_assets.py tests\unit\test_config.py -q -p no:cacheprovider` -> `35 passed, 8 warnings`
**Next**: Run final validation, then continue with real container engine build/run validation when Docker or Podman is available.

### 2026-05-07 - Docker Desktop Build And Runtime Validation
**Objective**: Validate the Docker-compatible image and Compose runtime now that Docker Desktop's Linux engine is available locally.
**Context**: Earlier validation could only run Dockerfile syntax and Compose normalization because Docker Desktop was not running. The owner confirmed Docker Desktop is now up, enabling real image build/start/restart validation.
**Decision**: Validate the source-checkout developer/support path with `compose.build.yaml` and asset-light startup. Keep release-image validation separate because `ghcr.io/towerscout/towerscout:latest` is not published or accessible yet.
**Execution**:
- Ran Dockerfile check.
- Built `towerscout:local` with `docker compose -f compose.yaml -f compose.build.yaml build towerscout`.
- Started the container with `docker compose -f compose.yaml -f compose.build.yaml up -d towerscout`.
- Queried `/api/health` and `/api/readiness` on `http://127.0.0.1:5000`.
- Restarted the container and compared SHA-256 hashes of the persisted `FLASK_SECRET_KEY` line before and after restart without printing the secret.
- Validated `scripts/start.cmd -Engine docker -Build`, `scripts/status.cmd -Engine docker`, `scripts/logs.cmd -Engine docker -Tail 5`, and `scripts/stop.cmd -Engine docker`.
- Added `.cmd` wrappers after direct `.ps1` execution was blocked by the default Windows execution policy.
**Output**:
- Dockerfile check completed with no warnings.
- Local image built successfully as `towerscout:local`.
- Built image ID: `sha256:2c483acc68e6609ceaeb3db79b58ca3906668f71fe4401f251267f91efcab7d5`.
- Built image size: `2798228750` bytes.
- Docker Compose reports `towerscout-towerscout-1` as `healthy` with `0.0.0.0:5000->5000/tcp`.
- `/api/health` returned `{"service":"towerscout","status":"ok"}`.
- `/api/readiness` returned HTTP 200 with state `setup_required`, `secret_key_persisted: true`, all runtime paths writable, asset manifest version `towerscout-v1-assets-2026-05-05`, and expected missing-asset recovery guidance.
- Persisted secret hash remained stable across restart.
- `status.cmd` prints Compose status and readiness JSON; `logs.cmd` prints recent container logs.
**Validation**:
- `docker build --check -f Dockerfile .` -> passed, no warnings
- `docker compose -f compose.yaml -f compose.build.yaml build towerscout` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml up -d towerscout` -> passed
- `curl.exe -s http://127.0.0.1:5000/api/health` -> `{"service":"towerscout","status":"ok"}`
- `curl.exe -s -i http://127.0.0.1:5000/api/readiness` -> HTTP 200, `state: setup_required`, assets `degraded`, config `secret_key_persisted: true`
- Secret persistence check -> `secret_persistence=pass`
- `.\scripts\start.cmd -Engine docker -Build` -> passed
- `.\scripts\status.cmd -Engine docker` -> passed
- `.\scripts\logs.cmd -Engine docker -Tail 5` -> passed
- `.\scripts\stop.cmd -Engine docker` -> passed, followed by restart through `start.cmd -Engine docker -Build`
**Issues Identified**:
- Direct `.ps1` helper execution is blocked on this Windows host by execution policy. Remediated by adding `.cmd` wrappers and updating quick-start docs to use them by default.
- `scripts/start.cmd -Engine docker` without `-Build` tries the release-image path and fails until a published/pinned GHCR image exists. This is expected for source checkout validation; release validation remains pending.
- Build output reported existing npm audit findings from the frontend dependency set: one moderate and one high vulnerability. This did not block the image build but should be tracked in dependency/security follow-up.
**Next**: Validate release-image packaging after GHCR publication/pinning, add asset import/bootstrap validation, then run real-asset readiness and detection smoke inside the container.

### 2026-05-07 - Docker Named-Volume Asset Import And Hash Validation
**Objective**: Validate that local release assets can be imported into the Docker named-volume profile and verified by TowerScout readiness.
**Context**: The prior container run proved asset-light startup and degraded readiness. The next gate is proving the same named-volume profile can receive the existing local model and ZIP-code assets, clear the asset-degraded state, and pass SHA-256 verification through the runtime manifest.
**Decision**: Use the existing local `webapp/model_params/` and `webapp/data/` assets as the asset-bundle source for this validation pass. Copy them into the running container's mounted named volumes with `docker compose cp`, then recreate the container once with `TOWERSCOUT_VERIFY_ASSET_HASHES=1` to validate endpoint-level hash checks. Return the running container to normal non-hashing readiness afterward so routine status checks stay fast.
**Execution**:
- Confirmed local asset sources exist:
  - `webapp/model_params/yolov5/newest.pt` -> `175084429` bytes
  - `webapp/model_params/EN/b5_unweighted_best.pt` -> `118567303` bytes
  - `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp` -> `822559684` bytes
- Copied `webapp/model_params/.` into `/app/webapp/model_params/`.
- Copied `webapp/data/.` into `/app/webapp/data/`.
- Ran in-container manifest preflight without hashes.
- Recreated the container with `TOWERSCOUT_VERIFY_ASSET_HASHES=1`.
- Queried `/api/health` and `/api/readiness`.
- Ran explicit in-container `ts_assets.build_asset_status(verify_hashes=True)`.
- Verified the in-container model catalog loads and sees `newest`.
- Recreated the container with `TOWERSCOUT_VERIFY_ASSET_HASHES=0` after validation.
**Output**:
- Copied asset footprint inside volumes:
  - `/app/webapp/model_params` -> `281M`
  - `/app/webapp/data` -> `788M`
- In-container asset preflight without hashes returned `ok`, no missing assets, no corrupt assets, no optional missing assets.
- Hash-verified readiness returned:
  - `state: setup_required`
  - `asset_status: ok`
  - `verify_hashes: true`
  - `missing: []`
  - `corrupt: []`
  - `optional_missing: []`
  - `secret_key_persisted: true`
  - `manifest: towerscout-v1-assets-2026-05-05`
- Explicit in-container hash verification returned `ok`, `verify_hashes: True`, no missing/corrupt/optional-missing assets.
- `towerscout.load_model_catalog()` returned `True` and model catalog keys included `newest`.
- After returning to normal readiness mode, the container remained healthy and readiness reported `asset_status: ok`, `verify_hashes: false`, no missing/corrupt assets.
**Validation**:
- `docker compose -f compose.yaml -f compose.build.yaml cp webapp/model_params/. towerscout:/app/webapp/model_params/` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml cp webapp/data/. towerscout:/app/webapp/data/` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout python -c "import ts_assets; s=ts_assets.build_asset_status(verify_hashes=False); ..."` -> `ok`, `[]`, `[]`, `[]`
- `TOWERSCOUT_VERIFY_ASSET_HASHES=1 docker compose -f compose.yaml -f compose.build.yaml up -d --force-recreate towerscout` -> passed
- `GET /api/health` -> `{"service":"towerscout","status":"ok"}`
- Hash-verified `GET /api/readiness` -> assets `ok`, no missing/corrupt assets, secret persisted
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout python -c "import ts_assets; s=ts_assets.build_asset_status(verify_hashes=True); ..."` -> `ok`, `True`, `[]`, `[]`, `[]`
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout python -c "import towerscout; print(towerscout.load_model_catalog()); print(sorted(towerscout.engines.keys()))"` -> `True`, `['newest']`
- `TOWERSCOUT_VERIFY_ASSET_HASHES=0 docker compose -f compose.yaml -f compose.build.yaml up -d --force-recreate towerscout` -> passed
**Issues Identified**:
- This validates manual/local asset import into named volumes, not a packaged download/bootstrap script yet.
- Readiness still reports `setup_required` because provider configuration has not been saved in the container. This is expected and will be the next persistence validation slice.
**Next**: Validate Setup Wizard/Settings persistence across container restart, then run a containerized `TASK-052` smoke path with real assets present.

### 2026-05-07 - Settings Persistence And Google TLS Finding
**Objective**: Validate saved provider configuration persistence across container restart and investigate Google key validation failure in the container.
**Context**: The owner entered an Azure Maps key through the containerized UI and confirmed it worked. Google key validation returned `502 BAD GATEWAY` with the UI message `Could not reach the provider validation service.`
**Decision**: Use the saved Azure configuration to validate Setup/Settings persistence without printing secret values. Treat the Google failure as a container TLS trust issue rather than a key-validity issue, because the failure occurs before Google can evaluate the key.
**Execution**:
- Inspected container logs for the failed Google validation.
- Tested Google HTTPS reachability from inside the container without an API key.
- Compared certifi and system CA bundle behavior from inside the container.
- Patched log and structured-error sanitization to prevent provider keys from leaking through exception tracebacks or API error payload causes.
- Added Compose environment support and docs for `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, and last-resort `TOWERSCOUT_ALLOW_INSECURE_TLS`.
- Added `.cmd`/docs support earlier remains the Windows-first helper path.
- Rebuilt and restarted `towerscout:local`.
- Triggered a fake Google-shaped key validation failure and scanned recent logs for the fake key.
- Restarted the container and verified the saved Azure key line stayed stable by SHA-256 hash without printing the key.
**Output**:
- Google validation failure root cause: TLS verification failure contacting `maps.googleapis.com`: `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`.
- The same TLS failure occurs without a key and with both certifi and `/etc/ssl/certs/ca-certificates.crt`, which points to a host/network TLS inspection CA not trusted by the container rather than an invalid Google key.
- Raw provider-key leakage through exception tracebacks was fixed and validated with a fake key.
- Azure provider configuration persisted across container restart.
- After restart, readiness reported:
  - `state: ready`
  - `assets: ok`
  - `azure_configured: true`
  - `google_configured: false`
  - `secret_key_persisted: true`
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_logging_sanitization.py tests\unit\test_error_sanitization.py tests\unit\test_config.py -q -p no:cacheprovider` -> `23 passed, 9 warnings, 5 subtests passed`
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_logging_sanitization.py tests\unit\test_error_sanitization.py -q -p no:cacheprovider` -> `11 passed, 1 warning, 5 subtests passed`
- `docker compose -f compose.yaml -f compose.build.yaml up -d --build --force-recreate towerscout` -> passed
- Fake Google key validation failure log scan -> `fake_key_not_found_in_recent_logs`
- Azure persistence restart check -> `azure_hash_stable: true`, `readiness_state: ready`, `assets: ok`, `azure_configured: true`, `secret_key_persisted: true`
**Issues Identified**:
- A real Google key was attempted before the redaction fix, so the operator should rotate that Google key if there is any chance the container logs are retained or shared.
- Google validation remains blocked in this Docker environment until the local TLS inspection/root CA is trusted in the container or an explicit insecure validation workaround is enabled.
- `TOWERSCOUT_ALLOW_INSECURE_TLS=1` should be treated only as a local validation fallback, not the release default.
**Next**: Add or validate a documented local CA import procedure if Google validation is required in this environment; otherwise proceed with containerized `TASK-052` smoke using the validated Azure configuration and real assets.

### 2026-05-07 - Containerized TASK-052 Smoke Validation
**Objective**: Run the maintained `TASK-052` bounded detection-readiness smoke inside the Docker container with real assets present.
**Context**: Docker named-volume asset import is validated, Azure configuration persists, and readiness is `ready`. The next validation gate is proving the containerized app can load the real local YOLO runtime and reach the expected controlled imagery-failure boundary.
**Decision**: Add a reusable `scripts/validate_container_task052_smoke.py` helper that mirrors the host-side `TASK-052` smoke while executing inside the built image. Copy it into the running container for validation rather than baking test code into the release image.
**Execution**:
- Added `scripts/validate_container_task052_smoke.py`.
- Ran local syntax validation for the script.
- Copied the script into the running container at `/tmp/validate_container_task052_smoke.py`.
- Executed it from `/app/webapp` with `PYTHONPATH=/app/webapp`.
- Verified readiness and Docker health after the smoke.
**Output**:
- The first execution attempt failed with `ModuleNotFoundError: No module named 'towerscout'` because Python used `/tmp` as the import root. Re-running with `PYTHONPATH=/app/webapp` fixed the validation harness path without changing app behavior.
- The smoke loaded the real container-mounted YOLO model at `/app/webapp/model_params/yolov5/newest.pt`.
- The app reached the expected controlled imagery failure boundary and returned `502`.
- Progress title was `Imagery download failed`.
- Container remained healthy afterward.
- Readiness after the smoke remained `ready`, assets `ok`, Azure configured, persisted secret present, no missing/corrupt assets.
**Validation**:
- `.\.venv\Scripts\python.exe -m py_compile scripts\validate_container_task052_smoke.py` -> passed
- `git diff --check -- scripts\validate_container_task052_smoke.py` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml cp scripts/validate_container_task052_smoke.py towerscout:/tmp/validate_container_task052_smoke.py` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout sh -c "cd /app/webapp && PYTHONPATH=/app/webapp python /tmp/validate_container_task052_smoke.py"` -> passed
- Smoke output:
  - `container_task052_smoke=pass`
  - `engine_id=newest`
  - `model_path=/app/webapp/model_params/yolov5/newest.pt`
  - `response_status=502`
  - `progress_title=Imagery download failed`
- Post-smoke readiness -> `state: ready`, `assets: ok`, `azure_configured: true`, `secret_key_persisted: true`, no missing/corrupt assets
- Post-smoke Docker status -> container `healthy`
**Issues Identified**:
- Initial smoke validation surfaced an Ultralytics warning because `/root/.config/Ultralytics` was not writable. Remediated by setting `YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics` in the image and Compose profile and ensuring that directory exists at app startup.
**Next**: Continue with packaged asset bootstrap/import scripting and release-image/GHCR validation.

### 2026-05-07 - YOLO Config Directory Container Fix
**Objective**: Remove the non-blocking Ultralytics first-run config warning from containerized model-load validation.
**Context**: The containerized `TASK-052` smoke passed, but Ultralytics warned that its default config path was unwritable and fell back to `/tmp/Ultralytics`.
**Decision**: Persist Ultralytics config under the existing cache volume rather than leaving it in `/tmp` or adding a new persistence surface.
**Execution**:
- Added `YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics` to the Dockerfile environment.
- Added `YOLO_CONFIG_DIR` to `compose.yaml` and `.env.example`.
- Documented the setting in `docs/oci-runtime-contract.md`.
- Added `towerscout.ensure_yolo_config_dir()` and a focused unit test so the configured directory is created before model loading.
- Rebuilt and restarted the container.
- Re-ran the containerized `TASK-052` smoke and failed the command if the prior unwritable-config warning appeared.
**Output**:
- Re-run smoke passed with `container_task052_smoke=pass`.
- Ultralytics created settings at `/app/webapp/cache/ultralytics/Ultralytics/settings.json`.
- The prior `user config directory ... is not writable` warning did not recur.
- Post-smoke readiness remained `ready`, assets `ok`, Azure configured, and secret persisted.
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py -q -p no:cacheprovider` -> `16 passed`
- `docker compose -f compose.yaml -f compose.build.yaml up -d --build --force-recreate towerscout` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout sh -c "cd /app/webapp && PYTHONPATH=/app/webapp python /tmp/validate_container_task052_smoke.py"` -> passed, no unwritable-config warning
- Post-smoke readiness -> `state: ready`, `assets: ok`, `azure_configured: true`, `secret_key_persisted: true`
**Next**: Continue with packaged asset bootstrap/import scripting, release-image/GHCR validation, and Podman compatibility work.

### 2026-05-07 - Packaged Asset Import Helper
**Objective**: Add and validate a release-package helper for importing model and ZIP-code assets into the Compose named-volume profile.
**Context**: Manual `docker compose cp` asset import was validated earlier, but `TASK-025` requires a packaged path normal users/support staff can run from a GitHub Release ZIP. The expected release bundle layout is `assets/model_params/` and `assets/data/`.
**Decision**: Add a Windows-first `import-assets` helper that starts the service if needed, copies asset directories into the running service's mounted volumes, and verifies the runtime manifest in-container. Keep SHA-256 verification optional because it is appropriate for release/support validation but expensive for routine use.
**Execution**:
- Added `scripts/import-assets.ps1`.
- Added `scripts/import-assets.cmd` so Windows users are not blocked by PowerShell execution policy.
- Updated `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md` with asset bundle layout and import commands.
- Validated PowerShell parsing.
- Ran the helper against the current source-checkout asset layout with `-Source webapp -Engine docker -Build -VerifyHashes`.
**Output**:
- The import helper copied `webapp/model_params/.` to `/app/webapp/model_params/`.
- The import helper copied `webapp/data/.` to `/app/webapp/data/`.
- In-container manifest verification returned:
  - `asset_status=ok`
  - `verify_hashes=True`
  - `missing=`
  - `corrupt=`
  - `optional_missing=`
- Readiness after import remained `ready`, assets `ok`, Azure configured, secret persisted, and no missing/corrupt assets.
**Validation**:
- PowerShell AST parse of helper scripts -> passed
- `git diff --check -- scripts\import-assets.ps1 scripts\import-assets.cmd docs\oci-quick-start.md docs\oci-runtime-contract.md` -> passed
- `.\scripts\import-assets.cmd -Source webapp -Engine docker -Build -VerifyHashes` -> passed
- `GET /api/readiness` after import -> `state: ready`, `assets: ok`, `azure_configured: true`, `secret_key_persisted: true`, no missing/corrupt assets
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout sh -c "test -f /app/webapp/cache/ultralytics/Ultralytics/settings.json && echo yolo_config_present"` -> `yolo_config_present`
**Issues Identified**:
- This provides local/release-folder import, not a network downloader. If assets are hosted externally, a future helper still needs download, checksum, and staged activation behavior.
**Next**: Continue with release-image/GHCR digest validation and Podman compatibility spike, or add a network asset downloader if the release process requires direct object-storage/bootstrap support.

### 2026-05-07 - Local Release Package Assembly Helper
**Objective**: Add and validate the GitHub Release control-package assembly path without requiring GHCR credentials or a published release image.
**Context**: The release package contract requires a ZIP containing Compose runtime files, `.env` template, Windows helper wrappers, docs, asset manifest metadata, checksums, and a pinned image reference. The actual GHCR image digest is not available yet, so this slice validates package assembly and marks digest pinning as the remaining release-image gate.
**Decision**: Add a Windows-first `package-release` helper that stages only release-control-plane files and writes image metadata/checksums. Keep large model/data assets out of the ZIP and include an `assets/README.txt` placeholder for the separate asset bundle layout.
**Execution**:
- Added `scripts/package-release.ps1`.
- Added `scripts/package-release.cmd` to avoid Windows PowerShell execution-policy friction.
- Updated `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md` with package contents, maintainer command, `IMAGE.txt`, `SHA256SUMS.txt`, and ZIP checksum behavior.
- Validated PowerShell parsing for the package helper and existing helper scripts.
- Built a local package under `.agent_work/pytest-temp/release-package/` using `-Image towerscout:local`.
- Verified required package files, `SHA256SUMS.txt`, ZIP creation, and `.zip.sha256` creation.
**Output**:
- The package helper stages:
  - `compose.yaml`
  - `.env.example`
  - `docs/oci-quick-start.md`
  - `docs/oci-runtime-contract.md`
  - `webapp/asset_manifest.v1.json`
  - `scripts/lib/TowerScoutCompose.ps1`
  - `scripts/start|stop|logs|status|import-assets` `.cmd` and `.ps1` helpers
  - `assets/README.txt`
  - `IMAGE.txt`
  - `SHA256SUMS.txt`
- Local validation produced `towerscout-task025-local-20260507114315.zip` plus `towerscout-task025-local-20260507114315.zip.sha256` in scratch space.
- `IMAGE.txt` recorded `Image: towerscout:local` and an empty digest, correctly marking the package as local-validation only.
**Validation**:
- PowerShell AST parse of `scripts/package-release.ps1` and helper scripts -> passed
- `git diff --check -- scripts\package-release.ps1 scripts\package-release.cmd docs\oci-quick-start.md docs\oci-runtime-contract.md` -> passed
- `.\scripts\package-release.cmd -Version task025-local-20260507114315 -Image towerscout:local -OutputDir .agent_work\pytest-temp\release-package` -> passed
- Required package file verification -> passed
- Package ZIP and `.zip.sha256` verification -> passed
**Issues Identified**:
- This validates release control-package assembly, not registry publication.
- Release-image validation remains blocked until a GHCR image exists and can be referenced by immutable digest.
- Optional OCI image archive packaging is still a documented fallback concept, not implemented in this helper.
**Next**: Continue with GHCR image publication/digest validation when credentials and repository target are available, or run the Podman compatibility spike if Podman is installed and configured.

### 2026-05-07 - Windows Podman Runtime Compatibility Spike
**Objective**: Validate the TowerScout Compose/runtime contract against the installed Windows Podman WSL engine without relying on a published GHCR image.
**Context**: `TASK-025` requires Podman Desktop / Podman machine validation or explicit risk acceptance before Podman is promised as the supported open-source runtime. Docker Desktop is also installed on this host, so the spike needed to distinguish the Podman engine result from the Compose-provider dependency.
**Decision**: Reuse the already-built `towerscout:local` image by exporting it from Docker and loading it into Podman. Run the release-style Compose profile through `scripts/start.cmd -Engine podman` on port `5001` to avoid the active Docker validation service on port `5000`. Validate asset-light startup, named volumes, asset import, readiness, and the maintained containerized `TASK-052` smoke.
**Execution**:
- Confirmed Podman is installed at `C:\Users\bg90\AppData\Local\Programs\Podman\podman.exe`.
- Started `podman-machine-default`, a rootless WSL machine.
- Verified the Docker-compatible API path through `npipe:////./pipe/podman-machine-default`.
- Exported `towerscout:local` from Docker to a scratch tar and loaded it into Podman.
- Started TowerScout with `TOWERSCOUT_IMAGE=towerscout:local`, `TOWERSCOUT_PORT=5001`, `TOWERSCOUT_CONTAINER_ENGINE=podman`, and `.\scripts\start.cmd -Engine podman`.
- Queried health/readiness and checked the runtime reported `container_engine: podman`.
- Ran `.\scripts\import-assets.cmd -Source webapp -Engine podman -VerifyHashes`.
- Copied and ran `scripts/validate_container_task052_smoke.py` inside the Podman container.
- Stopped the Podman Compose project and removed the scratch image-transfer tar.
**Output**:
- Podman client: `5.8.2`, Windows/AMD64.
- Podman server: `5.8.2`, Linux/AMD64 on WSL2.
- Podman machine: rootless WSL, user-mode networking, API forwarding on `npipe:////./pipe/podman-machine-default`.
- `podman compose` worked, but delegated to Docker Desktop's bundled `docker-compose.exe`; Podman sets up the provider to talk to the Podman socket.
- Asset-light Podman startup succeeded on `http://127.0.0.1:5001`.
- Readiness returned `state: setup_required`, expected asset-degraded recovery guidance, persisted secret present, and writable runtime paths.
- Podman asset import returned `asset_status=ok`, `verify_hashes=True`, no missing/corrupt/optional-missing assets.
- Containerized `TASK-052` smoke passed in Podman:
  - `container_task052_smoke=pass`
  - `engine_id=newest`
  - `model_path=/app/webapp/model_params/yolov5/newest.pt`
  - `response_status=502`
  - `progress_title=Imagery download failed`
**Validation**:
- `podman machine start podman-machine-default` -> passed
- `docker --host npipe:////./pipe/podman-machine-default version` -> passed against Podman server
- `podman load -i .agent_work\pytest-temp\podman-image-transfer\towerscout-local.tar` -> loaded `docker.io/library/towerscout:local`
- `.\scripts\start.cmd -Engine podman` with `TOWERSCOUT_PORT=5001` -> passed
- `GET /api/health` on port `5001` -> `{"service":"towerscout","status":"ok"}`
- `GET /api/readiness` on port `5001` -> setup-required/degraded asset-light state with writable paths and persisted secret
- `.\scripts\import-assets.cmd -Source webapp -Engine podman -VerifyHashes` -> passed
- `podman compose -f compose.yaml exec -T towerscout sh -c "cd /app/webapp && PYTHONPATH=/app/webapp python /tmp/validate_container_task052_smoke.py"` -> passed
- `.\scripts\stop.cmd -Engine podman` -> passed
**Issues Identified**:
- This validates the Podman engine path on a host that also has Docker Desktop installed.
- `podman compose` used Docker Desktop's bundled `docker-compose.exe` as the external Compose provider. A follow-up should test the same Podman path while the Docker Desktop engine is stopped, and a Docker-Desktop-free Podman release path still needs validation with `podman-compose` or another approved Compose provider.
- This spike reused an image transferred from Docker rather than pulling a published GHCR image by digest.
- Podman provider setup persisted assets in Podman named volumes; volumes were intentionally not deleted after the spike.
**Next**: Validate GHCR pull-by-digest under Docker and Podman after image publication; separately validate Podman with the Docker Desktop engine stopped and validate a Docker-Desktop-free Podman Compose provider before promising Podman as the normal open-source runtime.

### 2026-05-07 - Google TLS Inspection CA Import Validation
**Objective**: Validate the secure Google provider TLS fix for the containerized app behind local TLS inspection without disabling certificate verification.
**Context**: Google key validation previously failed with `502 BAD GATEWAY` and container logs showed `CERTIFICATE_VERIFY_FAILED` for `maps.googleapis.com`. A peer-certificate probe inside the container showed Google traffic was being intercepted by Zscaler and issued by the CDC `CDC-G2-ZSH` certificate chain.
**Decision**: Add a release/support helper that imports a Windows CA certificate by thumbprint or a PEM/CER/CRT file into the persistent config volume, builds a combined CA bundle from the container's default Debian bundle plus the local CA chain, and verifies Google TLS with an invalid test key. Keep `TOWERSCOUT_ALLOW_INSECURE_TLS=1` as a last-resort local validation fallback only.
**Execution**:
- Confirmed the baseline container still failed Google HTTPS with `CERTIFICATE_VERIFY_FAILED` using `/etc/ssl/certs/ca-certificates.crt`.
- Inspected the peer certificate inside the container with `openssl s_client`.
- Identified the intercepted Google certificate as `subject=CN = upload.video.google.com, O = Zscaler Inc., OU = Zscaler Inc.` with issuer `CDC-G2-ZSH`.
- Located `CDC-G2-ZSH` in the Windows certificate store with thumbprint `C69667336E90D872FA44ACE4EB25412E52F406B9`.
- Added `scripts/import-tls-ca.ps1` and `scripts/import-tls-ca.cmd`.
- Updated the helper after validation exposed two issues:
  - initial shell quoting for inline Python verification was fragile through Windows Compose
  - importing only `CDC-G2-ZSH` was insufficient because the container also needed the `CDC-G2` issuer
- Updated the helper to run verification without shell quoting and to include the Windows certificate chain for thumbprint imports.
- Imported the CDC/Zscaler CA chain into `/app/webapp/config/certs/local-ca.pem` and built `/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- Recreated the Docker container with `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem` and `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- Posted an intentionally invalid Google key to TowerScout's `/api/config/validate-key` endpoint to prove provider validation now reaches Google.
- Owner re-entered the real Google key through the containerized UI after the CA bundle fix.
**Output**:
- CA helper verification returned:
  - `google_tls_status=200`
  - `google_tls_body={ "error_message" : "The provided API key is invalid. ", "results" : [], ... }`
- TowerScout validation endpoint returned HTTP `200` with:
  - `valid: false`
  - `provider: google`
  - `message: Google Maps validation failed with status 403.`
- The result confirms the failure mode changed from network/TLS `502` to normal provider invalid-key handling.
- Owner confirmed real Google key entry worked in the UI after the CA bundle fix.
**Validation**:
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout python -c "...requests.get('https://maps.googleapis.com/...')"` before CA import -> reproduced `CERTIFICATE_VERIFY_FAILED`
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout sh -c "echo | openssl s_client ..."` -> identified Zscaler/CDC certificate issuer
- Windows certificate-store lookup for `CDC-G2-ZSH` -> found thumbprint `C69667336E90D872FA44ACE4EB25412E52F406B9`
- PowerShell AST parse of `scripts/import-tls-ca.ps1` -> passed
- `.\scripts\import-tls-ca.cmd -Engine docker -Thumbprint C69667336E90D872FA44ACE4EB25412E52F406B9` -> passed after chain-export fix
- Container recreate with combined CA bundle environment variables -> passed
- `POST /api/config/validate-key` with invalid Google test key -> HTTP `200`, provider-level invalid-key response, no `502`
- Owner UI validation with real Google key after CA bundle fix -> passed
**Issues Identified**:
- The helper currently imports and verifies the CA bundle but does not edit `.env`; release/support docs instruct operators to set `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` to the combined bundle path and recreate the container.
- Real Google key validation through the UI now succeeds after the CA bundle import and container recreate.
**Next**: Persist the combined CA bundle path in the release `.env` or support environment so the Google TLS fix survives future container recreates. Continue GHCR image digest validation when a published image target is available.

### 2026-05-07 - GHCR Publish Workflow And Digest Package Preparation
**Objective**: Prepare the GHCR image publication and digest-pinned release-package path, then assess what blocks real digest validation from this workstation.
**Context**: The release package contract requires a pinned GHCR image digest. The existing CI only builds a local Docker image on `main` and does not publish a container image. The repo remote is `https://github.com/J-Schulein/TowerScout.git`, so the concrete GHCR target should be `ghcr.io/j-schulein/towerscout`.
**Decision**: Add a manual GHCR publish workflow with `packages: write`, align Compose/release defaults with `ghcr.io/j-schulein/towerscout`, and validate that `package-release` can generate digest-pinned package metadata locally. Treat real GHCR pull-by-digest validation as blocked until the workflow is pushed/run or package-scoped credentials are available.
**Execution**:
- Checked repository remote and branch.
- Checked GHCR manifests for `ghcr.io/towerscout/towerscout:latest` and `ghcr.io/j-schulein/towerscout:latest`.
- Checked GitHub CLI authentication scope.
- Added `.github/workflows/container-publish.yml` as a manual `workflow_dispatch` publisher.
- Updated `compose.yaml`, `.env.example`, `scripts/package-release.ps1`, `docs/oci-quick-start.md`, and `docs/oci-runtime-contract.md` to use `ghcr.io/j-schulein/towerscout`.
- Ran `package-release` with a placeholder digest to validate pinned metadata output.
**Output**:
- `docker manifest inspect ghcr.io/towerscout/towerscout:latest` -> `denied`
- `docker manifest inspect ghcr.io/j-schulein/towerscout:latest` -> `denied`
- `gh auth status` shows account `J-Schulein` is logged in, but available token scopes are `gist`, `read:org`, `repo`, and `workflow`; package scopes are not present.
- Manual workflow target:
  - image: `ghcr.io/${GITHUB_REPOSITORY,,}`
  - concrete repo target: `ghcr.io/j-schulein/towerscout`
  - platform: `linux/amd64`
  - output: `image-metadata.json` artifact plus digest reference in the workflow summary
- Local package validation with placeholder digest produced:
  - `Image: ghcr.io/j-schulein/towerscout@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
  - `.env.example` with `TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout@sha256:...`
  - `.env.example` with `TOWERSCOUT_IMAGE_DIGEST=sha256:...`
  - release package includes `scripts/import-tls-ca.cmd` and `scripts/import-tls-ca.ps1`
**Validation**:
- PowerShell AST parse of `scripts/import-tls-ca.ps1` and `scripts/package-release.ps1` -> passed
- `git diff --check -- .github\workflows\container-publish.yml compose.yaml .env.example scripts\package-release.ps1 scripts\import-tls-ca.ps1 scripts\import-tls-ca.cmd docs\oci-quick-start.md docs\oci-runtime-contract.md .agent_work\tasks\active\TASK-025-docker-containerization.md .agent_work\current-tasks.md` -> passed
- `.\scripts\package-release.cmd -Version task025-ghcr-local-20260507121903 -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -OutputDir .agent_work\pytest-temp\release-package` -> passed
- Package required-file check for `scripts\import-tls-ca.cmd`, `scripts\import-tls-ca.ps1`, `IMAGE.txt`, `.env.example`, and `SHA256SUMS.txt` -> passed
**Issues Identified**:
- Real GHCR digest validation is still blocked locally because no accessible image manifest exists yet and the current GitHub CLI token does not show package scopes.
- The publish workflow must be pushed and run, or an appropriately scoped GHCR token must be provided, before `docker pull ghcr.io/j-schulein/towerscout@sha256:<digest>` and release-image Compose validation can be completed.
**Next**: After publishing, validate Docker and Podman pull-by-digest paths and regenerate the release ZIP with the real digest. Continue real Google UI key validation after persisting the trusted CA bundle env vars.

### 2026-05-07 - Branch Publish Trigger For GHCR Validation
**Objective**: Make the GHCR publish workflow runnable before merge so Task-025 can validate pull-by-digest behavior from the feature branch.
**Context**: GitHub did not show the manual `workflow_dispatch` workflow in the Actions UI because the workflow file was only present on `feature/task-025-docker-baseline`, not the default branch.
**Decision**: Add a temporary branch-scoped `push` trigger for `feature/task-025-docker-baseline` and derive an RC tag automatically as `task-025-<short-sha>` for push events. Keep manual `workflow_dispatch` behavior for future release tags.
**Execution**:
- Added `push.branches: feature/task-025-docker-baseline` to `.github/workflows/container-publish.yml`.
- Updated the publish script to use `inputs.tag` only for `workflow_dispatch` and `task-025-${GITHUB_SHA::7}` for feature-branch pushes.
- Replaced the embedded Python heredoc with a one-line Python digest parser to avoid YAML/heredoc indentation fragility.
- Updated `docs/oci-quick-start.md` to describe the branch RC tag behavior.
**Output**:
- Next push to `feature/task-025-docker-baseline` should publish `ghcr.io/j-schulein/towerscout:task-025-<short-sha>`.
**Validation**:
- Pending local YAML parse and push-trigger run.
**Next**: Push the workflow update, wait for the publish run, capture the digest, and validate release Compose startup by digest.

### 2026-05-07 - Local Compose CA Bundle Persistence
**Objective**: Persist the validated TLS CA bundle configuration for local Docker Compose restarts without storing provider secrets in the repo.
**Context**: The containerized Google validation path worked after importing the CDC/Zscaler CA chain and recreating the container with `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` set to `/app/webapp/config/certs/towerscout-ca-bundle.pem`. The remaining local risk was that a later Compose recreate would fall back to the default Debian bundle unless the setting was persisted outside the one-off shell environment.
**Decision**: Create a local, git-ignored `.env` containing non-secret Compose/runtime settings only. Keep provider API keys in the container's persistent `webapp/config/.env` volume through Setup Wizard/Settings.
**Execution**:
- Confirmed repo-root `.env` did not exist and is ignored by `.gitignore`.
- Added local `.env` with:
  - `TOWERSCOUT_IMAGE=towerscout:local`
  - `TOWERSCOUT_CONTAINER_ENGINE=docker`
  - `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - non-secret runtime defaults
- Updated `.env.example` comments to point at the combined CA bundle path produced by `scripts/import-tls-ca.cmd`.
- Recreated the Docker container with `docker compose -f compose.yaml -f compose.build.yaml up -d --force-recreate towerscout` without ad hoc CA environment variables.
- Verified the recreated container inherited the CA bundle paths from local `.env`.
- Queried readiness and the Google validation endpoint after recreate.
**Output**:
- Recreated container environment includes:
  - `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - `TOWERSCOUT_CONTAINER_ENGINE=docker`
- Readiness after recreate returned:
  - `state: ready`
  - assets `ok`
  - `azure.configured: true`
  - `google.configured: true`
  - `secret_key_persisted: true`
- Invalid Google test-key validation returned HTTP `200` with provider-level invalid-key response, not TLS/network `502`.
**Validation**:
- `docker compose -f compose.yaml -f compose.build.yaml up -d --force-recreate towerscout` -> passed using local `.env`
- In-container env check for `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, and `TOWERSCOUT_CONTAINER_ENGINE` -> passed
- `GET /api/readiness` -> `ready`, assets `ok`, Azure configured, Google configured, persisted secret present
- `POST /api/config/validate-key` with invalid Google test key -> HTTP `200`, `valid: false`, `message: Google Maps validation failed with status 403.`
**Issues Identified**:
- Local `.env` is intentionally ignored and should not be committed.
- Release packages still need users/operators to copy `.env.example` to `.env` and set the CA bundle path after running `import-tls-ca.cmd` when their network performs TLS inspection.
**Next**: Continue with GHCR publish/digest validation when the workflow is available on GitHub, or proceed to Podman-with-Docker-engine-stopped validation if we want to advance the remaining local runtime gate first.

### 2026-05-07 - Podman Docker-Engine-Stopped Validation Attempt
**Objective**: Test whether the Podman Compose path works while the Docker Desktop engine is stopped.
**Context**: The prior Podman spike proved the TowerScout runtime works on the Podman WSL engine, but `podman compose` delegated to Docker Desktop's bundled `docker-compose.exe`. The next question was whether that Compose provider can still drive Podman when the Docker daemon itself is unavailable.
**Decision**: Stop the Docker Compose TowerScout service, terminate the `docker-desktop` WSL distro, start Podman, and run `scripts/start.cmd -Engine podman` on port `5001`. Treat the validation as passing only if Docker daemon access is unavailable while Podman Compose still starts TowerScout.
**Execution**:
- Confirmed `podman-compose` is not installed.
- Stopped the current Docker TowerScout container with `docker compose -f compose.yaml -f compose.build.yaml stop towerscout`.
- Ran `wsl --terminate docker-desktop`.
- Started `podman-machine-default`.
- Ran `docker version --format '{{.Server.Version}}'` to verify Docker daemon unavailability.
- Ran `.\scripts\start.cmd -Engine podman` with `TOWERSCOUT_IMAGE=towerscout:local`, `TOWERSCOUT_PORT=5001`, and `TOWERSCOUT_CONTAINER_ENGINE=podman`.
- Checked WSL running distributions and Podman readiness.
- Stopped the Podman Compose project and stopped the Podman machine.
- Attempted to restart the Docker TowerScout container.
**Output**:
- `podman-compose` was not found on PATH.
- `wsl --terminate docker-desktop` completed successfully, but `docker version` still returned server version `29.4.1`.
- `wsl --list --running` showed `docker-desktop` running again during the validation, along with Podman WSL distributions.
- Podman Compose start on port `5001` succeeded and readiness showed:
  - `runtime.container_engine: podman`
  - assets `ok`
  - writable runtime paths
  - state `setup_required` because this used Podman volumes, not the Docker config volume with saved provider keys
- The attempt is inconclusive for the Docker-engine-stopped gate because Docker Desktop restarted or stayed reachable.
- Restarting the Docker TowerScout container failed because Docker Desktop reported: `Docker Desktop is manually paused. Unpause it through the Whale menu or Dashboard.`
- After the owner unpaused/restarted Docker Desktop, the Docker TowerScout container restarted successfully on port `5000`.
**Validation**:
- `docker compose -f compose.yaml -f compose.build.yaml stop towerscout` -> passed
- `wsl --terminate docker-desktop` -> passed
- `docker version --format '{{.Server.Version}}'` after termination -> returned `29.4.1`, so Docker daemon was still reachable
- `.\scripts\start.cmd -Engine podman` with `TOWERSCOUT_PORT=5001` -> passed
- `.\scripts\status.cmd -Engine podman` -> passed with Podman readiness output
- `.\scripts\stop.cmd -Engine podman` -> passed
- `podman machine stop podman-machine-default` -> passed
- `docker compose -f compose.yaml -f compose.build.yaml up -d towerscout` -> blocked by Docker Desktop paused state
- After Docker Desktop was unpaused, `docker compose -f compose.yaml -f compose.build.yaml up -d towerscout` -> passed
- Restored Docker readiness -> `state: ready`, assets `ok`, Azure configured, Google configured, persisted secret present
- Restored Docker env check -> `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem`, `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
**Issues Identified**:
- This does not close the Docker-engine-stopped gate because Docker daemon access remained available after attempting to stop `docker-desktop`.
- Docker Desktop had to be unpaused in the UI before the Docker validation service could be restarted.
- A stronger follow-up should use a machine where Docker Desktop is fully quit/uninstalled or use a validated non-Docker Compose provider such as `podman-compose`.
**Next**: Keep the Docker-engine-stopped and Docker-Desktop-free Podman Compose-provider checks open; rerun on a host where Docker Desktop can be fully quit or unavailable without auto-restarting.

### 2026-05-07 - GHCR Digest Pull And Release Image Validation
**Objective**: Validate the real GHCR publish output by digest and regenerate the release package with an immutable image reference.
**Context**: The branch publish trigger ran successfully after the workflow YAML fix. `TASK-025` still needed proof that the published image can be resolved, pulled, and started without `compose.build.yaml`, and that release-package metadata can be generated with the real digest.
**Decision**: Use the successful feature-branch publish run as the release-candidate image source. Validate the pinned digest directly, then start a separate Compose project on port `5002` so the existing Docker validation service on port `5000` and its persisted keys/assets are not touched.
**Execution**:
- Retrieved workflow run `25511018110` artifact metadata from GitHub Actions.
- Downloaded `image-metadata.json` into `.agent_work/pytest-temp/ghcr-run-25511018110-verify`.
- Extracted published image `ghcr.io/j-schulein/towerscout:task-025-0b5d0a7` and digest `sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`.
- Ran `docker manifest inspect` and `docker pull` against the pinned digest.
- Started an isolated release-image Compose project with `TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`, `TOWERSCOUT_IMAGE_DIGEST=sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`, and `TOWERSCOUT_PORT=5002`.
- Queried `/api/health`, `/api/readiness`, and Compose status for the release-image project.
- Stopped and removed the temporary release-image container/network with `docker compose -p towerscout-ghcr-validate -f compose.yaml down`.
- Generated `towerscout-task025-ghcr-0b5d0a7.zip` with `scripts/package-release.cmd` using the real digest.
- Patched `.github/workflows/container-publish.yml` so future metadata artifacts use the resolved build tag for both branch push and manual dispatch runs.
- Pushed follow-up commit `03c6084` and confirmed workflow run `25511697887` succeeded with artifact `image-metadata-task-025-03c6084`.
**Output**:
- GHCR published image: `ghcr.io/j-schulein/towerscout:task-025-0b5d0a7`
- Pinned image: `ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`
- Manifest inspection returned an OCI image index with Linux/AMD64 manifest digest `sha256:a3df1bdae1dfc84598e41413002eacc92025ed05eb66a6ea18bc88862f594633`.
- Docker pull completed with digest `sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`.
- Release-image health on port `5002` returned `{"service":"towerscout","status":"ok"}`.
- Release-image readiness returned expected fresh-volume state: `setup_required`, assets `degraded`, writable runtime paths, persisted secret, and `version.image_digest` matching the pinned digest.
- Release package output:
  - `.agent_work/pytest-temp/release-package/towerscout-task025-ghcr-0b5d0a7`
  - `.agent_work/pytest-temp/release-package/towerscout-task025-ghcr-0b5d0a7.zip`
  - `.env.example` and `IMAGE.txt` pin `ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`.
- Follow-up workflow output:
  - run: `25511697887`
  - commit: `03c6084`
  - artifact: `image-metadata-task-025-03c6084`
**Validation**:
- GitHub Actions run `25511018110` -> success.
- `gh api repos/J-Schulein/TowerScout/actions/runs/25511018110/artifacts` -> found `image-metadata-` artifact.
- `gh run download 25511018110 --repo J-Schulein/TowerScout --name image-metadata-` -> passed.
- `docker manifest inspect ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30` -> passed.
- `docker pull ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30` -> passed.
- `docker compose -p towerscout-ghcr-validate -f compose.yaml up -d towerscout` using the pinned image -> passed; container reported healthy.
- `GET http://127.0.0.1:5002/api/health` -> passed.
- `GET http://127.0.0.1:5002/api/readiness` -> passed with expected fresh-release degraded/setup state and correct image digest.
- `scripts\package-release.cmd -Version task025-ghcr-0b5d0a7 -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30 -OutputDir .agent_work\pytest-temp\release-package` -> passed.
- `IMAGE.txt` and package `.env.example` digest checks -> passed.
- GitHub Actions run `25511697887` -> success.
- Artifact list for run `25511697887` -> `image-metadata-task-025-03c6084`.
**Issues Identified**:
- The first successful branch-triggered run uploaded the artifact as `image-metadata-` because the workflow used `${{ inputs.tag }}` for the artifact name on a `push` event. The follow-up workflow patch is validated by run `25511697887`.
- The Actions run emitted a warning that `docker/setup-buildx-action@v2` uses a deprecated Node.js 20 runtime. It is advisory for this task and should be handled in a future pinned-action review/update.
**Next**: Keep the clean Docker-Desktop-unavailable Podman validation as the remaining local runtime gate before promising Podman broadly. Track the Buildx Node 20 warning as future pinned-action maintenance.

### 2026-05-07 - Retire Temporary Branch Publish Trigger
**Objective**: Stop incidental GHCR image publication from routine feature-branch pushes after the pre-merge digest validation gate passed.
**Context**: The branch-scoped `push` trigger was added only because the manual workflow was not visible in the Actions UI before the workflow file existed on the default branch. It served its validation purpose, but keeping it would publish a new GHCR image for docs-only or task-tracker commits.
**Decision**: Remove the `push.branches: feature/task-025-docker-baseline` trigger and keep `.github/workflows/container-publish.yml` as an intentional `workflow_dispatch` publisher. Future automated publishing should use release or RC tag triggers rather than feature-branch pushes.
**Execution**:
- Removed the feature-branch `push` trigger from `.github/workflows/container-publish.yml`.
- Simplified the publish script to use manual workflow inputs for `tag` and `push_latest`.
- Updated `docs/oci-quick-start.md` to remove branch-push RC publishing guidance.
- Updated `current-tasks.md` to mark the temporary trigger retired.
**Output**:
- Routine pushes to `feature/task-025-docker-baseline` will no longer publish GHCR images.
- Manual release/RC publication remains available through `workflow_dispatch`.
**Validation**:
- `git diff --check -- .github\workflows\container-publish.yml docs\oci-quick-start.md .agent_work\current-tasks.md .agent_work\tasks\active\TASK-025-docker-containerization.md` -> passed.
- `python .agent_work\scripts\validate_agent_work.py` -> passed.
**Next**: Commit and push the cleanup. No follow-up publish run is expected from this cleanup because the branch trigger is removed.

### 2026-05-07 - Podman With Docker Desktop Engine Unavailable
**Objective**: Validate whether TowerScout can run through the Podman engine path while Docker Desktop is fully quit and the Docker daemon is unreachable.
**Context**: The earlier Docker-engine-stopped attempt was inconclusive because Docker Desktop restarted or stayed reachable. The owner quit Docker Desktop from the UI, allowing a cleaner check of Docker daemon unavailability before rerunning the Podman path.
**Decision**: Treat this validation as passing only if Docker daemon calls fail, `docker-desktop` is not among running WSL distributions, Podman starts TowerScout, readiness reports the Podman runtime, the containerized `TASK-052` smoke passes, and Docker remains unreachable afterward.
**Execution**:
- Verified `docker version` and `docker info` could see the Docker client only and failed to connect to `npipe:////./pipe/dockerDesktopLinuxEngine`.
- Verified `wsl --list --running` showed only `podman-net-usermode` and `podman-machine-default`.
- Verified Podman server `5.8.2` was reachable and `docker.io/library/towerscout:local` existed in the Podman image store.
- Ran `scripts\start.cmd -Engine podman` with `TOWERSCOUT_PORT=5001`, `TOWERSCOUT_IMAGE=towerscout:local`, and `TOWERSCOUT_CONTAINER_ENGINE=podman`.
- Checked Podman Compose status plus `/api/health` and `/api/readiness` on port `5001`.
- Confirmed `docker version` still failed to connect to the Docker daemon after Podman startup.
- Copied `scripts\validate_container_task052_smoke.py` into the running Podman container and executed it with `PYTHONPATH=/app/webapp` from `/app/webapp`.
- Stopped the Podman validation service with `scripts\stop.cmd -Engine podman`.
- Confirmed no Podman containers remained running and Docker daemon access still failed.
**Output**:
- Docker daemon unavailable:
  - `docker version` and `docker info` failed to connect to `dockerDesktopLinuxEngine`.
  - running WSL distros: `podman-net-usermode`, `podman-machine-default`.
- Podman runtime:
  - client/server version `5.8.2`.
  - container image `docker.io/library/towerscout:local`.
  - `podman compose` still used Docker Desktop's bundled `docker-compose.exe` as the external Compose provider, but it successfully drove the Podman socket without Docker daemon access.
- TowerScout Podman readiness:
  - health `{"service":"towerscout","status":"ok"}`.
  - readiness `state: setup_required`, assets `ok`, `runtime.container_engine: podman`, writable runtime paths, and persisted secret present.
- Containerized smoke:
  - `container_task052_smoke=pass`
  - `engine_id=newest`
  - `response_status=502`
  - `progress_title=Imagery download failed`
**Validation**:
- `docker version` before Podman start -> Docker client present, daemon unavailable.
- `docker info` before Podman start -> Docker client present, daemon unavailable.
- `wsl --list --running` -> no `docker-desktop`, only Podman WSL distributions.
- `podman info --format json` -> passed.
- `podman images` -> `docker.io/library/towerscout:local` present.
- `scripts\start.cmd -Engine podman` on port `5001` -> passed.
- `scripts\status.cmd -Engine podman` -> passed.
- `GET http://127.0.0.1:5001/api/health` -> passed.
- `GET http://127.0.0.1:5001/api/readiness` -> passed with Podman runtime and assets `ok`.
- `docker version` after Podman start -> still daemon unavailable.
- `podman exec -e PYTHONPATH=/app/webapp -w /app/webapp towerscout-towerscout-1 python /tmp/validate_container_task052_smoke.py` -> passed.
- `scripts\stop.cmd -Engine podman` -> passed.
- `podman ps` -> no running containers.
- `docker version` after stop -> still daemon unavailable.
**Issues Identified**:
- This closes the Docker-engine-unavailable Podman runtime gate on this host.
- It does not prove a Docker-Desktop-free host because the external Compose provider binary is still `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe`.
- A final broad Podman support claim should still validate `podman-compose` or another approved Compose provider on a host without Docker Desktop installed.
**Next**: Update final Task-025 validation status to treat Podman runtime support as validated on this host, with Docker-Desktop-free Compose-provider validation retained as a release-support caveat rather than a core container-runtime blocker.

### 2026-05-07 - Docker Desktop Restore After Podman Validation
**Objective**: Confirm the Docker validation service restores cleanly after the Docker-engine-unavailable Podman test.
**Context**: The owner restarted Docker Desktop after the Podman validation. The prior Docker service on port `5000` should resume without losing persisted keys, assets, secret, or the local TLS CA bundle configuration.
**Decision**: Verify Docker daemon reachability, Compose service health, HTTP health/readiness, and non-secret runtime environment values.
**Execution**:
- Checked Docker client/server versions.
- Inspected the Docker Compose service state.
- Queried `/api/health` and `/api/readiness` on port `5000`.
- Ran `docker compose ... exec -T towerscout printenv` to confirm the CA bundle and runtime engine env vars.
**Output**:
- Docker engine: client `29.4.1`, server `29.4.1`.
- Docker Compose service `towerscout-towerscout-1` is `healthy` on `0.0.0.0:5000->5000/tcp`.
- Health returned `{"service":"towerscout","status":"ok"}`.
- Readiness returned `state: ready`, assets `ok`, Azure configured, Google configured, and persisted secret present.
- Runtime env includes:
  - `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem`
  - `TOWERSCOUT_CONTAINER_ENGINE=docker`
**Validation**:
- `docker version --format "Client={{.Client.Version}} Server={{.Server.Version}}"` -> `Client=29.4.1 Server=29.4.1`.
- `docker compose -f compose.yaml -f compose.build.yaml ps` -> container healthy on port `5000`.
- `GET http://127.0.0.1:5000/api/health` -> passed.
- `GET http://127.0.0.1:5000/api/readiness` -> passed with `ready`.
- `docker compose -f compose.yaml -f compose.build.yaml exec -T towerscout printenv` -> passed and confirmed CA bundle/runtime env.
**Next**: Run final focused tests and complete the Task-025 closeout/PR preparation pass.

### 2026-05-07 - Closeout Checklist Alignment
**Objective**: Align the active Task-025 checklist with the validation evidence gathered during the Docker, GHCR, TLS, and Podman passes.
**Context**: Several checklist items were still unchecked after validation passed because the evidence was recorded incrementally across the implementation log. The remaining work should distinguish true release-support caveats from completed Task-025 container-runtime gates.
**Decision**: Mark completed acceptance criteria and current-sprint checklist items only where there is explicit implementation, documentation, or validation evidence. Keep Docker-Desktop-free Podman Compose-provider validation, broad Sprint 04 regression coverage, the Buildx Node 20 warning, and hosted asset downloader work as caveats/follow-ups rather than hidden blockers.
**Execution**:
- Updated `docs/oci-runtime-contract.md` with explicit persistence classifications for config, assets, logs, sessions, temp, uploads, and cache/geocode data.
- Updated `docs/oci-runtime-contract.md` and `docs/oci-quick-start.md` to reflect that Podman works while Docker Desktop's engine is unavailable, while Docker-Desktop-free Compose-provider validation remains a support caveat.
- Updated `current-tasks.md` and this task's acceptance checklist to mark validated gates complete and leave broad regression/support caveats open.
**Output**:
- Task-025 is now in closeout/PR preparation status.
- The remaining main caveat is Docker-Desktop-free Podman Compose-provider validation for hosts without Docker Desktop installed.
- Hosted asset download/bootstrap, optional OCI archive packaging, Buildx Node 20 action maintenance, and broad non-container Sprint 04 regression remain future/follow-up work.
**Validation**:
- Final focused unit tests passed: `47 passed, 9 warnings, 5 subtests passed`.
- `.agent_work` structure validation passed.
**Next**: Add explicit follow-up ownership for deferred release-support items and complete the PR handoff.

### 2026-05-07 - Completion And Follow-Up Handoff
**Objective**: Mark `TASK-025` complete while preserving clear ownership for residual release-support work.
**Context**: Docker, Podman engine, GHCR digest, TLS CA, asset import, persistence, readiness, and containerized smoke validation have all passed. The remaining items are not blockers for the container/runtime baseline, but they must be tracked before broader release promises.
**Decision**: Complete `TASK-025` and hand deferred release-support items to `TASK-065`, with launcher UX still owned by `TASK-054`.
**Execution**:
- Updated this task status to `COMPLETED - PR #7 OPEN`.
- Updated `.agent_work/current-tasks.md` to mark `TASK-025` complete and to classify broad Sprint 04 regression validation as release-readiness follow-through rather than a hidden Task-025 blocker.
- Added `TASK-065` to `.agent_work/task-backlog.md` for Docker-Desktop-free Podman Compose-provider validation, hosted asset download/bootstrap decisions, optional OCI archive fallback implementation, Buildx Node 20 action maintenance, and broad release-readiness regression validation.
**Output**:
- `TASK-025` is complete for the Docker-compatible / OCI container runtime baseline.
- Residual support/release caveats have named follow-up ownership instead of staying as ambiguous Task-025 leftovers.
**Validation**:
- `git diff --check -- .agent_work\current-tasks.md .agent_work\task-backlog.md .agent_work\tasks\active\TASK-025-docker-containerization.md` -> passed.
- `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` -> passed.
**Next**: Commit the closeout handoff and push PR #7 updates.

---

## Validation Results

### Current Validation Summary

**Last Updated**: 2026-05-07

**Validated**:
- App-side runtime contract: persistent first-run `FLASK_SECRET_KEY`, `/api/health`, `/api/readiness`, app-anchored ZIP-code path lookup, asset manifest/preflight, and redacted readiness details.
- Local Docker Desktop build path: `Dockerfile` check, local image build, Compose startup, Docker healthcheck, HTTP health/readiness, and restart persistence.
- Default named-volume runtime profile through `compose.yaml`.
- Developer/support local build override through `compose.build.yaml`.
- Windows helper script path through `.cmd` wrappers: `start.cmd -Build`, `status.cmd`, `logs.cmd`, and `stop.cmd`.
- Release-package documentation baseline through `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md`.
- Local GitHub Release control-package assembly through `scripts/package-release.cmd`, including package staging, `IMAGE.txt`, `SHA256SUMS.txt`, ZIP creation, and ZIP checksum output.
- Windows Podman WSL runtime spike: Podman engine startup, named volumes, asset-light readiness, asset import, and containerized `TASK-052` smoke.
- Podman with Docker Desktop engine unavailable: Docker daemon calls failed, `docker-desktop` was not running in WSL, Podman started TowerScout on port `5001`, readiness reported Podman runtime with assets `ok`, and the containerized `TASK-052` smoke passed. Docker-Desktop-free Compose-provider validation remains a support caveat because `podman compose` still used Docker Desktop's bundled `docker-compose.exe`.
- Google TLS inspection CA import path: Windows CA thumbprint export with chain, combined container CA bundle, and TowerScout Google validation endpoint reaching provider-level invalid-key response instead of TLS `502`.
- Local `.env` persistence for the combined TLS CA bundle path, validated across Docker Compose recreate.
- GHCR publish and pull-by-digest path: feature-branch image published to `ghcr.io/j-schulein/towerscout:task-025-0b5d0a7`, pinned digest validated by manifest inspect, Docker pull, release-image Compose startup, and release-package generation.
- Docker Desktop restore after Podman validation: Docker service returned healthy on port `5000`, readiness returned `ready`, assets and provider config remained persisted, and CA bundle env vars remained configured.

**Latest Test Evidence**:
- `docker build --check -f Dockerfile .` -> passed, no warnings.
- `docker compose -f compose.yaml -f compose.build.yaml build towerscout` -> passed.
- Built image: `towerscout:local`, image ID `sha256:2c483acc68e6609ceaeb3db79b58ca3906668f71fe4401f251267f91efcab7d5`, size `2798228750` bytes.
- `docker compose -f compose.yaml -f compose.build.yaml up -d towerscout` -> passed; container reported `healthy`.
- `GET /api/health` -> `{"service":"towerscout","status":"ok"}`.
- `GET /api/readiness` -> HTTP 200 with `state: setup_required`, assets `degraded`, `secret_key_persisted: true`, all runtime paths writable, and expected missing-asset recovery guidance.
- Restart secret persistence check -> passed without exposing the secret.
- `.\scripts\start.cmd -Engine docker -Build` -> passed.
- `.\scripts\status.cmd -Engine docker` -> passed.
- `.\scripts\logs.cmd -Engine docker -Tail 5` -> passed.
- `.\scripts\stop.cmd -Engine docker` -> passed.
- Docker named-volume asset import -> passed.
- Hash-verified readiness with real assets -> passed, assets `ok`, no missing/corrupt assets.
- In-container model catalog after asset import -> passed, `newest` detected.
- Azure Settings persistence across container restart -> passed by hash, readiness `ready`.
- Google validation TLS failure identified as untrusted local issuer inside container, not key-invalid response.
- Provider-key log/error redaction patch -> passed with fake-key failure scan.
- Containerized `TASK-052` smoke -> passed with real model assets, controlled imagery failure, and post-smoke readiness still `ready`.
- Packaged asset import helper -> passed against source-checkout assets with SHA-256 verification.
- PowerShell AST parse of `scripts/package-release.ps1` and helper scripts -> passed.
- `git diff --check -- scripts\package-release.ps1 scripts\package-release.cmd docs\oci-quick-start.md docs\oci-runtime-contract.md` -> passed.
- `.\scripts\package-release.cmd -Version task025-local-20260507114315 -Image towerscout:local -OutputDir .agent_work\pytest-temp\release-package` -> passed.
- Local release package required-file, `SHA256SUMS.txt`, ZIP, and `.zip.sha256` verification -> passed.
- Podman machine start and Docker-compatible API probe -> passed against Podman `5.8.2`, Linux/AMD64 WSL server.
- Docker image transfer into Podman store -> passed; `towerscout:local` loaded as `docker.io/library/towerscout:local`.
- `.\scripts\start.cmd -Engine podman` with `TOWERSCOUT_PORT=5001` -> passed.
- Podman `GET /api/health` -> `{"service":"towerscout","status":"ok"}`.
- Podman `GET /api/readiness` asset-light state -> `setup_required`, assets `degraded`, writable paths, persisted secret.
- `.\scripts\import-assets.cmd -Source webapp -Engine podman -VerifyHashes` -> passed with `asset_status=ok`.
- Podman containerized `TASK-052` smoke -> passed with real model load and expected controlled imagery failure.
- Podman Docker-engine-unavailable validation -> passed; Docker client could not reach `dockerDesktopLinuxEngine`, no `docker-desktop` WSL distro was running, Podman started TowerScout on port `5001`, readiness reported `runtime.container_engine: podman` and assets `ok`, containerized `TASK-052` smoke passed, and Docker remained unavailable afterward.
- Docker Desktop restore after Podman validation -> passed; Docker server `29.4.1`, Compose service healthy on port `5000`, health `ok`, readiness `ready`, assets `ok`, Azure and Google configured, persisted secret present, and CA bundle env vars configured.
- Baseline in-container Google HTTPS probe before CA import -> reproduced `CERTIFICATE_VERIFY_FAILED`.
- `.\scripts\import-tls-ca.cmd -Engine docker -Thumbprint C69667336E90D872FA44ACE4EB25412E52F406B9` -> passed after chain-export fix, Google TLS returned provider invalid-key JSON.
- Docker container recreate with `REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem` and `SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem` -> passed.
- `POST /api/config/validate-key` with invalid Google test key -> HTTP `200`, `valid: false`, `message: Google Maps validation failed with status 403.`
- Real Google key entry through containerized UI after CA bundle fix -> passed per owner validation.
- Local `.env` recreate proof -> passed; readiness `ready`, assets `ok`, Azure configured, Google configured, persisted secret present, and Google invalid-key probe returned provider-level `403` handling.
- GHCR manifest probes for `ghcr.io/towerscout/towerscout:latest` and `ghcr.io/j-schulein/towerscout:latest` -> `denied`.
- `gh auth status` -> logged in as `J-Schulein`, but token scopes do not include package scopes.
- Manual GHCR publish workflow added at `.github/workflows/container-publish.yml`.
- Digest-pinned release package dry run with `ghcr.io/j-schulein/towerscout@sha256:aaaaaaaa...` -> passed.
- GitHub Actions run `25511018110` for `.github/workflows/container-publish.yml` -> success.
- Published image metadata -> `ghcr.io/j-schulein/towerscout:task-025-0b5d0a7`, digest `sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`.
- `docker manifest inspect ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30` -> passed.
- `docker pull ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30` -> passed.
- Isolated release-image Compose validation on port `5002` -> passed; health `ok`, readiness `setup_required`/assets `degraded` with writable paths and matching `version.image_digest`.
- Real-digest release package `towerscout-task025-ghcr-0b5d0a7.zip` -> passed; `IMAGE.txt` and package `.env.example` pin the immutable GHCR digest.
- Follow-up GitHub Actions run `25511697887` -> passed; artifact name fixed to `image-metadata-task-025-03c6084`.
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py tests\unit\test_assets.py tests\unit\test_config.py -q -p no:cacheprovider` -> `35 passed, 8 warnings`.
- Final focused unit tests after Docker/Podman restore: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_runtime_contract.py tests\unit\test_assets.py tests\unit\test_config.py tests\unit\test_logging_sanitization.py tests\unit\test_error_sanitization.py -q -p no:cacheprovider` -> `47 passed, 9 warnings, 5 subtests passed`.
- `python .agent_work\scripts\validate_agent_work.py` -> passed.

**Findings**:
- Direct `.ps1` helper execution is blocked by the default Windows execution policy on this host. This is remediated by `.cmd` wrappers and quick-start updates that use the wrappers by default.
- The release-image path is now validated against `ghcr.io/j-schulein/towerscout@sha256:e27340947a48082433dcc996beb12c0050f6e9a2c2f20e44b4148923ab9ffa30`. Source checkout validation still uses `start.cmd -Build` and `compose.build.yaml`.
- Asset-light startup behaves correctly: the container serves setup and readiness without model/ZIP assets, and readiness reports assets as degraded with recovery guidance.
- Manual/local asset import into named volumes works and clears asset-degraded readiness. A packaged asset bootstrap/download script is still not implemented.
- The release control-package helper is validated with both `towerscout:local` and the real GHCR digest-pinned image reference.
- The successful branch-triggered GHCR run exposed an artifact naming bug (`image-metadata-` on push events); the workflow patch is validated by run `25511697887`, which uploaded `image-metadata-task-025-03c6084`.
- Podman's Windows WSL engine path works for the TowerScout runtime contract on this host, including while Docker Desktop's engine is unavailable.
- `podman compose` still delegated to Docker Desktop's bundled `docker-compose.exe`; a Docker-Desktop-free Podman support promise still requires independent Compose-provider validation with `podman-compose` or another approved provider.
- Azure provider configuration saved through the containerized UI persists across restart.
- Google validation behind this TLS-inspecting network works after importing the CDC/Zscaler CA chain into the container config volume and pointing `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` at the combined bundle; owner-confirmed real Google key entry now succeeds in the UI.
- Local `.env` now preserves the CA bundle path for Docker Compose recreates without storing provider secrets.
- Provider validation failures previously risked exposing keys in exception tracebacks; log and structured-error redaction have been tightened.
- Containerized smoke initially surfaced a non-blocking Ultralytics config warning; this is remediated by `YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics` plus startup directory creation.
- The build surfaced existing frontend dependency audit findings: one moderate and one high npm vulnerability. This is not a container-contract blocker, but it should be tracked as dependency/security follow-up.

**Deferred Follow-Up Work**:
- `TASK-065`: Decide whether hosted asset download/bootstrap is needed beyond the validated manual/restricted-network asset import path.
- `TASK-065`: Validate a Docker-Desktop-free Podman Compose provider before promising Podman broadly on hosts without Docker Desktop installed.
- `TASK-065`: Decide whether to implement the optional OCI image archive fallback for restricted-network release packages.
- `TASK-065`: Track the `docker/setup-buildx-action@v2` Node 20 deprecation warning as future pinned-action maintenance.
- `TASK-065`: Run the broad release-readiness browser/provider regression pass before end-user release support language is finalized.
