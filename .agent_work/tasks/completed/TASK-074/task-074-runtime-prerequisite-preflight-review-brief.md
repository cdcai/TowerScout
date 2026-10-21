# Task-074 Runtime Prerequisite Preflight Review Brief

**Date**: 2026-05-28
**Branch**: `codex/task-074-runtime-prerequisite-preflight`
**Task**: `TASK-074: Runtime Prerequisite Preflight`
**Purpose**: Give a reviewer enough implementation, validation, and risk context to assess whether the Task-074 bootstrap/preflight path is appropriate for V1 RC1.

## Executive Summary

Task-074 adds a guided Windows first-setup entry point for the TowerScout V1 RC1 package without replacing the existing validated launcher and asset-import paths.

The new top-level `bootstrap.cmd` delegates to `scripts/bootstrap.ps1`, which performs prerequisite checks, optional release ZIP checksum checks, optional Model & Data Package ZIP safety/layout checks, temporary asset ZIP extraction staging, asset-manifest matching, verified asset import through the existing importer, and launch through the existing launcher. `start.bat` remains the direct launch path after setup.

The implementation keeps Docker Desktop as the primary RC1 pilot path and preserves Podman as a qualified support-directed path when a running Podman machine and Compose provider are available. It does not add hosted asset download, native installer behavior, bundled OCI archives, broad Podman claims, or new GPU claims.

## What Was Accomplished

### 1. Added A Guided First-Setup Entry Point

New files:

- `bootstrap.cmd`
- `scripts/bootstrap.ps1`
- `scripts/lib/TowerScoutBootstrap.ps1`

The bootstrap command supports:

- `-Engine auto|docker|podman`
- `-Port`
- `-Gpu off|auto|on`
- `-TimeoutSeconds`
- `-RestartWaitSeconds`
- `-AssetsPath`
- `-AssetZip`
- `-PackageZip`
- `-MinimumFreeGB`
- `-VerifyOnly`
- `-NoBrowser`
- `-SkipAssetImport`

`-VerifyOnly` is intentionally non-mutating. It runs preflight, release checks, and asset-layout checks without importing assets or starting TowerScout.

Post-merge package validation found and corrected an ordering gap in that contract: `-AssetZip` final staging originally happened before the `-VerifyOnly` exit. The follow-up patch now checks `-AssetZip` checksum, layout, and manifest/release matching without final staging, runs engine preflight, and exits before asset mutation when `-VerifyOnly` is used.

### 2. Added Runtime Preflight Checks

The helper library now checks:

- Disk space on the package drive.
- Host port availability.
- Existing TowerScout readiness on an occupied host port, validated by a TowerScout-shaped `/api/readiness` payload.
- Existing selected-engine container port mappings that may reserve the requested port even when Windows reports it free.
- Docker CLI availability.
- Docker daemon reachability.
- Docker Compose availability.
- WSL availability/status hint for Docker Desktop on Windows.
- Podman CLI availability.
- Podman engine reachability.
- Podman machine state.
- Podman Compose provider availability.
- `PODMAN_COMPOSE_PROVIDER` existence when explicitly set.
- Whether the selected image is present in the selected engine image store.

The image check uses `docker|podman image inspect <image> --format "{{.Id}}"` to avoid blocking on large redirected JSON output.

### 3. Added Release And Asset Validation Before Import

Bootstrap can verify:

- `-PackageZip` checksum sidecar.
- `-AssetZip` checksum sidecar.
- Unsafe ZIP entries such as rooted paths, drive-letter paths, and `.`/`..` segments.
- Unexpected asset ZIP root entries.
- Nested `assets/...` ZIP roots.
- Required root-level `model_params/`, `data/`, and `asset_manifest.v1.json`.
- Asset manifest file hash against the control package `webapp/asset_manifest.v1.json`.
- Expected asset ZIP filename when `release-manifest.v1.json` has a concrete release version.
- `IMAGE.txt`, `.env.example`, and `release-manifest.v1.json` consistency where package metadata is available.
- Temporary extraction into `assets/.staging-<guid>` before final asset promotion.
- Non-mutating asset ZIP manifest/release matching for `-VerifyOnly`.

After these checks, bootstrap promotes only `model_params/`, `data/`, and
`asset_manifest.v1.json` into the final package `assets/` folder, removes
temporary staging on success or failure, and imports staged assets using the
existing importer:

```powershell
scripts/import-assets.ps1 -VerifyHashes
```

This is deliberate. The implementation does not duplicate named-volume copy behavior or manifest hash verification already covered by `scripts/import-assets.ps1` and runtime readiness.

### 4. Preserved Existing Launch And Runtime Behavior

Bootstrap launches through:

```powershell
scripts/launch.ps1
```

The existing launcher remains responsible for:

- Creating `.env` from `.env.example`.
- Compose startup.
- GPU mode environment behavior.
- Readiness polling.
- Browser launch or `-NoBrowser`.

`scripts/launch.ps1` now also maps readiness states to plain-English next actions:

- `setup_required`: complete Setup Wizard or Settings.
- `degraded`: follow recovery hints, usually asset import.
- `ready`: normal use.
- `fatal`: stop validation and collect support evidence.

### 5. Updated Release Package Assembly

`scripts/package-release.ps1` now includes the new bootstrap files in generated release packages:

- `bootstrap.cmd`
- `scripts/bootstrap.ps1`
- `scripts/lib/TowerScoutBootstrap.ps1`

The staged package `assets/README.txt` now recommends bootstrap first setup and keeps manual `scripts/import-assets.cmd` as a fallback.

### 6. Updated User And Support Documentation

Updated docs include:

- `docs/v1-rc1-quick-start.md`
- `docs/v1-rc1-quick-start.html`
- `docs/v1-rc1-package-guide.md`
- `docs/oci-quick-start.md`
- `docs/oci-runtime-contract.md`
- `docs/project-overview.md`
- `docs/project-overview.html`
- `docs/release-asset-bundle-contract.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`

The docs now present `bootstrap.cmd` as the first setup path and `start.bat` as the later direct launch path. They also document the Podman/rootless port caveat observed during validation.

### 7. Added Focused Automated Coverage

New tests:

- `tests/unit/test_task_074_bootstrap.py`

Existing tests updated:

- `tests/unit/test_release_package_script.py`

Coverage includes:

- Bootstrap command surface and packaging inclusion.
- Checksum sidecar parsing and matching.
- Readiness guidance text.
- Asset ZIP direct-root validation.
- Nested `assets/` rejection.
- Control/asset manifest file-hash matching.
- Temporary asset ZIP extraction staging and cleanup after failed manifest validation.
- Verify-only ordering so asset ZIPs are checked without final package mutation.
- Digest-pinned image reference composition.
- Small formatted Docker/Podman image inspect command.
- Stale stopped/created engine port mapping detection.

## Validation Evidence

### Automated Validation

Passed:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_import_assets_script.py tests\unit\test_release_package_script.py tests\unit\test_flask_routes.py::test_docs_routes_expose_package_local_docs -q -p no:cacheprovider
```

Result after reviewer hardening:

```text
14 passed
```

Passed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "[scriptblock]::Create((Get-Content -Raw 'scripts\bootstrap.ps1')) | Out-Null; [scriptblock]::Create((Get-Content -Raw 'scripts\lib\TowerScoutBootstrap.ps1')) | Out-Null; [scriptblock]::Create((Get-Content -Raw 'scripts\launch.ps1')) | Out-Null; [scriptblock]::Create((Get-Content -Raw 'scripts\package-release.ps1')) | Out-Null; Write-Output 'ok'"
```

Passed:

```powershell
.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py
git diff --check
```

Docs command check passed with the known intentional `127.0.0.1` warning in `docs/oci-quick-start.md`.

### Docker Desktop Smoke

With Docker Desktop running:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -VerifyOnly -NoBrowser -MinimumFreeGB 1
```

Passed and reported:

- Docker CLI found.
- Docker daemon reachable.
- Docker Compose available.
- WSL available.
- Selected image present in Docker image store.

Then:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -NoBrowser -TimeoutSeconds 180 -MinimumFreeGB 1
```

Passed and reached readiness `ready`.

Follow-up status check:

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
```

Confirmed readiness `ready`, assets `ok`, config `ok`, and CPU device policy.

### Podman Boundary Smoke

Docker Desktop was stopped, Podman was running.

Preflight:

```powershell
.\bootstrap.cmd -Engine podman -Gpu off -VerifyOnly -NoBrowser -MinimumFreeGB 1
```

Passed and reported:

- Podman CLI found.
- Podman engine reachable.
- Podman machine running.
- Podman Compose provider available.
- Selected image present in Podman image store.

Default port launch on `5000` failed with:

```text
rootlessport listen tcp4 0.0.0.0:5000: bind: address already in use
```

This happened even though the Windows port check reported `localhost:5000` as available. The failed attempt also created a stopped/created Podman container reserving host port `5000`, so preflight was hardened to catch that stale engine-container mapping before Compose mutates state.

After removing the failed validation container, a non-default port launch passed:

```powershell
.\bootstrap.cmd -Engine podman -Gpu off -Port 5009 -NoBrowser -TimeoutSeconds 180 -MinimumFreeGB 1
```

Status:

```powershell
.\scripts\status.cmd -Engine podman -Port 5009
```

Confirmed readiness `ready`, assets `ok`, config `ok`, and `runtime.container_engine: podman`.

The Podman validation container was removed afterward.

## Known Caveats And Design Tradeoffs

### Source Checkout Versus Final Package Artifact

The Docker and Podman smokes above were run from the current source checkout. In this checkout, `.env` points to `towerscout:local`. A generated final RC package will instead include release metadata and an immutable image reference. Package-artifact bootstrap validation should be run after this PR is merged into the RC baseline.

Reviewer question: Is source-checkout validation sufficient for PR review if final package-artifact validation is explicitly required after merge?

### Asset ZIP Extraction Uses Temporary Staging

Bootstrap validates the asset ZIP and refuses to promote if `assets/model_params`, `assets/data`, or `assets/asset_manifest.v1.json` already exist. It also prevents path traversal and unexpected root entries.

Reviewer feedback recommended avoiding direct extraction into final `assets/`. That hardening is now implemented: ZIP contents are extracted into `assets/.staging-<guid>`, the staged manifest/release match is validated before final promotion, only the three expected root entries are moved into final `assets/`, the staging folder is removed on success or failure, and any promoted entries are cleaned up if final promotion fails.

Remaining reviewer question: Is the lightweight staging and cleanup behavior sufficient for RC1, or should the implementation go further and swap an entire assets directory atomically?

### Podman Port Behavior Is Host-Specific

Podman successfully launched TowerScout on port `5009`, but port `5000` hit a rootless port-forwarding bind conflict on this workstation even when Windows reported the port free. The docs now advise retrying with a non-default `-Port` and keeping that port consistent across status/log/import commands.

Reviewer question: Is this Podman caveat framed correctly, or should `bootstrap.cmd -Engine podman` default to a non-5000 port in support-directed docs?

### Podman Compose Provider Boundary

The observed Podman validation used `podman compose`, which reported an external Docker Compose binary provider:

```text
C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe
```

Docker Desktop was stopped, and readiness reported `container_engine: podman`, but the Compose provider binary came from a Docker Desktop install. Earlier Task-065 evidence validated `podman-compose 1.5.0` explicitly through `PODMAN_COMPOSE_PROVIDER`.

Reviewer feedback recommended documentation tightening rather than a code requirement. The Package Guide now states that the selected Compose provider must be validated in the target environment and that when Docker Desktop is uninstalled, `podman-compose` or another approved provider should be installed and selected with `PODMAN_COMPOSE_PROVIDER` when support needs to force that provider.

Remaining reviewer question: Is reporting the provider and documenting `PODMAN_COMPOSE_PROVIDER` enough for RC1, or should Podman validation scripts require an explicit provider override in Docker-Desktop-free environments?

### No Hosted Asset Download

Bootstrap accepts a local `-AssetZip`, verifies it, and imports it. It does not download assets. This is intentional and matches the current RC1 package boundary.

Reviewer question: Is the wording clear enough that bootstrap is local ZIP staging, not hosted download?

### GPU Boundary

Bootstrap accepts `-Gpu off|auto|on` only so it can pass through to the existing launcher. It does not broaden GPU claims. Default remains CPU-safe.

Reviewer question: Is GPU exposure in bootstrap acceptable as pass-through, or should docs further discourage `-Gpu auto|on` during first setup?

## Reviewer Feedback Requested

Please review the Task-074 changes with these questions in mind:

1. Does the bootstrap/preflight path stop early enough before mutating assets, engine state, or local configuration?
2. Are Docker and Podman checks accurate and sufficiently bounded for RC1?
3. Is the Podman `rootlessport` default-port caveat handled in the right place, with the right guidance?
4. Is the local asset ZIP validation strict enough for RC1, especially around checksums, unsafe paths, nested layouts, release matching, and manifest matching?
5. Is the temporary asset ZIP staging and cleanup behavior sufficient for RC1?
6. Does bootstrap reuse the existing validated launch/import path appropriately, without duplicating Compose or asset-import behavior?
7. Are the docs clear for non-command-line users and first-line support?
8. Is package generation complete, meaning all necessary bootstrap files are included in release packages?
9. Are there any negative cascading impacts on Task-066 RC validation, Task-073 pilot/UAT instructions, Task-075 GPU boundaries, or Settings-linked docs?
10. Is the remaining validation plan acceptable: PR review now, final package-artifact bootstrap validation after merge into the RC package baseline?

## Suggested Reviewer Inputs

To give a grounded review, the reviewer should inspect:

- The full PR diff.
- `TASK-074` task documentation and validation log.
- Bootstrap implementation and helper library.
- Existing Compose/launch/import helper code that bootstrap delegates to.
- Package generation changes.
- Focused tests.
- User-facing docs and Settings-linked HTML docs.
- UAT checklist updates.

## Files Most Relevant To Review

Implementation:

- `bootstrap.cmd`
- `scripts/bootstrap.ps1`
- `scripts/lib/TowerScoutBootstrap.ps1`
- `scripts/launch.ps1`
- `scripts/package-release.ps1`
- `scripts/import-assets.ps1`
- `scripts/lib/TowerScoutCompose.ps1`

Tests:

- `tests/unit/test_task_074_bootstrap.py`
- `tests/unit/test_release_package_script.py`
- `tests/unit/test_import_assets_script.py`
- `tests/unit/test_flask_routes.py`

Task and validation context:

- `.agent_work/tasks/completed/TASK-074-runtime-prerequisite-preflight.md`
- `.agent_work/current-tasks.md`
- `.agent_work/tasks/completed/TASK-073-clean-machine-uat-plan.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`

User/support docs:

- `docs/v1-rc1-quick-start.md`
- `docs/v1-rc1-quick-start.html`
- `docs/v1-rc1-package-guide.md`
- `docs/oci-quick-start.md`
- `docs/oci-runtime-contract.md`
- `docs/release-asset-bundle-contract.md`
- `docs/project-overview.md`
- `docs/project-overview.html`

Runtime/package baseline:

- `compose.yaml`
- `compose.gpu.yaml`
- `.env.example`
- `release-manifest.v1.json`
- `webapp/asset_manifest.v1.json`

## Suggested Reviewer Prompt

Please review the Task-074 runtime prerequisite preflight work for TowerScout V1 RC1. Focus on whether the new `bootstrap.cmd` / `scripts/bootstrap.ps1` path is safe, correctly bounded, and clear enough for RC1 pilot users and support staff.

Please assess:

- Whether preflight checks stop early enough before unsafe mutation.
- Whether Docker and qualified Podman support boundaries are accurately implemented and documented.
- Whether local Model & Data Package ZIP validation is strict enough.
- Whether asset ZIP extraction should be transactional before merge.
- Whether bootstrap correctly reuses existing `scripts/import-assets.ps1` and `scripts/launch.ps1`.
- Whether the user-facing docs and UAT checklist are comprehensive and internally consistent.
- Whether the Podman `rootlessport` default-port caveat is handled appropriately.
- Whether any changes could regress Task-066 RC validation, Task-073 UAT flow, Task-075 GPU boundaries, or package assembly.

Please provide findings ordered by severity, with concrete file/line references where possible, and include any recommended changes that should be made before PR merge versus deferred to post-merge package-artifact validation.
