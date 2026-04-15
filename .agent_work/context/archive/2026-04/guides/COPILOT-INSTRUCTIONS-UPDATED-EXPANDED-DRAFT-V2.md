# TowerScout AI Coding Guide (Expanded Updated Draft)

This expanded draft is intended to function as a high-context replacement candidate for `.github/copilot-instructions.md` if the project wants a single, authoritative guidance file for agent context. It preserves much more of the original document's project context, guardrails, and workflow guidance, while correcting stale or superseded claims against the current repository state as of 2026-04-06.

## Mission and Product Context

TowerScout is a Flask web application for identifying cooling towers from satellite and aerial imagery using a YOLOv5 detector plus an EfficientNet secondary classifier. It began as a graduate project, but the repo and surrounding workflow are now oriented around practical outbreak-investigation and registry-building use cases rather than a purely academic prototype.

The project still carries public-health workflow expectations:

- support fast area definition and tower detection
- preserve manual review and manual correction workflows
- preserve export and restoration workflows for iterative investigation and labeling
- keep Google Maps and Azure Maps workflows operational
- keep the path open for non-technical local deployment

## Current Repository Status

### Current State

- Sprint 04 is in wrap-up, with most planned implementation work completed.
- Setup Wizard and Settings are implemented in the repo.
- Detection progress, estimate/detect separation, and cancel handling are implemented in the repo.
- Docker containerization is still planned work, not implemented work.
- The repo contains substantial recent architecture and workflow changes that are not reflected in the original `copilot-instructions.md`.

### Sprint 04 Summary

Sprint 04 moved the repo from a "major usability and stabilization work still pending" state into a late pre-containerization state. The sprint started with Setup Wizard delivery as the primary objective, but it expanded into a broader closeout of setup/configuration, logging, performance quick wins, stale-surface cleanup, detection-workflow stabilization, live browser validation, and UI polish.

At the current tracker state, Sprint 04 wrap-up records `TASK-046`, `TASK-047`, `TASK-048`, `TASK-049`, `TASK-050`, `TASK-053`, and the `ISSUE-003` follow-up work as complete, with only optional quick wins and Sprint 05 intake still open.

**Sprint 04 Bundle Evolution:**
- frontend bundle size grew from `412.8 KB` to `446.1 KB` (`+33.3 KB`) as setup/configuration flows, progress status UX, logging improvements, and stabilized detection-workflow behavior were added

**Sprint 04 Objective:**
- eliminate manual `.env` editing through first-launch setup and in-app settings
- improve operational polish and end-user clarity
- validate and stabilize the live detection workflow before containerization work begins

**Sprint 04 Major Accomplishments:**

1. **Setup and Configuration Became First-Class Runtime Features**
   - `TASK-046` landed `ts_config.py`, config validation/save/status/reset/performance endpoints, setup-required boot mode, Setup Wizard, Settings, `.env` persistence, masked key previews, and runtime config refresh.
   - The repo no longer depends on users editing config files by hand for normal setup.

2. **Logging and UX Were Tightened for Real End Users**
   - `TASK-048` converted the settings debug toggle into a real browser-console gating mechanism.
   - `TowerScoutLogger` now supports layered status messaging so users still see useful in-app output when debug mode is off.
   - `TASK-047` added main-screen polish, settings readability improvements, longer polygon-complete notifications, and the lightweight progress-overlay phase/status UX.

3. **Performance Investigation Produced Bounded, Shipped Wins**
   - `ISSUE-003` established evidence-backed profiling instead of anecdotal performance assumptions.
   - Azure overlay hot-path lookups were indexed to remove repeated full-shape scans.
   - Follow-up quick wins reduced unnecessary EfficientNet debug-image writes, redundant frontend hydration/visibility passes, and metadata-only overlay allocation.

4. **Detection Workflow Stabilization Became a Dedicated Workstream**
   - `TASK-053` added or stabilized estimate/detect separation, live progress plumbing, cancel lifecycle cleanup, provider-aware geocoding behavior, duplicate suppression, restore correctness, and browser-validated Google/Azure detection flows.
   - Live browser validation was restored as a maintained workflow through Puppeteer smoke coverage and manual browser QA.
   - The sprint treated setup/settings, export/restore, manual towers, and provider behavior as explicit non-regression surfaces rather than incidental side effects.

5. **Cleanup and Audit Work Clarified the Path to Sprint 05**
   - `TASK-050` produced a full-repo stale-code/performance audit.
   - `TASK-049` removed low-risk tracked artifacts, repaired the pytest collection gate, and archived stale helper/test surfaces without discarding historical context.
   - Remaining work was cleanly split into `TASK-051` and `TASK-052` so Docker work can start from a narrower, better-defined foundation.

**Sprint 04 Outcome:**

Sprint 04 materially changed what an agent should assume about the project. The repo is no longer best described as "missing setup, logging discipline, and stable live detection behavior." A better current mental model is:

- setup and settings are implemented
- progress and cancellation are implemented
- live Google/Azure detection flows have been actively browser-validated
- the main unresolved project frontier is deployment readiness, not baseline usability

### Immediate Path Forward

The current path forward is centered on Sprint 05 intake and deployment readiness:

1. `TASK-051`: runtime dependency verification and split
2. `TASK-052`: current integration smoke-test baseline
3. `TASK-025`: Docker containerization
4. `TASK-026`: CPU optimization follow-on work
5. `TASK-029`: multi-provider fallback and reliability improvements

### Important Status Correction

Do not describe the project as still lacking in-app API-key management or a first-launch setup experience. Those features now exist. The next path forward is deployment readiness and validation, not re-inventing setup/settings from scratch.

## Architecture Overview

### Core Backend Components

- `webapp/towerscout.py`
  - Main Flask app
  - Setup-required boot mode
  - Config, detection, geocoding, export, restore, and upload routes
  - Session-backed workflow state
- `webapp/ts_config.py`
  - `.env` discovery and migration
  - API key validation
  - config persistence and rollback
  - performance summary helpers for setup/settings flows
- `webapp/ts_progress.py`
  - in-memory progress tracker for active detection runs
  - cancel-request and terminal-status handling
- `webapp/ts_yolov5.py`
  - primary detection wrapper
- `webapp/ts_en.py`
  - EfficientNet secondary classifier
- `webapp/ts_maps.py`
  - shared map/provider helpers and geographic utilities
- `webapp/ts_gmaps.py`
  - Google Maps backend provider support
- `webapp/ts_azure_maps.py`
  - Azure Maps backend provider support
- `webapp/ts_geocoding.py`
  - forward and reverse geocoding
- `webapp/ts_geocache.py`
  - geocoding cache behavior
- `webapp/ts_validation.py`
  - request validation
  - polygon/bounds/search validation
  - file-upload validation
  - rate limiting
- `webapp/ts_errors.py`
  - structured application error types
- `webapp/ts_logging.py`
  - logging helpers and sensitive-data sanitization
- `webapp/ts_performance.py`
  - performance metrics capture
- `webapp/ts_events.py`
  - cancel/exit event coordination
- `webapp/ts_imgutil.py`
  - imagery and coordinate transforms
- `webapp/ts_zipcode.py`
  - ZIP code boundary support

### Frontend Components

- `webapp/templates/towerscout.html`
  - main application shell
  - setup wizard markup
  - settings modal
  - progress overlay
  - provider boot scripts
- `webapp/build.js`
  - concatenation-based frontend build
- `webapp/js/src/`
  - modular frontend sources
  - current source layout includes setup/settings, progress, provider switching, detection review, and map abstractions

### Supporting Project Areas

- `Model/`
  - notebooks and model training/evaluation artifacts
- `SyntheticData/`
  - synthetic-data generation and augmentation
- `TowerScoutSite/`
  - marketing/static site
- `.agent_work/`
  - task management
  - design and requirement artifacts
  - architecture/context/status documents

## Current Runtime and Data Flow

1. Startup loads environment/config state from `webapp/config/.env` when present, or migrates from legacy `webapp/.env`.
2. App determines whether it must run in setup-required mode based on available provider keys.
3. Setup Wizard and Settings interact with config API endpoints to validate keys, persist configuration, and refresh runtime settings.
4. User defines an area via address search, ZIP code, circle, or custom polygon.
5. Frontend can estimate tiles via `POST /api/detection/estimate`.
6. Frontend runs full detection via `POST /getobjects`.
7. Backend tiles the region, downloads imagery, runs YOLOv5, conditionally applies EfficientNet, deduplicates detections, reverse-geocodes results, and stores workflow state in the session.
8. Frontend polls `GET /api/detection/progress` for live progress detail and supports user cancellation.
9. Results are displayed on the map and in the review panel, then exported or restored as needed.

## Production-Critical Legacy Requirements

These expectations from the original guidance remain valid and should still be treated as high-priority preservation constraints unless the user explicitly asks to change them:

### Core Detection Workflow

- machine learning-based cooling tower detection with confidence scores
- multi-provider imagery support using Google Maps and Azure Maps
- confidence filtering and result toggling
- automatic address geocoding for detections

### Search and Navigation

- location search
- ZIP code search
- polygon search
- circular search
- tile estimation before long-running detection work
- map pan/zoom/drag behavior with provider switching

### Review and Editing

- interactive map overlays with clickable results
- right-panel review flow
- bidirectional highlight behavior between list and map
- false-positive deselection
- manual tower addition
- tile review and tower review modes

### Export and Investigation Workflow

- CSV export
- KML export
- dataset export/restore
- provenance between ML detections and manual detections
- support for outbreak investigation and registry workflows

## Current User-Facing Capabilities

### Setup and Configuration

- setup-required boot mode when no valid provider key is configured
- first-launch Setup Wizard
- API-key validation against provider endpoints
- default-provider selection
- performance summary display in setup/settings flows
- settings modal with masked previews, save path, debug toggle, and cache/session reset
- runtime reload of configuration after successful save

### Detection Workflow

- estimate-first workflow via dedicated estimate route
- full detection with progress overlay
- cancel support during active detection
- live progress phase titles and details
- provider-aware reverse geocoding
- duplicate suppression before geocoding

### Review and Data Management

- confidence filtering
- review mode toggles
- manual tower creation and saving
- dataset restore via `contents.txt`
- CSV/KML/YOLO/XML export behavior

### Search and Provider UX

- Google search via `PlaceAutocompleteElement`
- Azure search via service SDK
- custom Google polygon drawing instead of deprecated `DrawingManager`
- Azure native drawing tooling
- provider switching with shared app state

## Security Status and Validation Reality

### Security Work Already Completed

- API keys are no longer stored in `apikey.txt`
- environment/config-based key handling is implemented
- sensitive values are sanitized in logging
- settings/status responses mask keys

### Validation Already Implemented

The original document listed several of these as missing, but they are now implemented:

- polygon coordinate validation
- polygon geometry validation
- bounds validation
- provider validation
- engine validation
- search query sanitization
- dataset/image/model upload validation
- route-level rate limiting

### Current Provider Environment Variables

- `GOOGLE_API_KEY`
- `AZURE_MAPS_SUBSCRIPTION_KEY`
- `DEFAULT_MAP_PROVIDER`
- `FLASK_SECRET_KEY`

### Legacy Compatibility Note

`BING_API_KEY` still appears in the repo and backend provider-loading logic as a legacy compatibility surface. Do not treat Bing as the primary path forward, but do not delete or ignore the compatibility implications without checking current usage.

## Key Runtime Patterns

### Session Management

The app currently uses server-side filesystem sessions through `Flask-Session`. The original document's signed-cookie-only statement is no longer correct.

Important implications:

- session-backed workflow state remains central to detection, export, restore, and temp-file cleanup
- setup/settings also touch session state, though saved configuration is persisted to disk rather than only to session
- containerization must account for writable session storage

Common session values include:

- `results`
- `detections`
- `metadata`
- `tiles`
- `tmpdirname`
- `needs_setup`
- geocoding usage/limit state

### Temp and File Storage

- temporary session directories are created under `webapp/temp/session`
- uploads are written under `uploads/`
- config is persisted under `webapp/config/.env`

### Config Management

`ts_config.py` is now a major part of the app architecture and should be treated as such.

It handles:

- active config path selection
- migration from legacy `.env`
- best-effort locking for config writes
- env backup and rollback
- provider-key validation
- runtime reload after save

### Model Loading

#### YOLOv5

- engines are loaded lazily through `get_engine()`
- current CUDA path in `ts_yolov5.py` uses batch size `8`
- current semaphore count in `ts_yolov5.py` is `8`

#### EfficientNet

- eager initialization is still the default runtime behavior
- lazy initialization exists behind `TOWERSCOUT_LAZY_MODEL_INIT`
- debug-image dumping is gated by `TOWERSCOUT_SAVE_EN_DEBUG_IMAGES`

### Detection Progress

Detection progress is now a first-class runtime feature:

- in-memory tracker in `ts_progress.py`
- progress endpoint in Flask
- frontend polling and stale-terminal-state handling
- explicit cancel-request state

This is important enough to be included in any authoritative context document.

## Map Provider Architecture

### Current Provider Reality

- Google Maps and Azure Maps are the active providers that matter for current user-facing workflows.
- Provider availability is driven by configured keys and surfaced to the UI.
- Default provider ordering is influenced by `DEFAULT_MAP_PROVIDER`.

### Google Maps

Current important state:

- `SearchBox` has been replaced by `PlaceAutocompleteElement`
- Google script loading is dynamic
- custom drawing replaced dependency on deprecated `DrawingManager`
- `google.maps.Marker` deprecation is still active in current Google documentation; `AdvancedMarkerElement` remains the recommended replacement, but Google does not currently list legacy `Marker` as scheduled for discontinuation
- migration to `AdvancedMarkerElement` is still relevant future work, but it should be treated as an informed modernization item rather than an immediate break/fix requirement

### Azure Maps

Current important state:

- Azure uses the Azure Maps Web SDK plus service SDK
- drawing and search integrations are active
- Azure remains a first-class backend and frontend provider

## Frontend Architecture

### Build System

- `webapp/build.js` concatenates frontend source modules into `webapp/js/towerscout.js`
- the source build order currently covers 30 JavaScript modules
- generated output should be treated as build output, not hand-authored source

### Current Source Areas

#### Foundation

- `src/config.js`
- `src/store.js`

#### Managers

- `ProviderStateManager.js`
- `TimerManager.js`
- `EventListenerManager.js`
- `ErrorHandler.js`

#### Boundaries

- `CircleBoundary.js`
- `PolygonBoundary.js`
- `ZipcodeBoundary.js`

#### Providers

- `TSMap_base.js`
- `GoogleMap.js`
- `AzureMap.js`
- `providerInit.js`
- `providerSwitch.js`

#### Detection

- `PlaceRect.js`
- `Detection.js`
- `DetectionList.js`
- `DetectionReview.js`
- `Tile.js`

#### UI and Shared Helpers

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

### Frontend Behaviors That Should Be Preserved

- setup wizard auto-check on startup
- progress overlay and polling behavior
- stale response suppression for cancelled/superseded detection requests
- provider-switch behavior
- manual tower drawing UX
- layered app logging via `TowerScoutLogger`

## Route Surface Worth Knowing

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

### Geocoding and Detection Routes

- `POST /api/geocode/forward`
- `POST /api/geocode/reverse`
- `POST /api/detection/estimate`
- `GET /api/detection/progress`
- `POST /getobjects`
- `POST /getobjectscustom`

### Data Management Routes

- `POST /uploaddataset`
- image/model upload routes still exist and should be checked before changing upload behavior

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

### CI Reality

Current CI includes:

- Python 3.11 and 3.12
- `flake8`
- `black --check`
- `mypy` as non-blocking
- `bandit` as non-blocking
- unit tests
- integration tests as non-blocking
- placeholder Docker build check that tolerates a missing Dockerfile
- Trivy security scan

Do not describe Docker build validation as fully implemented CI coverage yet.

## Docker and Deployment Strategy

### Current Reality

Docker containerization remains planned work. There is no `Dockerfile` in the repo today.

### TASK-025 Guardrails

When Docker work begins, the current app architecture requires:

- writable filesystem-backed session storage
- stable `FLASK_SECRET_KEY`
- persistent writable config storage for `webapp/config/`
- awareness that setup/settings persist configuration to disk, not just in memory

Without those constraints, first-launch setup may fail or saved configuration may be lost when the container is replaced.

## File Structure Conventions

- `ts_*.py` backend module naming remains conventional in `webapp/`
- `model_params/` contains model weights and is excluded from git
- `uploads/` is temporary user-file storage
- `templates/` contains Jinja templates
- `.agent_work/` holds planning, documentation, decisions, and context

## Work Planning and Documentation Guidance

The original document carried substantial workflow guidance. Much of that remains useful if rephrased as current project preference rather than rigid agent protocol.

### Request Classification

#### Type A

- quick fixes
- small documentation changes
- low-risk config or validation adjustments
- usually no heavy design artifact overhead

#### Type B

- user-facing feature work
- UI/UX changes
- new endpoint or workflow additions
- should usually sync task/design context when the change is non-trivial

#### Type C

- architecture changes
- security-sensitive work
- major performance work
- deployment and infrastructure shifts
- should include explicit impact analysis and stronger documentation discipline

### Task Tracking Expectations

Current preferred project artifacts:

- `.agent_work/current-tasks.md` for active work
- `.agent_work/task-backlog.md` for future work
- `.agent_work/completed-tasks.md` for recent completions
- `.agent_work/requirements.md`
- `.agent_work/design.md`
- task-specific files under `.agent_work/tasks/` when work is substantial

### Workspace Context Layout

- `.agent_work/context/guides/`
- `.agent_work/context/analysis/`
- `.agent_work/context/status/`
- `.agent_work/decisions/`

## Project-Specific Guardrails

### ML and Detection Guardrails

- preserve detection behavior unless the user explicitly asks to change it
- be cautious in `ts_yolov5.py` and `ts_en.py`
- preserve export/restore semantics, especially manual-tower provenance
- preserve geographic accuracy and coordinate precision

### Setup and Deployment Guardrails

- do not describe setup/settings as future work
- do not ignore filesystem-session implications in deployment work
- do not treat config persistence as only a documentation concern; it is an active runtime requirement

### Legacy Feature Preservation

- outbreak investigation workflows remain the priority preservation surface
- registry/labeling workflows remain important
- provider-specific UX differences should be preserved unless intentionally redesigned

## Git Workflow and Change Hygiene

The original document contained useful Git guidance. The following remains a reasonable project preference:

### Branching

- use feature/fix/docs/refactor style branch names when preparing reviewable work

### Commits

- prefer clear conventional-commit-style messages
- keep a readable paper trail for architecture or workflow changes

### PR-Level Documentation Expectations

For substantial work, it is useful to preserve:

- executive summary
- impact assessment
- validation evidence
- note on ML/detection safety when relevant
- links to task or decision artifacts when architecture changes are involved

## Coding and Quality Guidelines

### Security First

- never introduce hardcoded secrets
- keep validation in place for user input and uploads
- preserve sanitized logging behavior

### Code Quality

- prefer explicit, testable code paths
- keep backend exceptions structured
- preserve current validation and rate-limiting surfaces
- avoid unnecessary complexity in legacy-critical workflows

### Performance

- respect current performance-sensitive paths in detection, provider overlays, and geocoding
- be careful with any work that affects under-100-tile investigation speed
- keep CPU-only deployment needs in mind for future work

## Work Completed Recently

The original guidance benefited from explicitly naming recent completed work. That remains useful for agent context.

### Completed or Landed in Recent Sprints

- API key migration to environment/config handling
- setup wizard and settings implementation
- config validation and persistence flow
- detection progress tracking and cancel lifecycle
- Google Maps API migration to modern search/drawing approach
- frontend modularization and build system
- manual tower workflow restoration and export provenance improvements
- console log gating and layered in-app logging
- large-dataset performance investigation and quick wins
- detection workflow stabilization with live browser validation

## Current Path Forward

### Sprint 05 Priority Sequence

1. verify runtime dependencies and separate true runtime requirements from drift
2. establish a current integration smoke-test baseline
3. implement Docker containerization with setup/config/session requirements in mind
4. continue CPU optimization and deployment-readiness work
5. revisit multi-provider fallback and broader reliability improvements

### Practical Agent Takeaway

If this file becomes the single project-context source, an agent should leave with the following understanding:

- the app is no longer missing setup/settings
- the repo is in a late pre-containerization state
- filesystem sessions and disk-backed config writes are real architectural constraints
- Google and Azure workflows are both important
- outbreak-investigation workflows are the highest-value legacy surface to preserve
- the next path forward is validation and deployment readiness, not foundational UI rebuilds

## References

- `.github/instructions/spec-driven-approach.instructions.md`
- `.agent_work/current-tasks.md`
- `.agent_work/task-backlog.md`
- `.agent_work/completed-tasks.md`
- `.agent_work/context/guides/COPILOT-INSTRUCTIONS-UPDATED-DRAFT.md`
- `AGENTS.md/architecture.md`
- `AGENTS.md/dev-workflow.md`
- `AGENTS.md/security.md`
