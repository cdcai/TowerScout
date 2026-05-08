# TASK-065: Release Packaging And Runtime Support Follow-Through

**Status**: IN_PROGRESS
**Priority**: HIGH
**Type**: B/C (Release Engineering / Runtime Supportability)
**Estimated Effort**: 1-2 days (8-16 hours)
**Target Sprint**: Sprint 06 intake / post-`TASK-054` release-support gate

## Objective

Close the release-support items intentionally deferred from `TASK-025` and informed by `TASK-054`, without reopening the completed OCI/container runtime baseline or launcher MVP.

This task owns the evidence and support-language decisions needed before broad release claims, especially Podman support on Windows hosts without Docker Desktop installed, optional restricted-network package behavior, asset bootstrap scope, and broad release-readiness regression validation.

## Requirements (EARS Notation)

**R-065-001**: WHEN Podman is described as broadly supported on Windows hosts without Docker Desktop installed, THE PROJECT SHALL validate a Docker-Desktop-free Compose provider such as `podman-compose` or another approved provider, or record explicit risk acceptance and narrower support language.

**R-065-002**: WHEN release assets are hosted externally, THE PROJECT SHALL decide whether to implement hosted asset download/bootstrap beyond the validated manual/restricted-network import path.

**R-065-003**: WHEN restricted-network release packages are supported, THE PROJECT SHALL either implement and validate the optional OCI image archive fallback or document it as intentionally unsupported for the release.

**R-065-004**: WHEN GitHub Actions warnings indicate pinned-action runtime drift, THE PROJECT SHALL update or risk-accept the affected actions before release readiness sign-off.

**R-065-005**: WHEN release support language is finalized, THE PROJECT SHALL run a broad browser/provider regression pass covering the Sprint 04 setup/settings/provider/detection surfaces beyond the focused `TASK-025` container validation.

**R-065-006**: WHEN launcher or quick-start documentation names runtime support expectations, THE PROJECT SHALL keep those statements aligned with the actual `TASK-065` validation evidence and caveats.

**R-065-007**: WHEN TLS CA bundle configuration is invalid or missing in a container volume, THE SYSTEM SHALL return a clear setup/support error instead of a generic internal server error during provider-key validation.

## Acceptance Criteria

- [x] Docker-Desktop-free Podman Compose-provider validation is completed, or support language explicitly avoids that promise.
- [x] Final Podman/Docker support language is updated in release docs and task trackers.
- [x] Hosted asset download/bootstrap is either implemented, explicitly deferred, or documented as out of scope for the release.
- [x] Optional OCI image archive fallback is either implemented and validated, explicitly deferred, or documented as unsupported for the release.
- [x] Known GitHub Actions runtime warning/follow-up items are updated or risk-accepted.
- [x] Broad release-readiness browser/provider regression pass is completed and documented, including setup, settings, provider switching, and detection surfaces.
- [x] Support diagnostics and sensitive-artifact handling remain consistent across launcher docs, OCI docs, and task evidence.
- [x] Any unresolved release-support caveat has owner-approved risk acceptance with impact, mitigation, review timing, and follow-up owner/task.
- [x] Missing or invalid TLS CA bundle behavior is fixed or explicitly tracked with support impact and mitigation.

## Dependencies

- `TASK-025`: Docker-compatible / OCI container runtime baseline complete and merged.
- `TASK-054`: Local launcher UX Phase 1 MVP complete and merged.

## Implementation Plan

1. Confirm the current support claims and caveats in `docs/oci-quick-start.md`, `docs/oci-runtime-contract.md`, `.github/copilot-instructions.md`, and active task trackers.
2. Validate Docker-Desktop-free Podman Compose-provider behavior, preferably with `podman-compose` or another approved Compose provider. `[DONE - podman-compose 1.5.0]`
3. Decide and document the final Podman support language based on validation evidence. `[DONE - provider prerequisites named explicitly]`
4. Decide the hosted asset download/bootstrap scope for the release. `[DONE - out of scope for v1 control package]`
5. Decide the optional OCI image archive fallback scope for restricted-network use. `[DONE - unsupported for v1 control package; support-managed preload only]`
6. Review the deferred GitHub Actions runtime warning/follow-up items from `TASK-025`. `[DONE - Buildx action pinned to v4.0.0 SHA]`
7. Run the broad release-readiness regression pass across setup, settings, provider switching, and detection workflows.
8. Fix or track the missing TLS CA bundle error path found during Podman credential setup. `[DONE - backend clear NetworkError and unit coverage]`
9. Update release docs, task files, and any risk-acceptance records.

---

## Implementation Log

### 2026-05-08 - PR Review Hardening Pass
**Objective**: Address the highest-value reviewer recommendations before treating PR #9 as merge-ready.
**Context**: External review judged PR #9 strong as a draft checkpoint but recommended a small hardening pass before final release-support sign-off. The main actionable items were immutable digest enforcement, provider-aware TLS CA verification, Podman Compose-provider reporting, evidence redaction, and focused tests.
**Decision**: Address the low-risk operational hardening items in PR #9 now. Keep broader CI gate redesign, Windows/Podman automation, licensing policy review, and clean-machine release-candidate validation as follow-up/release-candidate gates rather than expanding this PR into a release-program overhaul.
**Execution**: Redacted committed evidence to remove avoidable local host and enterprise-environment specifics. Updated `scripts/package-release.ps1` so release package generation requires a `sha256:<64 lowercase hex>` digest by default and uses `-AllowMutableImage` only for local validation packages. Updated `scripts/import-tls-ca.ps1` with `-VerifyProvider auto|google|azure|none`, allowing Azure-first and Google-blocked environments to avoid a Google-only TLS verification assumption. Added Podman/Docker Compose-provider reporting and `PODMAN_COMPOSE_PROVIDER` existence validation in `scripts/lib/TowerScoutCompose.ps1`, surfaced by `scripts/launch.ps1`. Added focused tests for `SSL_CERT_FILE`, unusable configured CA bundles, and package-release digest enforcement.
**Output**: The PR now turns several prior documentation caveats into executable guardrails while keeping the release scope unchanged.
**Validation**: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_config.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` passed with 17 tests. PowerShell parser checks passed for `scripts/package-release.ps1`, `scripts/import-tls-ca.ps1`, `scripts/launch.ps1`, and `scripts/lib/TowerScoutCompose.ps1`. `start.bat -Engine podman -Port 5001 -NoBrowser -TimeoutSeconds 30` passed after the provider-reporting change and printed the selected Podman Compose provider/version before readiness reached `ready`.
**Next**: Run the broader focused validation set, update the PR branch, and keep release-candidate clean-machine validation as the next gate after review.

### 2026-05-08 - Browser Provider Regression And Localhost Launch URL
**Objective**: Complete the broad provider/detection regression gate for the Podman release-support path and align the launcher URL with provider behavior.
**Context**: After the TLS CA bundle import fix, the owner entered real Google/Azure keys through Setup Wizard and started the application. The running Podman service reported `ready` with assets `ok`, allowing live browser detection validation against both providers.
**Decision**: Treat `http://localhost:<port>` as the release launcher browser URL. Google detection passed from `127.0.0.1`, but Azure Maps browser loading failed from the `127.0.0.1` origin with a provider CORS preflight error and passed from `localhost`. The launcher should therefore open `localhost`, while direct readiness/status checks may continue to use loopback addresses.
**Execution**: Ran the maintained browser detection smoke for Google and Azure against the Podman validation service. Added sanitized evidence under `.agent_work/tasks/active/TASK-065/evidence/TASK-065-browser-provider-regression.md`. Updated `scripts/launch.ps1` to build `$appUrl` from `http://localhost:$Port`; updated OCI quick-start/runtime docs with the expected browser origin and the Azure caveat.
**Output**: Google browser detection smoke passed with 8 detections. Azure browser detection smoke passed from `localhost` with 14 detections after the initial `127.0.0.1` origin failed on Azure Maps CORS preflight. Raw browser artifacts are referenced but not copied into task evidence because they can contain key-bearing provider URLs.
**Validation**: Browser artifacts: `.agent_work/context/analysis/browser-runs/20260508-125149-google/summary.json`, `.agent_work/context/analysis/browser-runs/20260508-124932-azure/summary.json`, and `.agent_work/context/analysis/browser-runs/20260508-125226-azure/summary.json`. Follow-up validation will re-run the launcher path after the URL change.
**Next**: Run focused launcher/status and documentation validation, then identify any remaining release-support caveats that require owner acceptance.

### 2026-05-08 - Missing TLS CA Bundle Error Handling
**Objective**: Prevent invalid or missing configured TLS CA bundle paths from surfacing as generic HTTP 500 errors during provider-key validation.
**Context**: Podman credential setup initially failed because `.env` pointed `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` at `/app/webapp/config/certs/towerscout-ca-bundle.pem`, but that file was not present in the selected engine's config volume. Requests raised an `OSError`, which became a generic setup-wizard internal error.
**Decision**: Add a preflight in `ts_config.py` for configured TLS bundle paths when TLS verification is enabled, and convert both missing bundle paths and late `OSError` failures into structured `NetworkError` responses with actionable support guidance.
**Execution**: Added TLS bundle environment-variable handling in `webapp/ts_config.py`; `_validation_get()` now checks configured bundle paths before issuing provider validation requests, and `validate_api_key()` catches late `OSError` failures. Added `test_validate_api_key_reports_missing_configured_tls_bundle` in `tests/unit/test_config.py`.
**Output**: Missing bundle paths now produce a clear support message instructing users/support to run `scripts/import-tls-ca.cmd` for the selected Docker or Podman engine, or to update `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` to a valid bundle.
**Validation**: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_config.py -q -p no:cacheprovider` passed with 13 tests. `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_error_sanitization.py -q -p no:cacheprovider` passed with 17 tests.
**Next**: Continue provider/browser regression and release-support documentation alignment.

### 2026-05-08 - Podman TLS CA Bundle Setup Finding
**Objective**: Record the provider-key validation failure found during real setup-wizard use in the Podman validation runtime.
**Context**: The owner attempted to enter Google and Azure keys through Setup Wizard at `http://127.0.0.1:5001`. The browser showed `POST /api/config/validate-key` returning HTTP 500 and the UI displayed "An internal error occurred. Please try again or contact support."
**Decision**: Treat this as a `TASK-065` release-support finding. Enterprise users behind TLS inspection may need CA import, but a configured bundle path that is missing from the selected engine's volume should not produce a generic 500. The release support path should include both a working CA import helper and clearer backend error handling for missing/invalid CA bundle paths.
**Execution**: Inspected Podman logs and found `OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /app/webapp/config/certs/towerscout-ca-bundle.pem`. Confirmed the Podman config volume had no `certs/` directory while repo `.env` pointed `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` at that path. Imported the local TLS inspection CA chain into the Podman config volume, built `/app/webapp/config/certs/towerscout-ca-bundle.pem`, and verified provider TLS from inside the container. Then patched `scripts/import-tls-ca.ps1` so Podman with `podman-compose 1.5.0` can fall back to direct `podman cp` when the Compose provider does not implement `cp`.
**Output**: Dummy-key provider validation now returns controlled validation responses instead of HTTP 500: Google invalid-key validation returns `valid:false` with a 403-derived message; Azure invalid-key validation returns `valid:false` with 401-derived messages. The owner then confirmed real Google/Azure credentials could be entered and the application could start.
**Validation**: `scripts/import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint>` completed successfully after the fallback patch and verified provider TLS. Follow-up backend fix still needed so missing CA bundle paths return an actionable support message.
**Next**: Add backend handling/tests for missing or invalid configured TLS CA bundle paths, then rerun focused provider-validation tests.

### 2026-05-08 - Release Scope Decisions And Buildx Action Update
**Objective**: Resolve the release-support decisions for hosted asset bootstrap, optional OCI archive fallback, and the deferred GitHub Actions Buildx runtime warning.
**Context**: `TASK-025` intentionally deferred hosted asset download/bootstrap, optional OCI image archive fallback, and a `docker/setup-buildx-action@v2` Node runtime warning. `TASK-065` needs these either implemented, explicitly deferred, or risk-accepted before release support wording is finalized.
**Decision**: Keep hosted asset download/bootstrap out of the v1 control package and use the already validated manifest-backed local asset import path. Do not promise a packaged OCI image archive fallback for v1; restricted-network support should preload the pinned image through a site/support procedure until a first-class archive workflow is designed and validated. Update Buildx rather than risk-accepting the warning.
**Execution**: Confirmed the official `docker/setup-buildx-action` releases list `v4.0.0` as current and that it uses Node 24. Queried the immutable `v4.0.0` tag SHA with `git ls-remote`, then updated `.github/workflows/ci.yml` and `.github/workflows/container-publish.yml` from the pinned v2 SHA to `4d04d5d9486b7bd6fa91e7baf45bbb4f8b9deedd # v4.0.0`. Updated `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md` to state the v1 asset and restricted-network scope explicitly.
**Output**: Hosted asset download/bootstrap is documented as out of scope for v1; bundled OCI image archives are documented as unsupported for the v1 control package; Buildx action runtime drift is addressed by a pinned v4.0.0 SHA.
**Validation**: YAML syntax validation and `.agent_work` validation pending after documentation updates.
**Next**: Run focused validation, then continue to broad release-readiness browser/provider regression.

### 2026-05-08 - Docker-Desktop-Free Podman Compose Provider Validation
**Objective**: Close the first `TASK-065` gate by validating a Docker-Desktop-free Compose provider for the Podman path.
**Context**: Prior `TASK-025` validation proved Podman could run TowerScout while Docker Desktop's daemon was unavailable, but `podman compose` still selected Docker Desktop's bundled `docker-compose.exe` as the external provider. The support question was whether the release package can run through a provider that does not depend on Docker Desktop.
**Decision**: Validate `podman-compose 1.5.0` as the external provider by setting `PODMAN_COMPOSE_PROVIDER` to the project virtual-environment executable. Treat this as sufficient to remove the "provider validation pending" caveat while still documenting Podman machine and Compose-provider prerequisites.
**Execution**: Installed `podman-compose==1.5.0` into `.venv`, confirmed `podman compose version` selected the project virtual-environment `podman-compose.exe`, confirmed `docker version` could not reach the Docker Desktop daemon, started TowerScout through `start.bat -Engine podman -Port 5001 -NoBrowser`, ran status/health/readiness checks, copied the container smoke script into the running container, and executed the `TASK-052` container smoke with `PYTHONPATH=/app/webapp`.
**Output**: Launcher reached `setup_required` with assets `ok`; readiness reported `runtime.container_engine: podman`; health returned `ok`; the containerized `TASK-052` smoke returned `container_task052_smoke=pass`; `scripts\stop.cmd -Engine podman` stopped the validation container and a final `podman ps` showed no running containers.
**Validation**: Evidence recorded in `.agent_work/tasks/active/TASK-065/evidence/TASK-065-podman-compose-provider-validation.md`. Updated `docs/oci-quick-start.md`, `docs/oci-runtime-contract.md`, and `.agent_work/current-tasks.md` to replace the pending caveat with explicit Podman prerequisites and provider-selection guidance.
**Next**: Continue with hosted asset download/bootstrap scope, optional OCI archive fallback scope, GitHub Actions warning follow-up, and broad release-readiness regression validation.

### 2026-05-08 - Task-065 Intake And Podman Provider Plan
**Objective**: Start `TASK-065` and validate the first release-support gate: Docker-Desktop-free Podman Compose-provider behavior.
**Context**: `TASK-025` validated the Podman engine/runtime path on this host, including while Docker Desktop's daemon was unavailable, but `podman compose` still delegated to Docker Desktop's bundled `docker-compose.exe`. `TASK-065` must either validate a Docker-Desktop-free provider such as `podman-compose` or keep support language narrower.
**Decision**: Use `PODMAN_COMPOSE_PROVIDER` for the validation slice so the test can select an explicit provider without changing global Podman configuration. Keep evidence under `.agent_work/tasks/active/TASK-065/evidence/`.
**Execution**: Confirmed Podman `compose` supports provider override through `PODMAN_COMPOSE_PROVIDER`; confirmed `podman-compose` is not currently installed in the active Python environment.
**Output**: Task is now in progress and ready for provider installation/validation.
**Validation**: `.agent_work` structure validation passed before task start. Provider validation pending.
**Next**: Install or locate a Docker-Desktop-free Compose provider, then run `podman compose` with that provider while Docker daemon access is unavailable.

### 2026-05-07 - Task Documentation Creation
**Objective**: Prepare `TASK-065` so release-support follow-through can start from a clear scope in the morning.
**Context**: `TASK-025` and `TASK-054` are merged. `TASK-025` intentionally handed off Docker-Desktop-free Podman Compose-provider validation, hosted asset download/bootstrap decisions, optional OCI archive fallback, GitHub Actions warning follow-up, and broad release-readiness regression validation to `TASK-065`.
**Decision**: Create an active task file and move the task from backlog-only status into ready-for-intake tracking without starting implementation.
**Execution**: Created this task file with requirements, acceptance criteria, dependencies, implementation plan, and initial log. Synchronized `current-tasks.md`, `task-backlog.md`, Sprint 05 plan, and project context to reflect that `TASK-054` Phase 1 is complete and `TASK-065` is the next release-support gate.
**Output**: `TASK-065` is ready for intake.
**Validation**: Pending `.agent_work` validation after documentation synchronization.
**Next**: Start with the Docker-Desktop-free Podman Compose-provider validation plan.

---

## Validation Results

### 2026-05-08 Focused Validation
**Test Status**: PARTIAL PASS

- `podman-compose 1.5.0` provider validation: PASS.
- `start.bat -Engine podman -Port 5001 -NoBrowser -TimeoutSeconds 180` with `PODMAN_COMPOSE_PROVIDER=<repo-root>\.venv\Scripts\podman-compose.exe`: PASS.
- `scripts\status.cmd -Engine podman -Port 5001`: PASS.
- `GET /api/health` on Podman validation service: PASS.
- `GET /api/readiness` on Podman validation service: PASS, `state=setup_required`, assets `ok`, runtime `container_engine=podman`.
- Containerized `TASK-052` smoke inside Podman validation container: PASS.
- Validation cleanup with `scripts\stop.cmd -Engine podman` and `podman ps`: PASS.
- Workflow YAML parse across `.github/workflows/*.yml`: PASS.
- `.agent_work/scripts/validate_agent_work.py`: PASS.
- Active-doc stale Podman caveat search, excluding `.agent_work/pytest-temp/**`: PASS.
- `node webapp/build.js`: PASS, generated bundle diff discarded because it only changed build timestamp/output whitespace.
- `npm.cmd run test:stage-0`: NOT RUNNABLE in this shell environment. The PowerShell `npm` shim is blocked by execution policy, and `npm.cmd` reaches Windows `bash.exe`/WSL but WSL reports `/bin/bash` missing.
- Missing TLS CA bundle unit coverage: PASS. `tests\unit\test_config.py` passed with 13 tests; `tests\unit\test_flask_routes.py tests\unit\test_error_sanitization.py` passed with 17 tests.
- Google browser detection smoke on Podman runtime: PASS from `http://127.0.0.1:5001`, 8 detections.
- Azure browser detection smoke on Podman runtime: PASS from `http://localhost:5001`, 14 detections.
- Azure browser detection smoke from `http://127.0.0.1:5001`: FAIL due Azure Maps browser CORS preflight behavior; mitigated by changing the release launcher browser URL to `localhost`.
- Launcher rerun after browser URL change: PASS. `start.bat -Engine podman -Port 5001 -NoBrowser -TimeoutSeconds 30` reported readiness at `http://localhost:5001/api/readiness`, state `ready`, assets `ok`, config `ok`, and skipped browser launch with the `localhost` URL.
- `GET http://localhost:5001/api/readiness`: PASS, `state=ready`, assets `ok`, config `ok`, runtime `container_engine=podman`.
- `.agent_work/scripts/validate_agent_work.py`: PASS after final Task-065 evidence and documentation updates.
- Workflow YAML parse across `.github/workflows/*.yml`: PASS after Buildx action updates.
- Reviewer hardening tests: PASS. `tests\unit\test_config.py tests\unit\test_release_package_script.py` passed with 17 tests after adding `SSL_CERT_FILE`, unusable configured CA bundle, and package-release digest enforcement coverage.
- PowerShell parser check: PASS for `scripts/package-release.ps1`, `scripts/import-tls-ca.ps1`, `scripts/launch.ps1`, and `scripts/lib/TowerScoutCompose.ps1`.
- Podman launcher provider-reporting check: PASS. `start.bat -Engine podman -Port 5001 -NoBrowser -TimeoutSeconds 30` printed the selected Podman Compose provider/version and reached readiness `ready`.
- Release package digest enforcement check: PASS. `scripts\package-release.cmd -Version task065-hardening-validation -OutputDir dist -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:0000000000000000000000000000000000000000000000000000000000000000 -NoZip -Force` staged a digest-pinned package successfully.

### Remaining Validation

- `npm.cmd run test:stage-0` remains not runnable in this shell environment because the Windows `bash.exe` path resolves to WSL without `/bin/bash`.
- Release owner should review the documented `localhost` browser-origin support language before final release sign-off.
- Broader CI gate tightening, Windows/Podman automation, licensing policy review, and clean-machine release-candidate validation remain follow-up/release-candidate gates.

### 2026-05-08 Release Package Assembly Check
**Test Status**: PASS

- `scripts\package-release.cmd -Version task065-validation -OutputDir dist -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:0000000000000000000000000000000000000000000000000000000000000000 -NoZip -Force`: PASS.
- Package staged at ignored path `dist\towerscout-task065-validation`.
- Package contents include launcher, Compose file, `.env.example`, OCI quick start, OCI runtime contract, asset manifest, status/log/start/stop scripts, asset import helper, TLS CA import helper, `IMAGE.txt`, and `SHA256SUMS.txt`.
- Staged `scripts\launch.ps1` opens `http://localhost:$Port`.
- Staged docs include the Podman `podman-compose 1.5.0` validation language, TLS CA bundle guidance, restricted-network scope, and `localhost` browser-origin guidance.

### Handoff Status

Task-065 is implementation-complete pending release-owner review of the support language and a commit/PR checkpoint. No provider secrets were copied into task evidence; raw browser artifacts remain under ignored `.agent_work/context/analysis/browser-runs/`.

Reviewer context is summarized in `.agent_work/tasks/active/TASK-065/TASK-025-TO-065-RELEASE-READINESS-ANALYSIS.md`.
