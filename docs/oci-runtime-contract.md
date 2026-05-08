# TowerScout OCI Runtime Contract

This document summarizes the v1 container runtime contract. The detailed task evidence lives under `.agent_work/tasks/active/TASK-025/`.

## Runtime Shape

- Application process: `python towerscout.py`
- HTTP port: `5000`
- Server: Waitress
- Health: `GET /api/health`
- Readiness: `GET /api/readiness`
- Default container startup: `TOWERSCOUT_STARTUP_PRELOAD=0` and `TOWERSCOUT_LAZY_MODEL_INIT=1`
- YOLO/Ultralytics config directory: `YOLO_CONFIG_DIR=/app/webapp/cache/ultralytics`

The container startup defaults allow TowerScout to serve setup and readiness responses before large runtime assets are present. Readiness reports missing assets instead of hiding them behind startup failure.

## Readiness States

- `setup_required`: app is usable, but provider setup is incomplete
- `degraded`: app is usable, but recoverable runtime capability is missing, such as required assets
- `ready`: provider config and required assets are present
- `fatal`: app cannot safely serve normal or recovery workflows

`/api/readiness` returns HTTP 503 only for `fatal`. Other states return HTTP 200 with machine-readable JSON.

## Required Writable Paths

The default Compose profile maps each path to a named volume:

| Container path | Purpose |
| --- | --- |
| `/app/webapp/config` | `.env`, backups, generated `FLASK_SECRET_KEY` |
| `/app/webapp/model_params` | YOLO and EfficientNet model assets |
| `/app/webapp/data` | ZIP-code shapefile assets |
| `/app/webapp/logs` | app, error, and performance logs |
| `/app/webapp/flask_session` | Flask-Session files |
| `/app/webapp/temp/session` | detection/export/restore working state |
| `/app/webapp/uploads` | uploads and optional debug images |
| `/app/webapp/cache` | map and geocoding caches |

## Persistence Classification

V1 uses named volumes as the default persistence profile. A host-visible data directory can be considered later, but it is not part of the validated default release profile.

| Path | Classification | Notes |
| --- | --- | --- |
| `/app/webapp/config` | restart/update durable | Contains provider config, generated `FLASK_SECRET_KEY`, backups, and optional local CA bundles. |
| `/app/webapp/model_params` | restart/update durable | Contains imported model assets. Detection depends on this volume. |
| `/app/webapp/data` | restart/update durable | Contains imported ZIP-code shapefile assets. ZIP search depends on this volume. |
| `/app/webapp/logs` | restart/update durable support data | Useful for diagnostics and should survive container replacement. |
| `/app/webapp/flask_session` | writable runtime state | Preserves active user session state across container restart. It may be cleared as a support/reset action. |
| `/app/webapp/temp/session` | cleanup-safe working state | Used for detection/export/restore working files. It should be writable and may be cleaned when no run is active. |
| `/app/webapp/uploads` | restart/update durable user data | May contain uploaded datasets, images, or support artifacts. Treat as sensitive. |
| `/app/webapp/cache` | best-effort durable cache | Contains map, geocoding, and Ultralytics cache/config data. It may be cleared to recover from cache problems, but preserving it improves repeated local use. |

## Secret Key Contract

If `FLASK_SECRET_KEY` is absent on startup, TowerScout generates a secure value and persists it to `/app/webapp/config/.env`. The value must survive container restart/recreate through the mounted config volume and must not be exposed through config status, readiness, logs, or UI.

## Asset Contract

Tracked manifest: `/app/webapp/asset_manifest.v1.json`

Default release import layout:

```text
assets/model_params/
assets/data/
```

Windows import helper:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
```

Readiness checks:

- manifest is present and valid
- required asset files exist
- expected byte sizes match

SHA-256 verification is available with `TOWERSCOUT_VERIFY_ASSET_HASHES=1` for release validation and support diagnostics.

Hosted asset download/bootstrap is out of scope for the v1 control package. The supported v1 path is manifest-backed asset import from a local bundle using `scripts/import-assets.cmd`, with optional SHA-256 verification for release-candidate and support validation. A hosted downloader requires a separate design for asset hosting, checksum enforcement, retries, proxy/TLS behavior, partial-download recovery, and restricted-network fallback.

## Release Package Contract

The GitHub Release control package is assembled by `scripts/package-release.cmd` / `scripts/package-release.ps1`. It contains:

- Compose runtime configuration
- `.env.example` with the selected image reference
- Windows `.cmd` wrappers and PowerShell helpers for start, stop, logs, status, asset import, and TLS CA import
- top-level `start.bat` launcher that starts Compose, polls `/api/readiness`, and opens the browser at `http://localhost:<port>` after the app shell is reachable
- this runtime contract and the quick start
- `webapp/asset_manifest.v1.json`
- `IMAGE.txt`
- `SHA256SUMS.txt`
- a top-level ZIP checksum beside the package ZIP

Normal release packages must set `TOWERSCOUT_IMAGE` to an immutable registry digest reference such as `ghcr.io/j-schulein/towerscout@sha256:<digest>`. The package script requires `-ImageDigest` by default; packages without an image digest can be generated only by passing `-AllowMutableImage` and are for local validation or developer/support use only.

Current repository package target: `ghcr.io/j-schulein/towerscout`.

Image publication is handled by the manual GitHub Actions workflow `.github/workflows/container-publish.yml`. The workflow requires `packages: write`, pushes a Linux/AMD64 image, uploads `image-metadata.json`, and reports the digest reference in the workflow summary.

Bundled OCI image archives are not part of the supported v1 release package. Restricted-network support for v1 should preload the pinned image into the selected engine image store through a site/support procedure, then use the normal control package. A packaged OCI archive fallback remains follow-on release engineering work until archive creation, checksum/signature handling, import UX, and Docker/Podman validation are implemented.

## Upload Limit

`TOWERSCOUT_MAX_REQUEST_BODY_BYTES` remains the single request-body/upload-size knob. Model upload remains disabled unless `TOWERSCOUT_ENABLE_MODEL_UPLOAD` is explicitly truthy.

## TLS Trust

Provider-key validation and provider API calls should verify TLS by default. Container deployments behind TLS-inspecting proxies or endpoint tools may need to provide a local CA bundle through the persistent config volume and set `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` to the in-container PEM path.

`scripts/import-tls-ca.cmd` can export a Windows certificate-store entry by thumbprint, include its Windows chain, copy it into `/app/webapp/config/certs/`, and build `/app/webapp/config/certs/towerscout-ca-bundle.pem` by appending the imported CA material to the container's default Debian CA bundle. The release `.env` should then point both `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` at that combined bundle path.

Docker and Podman use separate named volumes, so CA import must be run for the selected engine. If `.env` points at `/app/webapp/config/certs/towerscout-ca-bundle.pem` but that file is missing from the selected engine's config volume, provider-key validation will fail until the CA helper is run for that engine. `TASK-065` identified this as a supportability case that should return a clearer setup error instead of a generic internal server error.

The CA import helper supports `-VerifyProvider auto|google|azure|none`. `auto` follows `DEFAULT_MAP_PROVIDER` when available and otherwise uses Google; `azure` avoids a Google-only verification assumption for Azure-first or Google-blocked sites; `none` builds the bundle without making a remote verification request.

`TOWERSCOUT_ALLOW_INSECURE_TLS=1` exists only as a local validation fallback for provider-key checks and should not be used as the normal release posture.

## Validation Split

Routine CI should prove image build, asset-light startup, health/readiness, and persistent config/secret behavior without provider credentials or large assets.

Release-candidate validation should add real asset import, SHA-256 verification, setup/settings persistence across restart, and the maintained detection smoke path.

## Podman Compatibility Boundary

The engine-aware scripts support `-Engine podman` through `podman compose`. On Windows, `podman compose` delegates Compose behavior to an external provider such as Docker Compose or `podman-compose` while wiring that provider to the Podman socket.

The current local validation covers the Podman WSL engine path, named volumes, asset import, readiness, and containerized smoke behavior. A follow-up validation also proved that the Podman runtime path can start and smoke-test TowerScout while Docker Desktop is fully quit and the Docker daemon is unreachable.

`TASK-065` validated a Docker-Desktop-free Compose-provider path with `podman-compose 1.5.0` selected explicitly through `PODMAN_COMPOSE_PROVIDER`. The release launcher reached readiness on Podman, status and health/readiness checks passed, the containerized `TASK-052` smoke passed, and Docker Desktop daemon access remained unavailable during the validation.

Release qualification for Podman should include the selected Compose provider explicitly. The supported Podman path requires a running Podman machine and an approved Compose provider such as `podman-compose` that can talk to the Podman socket; if multiple providers are installed, `PODMAN_COMPOSE_PROVIDER` can be used to force the intended provider.

The launcher reports Compose-provider information before startup. For Podman, a `PODMAN_COMPOSE_PROVIDER` override is checked for existence before Compose is invoked so a mistyped provider path fails early with an actionable message.

## Browser Origin

The launcher opens TowerScout with a `localhost` browser origin. During `TASK-065` Podman browser regression, Google detection passed from `127.0.0.1`, but Azure Maps browser loading failed from `127.0.0.1` with a provider CORS preflight error and passed from `localhost`. Release support should therefore treat `localhost` as the expected browser URL while still allowing health/readiness tooling to use loopback addresses.
