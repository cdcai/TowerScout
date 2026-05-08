# Task-025 Through Task-065 Release Readiness Analysis

**Date**: 2026-05-08
**Branch**: `feature/task-065-release-support`
**Purpose**: Give reviewers a single narrative for the container/runtime, launcher, and release-support work from `TASK-025` through the current `TASK-065` checkpoint.

## Executive Summary

TowerScout has moved from a source-checkout Flask application into a release-oriented local container package shape.

The current direction is a Windows/AMD64, single-user, CPU-baseline v1 release that uses:

- a GitHub Release control package
- a pinned GHCR container image digest
- Docker-compatible or OCI-compatible local runtime support
- Podman as the preferred open-source Windows runtime target when Podman machine and Compose-provider prerequisites are met
- persistent named volumes for config, sessions, model/data assets, logs, uploads, caches, and working files
- a Windows launcher (`start.bat`) that starts the selected engine, waits for readiness, and opens the browser
- explicit support tooling for status, logs, asset import, and TLS CA import

The first release is intentionally not a native installer and not an all-in-one offline package. Large runtime assets remain outside git and outside the default control ZIP. Restricted-network environments are supported through support-managed image preload and local asset import, not through a bundled OCI archive workflow in v1.

## Starting Context Before Task-025

Several Sprint 04 and Sprint 05 tasks changed what containerization needed to preserve:

- Setup Wizard and Settings already existed, so release work needed to preserve in-app provider-key setup rather than invent a separate config flow.
- Detection progress, cancel handling, estimate/detect separation, provider switching, export/restore, and manual-review workflows were already user-facing behavior.
- Runtime hardening tasks had already moved the project toward deterministic startup, local YOLO ownership, and smoke-test baselines.
- Pre-container release hardening and provider-state work had cleared or documented the main blockers before containerization.

The important implication was that `TASK-025` could not be treated as "just add a Dockerfile." It had to preserve configuration persistence, provider setup, filesystem sessions, large assets, health/readiness behavior, and support diagnostics.

## Task-025: OCI Container Runtime Baseline

`TASK-025` created the core local container runtime contract.

Major outcomes:

- Added the Docker-compatible / OCI image baseline.
- Added Compose configuration for local runtime startup.
- Added persistent named volumes for:
  - `webapp/config`
  - model assets
  - ZIP-code data
  - logs
  - Flask sessions
  - temp/session working files
  - uploads
  - map/geocoding cache
- Added `/api/health` for liveness.
- Added structured `/api/readiness` for launcher/support use.
- Added readiness states such as `setup_required`, `degraded`, `ready`, and `fatal`.
- Preserved Setup Wizard and Settings persistence across container replacement.
- Added first-run `FLASK_SECRET_KEY` generation and persistence in the config volume.
- Added asset manifest checks and recovery guidance for missing or corrupt assets.
- Added asset import helper scripts.
- Added TLS CA import helper scripts for TLS-inspecting enterprise networks.
- Added release package assembly scripts and runtime docs.
- Added GHCR-oriented image publication workflow.

Key decision:

The project reframed the work as an engine-aware OCI/container baseline instead of a Docker Desktop-specific product path. Docker Desktop remains useful where licensed and approved, but it is not assumed to be available for all end users.

Validation highlights:

- Container startup and readiness passed.
- Setup/config persistence was validated.
- Asset-aware readiness behavior was validated.
- Containerized detection smoke was validated.
- Podman engine behavior was validated on this host, including while Docker Desktop's engine was unavailable.

Remaining handoff from `TASK-025`:

- Podman still needed Docker-Desktop-free Compose-provider validation before broad Podman support language could be trusted.
- Launcher/user-startup UX belonged in `TASK-054`.
- Release scope decisions and broad provider/browser regression belonged in `TASK-065`.

## Task-054: Local Launcher And Support UX

`TASK-054` added the user-facing launcher layer over the `TASK-025` runtime contract.

Major outcomes:

- Added top-level `start.bat`.
- Added `scripts/launch.ps1`.
- Launcher creates `.env` from `.env.example` when missing.
- Launcher starts the selected engine and Compose stack.
- Launcher polls `/api/readiness` before opening the browser.
- Launcher prints readiness state, asset status, config status, and recovery hints.
- Added `-NoBrowser`, `-Port`, `-TimeoutSeconds`, `-Build`, and engine-selection support.
- Preserved lower-level support scripts for start, stop, logs, and status.
- Added Windows startup-failure diagnostics for WSL/virtualization and Podman machine state.
- Updated quick-start and runtime docs to describe support diagnostics and sensitive artifact handling.

Key decision:

The launcher is host-side support UX, not part of the application container. The container serves TowerScout; the host launcher handles starting the runtime, waiting for readiness, and opening the browser.

Validation highlights:

- Happy-path launcher startup passed.
- Owner confirmed the launcher opened the app and console messaging was understandable.
- Invalid engine, invalid timeout, and unreachable-readiness paths failed visibly with actionable output.
- Release package assembly included the launcher and checksums.

Remaining handoff from `TASK-054`:

- Final Podman support language and broader release readiness remained gated by `TASK-065`.

## Task-065: Release Packaging And Runtime Support Follow-Through

`TASK-065` closed the release-support items that were intentionally deferred from `TASK-025` and informed by `TASK-054`.

### Podman Compose Provider Validation

The main Podman question was whether TowerScout could run through Podman without relying on Docker Desktop's bundled Compose provider.

Outcome:

- Installed and validated `podman-compose 1.5.0`.
- Set `PODMAN_COMPOSE_PROVIDER` to the project virtual-environment executable.
- Confirmed `podman compose version` selected that provider.
- Confirmed Docker Desktop daemon access was unavailable during validation.
- Started TowerScout through `start.bat -Engine podman`.
- Ran status, health, readiness, and containerized smoke checks.

Support language now says Podman support requires:

- a created/running Podman machine
- an approved Compose provider such as `podman-compose`
- provider selection through `PODMAN_COMPOSE_PROVIDER` when needed

### Release Scope Decisions

The v1 release package is a control package, not a fully offline installer.

Supported in v1:

- pinned GHCR image digest
- release ZIP containing Compose files, scripts, docs, manifest, checksums, and image metadata
- local asset import with `scripts/import-assets.cmd`
- support-managed image preload for restricted-network sites

Out of scope for v1:

- automatic hosted asset downloader
- bundled OCI image archive inside the release ZIP
- fully offline one-ZIP installer behavior
- native installer behavior

Reason:

Hosted asset download and bundled image archives are both useful future work, but they need separate validation for hosting, checksums, retries, partial-download recovery, proxy/TLS behavior, import UX, Docker/Podman compatibility, and package size. Promising either in v1 without building and testing it would create release-support risk.

### GitHub Actions Runtime Drift

The deferred Buildx action runtime warning was addressed.

Outcome:

- Updated `docker/setup-buildx-action` usage to pinned `v4.0.0` SHA in:
  - `.github/workflows/ci.yml`
  - `.github/workflows/container-publish.yml`

### TLS CA Bundle Finding

During Podman setup, provider-key validation initially failed with a generic internal error.

Root cause:

- `.env` pointed `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` at `/app/webapp/config/certs/towerscout-ca-bundle.pem`.
- The selected Podman config volume did not contain that bundle.
- Requests raised an `OSError` for the missing CA bundle path.

Fixes:

- Imported the local TLS inspection CA into the Podman config volume.
- Patched `scripts/import-tls-ca.ps1` so Podman can fall back to direct `podman cp` when `podman-compose` does not implement Compose `cp`.
- Added backend preflight handling in `webapp/ts_config.py` so missing configured CA bundle paths produce a clear support error instead of a generic 500.
- Added unit coverage in `tests/unit/test_config.py`.

Important support note:

Docker and Podman use separate named volumes. If a user switches engines, CA import must be run for the selected engine.

### Browser Provider Regression

After TLS CA import, real Google and Azure keys were entered through Setup Wizard and the Podman app reached `ready`.

Results:

- Google browser detection smoke passed with 8 detections.
- Azure browser detection smoke failed from `http://127.0.0.1:5001` because Azure Maps browser requests hit provider CORS preflight behavior.
- Azure browser detection smoke passed from `http://localhost:5001` with 14 detections.

Decision:

The release launcher now opens `http://localhost:<port>`. Docs also tell users to use `localhost` when opening the app manually.

Sensitive artifact handling:

Raw browser-run artifacts are ignored and not copied into task evidence because provider request URLs can contain key-bearing query strings. Task evidence records only sanitized counts, status, and artifact paths.

### Release Package Assembly Check

The package assembly path was validated after the launcher/docs/TLS updates.

Validation command:

```powershell
.\scripts\package-release.cmd -Version task065-validation -OutputDir dist -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:0000000000000000000000000000000000000000000000000000000000000000 -NoZip -Force
```

Result:

- Package staged successfully under ignored `dist/`.
- Package includes updated launcher, Compose file, `.env.example`, quick start, runtime contract, asset manifest, status/log/start/stop scripts, asset import helper, TLS CA import helper, `IMAGE.txt`, and `SHA256SUMS.txt`.

## Current V1 Support Position

Supported target:

- Windows 11 / AMD64
- single-user local use
- CPU baseline
- normal outbound internet access
- Docker-compatible or OCI-compatible local container engine
- Podman preferred where Podman machine and Compose-provider prerequisites are met
- Docker compatible where Docker Desktop or Docker engine use is approved

Expected package shape:

- GitHub Release ZIP control package
- pinned GHCR image digest
- separate asset bundle or site/support-provided asset folder
- local asset import
- checksums and manifest-backed validation
- named-volume persistence
- host-side launcher and support scripts

Unsupported or deferred for v1:

- Mac and ARM64
- air-gapped/offline all-in-one install
- native installer
- shared multi-user hosting
- VDI as a tested support promise
- automatic hosted asset downloader
- bundled OCI image archive workflow
- provider-key-free or offline map operation

## Validation Summary

Completed validation includes:

- Podman `podman-compose 1.5.0` provider validation.
- Podman launcher readiness validation.
- Podman status, health, and readiness checks.
- Containerized `TASK-052` smoke.
- Missing TLS CA bundle unit coverage.
- Flask route/error sanitization coverage.
- Google browser detection smoke.
- Azure browser detection smoke from `localhost`.
- Release package assembly check.
- Workflow YAML parse.
- `.agent_work` structure validation.
- `git diff --check`.

Known validation gap:

- `npm.cmd run test:stage-0` is not runnable in this Windows shell because `bash.exe` resolves to WSL without `/bin/bash`. This is a tooling portability issue already visible before the release-support work and should be handled as follow-up unless reviewers want it promoted.

## Reviewer Focus Areas

Reviewers should focus on these questions:

1. Does the v1 release scope avoid over-promising what has not been implemented or validated?
2. Is Podman support language precise enough about Podman machine and Compose-provider prerequisites?
3. Is the `localhost` browser-origin decision acceptable for release support?
4. Is the TLS CA import/support path clear enough for enterprise TLS inspection environments?
5. Are secrets and sensitive artifacts handled correctly in docs, evidence, logs, and browser-run outputs?
6. Does the package shape make sense as a first release control package rather than a native installer?
7. Are the deferred items acceptable as follow-up work rather than v1 blockers?

## Path Forward

Immediate next steps:

1. Keep PR #9 in draft while addressing the targeted reviewer hardening items.
2. Complete evidence redaction, immutable image-digest enforcement, provider-aware TLS CA verification, Podman Compose-provider reporting, and focused tests.
3. Ask reviewers to re-check the release-support stance, package contract, Podman language, TLS CA flow, and browser-provider evidence after the hardening commit.
4. After review, decide whether the PR is ready for merge or whether any remaining release-gate items need to split into follow-up tasks.

Release-candidate next steps:

1. Publish or select a real GHCR image digest.
2. Generate a release package with the real digest.
3. Prepare the asset bundle and verify manifest/hash behavior.
4. Run a clean-machine or clean-volume validation pass:
   - start package
   - import assets
   - configure provider key
   - verify readiness
   - run Google/Azure smoke where credentials are available
   - restart/recreate container and verify persistence
5. Confirm support-data collection and redaction guidance with the intended reviewer/support audience.

Follow-up engineering candidates:

- Portable replacement or wrapper for `npm run test:stage-0` on Windows.
- Broader CI gate tightening so release-critical checks fail PRs rather than relying mainly on local validation.
- Windows/Podman automation on a suitable runner.
- Release-owner/legal decision on the repository license posture before public release promises.
- First-class hosted asset downloader after hosting/checksum/retry/proxy/TLS behavior is designed.
- First-class OCI image archive import workflow for restricted-network sites.
- Optional host-visible data-directory profile if users need inspectable local folders.
- CPU performance optimization in the containerized path.
- Multi-provider fallback/reliability work under `TASK-029`.
- Native installer or managed desktop packaging only after the container package proves supportable.

## Bottom Line

The current checkpoint gives reviewers a concrete release-support baseline:

- container runtime contract exists
- launcher exists
- Podman provider path is validated without Docker Desktop's Compose provider
- TLS inspection support has a working helper and clearer backend errors
- Google/Azure browser detection has been revalidated
- release package assembly works
- v1 release boundaries are explicit

The main remaining work is reviewer feedback, release-owner sign-off on scope, and release-candidate validation using a real pinned image digest and asset bundle.
