# TASK-025 V1 Runtime And Persistence Contract

**Date**: 2026-05-05
**Status**: Phase 1 runtime-contract baseline
**Scope**: TowerScout v1 local Docker-compatible / OCI runtime, persistence, assets, readiness, release package, and validation contract

---

## Executive Summary

`TASK-025` should implement TowerScout as an engine-aware OCI-compatible local runtime, not a Docker Desktop-specific product path. The normal end-user path is a GitHub Release ZIP with Compose-compatible configuration, scripts, docs, checksums, an asset manifest, and a pinned GHCR image reference by digest. Podman is the preferred open-source Windows runtime target after a compatibility spike; Docker compatibility remains a supported developer/support and licensed/approved fallback path.

The current codebase is ready to containerize only if the container contract preserves these runtime facts:

- `webapp/config/.env` is the durable configuration and provider-key store.
- `FLASK_SECRET_KEY` must be stable and must be generated into persistent config on first container start if absent.
- Flask sessions are filesystem-backed under `webapp/flask_session/`.
- Detection tiles, restored datasets, and export working files are session-temp state under `webapp/temp/session/`.
- Logs, performance CSV/JSONL files, uploads, map cache, and geocoding cache are writable runtime surfaces under `webapp/`.
- Large runtime assets are gitignored and must be managed outside the image source checkout.
- Current non-dev startup eagerly loads ZIP-code data and the default YOLO engine; missing assets can prevent startup before users reach setup/recovery unless startup behavior is adjusted.

---

## V1 Support Boundary

| Area | V1 contract |
| --- | --- |
| User target | Windows 11 AMD64, single-user local use |
| Compute baseline | CPU required |
| GPU | Optional NVIDIA/CUDA on compatible AMD64 hosts after validation |
| Runtime | OCI-compatible image with Compose-compatible run config |
| Preferred open-source host | Podman Desktop plus WSL2/Hyper-V after spike passes or risk acceptance |
| Compatible fallback | Docker Desktop or Linux Docker/Podman where licensed, approved, and validated |
| Out of scope | Mac, ARM64, offline, air-gapped, VDI, shared multi-user, native installer, managed remote hosting |
| Network | Normal outbound internet required for providers and default asset bootstrap |
| Source clone/build | Developer/support path only, not normal user path |

---

## Runtime Path Contract

All container mounts should use normalized `webapp/` paths from `webapp/ts_paths.py`. Repo-root `logs/`, `uploads/`, `cache/`, `data/`, and `model_params/` are not the v1 container mount contract.

| Path | Current owner/source | V1 class | Default persistence | Notes |
| --- | --- | --- | --- | --- |
| `webapp/config/` | `ts_config.py` | Restart/update-durable | Named volume | Contains `.env`, backups, and lock file. Must persist provider keys, default provider, and generated `FLASK_SECRET_KEY`. |
| `webapp/model_params/` | `ts_paths.py`, `ts_yolov5.py`, `ts_en.py` | Restart/update-durable assets | Named volume | Gitignored model assets. Asset manifest owns expected files and checksums. |
| `webapp/data/` | `ts_zipcode.py` | Restart/update-durable assets | Named volume | Gitignored ZIP-code shapefile data. Current `ts_zipcode.py` uses `data/...` relative path and should be fixed or startup cwd must be controlled. |
| `webapp/logs/` | `ts_logging.py`, `ts_performance.py` | Restart/update-durable support data | Named volume | Contains `towerscout.log`, `towerscout_errors.log`, `performance.log`, `performance.jsonl`, and `performance_events.jsonl`. Sensitive local locations and operational details may appear here. |
| `webapp/flask_session/` | Flask-Session config in `towerscout.py` | Writable runtime state | Named volume | Preserve across restart for better continuity, but not a durable job-state guarantee. |
| `webapp/temp/session/` | detection/export/restore workflow | Cleanup-safe runtime state | Named volume or same app data volume | Contains tile images, labels, restored dataset working files, and export staging. Safe to clean when no run is active. |
| `webapp/uploads/` | custom image/model debug upload paths | Writable runtime state | Named volume | Current startup deletes existing files directly under uploads. EN debug images may write here if enabled. Model upload is disabled by default. |
| `webapp/cache/maps/` | map proxy cache in `towerscout.py` | Best-effort cache | Named volume preferred, cleanup-safe | Cache TTL is service-specific. Can contain provider-use/location-sensitive data. |
| `webapp/cache/geocoding/` | `ts_geocache.py` | Best-effort cache | Named volume preferred, cleanup-safe | Default file cache `geocoding_cache.json`, 24h max age. Can contain addresses and coordinates. |
| `webapp/vendor/yolov5_local/` | tracked source | Image/source code | Image layer | Must be present in image; `ts_yolov5_local.py` fails fast if missing. |
| `webapp/js/towerscout.js` | frontend build output | Image/source code | Image layer | Build in release/image pipeline. End users should not need Node. |

### Persistence Profile Decision

Default v1 profile: named volumes for config, assets, logs, sessions/temp/uploads, and cache.

Optional host-visible profile: allowed only as documented alternate Compose config after validation. It must warn that local folders may contain provider keys, logs, coordinates, cached addresses, user-uploaded files, and investigation exports.

---

## Asset Inventory

The current workspace contains these gitignored runtime assets. Checksums below are local evidence for the current asset set and should become manifest entries or release-package checksum inputs.

| Asset | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| YOLO weights | `webapp/model_params/yolov5/newest.pt` | 175084429 | `27315E156D8370D51D9C2A3C047C4BF5CC0C8AE1521036BDF800B7A8A81554E6` |
| EfficientNet project weights | `webapp/model_params/EN/b5_unweighted_best.pt` | 118567303 | `645113BADFCD17A1F9B451AABB54BF80E115A4FAACEB65E0CE3FC8DBFB108A5D` |
| ZIP-code CPG | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.cpg` | 5 | `3AD3031F5503A4404AF825262EE8232CC04D4EA6683D42C5DD0A2F2A27AC9824` |
| ZIP-code DBF | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.dbf` | 2838798 | `FB1CD7305831772FD375607A0561D9A7C9F126ED665D10D2D51E9A9772853D06` |
| ZIP-code PRJ | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.prj` | 165 | `0B9041E921D9EBB43247D314608FE9E38A0B008EE793067FC1806199EA1FB9DD` |
| ZIP-code SHP | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp` | 822559684 | `3A701EEBDF9982269F87AA19C49CCC6596CA303126E4901DD2EE814F22A591B4` |
| ZIP-code EA metadata | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp.ea.iso.xml` | 17697 | `648571DEA5799CF2011781635FD20AE7DEBD23DF34DA09CE37519F4202B166EA` |
| ZIP-code metadata | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp.iso.xml` | 50682 | `AEA0E75009756CA5B6FFF899C5053D8CBB91E5EBC17A67938B01977404CBE9F0` |
| ZIP-code SHX | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shx` | 270428 | `804A57259FC72A56E04FAE9B02617814E5C8F9853B353134FEF418973A227775` |

Total local gitignored asset footprint from `webapp/model_params/` and `webapp/data/`: `1119389191` bytes.

### Asset Decisions

- Large assets stay out of git and out of the default source checkout.
- The tracked v1 manifest location is `webapp/asset_manifest.v1.json`; `TOWERSCOUT_ASSET_MANIFEST` can override it for release validation or local support.
- Assets are staged before activation into durable `webapp/model_params/` and `webapp/data/` storage.
- Readiness checks manifest validity, file existence, and expected byte sizes. SHA-256 verification is available through `TOWERSCOUT_VERIFY_ASSET_HASHES=1` or explicit release validation, but is not enabled for every readiness poll because the ZIP-code geometry asset is large.
- Missing assets should produce `degraded` readiness when setup/recovery can still be served, or `fatal` only when Flask cannot safely serve support/recovery endpoints.
- Routine CI must not require private/heavy assets. It should validate image startup and health/readiness in missing-asset or degraded mode.
- Release-candidate validation must use real assets and run the `TASK-052` smoke path plus a real detection smoke where provider credentials and assets are available.
- `EfficientNet.from_pretrained('efficientnet-b5')` may rely on external base-weight download/cache behavior. `TASK-025` implementation must either manage those base weights as an explicit asset or change the model construction path to avoid hidden runtime download.

---

## Config And Secret-Key Contract

Current behavior:

- `ts_config.ensure_env_file()` creates `webapp/config/.env` or migrates legacy `webapp/.env`.
- Setup Wizard and Settings persist provider keys through `ts_config.update_env_file()`.
- `towerscout.py` currently generates an in-memory `SECRET_KEY` when `FLASK_SECRET_KEY` is absent.

Container v1 behavior:

1. On startup, ensure `webapp/config/.env` exists in persistent storage.
2. If `FLASK_SECRET_KEY` is absent in the active env file and environment, generate a secure key.
3. Persist that key to `webapp/config/.env` before Flask sessions are relied on.
4. Reload runtime environment after writing.
5. Do not expose the key in `/api/config/status`, `/api/readiness`, logs, or UI surfaces.
6. Verify restart/recreate keeps the same key.

Provider keys remain user-managed through Setup Wizard and Settings. Documentation must tell users to restrict Google and Azure keys in provider consoles because browser map integrations expose client-side keys by design.

---

## Startup And Readiness Contract

### Current Startup Risks

- Non-dev `python towerscout.py` calls `start_zipcodes()` and `get_engine(engine_default)` before serving Waitress.
- Missing ZIP-code data, missing YOLO weights, or hidden EfficientNet base-model download failure can prevent the app from serving the Setup Wizard or recovery guidance.
- `LAZY_MODEL_INIT` exists for EfficientNet, but the default remains eager initialization.

### Required Endpoints

`GET /api/health`

- Purpose: basic liveness for container engines, launcher, and support scripts.
- Response: `200` if Flask can serve requests.
- Payload: minimal JSON, for example `{"status":"ok","service":"towerscout"}`.
- Should not check heavyweight assets or provider credentials.

`GET /api/readiness`

- Purpose: structured application startup/support state.
- Response code should stay `200` for `starting`, `setup_required`, `degraded`, and `ready`; use `503` only for `fatal` if the app can still emit JSON.
- Payload must be redacted and machine-readable.

### Readiness States

| State | Meaning | Typical examples | Launcher behavior |
| --- | --- | --- | --- |
| `starting` | App process is up but startup checks are still running | Directory creation, manifest scan, lazy preflight | Wait and poll |
| `setup_required` | App shell is usable but no provider key is configured | Empty `webapp/config/.env` with generated secret | Open browser to setup |
| `degraded` | App shell/setup is usable, but optional or recoverable runtime capability is missing | Missing model assets, missing ZIP data, provider key invalid, cache not writable | Open browser with warning or show recovery |
| `ready` | Required config/assets for normal workflow are available | Provider configured, assets valid, writable paths ok | Open browser normally |
| `fatal` | App cannot run or cannot safely serve recovery flows | Config path not writable, asset manifest unreadable in a blocking way, incompatible runtime dependency | Show logs/support guidance |

### Readiness Components

Minimum component details:

- `config`: env path exists, writable, secret key persisted, setup required
- `providers`: configured Google/Azure availability, no raw key values
- `assets`: manifest status, missing/corrupt asset names, no external secrets
- `paths`: config/log/session/temp/upload/cache writability
- `version`: app version, image tag/digest when provided, asset manifest version
- `runtime`: Python version, CPU/GPU mode, container engine hint if provided by env
- `recovery`: short actionable next steps

---

## Upload And Request-Body Contract

Current behavior:

- `TowerScoutValidator.MAX_FILE_SIZE` defaults to 50 MB.
- `TOWERSCOUT_MAX_REQUEST_BODY_BYTES` overrides Flask and Waitress request-body limits.
- `MODEL_UPLOAD_ENABLED` is false unless `TOWERSCOUT_ENABLE_MODEL_UPLOAD` is truthy.
- `.pt` / `.pth` model uploads are disabled by default and are not the normal model update path.

Container v1 behavior:

- Preserve `TOWERSCOUT_MAX_REQUEST_BODY_BYTES` as the single request-body/upload limit knob.
- Keep model upload disabled by default.
- Treat trusted model updates as release asset updates through the manifest, not browser uploads.
- Document that dataset/custom-image uploads and generated exports may contain sensitive investigation data.

---

## Cache And Geocode Durability Decision

V1 classification: best-effort, cleanup-safe, persisted by default for performance and provider-quota friendliness.

Rationale:

- Map cache TTLs are short and provider/service-specific.
- Geocoding cache defaults to 24-hour expiration and stores coordinates/addresses.
- Persisting cache across restart is useful, but cache loss should not break correctness.
- Cache can contain sensitive location and provider-use data, so docs must include cleanup and sensitive-data warnings.

---

## Release Package Contract

Normal user package: GitHub Release ZIP.

Required contents:

- `compose.yaml`
- `.env.example` or runtime env template with no secrets
- `start`, `stop`, `logs`, and `status` scripts, with Windows-first behavior
- quick-start guide
- technical OCI runtime contract
- asset manifest and checksums
- restricted-network/manual asset import instructions
- troubleshooting and reset/update guidance
- sensitive local data warning
- pinned GHCR image reference by digest
- optional OCI image archive instructions for restricted-network fallback

The release package should not require normal users to install Python, Node, GDAL, PyTorch, or build frontend assets locally.

---

## Validation Contract

### Routine CI

Routine CI should prove:

- image builds from clean checkout
- frontend bundle is produced by the build pipeline
- container starts without provider keys and without heavyweight/private assets
- `/api/health` returns ok
- `/api/readiness` returns `setup_required` or `degraded` with explicit missing-asset details
- `webapp/config/.env` can be created in a mounted volume
- generated `FLASK_SECRET_KEY` persists across restart/recreate in a mounted config volume

Routine CI should not require:

- Google/Azure provider credentials
- large model/data assets
- real provider-backed detection
- browser automation against live maps

### Release-Candidate / Local Validation

Release validation should prove:

- real assets bootstrap/import into persistent storage and pass SHA-256 checks
- Setup Wizard works in the selected runtime host
- Settings save/load persists across restart
- `TASK-052` route and bounded detection-readiness smoke runs against the containerized app
- real detection smoke runs when provider keys and AOI fixture are available
- logs and support diagnostics are available through engine-aware scripts
- Podman compatibility spike passes before Podman is promised in end-user docs

### Reused `TASK-052` Smoke

Reuse the maintained smoke contract from:

- `tests/unit/test_flask_routes.py`
- `tests/integration/test_end_to_end.py`

The bounded detection-readiness smoke intentionally reaches real local YOLO initialization and stops at a mocked imagery boundary. Container validation should preserve that intent instead of adding an unrelated Docker-only readiness test.

---

## Implementation Implications For Phase 2

1. Add startup/preflight helpers before or alongside image work so missing assets do not block supportable readiness responses.
2. Fix ZIP-code data path handling or explicitly set container working directory to `webapp`.
3. Add first-run `FLASK_SECRET_KEY` persistence before sessions initialize.
4. Add `/api/health` and `/api/readiness` before launcher work begins.
5. Add an asset manifest format before implementing bootstrap/download.
6. Use named volumes in default Compose config.
7. Keep engine commands generic enough for Docker or Podman.
8. Split CI container checks from release-candidate asset-backed validation.

---

## Open Follow-Ups

- Decide release-package checksum format.
- Decide whether the first implementation downloads assets automatically or only validates/imports a manually supplied bundle.
- Decide whether to bake ZIP-code data into an optional image variant or keep it exclusively in durable asset storage.
- Decide whether `TOWERSCOUT_LAZY_MODEL_INIT=1` should become the default container mode.
- Record TowerScout application license/open-source suitability as product/legal follow-up before release promises.
