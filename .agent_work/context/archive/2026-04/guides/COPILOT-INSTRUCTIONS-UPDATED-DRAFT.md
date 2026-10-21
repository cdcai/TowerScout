# TowerScout AI Coding Guide (Updated Draft)

This draft updates the original `.github/copilot-instructions.md` against the current repository state as of 2026-04-06. It keeps the original intent of the project guide, but removes stale claims and adds current repo capabilities that are now part of the application.

## Project Overview

TowerScout is a Flask web application for identifying cooling towers from satellite and aerial imagery using a YOLOv5 detector plus an EfficientNet secondary classifier. The project remains centered on outbreak-investigation and registry-building workflows, with Google Maps and Azure Maps as the active map providers and a setup flow aimed at reducing local deployment friction for non-technical users.

## Current Repository Snapshot

- Sprint 04 is in wrap-up and Sprint 05 intake is focused on Docker containerization, runtime dependency verification, and a current smoke-test baseline.
- Setup Wizard and Settings work is complete in the repo.
- Docker containerization is still backlog work. There is no `Dockerfile` in the repo yet.
- The generated frontend bundle exists at `webapp/js/towerscout.js`; source modules live under `webapp/js/src/`.

## Architecture Overview

### Core Components

- `webapp/towerscout.py` - Main Flask application, route surface, setup-required boot mode, session-backed detection workflow, export and restore flows
- `webapp/ts_config.py` - Runtime configuration management, `.env` persistence, API-key validation, settings updates, performance summary helpers
- `webapp/ts_progress.py` - In-memory detection progress tracker used by the live progress overlay and cancel flow
- `webapp/ts_yolov5.py` - YOLOv5 detector wrapper
- `webapp/ts_en.py` - EfficientNet secondary classifier
- `webapp/ts_maps.py` - Shared provider helpers and geographic utilities
- `webapp/ts_gmaps.py` and `webapp/ts_azure_maps.py` - Google Maps and Azure Maps backend provider implementations
- `webapp/ts_geocoding.py` and `webapp/ts_geocache.py` - Reverse/forward geocoding and cache behavior
- `webapp/ts_validation.py` - Request, polygon, bounds, search, and file-upload validation plus rate limiting
- `webapp/ts_errors.py` - Structured error types for API and runtime failures
- `webapp/ts_logging.py` - Logging helpers and sanitization
- `webapp/ts_performance.py` - Performance metrics capture for detections
- `webapp/ts_events.py` - Exit/cancel event handling for long-running work
- `webapp/ts_imgutil.py` - Tile/image utilities and coordinate transforms
- `webapp/ts_zipcode.py` - ZIP code polygon lookup and validation
- `webapp/templates/towerscout.html` - Main UI template, setup wizard shell, settings modal, progress overlay
- `webapp/build.js` - Frontend bundle build script
- `Model/` - Model training and evaluation notebooks
- `SyntheticData/` - Synthetic data generation and augmentation tools
- `TowerScoutSite/` - Marketing/static site assets

### Current Detection Flow

1. App boots in normal mode or setup-required mode depending on configured provider keys.
2. Setup Wizard and Settings use `ts_config.py` plus config API routes to validate and save provider keys into `webapp/config/.env`.
3. User selects an area via search, ZIP code, circle, or polygon boundary.
4. Frontend can estimate tiles via `POST /api/detection/estimate` before running full detection.
5. Full detection runs through `POST /getobjects`, with live phase updates exposed through `GET /api/detection/progress`.
6. Backend generates tiles, downloads imagery, runs YOLOv5, applies EfficientNet where needed, deduplicates results, reverse-geocodes detections, and stores results in session for review/export.
7. Frontend renders results on the map and in the right-side list, supports filtering and review, and allows export/restore.

## Production-Critical Legacy Requirements

These behaviors still matter and should be preserved unless the user explicitly asks to change them:

- Cooling tower detection with confidence-based filtering
- Google Maps and Azure Maps provider support
- Polygon, circle, and ZIP code search workflows
- Manual tower addition and review workflows
- Dataset export and restore
- Tile-by-tile and tower-by-tower review modes
- Outbreak-investigation speed target of roughly under 30 seconds for under 100 tiles on suitable hardware
- Manual review support for detection completeness and provenance

## Current User-Facing Capabilities

### Setup, Configuration, and Deployment Prep

- Setup-required boot mode when no valid provider key is configured
- First-launch Setup Wizard with key validation, default-provider selection, and performance guidance
- Settings modal with masked key previews, configuration updates, debug toggle, and cache-clearing flow
- Runtime config refresh without app restart after saving keys
- Config persistence to `webapp/config/.env` with backup and rollback behavior

### Detection and Review

- Tile estimation before full detection
- Progress overlay with live phase titles/details and cancel support
- Provider-aware geocoding and geocoding cache behavior
- Duplicate suppression before geocoding
- Confidence filtering and review mode controls
- Manual tower addition with provider-specific drawing instructions
- Dataset export and restore via `contents.txt`

### Search and Map UX

- Google Maps search via `PlaceAutocompleteElement`
- Azure Maps search via the Azure service SDK
- Custom polygon drawing for Google Maps instead of deprecated `DrawingManager`
- Native Azure Maps drawing tools
- Provider switching and provider-aware state management
- Dynamic Google Maps script loading through a backend key-fetch path

### Export and Data Provenance

- CSV export with ML versus manual source tracking
- KML export
- YOLO and XML label generation in dataset exports
- Manual tower persistence across export/restore flows

## Session, Temp Storage, and Config Behavior

### Session Management

- The app uses server-side filesystem sessions through `Flask-Session`, not default signed-cookie-only sessions.
- Main Flask session state includes items such as `results`, `detections`, `metadata`, `tiles`, `tmpdirname`, `needs_setup`, and geocoding usage/limit state.
- Temporary detection/session directories are created under `webapp/temp/session`.
- Temporary uploads are still written under `uploads/`.

### Config Storage

- Preferred config path is `webapp/config/.env`.
- If a legacy `webapp/.env` exists, `ts_config.ensure_env_file()` copies it into `webapp/config/.env`.
- Settings updates are written through `ts_config.update_env_file()` and then reloaded into the running process.

### Docker Implications

- Docker support is not implemented yet.
- When TASK-025 is executed, containerization must preserve setup-wizard behavior by providing:
  - writable filesystem-backed session storage
  - a stable `FLASK_SECRET_KEY`
  - a persistent writable mount for `webapp/config/`
- A read-only container or ephemeral config storage would break or undermine current setup/settings behavior.

## Model Loading and Runtime Details

### YOLOv5

- YOLOv5 engines are loaded lazily through `get_engine()`.
- Current CUDA path in `ts_yolov5.py` uses batch size `8` and semaphore `8`.
- CPU path falls back to `torch.get_num_threads()` for batch sizing.

### EfficientNet

- EfficientNet is initialized eagerly by default at app import time.
- If `TOWERSCOUT_LAZY_MODEL_INIT` is enabled, the secondary classifier is loaded lazily instead.
- `TOWERSCOUT_SAVE_EN_DEBUG_IMAGES` controls debug image dumping and is off by default for normal runs.

### ZIP Code Provider

- ZIP code data remains a startup/runtime dependency and is loaded under a lock.

## Validation, Security, and Error Handling

### Validation Already Implemented

- Polygon coordinate validation and polygon geometry validation
- Bounds validation
- Provider and engine validation
- Search query validation
- Image, dataset, and model upload validation
- Route-level rate limiting for config, detection, geocoding, and upload flows

### Security Posture

- API keys are stored in environment/config files, not in `apikey.txt`
- Key values are masked in status responses used by the settings UI
- Logging helpers sanitize sensitive values
- Current provider env vars are `GOOGLE_API_KEY` and `AZURE_MAPS_SUBSCRIPTION_KEY`
- `BING_API_KEY` still exists as a legacy compatibility input, but Bing is not part of the current frontend focus

### Error Handling

- `TowerScoutError` subclasses are translated into structured JSON responses
- Validation errors return `400`
- Network failures return `502`
- Configuration failures return `400`

## Frontend Architecture

### Build System

- Frontend sources are concatenated by `webapp/build.js`.
- The current source bundle order covers 30 JavaScript modules.
- `webapp/js/towerscout.js` is generated output and should be rebuilt after source changes.

### Source Areas

- Foundation:
  - `src/config.js`
  - `src/store.js`
- Managers:
  - `ProviderStateManager.js`
  - `TimerManager.js`
  - `EventListenerManager.js`
  - `ErrorHandler.js`
- Boundaries:
  - `CircleBoundary.js`
  - `PolygonBoundary.js`
  - `ZipcodeBoundary.js`
- Providers:
  - `TSMap_base.js`
  - `GoogleMap.js`
  - `AzureMap.js`
  - `providerInit.js`
  - `providerSwitch.js`
- Detection:
  - `PlaceRect.js`
  - `Detection.js`
  - `DetectionList.js`
  - `DetectionReview.js`
  - `Tile.js`
- UI and helpers:
  - `search.js`
  - `export.js`
  - `navigation.js`
  - `apiHelpers.js`
  - `coordinates.js`
  - `imagery.js`
  - `polygonValidation.js`
  - `setup-wizard.js`
  - `settings.js`
  - `globals.js`
  - `towerscout.js`

### Current Frontend Behaviors Worth Preserving

- Setup Wizard auto-check on page load through `/api/config/status`
- Progress overlay polling and stale-response handling
- Layered logging through `TowerScoutLogger`
- Provider-aware request flows and provider switching
- Manual tower drawing workflows and visual differentiation

## Current Route Surface Worth Knowing

### Utility and Provider Routes

- `GET /getengines`
- `GET /getgooglekey`
- `GET /getproviders`

### Config and Setup Routes

- `POST /api/config/validate-key`
- `POST /api/config/save-keys`
- `GET /api/config/status`
- `POST /api/config/reset-session`
- `GET /api/config/performance`

### Detection and Geocoding Routes

- `POST /api/geocode/forward`
- `POST /api/geocode/reverse`
- `POST /api/detection/estimate`
- `GET /api/detection/progress`
- `POST /getobjects`
- `POST /getobjectscustom`

### Data Management Routes

- `POST /uploaddataset`
- Existing image/model upload routes remain part of the Flask app and should be checked before changing upload behavior

## Development Workflows

### Local Development

```bash
cd webapp
python towerscout.py dev
```

### Frontend Build and Browser Validation

```bash
node webapp/build.js
npm run test:stage-0
npm run test:browser:detect
npm run test:browser:detect:google
npm run test:browser:detect:azure
```

### CI Snapshot

- Python 3.11 and 3.12
- `flake8`
- `black --check`
- `mypy` (currently non-blocking)
- `bandit` (currently non-blocking)
- unit tests
- integration tests (currently non-blocking)
- placeholder Docker build step that is allowed to fail until containerization exists
- Trivy security scan

## Task and Workspace Integration

### Task Tracking Files

- `.agent_work/current-tasks.md` is the source of truth for active work
- `.agent_work/task-backlog.md` tracks future work
- `.agent_work/completed-tasks.md` tracks recent completions
- `.agent_work/requirements.md` and `.agent_work/design.md` hold spec/design artifacts

### Current Planning Snapshot

- Sprint 04 wrap-up is effectively complete
- Sprint 05 intake centers on:
  - TASK-025 Docker containerization
  - TASK-051 runtime dependency verification and split
  - TASK-052 current integration smoke-test baseline

## TowerScout-Specific Guardrails

- Preserve outbreak-investigation workflows unless the user explicitly changes them
- Be careful with `ts_yolov5.py` and `ts_en.py`; changes there can affect core detection behavior
- Do not break export/restore contracts, especially `contents.txt` semantics and manual tower provenance
- Do not treat setup/settings work as future or missing; it is already present in the repo
- Treat `webapp/js/towerscout.js` as generated output
- If containerization is discussed, remember the current filesystem session and config-write requirements

## Git and Change Hygiene

- Prefer feature branches and descriptive conventional-commit-style messages when preparing reviewable work
- Keep a clear paper trail for architecture or deployment changes
- For documentation or planning updates, sync the relevant `.agent_work/` task artifacts when the change materially affects current or upcoming work

## References

- `.github/instructions/spec-driven-approach.instructions.md`
- `.agent_work/current-tasks.md`
- `.agent_work/task-backlog.md`
- `AGENTS.md/architecture.md`
- `AGENTS.md/dev-workflow.md`
- `AGENTS.md/security.md`
