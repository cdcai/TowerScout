# TASK-053: Detection Workflow Stabilization and Live Browser Validation

**Status**: COMPLETED  
**Priority**: HIGH  
**Type**: C (Architecture / Workflow Stabilization)  
**Estimated Effort**: 12-20 hours  
**Created**: April 2, 2026  
**Last Updated**: April 6, 2026  
**Target Sprint**: Sprint 04 closeout / Sprint 05 prep

---

## Objective

Stabilize the core detection workflow from `Estimate tiles` and `Find towers` through backend processing, geocoding, duplicate suppression, and frontend map/right-panel rendering on both Google Maps and Azure Maps. This task adds live browser validation and runtime evidence capture before any additional progress-overlay or detection UX polish continues.

This is a correctness-and-regression-protection task, not a feature redesign task.

---

## Context

Static analysis in [DETECTION-WORKFLOW-REALITY-CHECK.md](../context/analysis/DETECTION-WORKFLOW-REALITY-CHECK.md) confirmed that the current workflow is carrying several high-value structural problems:

- `Find towers` always performs an estimate preflight before the actual detection request
- active cancel behavior is inconsistent (`POST /abort` in the modular frontend vs `GET /abort` in Flask)
- abort lifecycle state is coupled to the estimate path
- duplicate suppression is weak and can keep the wrong detection
- geocoding provider selection leaks through provider-blind cache reuse and manual-tower `provider: "auto"` behavior
- Google and Azure search/boundary flows are not standardized
- there are secondary provider-sync and dead-path issues that make startup and detection behavior harder to reason about

The user also reported real workflow symptoms that align with those findings:

- Google geocoding appearing to use Azure results
- duplicate detections for a single tower
- inconsistent rooftop addresses for towers on the same building

Because `TASK-047` Phase 4 would add more UX around this workflow, `TASK-047` was paused while this stabilization task was active.

---

## Current Status Snapshot

- Phase 0 complete: static code investigation captured in `DETECTION-WORKFLOW-REALITY-CHECK.md`
- Phase 1 tooling bootstrap is complete enough to run live browser validation: Puppeteer is pinned and installed as a dev-only dependency after dependency-tree verification
- A maintained smoke harness now exists at `tests/frontend/test_detection_workflow_smoke.js` with npm scripts wired in `package.json`
- A committed example AOI fixture exists at `tests/frontend/detection-workflow.example.json`; the real local AOI fixture remains intentionally untracked
- Baseline browser-run artifacts now exist under `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/` for both Azure and Google provider paths
- `DETECTION-WORKFLOW-LIVE-VALIDATION.md` now captures the first runtime findings and artifact references
- `webapp/ts_maps.py` has been patched in-repo to import `MapProviderError` and `NetworkError`, but that fix has not yet been verified against a clean live Flask instance
- Phase 2 through Phase 5 implementation is now in-repo but not yet runtime-signed-off:
  - `POST /api/detection/estimate` exists as the dedicated estimate contract
  - `POST /getobjects` now routes through a dedicated detection-run path with structured in-memory run tracking and unified cleanup
  - `/abort` now accepts both `POST` and `GET`, with `POST` used by the modular frontend
  - provider-aware geocoding cache behavior is implemented for reverse geocoding and detection-result address attachment
  - manual-tower reverse geocoding now sends the active backend provider instead of `"auto"`
  - score-ordered spatial dedupe now runs before geocoding instead of the older adjacent-coordinate suppression
  - `Find towers` now posts directly to detection, while `Estimate tiles` uses the new estimate endpoint and detection can run with an indeterminate overlay when no fresh estimate is cached
  - provider bootstrap/sync drift has been reduced so `fillProviders()` remains the active bootstrap path and `syncUIWithBackendProviders()` no longer re-fetches providers or touches phantom IDs
- Static/build validation for the implementation pass is complete:
  - `python -m py_compile` passed for the touched Python modules
  - `node --check` passed for the touched frontend files and the smoke harness
  - `node webapp/build.js` completed successfully after the frontend changes
- Live automation and manual validation are now complete:
  - an isolated helper server launcher now exists at `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py`
  - `localhost:5001` is now the authoritative validation target for Task-053 while stale `5000` listeners remain possible
  - earlier browser reruns intended for `5001` produced artifacts with `baseUrl: http://localhost:5000`; the smoke harness base-URL precedence bug has now been corrected
  - the first clean `5001` backend probe reproduced a `Permission denied` file-write failure while downloading Azure tile imagery
  - that blocker has now been corrected by replacing `tempfile.mkdtemp(dir=...)` session-dir creation with explicit `os.makedirs(...)` creation under `webapp/temp/session`
  - a direct multipart `curl.exe -F ... /getobjects` probe against `5001` now returns detections on current code, so Azure backend validation is green at the direct-request level
  - Azure browser smoke is now green on `5001` with artifact `20260403-142736-azure`
  - that passing artifact confirms:
    - `baseUrl: http://localhost:5001`
    - one `POST /api/detection/estimate`
    - one `POST /getobjects`
    - no hidden estimate preflight on `Find towers`
    - `14` rendered detections and `0` page errors
  - Google browser smoke is now green on `5001` with artifact `20260403-143013-google`
  - that passing artifact confirms:
    - `baseUrl: http://localhost:5001`
    - one `POST /api/detection/estimate`
    - one `POST /getobjects`
    - no hidden estimate preflight on `Find towers`
    - `8` rendered detections and `0` page errors
  - cancel validation is now green on `5001` with artifact `20260403-150354-azure-cancel`
  - that passing artifact confirms:
    - `POST /abort` returned `200`
    - the cancelled request stayed out of the final rendered state
    - the immediate follow-up run issued one `POST /getobjects`
    - no hidden estimate preflight was observed on `Find towers`
    - the follow-up run rendered `14` detections, `14` list entries, and `9` visible Azure map shapes
  - user manual QA on `5001` then surfaced three follow-up issues that were not covered by the earlier smoke harness:
    - Azure-only confidence slider visibility regression on initial load
    - fresh and restored detections falling back to `Address unavailable ...`
    - Azure restore inconsistencies for preserved selection state and stale manual-drawing geometry
  - those follow-up fixes are now in-repo:
    - the helper `5001` launcher now clears inherited proxy environment variables and forces UTF-8 stdio before importing `towerscout`
    - geocoding cache entries starting with `Address unavailable` are now treated as invalid, removed on read, and never written back to cache
    - Azure and Google provider views now force the confidence filter row to `display:flex` / `visibility:visible` when active
    - dataset export/restore selection persistence now keys off stable `(tile, id_in_tile)` identity instead of a flattened positional index
    - dataset restore now clears stale drawn shapes and boundaries before loading restored detections
  - April 6 manual QA then exposed two narrower follow-up issues:
    - Google address-group filtering could still hide inside-radius detections in `Find` mode when another detection at the same address was outside the radius
    - Azure tile review still hard-forced a center/zoom path that could show clipped tile coverage instead of the full tile bounds
  - those April 6 fixes are now in-repo:
    - grouped address visibility is now based on whether any detection in the address group is visible in the current mode
    - tile review now fits the active tile bounds on the current provider instead of forcing `zoom=19`
  - the final April 6 follow-up issue was then isolated to Google tile review:
    - `GoogleMap.fitBounds()` was constructing the bounds object incorrectly, which caused the `InvalidValueError` seen in the browser console
    - the global critical-error path also assumed `error.message` existed and threw a secondary `null.message` exception while reporting the first error
  - those final April 6 fixes are now in-repo:
    - `GoogleMap.fitBounds()` now passes a valid bounds-literal object to the Google Maps API
    - `TowerScoutErrorHandler.handleCriticalError()` now handles null-like errors without throwing a second exception
  - a final Google-only setup-wizard rerun then exposed one more startup regression:
    - after saving only a Google key in the Setup Wizard and reloading into the main app, startup could fail with `TowerScout initialization failed: Cannot read properties of undefined (reading 'Map')`
    - the root cause was the initial Google-provider startup path calling `initGoogleMap()` before `loadGoogleMaps()` had loaded the Google Maps SDK
  - that Google-only setup/startup fix is now in-repo:
    - the initial Google-provider branch in `fillProviders()` now loads the Google Maps SDK before requiring a Google map instance
    - `initGoogleMap()` now throws a precise SDK-not-loaded error instead of failing later with an undefined `.Map` dereference
  - one more April 6 follow-up then exposed a separate Google-only startup and key-validation gap:
    - startup still hit `Cannot read properties of undefined (reading 'getNorthEast')` because the initial provider switch path could ask Google Maps for bounds before `map.getBounds()` was populated
    - the currently configured Google key loads the Google Maps JavaScript path but Google Geocoding API calls return `REQUEST_DENIED`
  - those final April 6 Google-only fixes are now in-repo:
    - startup no longer wraps the main provider bootstrap in the redundant backend-sync promise chain
    - the initial provider switch now tolerates not-yet-ready Google bounds instead of failing startup
    - Google key validation now requires successful Geocoding API authorization, not just the existing map/static validation path
    - failed reverse-geocode results now return `success:false` with coordinate fallback instead of being surfaced as a successful `Address unavailable ...` address
  - the blank-config rerun, Google-only Setup Wizard validation, and broader manual regression QA are now complete:
    - Google-only setup/runtime passes with a geocoding-authorized key
    - manual towers worked as expected
    - export / restore worked as expected
    - Azure key entry through Settings worked as expected
    - a real browser `Find towers` click immediately after cancel worked as expected
- `TASK-047` was paused before Phase 4 while this task was active; its open Azure custom-search completion-message mismatch was absorbed into this task because it touched the same workflow boundary

---

## Active Validation Status

- `netstat -ano | findstr :5000` showed two different Python listeners bound to port `5000`
- This makes `5000`-based reruns unreliable because requests can still reach a stale Flask process after code changes are made
- To avoid that ambiguity, Task-053 validation now uses an isolated helper server on `localhost:5001` driven by `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py`
- The clean current-code Azure backend blocker on `5001` was the tile-download file-write path:
  - `ts_maps.py` surfaced the failure correctly as `Detection pipeline error: Failed to download satellite maps: All map tile downloads failed`
  - the underlying cause was `Permission denied` while writing the downloaded tile JPEG into the detection session temp directory
- That file-write blocker is now corrected by replacing `tempfile.mkdtemp(dir=...)` with explicit unique-directory creation under `webapp/temp/session`
- The smoke harness base-URL precedence bug is corrected so CLI/env target overrides win over the fixture default
- Google and Azure browser smoke are both green on `5001`
- Cancel validation is green on `5001` after:
  - request-local run tokens replaced session-keyed abort events in the active detection route
  - the modular frontend began aborting the in-flight detection fetch and ignoring stale cancelled responses
  - the smoke harness gained a click fallback only when a visible post-cancel `Find towers` click produces no output/progress delta within `1s` in headless mode
- Manual-QA follow-up fixes now landed after the first real-browser pass:
  - live reverse geocoding on `5001` now returns real addresses again after helper-launcher proxy cleanup plus negative-cache eviction
  - the Azure confidence slider is explicitly forced visible on active map providers, which fixes the missing-initial-load state seen in manual QA
  - dataset restore selection persistence now uses stable `(tile, id_in_tile)` matching and restore clears stale manual-drawing artifacts before rendering restored detections
- April 6 follow-up fixes now landed after the next manual pass:
  - grouped address visibility no longer lets an outside-radius detection hide an inside-radius detection at the same address in `Find` mode
  - tile-by-tile review now frames the selected tile bounds instead of forcing a hardcoded map zoom
- Task-053 validation is complete:
  1. smoke automation is green on Azure, Google, and cancel flows
  2. manual towers were retested successfully
  3. export / restore was retested successfully
  4. setup / settings was retested successfully
  5. real-browser click-after-cancel was retested successfully

---

## Execution Protocol

- Codex owns the isolated `5001` server for Task-053 validation
- The user-owned `5000` server is not the authoritative validation target while stale listeners remain possible
- Every command must be announced with:
  - expected duration
  - success signal
- Long-running work must be broken into visible checkpoints instead of opaque waits
- If a command exceeds its expected upper bound by about 30 seconds, switch to process/log/listener inspection instead of re-running blindly
- Browser smoke runs, direct backend probes, and artifact inspection should be sequenced as separate steps so runtime failures stay attributable
- Documentation must be updated as each major runtime milestone is reached so the current blocker and completed work remain visible in-repo

---

## Required Non-Regression Guarantees

### Manual Tower Workflows

- Manual towers SHALL keep their current identity and semantics:
  - `idInTile === -1`
  - `conf === 1.0`
- Manual towers SHALL continue to support add, save, geocode, highlight, clear, clear-all, and provider-switch preservation on both providers
- No `TASK-053` change may remove or redesign the current manual-tower workflow

### Export And Restore Workflows

- CSV, KML, and YOLO export formats SHALL remain unchanged
- Dataset ZIP structure and `contents.txt` contract SHALL remain unchanged
- Manual tower restore SHALL continue to preserve polygons, badges, addresses, and count integrity
- If a stabilization fix would require changing any export/restore contract, it SHALL be split into a follow-on task instead

### Setup Wizard And Settings

- Setup-required boot SHALL continue to display the Setup Wizard and block detection/map usage until configuration is complete
- Setup Wizard save flow SHALL continue to exit setup-required mode cleanly
- Settings SHALL continue to:
  - open without clearing session state
  - save keys and default provider through the existing config endpoints
  - preserve default-provider persistence after reload
  - clear cache through the existing reset-session path
  - display performance stats
- `TASK-053` SHALL NOT redesign the Setup Wizard or Settings screen

### Containerization And Runtime Contracts

- Browser automation SHALL remain a development/test dependency only
- No container runtime or production dependency SHALL be added for browser automation
- No change SHALL be made to `webapp/config/.env` persistence behavior, config paths, or Docker volume-mount strategy from `TASK-046`
- `TASK-053` may improve container-readiness by adding better validation targets, but SHALL NOT widen into Docker implementation work

### Dependency Security Gate

- No npm package installation for `TASK-053` SHALL proceed without a dependency-tree verification step first
- Puppeteer SHALL be pinned to an exact version before installation rather than added as an open-ended range
- A lockfile-only resolution check SHALL be used before the real install so the resolved dependency tree can be inspected safely
- `TASK-053` SHALL explicitly block installation if the resolved tree contains `axios@1.14.1` or `axios@0.30.4`
- Browser-automation package selection SHALL remain subject to supply-chain review if upstream dependency composition changes

### Model And Review Behavior

- `TASK-053` SHALL NOT change model weights, thresholds, classifier behavior, export semantics, or review-mode semantics
- If a proposed fix would materially alter model or review behavior, it SHALL be deferred into a separate task

---

## Scope For This Pass

**Included**:
- Live browser smoke harness for real-provider validation on Google and Azure
- Runtime evidence capture and analysis write-up
- Dedicated estimate contract and independent detection-run lifecycle
- Cancel lifecycle correction and cleanup
- Provider-aware geocoding behavior and cache isolation
- Duplicate suppression replacement before geocoding
- Provider propagation / startup synchronization fixes directly affecting the detection workflow
- Azure custom-search completion-message mismatch correction
- Explicit regression validation for manual towers, export/restore, setup wizard/settings, and containerization-adjacent behavior

**Explicitly Excluded**:
- Setup Wizard redesign or Settings UX redesign
- Export schema changes or dataset-restore format changes
- Dockerfile / container runtime implementation work
- Broad search UX redesign before boundary creation
- Model-threshold or model-weight changes
- Raw Flask terminal log streaming into the browser
- Broad visual polish work already scoped to `TASK-047`

---

## Key Decisions

1. Pause `TASK-047` before Phase 4 so workflow correctness is stabilized before more UX is added on top.
2. Use Puppeteer, not Playwright, because the repo already has a dormant Puppeteer path that can be revived with less churn.
3. Validate against real configured Google and Azure providers rather than mocked-only flows.
4. Keep browser automation as a dev/test-only dependency.
5. Protect downstream user workflows through explicit acceptance criteria rather than assuming they will survive the refactor.
6. If a fix requires breaking a non-regression guarantee, split it into a follow-on task instead of widening `TASK-053`.
7. Treat browser-test tooling as a dependency-security-reviewed addition, not a routine dev dependency.

---

## Requirements (EARS Notation)

**R-053-001**: WHEN the user clicks `Estimate tiles`, THE SYSTEM SHALL use a dedicated estimate path that does not create or rely on actual detection-run state.

**R-053-002**: WHEN the user clicks `Find towers`, THE SYSTEM SHALL start an independently cancellable detection run without requiring an estimate preflight request first.

**R-053-003**: WHEN a detection run starts, THE SYSTEM SHALL allocate structured run state keyed to the active session and SHALL clean that state up on success, cancellation, or error.

**R-053-004**: WHEN the user cancels an active detection run, THE SYSTEM SHALL honor `POST /abort` as the canonical cancel path and SHALL stop or wind down the active run cleanly.

**R-053-005**: WHEN geocoding detection results or manual towers, THE SYSTEM SHALL send an explicit provider preference instead of relying on `provider: "auto"`.

**R-053-006**: WHEN a geocoding cache hit is considered, THE SYSTEM SHALL NOT satisfy a provider-specific request with a result from a different provider silently.

**R-053-007**: WHEN multiple detections represent the same structure, THE SYSTEM SHALL deduplicate them before geocoding and SHALL retain the best-scoring representative.

**R-053-008**: WHEN a detection run completes, THE SYSTEM SHALL render the stabilized detection set consistently on the map and in the right-hand panel for both Google Maps and Azure Maps.

**R-053-009**: WHEN live browser validation runs, THE SYSTEM SHALL exercise end-to-end flows against real configured Google and Azure providers and SHALL capture runtime evidence for debugging and regression tracking.

**R-053-010**: WHEN manual tower workflows are re-tested during `TASK-053`, THE SYSTEM SHALL preserve add/save/geocode/highlight/clear/clear-all/provider-switch behavior on both providers.

**R-053-011**: WHEN export and restore workflows are re-tested during `TASK-053`, THE SYSTEM SHALL preserve existing CSV/KML/YOLO and `contents.txt` contracts without schema changes.

**R-053-012**: WHEN the application boots in setup-required mode, THE SYSTEM SHALL continue to show the Setup Wizard and block map/detection usage until configuration completes.

**R-053-013**: WHEN users open or save Settings during `TASK-053` validation, THE SYSTEM SHALL preserve session state and SHALL continue to save API keys and default provider through the existing configuration endpoints.

**R-053-014**: WHERE browser automation is added, THE SYSTEM SHALL keep it as a development/test-only dependency and SHALL NOT require it for runtime or container execution.

**R-053-015**: IF a proposed stabilization fix would break manual tower workflows, export/restore behavior, setup/settings behavior, or container/runtime contracts, THEN THE SYSTEM SHALL defer that change to a follow-on task instead of widening `TASK-053`.

**R-053-016**: WHEN browser automation dependencies are introduced, THE SYSTEM SHALL pin the selected package to an exact version and SHALL verify the resolved dependency tree before the real install proceeds.

**R-053-017**: IF the resolved dependency tree for browser automation contains `axios@1.14.1` or `axios@0.30.4`, THEN THE SYSTEM SHALL stop the installation and select a safe alternative version or tool path before continuing.

---

## Acceptance Criteria

### Detection Workflow Correctness

- [x] `Estimate tiles` uses a dedicated estimate contract
- [x] `Find towers` no longer depends on an estimate preflight to become cancellable
- [x] `POST /abort` works reliably for the active modular frontend path
- [x] Detection-run state allocates and cleans up correctly on success, cancel, and error
- [x] Duplicate detections are materially reduced without suppressing distinct nearby towers
- [x] Provider-aware geocoding behavior is enforced for both ML detections and manual towers
- [x] Google and Azure detection results appear correctly on the map and in the right-hand panel after stabilization

### Live Browser Validation

- [x] Browser automation dependency review is completed before installation
- [x] The pinned browser-automation version is resolved in a lockfile-only step before the real install
- [x] The resolved dependency tree is verified not to include `axios@1.14.1` or `axios@0.30.4`
- [x] Puppeteer harness is wired into `package.json` scripts and documented as a dev/test tool
- [x] Google UI + Google backend end-to-end run is exercised against real local provider configuration
- [x] Azure UI + Azure backend end-to-end run is exercised against real local provider configuration
- [x] Cancellation is exercised in the browser and leaves the app in a clean state
- [x] Runtime evidence is captured in `DETECTION-WORKFLOW-LIVE-VALIDATION.md`

### Manual Tower Non-Regression

- [x] Manual tower add/save still works on Google Maps
- [x] Manual tower add/save still works on Azure Maps
- [x] Manual tower reverse geocoding still populates addresses
- [x] Manual tower highlight/list interaction still works
- [x] Manual tower `Clear` and `Clear all` still work
- [x] Provider switching still preserves saved manual towers

### Export / Restore Non-Regression

- [x] CSV export still preserves manual vs ML distinction
- [x] KML export still includes selected manual towers
- [x] YOLO/dataset export still writes manual towers correctly
- [x] Dataset restore still restores manual towers, badges, polygons, and addresses
- [x] No schema changes are introduced to `contents.txt`

### Setup / Settings / Container Non-Regression

- [x] Setup-required mode still displays the Setup Wizard and blocks detection features
- [x] Setup Wizard save still exits setup-required mode cleanly
- [x] Settings still opens and saves without clearing session state
- [x] Saved default provider still appears correctly after reload
- [x] Settings clear-cache and performance sections still function
- [x] Browser automation remains a dev/test-only dependency and does not become a runtime/container requirement

---

## Dependencies

- [DETECTION-WORKFLOW-REALITY-CHECK.md](../context/analysis/DETECTION-WORKFLOW-REALITY-CHECK.md)
- [TASK-046-setup-wizard-settings-screen.md](./TASK-046-setup-wizard-settings-screen.md)
- Completed manual tower restoration work from `TASK-033`
- Completed export restoration work from `TASK-036`
- Active sprint tracking in [current-tasks.md](../current-tasks.md)

---

## Files Likely To Change

- `package.json`
- `tests/frontend/test_detection_workflow_smoke.js`
- `webapp/js/src/ui/search.js`
- `webapp/js/src/providers/GoogleMap.js`
- `webapp/js/src/providers/AzureMap.js`
- `webapp/js/src/utils/apiHelpers.js`
- `webapp/js/src/towerscout.js`
- `webapp/towerscout.py`
- `webapp/ts_geocoding.py`
- `webapp/ts_geocache.py`
- `webapp/ts_maps.py`
- `.agent_work/context/analysis/DETECTION-WORKFLOW-LIVE-VALIDATION.md`

---

## Implementation Plan

### Phase 0: Static Analysis Baseline (Complete)

- Use `DETECTION-WORKFLOW-REALITY-CHECK.md` as the baseline inventory of confirmed issues and likely root causes
- Treat that document as the pre-runtime evidence source of truth for this task

### Phase 1: Live Browser Harness And Evidence Capture

- Resolve Puppeteer as a pinned dev dependency in a lockfile-only step first and inspect the resolved tree before the real install
- Block the install if the resolved tree contains `axios@1.14.1` or `axios@0.30.4`
- Add Puppeteer as a dev dependency and wire stable npm scripts for headless and headed runs only after the dependency review passes
- Replace the dormant Stage 0 mutation script with a maintained detection-workflow smoke harness
- Keep the harness pointed at a manually started local Flask server (`http://localhost:5000`)
- Capture console errors, key network calls, screenshots on failure, and summary artifacts
- Publish the baseline live findings in `DETECTION-WORKFLOW-LIVE-VALIDATION.md`

### Phase 2: Estimate / Detect / Cancel Lifecycle Stabilization

- Add a dedicated estimate endpoint/contract
- Remove the hidden estimate-before-detect dependency from `Find towers`
- Standardize `POST /abort` as the canonical cancel path while keeping `GET /abort` as a temporary compatibility alias
- Allocate and clean up detection-run state independently of estimate behavior

### Phase 3: Geocoding Provider Consistency

- Make manual tower reverse geocoding send an explicit provider preference
- Make geocoding cache behavior provider-aware
- Prevent provider-blind cache reuse from leaking Azure results into Google-preferred requests and vice versa
- Preserve user-visible address behavior where possible without changing export or restore contracts

### Phase 4: Duplicate Suppression And Result Integrity

- Replace the existing adjacent `x1/y1` dedupe with score-ordered geospatial dedupe
- Deduplicate before geocoding
- Keep the best representative when duplicates merge
- Confirm same-structure duplicates are reduced without suppressing truly distinct nearby towers

### Phase 5: Provider Drift And Workflow Boundary Cleanup

- Correct provider propagation drift in active startup/detection paths
- Fix the Azure custom-search completion-message mismatch
- Correct any provider-sync issues that affect detection provider selection, but do not redesign Setup Wizard or Settings behavior

### Phase 6: Regression Validation And Closeout

- Re-run Google and Azure live browser flows after the fixes
- Re-run manual tower and export/restore regression flows explicitly
- Re-run setup-required / Settings default-provider sanity checks
- Document residual issues and split any non-trivial remaining work into follow-on tasks instead of widening scope

---

## Performance Guardrails

- Do not write live detection state into Flask cookie-backed session storage
- Do not add browser polling tighter than the stabilized workflow needs
- Do not introduce browser automation or Chromium as a runtime dependency
- Keep browser smoke coverage lightweight enough to remain useful before Sprint 05 containerization work

---

## Risks And Watchpoints

- Manual tower behavior is adjacent to the geocoding and provider fixes, so it must be treated as a first-class regression area
- Export/restore workflows depend on stable manual tower semantics; schema or contract drift is out of bounds
- Setup Wizard and Settings share provider/default-provider plumbing, so provider-sync fixes must be validated against those flows
- Real-provider browser tests may expose provider quota, SSL, or environment issues that are not code regressions; the harness and documentation should separate environment failures from application failures
- `TASK-053` can improve container-readiness, but it should not turn into `TASK-025`, `TASK-051`, or `TASK-052`
- Browser-test dependencies can change upstream independently of this repo, so lockfile review must be repeated at install time rather than assumed from prior checks

---

## Implementation Log

### TYPE C - TASK-053 DOCUMENTATION AND SEQUENCING LOCK - 2026-04-02
**Objective**: Create a decision-complete stabilization task that pauses `TASK-047` before its detection-progress overlay work and makes downstream non-regression guarantees explicit.
**Context**: Static analysis confirmed multiple structural issues in the detection workflow, and the user requested that downstream manual tower, export/restore, setup/settings, and containerization behavior be protected explicitly rather than implicitly.
**Decision**: Create `TASK-053` as the active workflow-stabilization task, keep browser automation dev-only via Puppeteer, require real-provider validation on both Google and Azure, and block any fix that would require breaking downstream contracts.
**Execution**: Created this task document, updated `current-tasks.md` to make `TASK-053` active and `TASK-047` paused, and recorded the regression guarantees for manual towers, export/restore, setup/settings, and containerization.
**Output**: The repo now has a dedicated `TASK-053` execution document and sprint tracking aligned to the new sequencing decision.
**Validation**: Documentation review only; no code or runtime behavior changed in this step.
**Next**: Implement the live browser harness, capture baseline runtime evidence, and then work through the bounded stabilization phases.

### TYPE C - TASK-053 DEPENDENCY SECURITY GATE ADDED - 2026-04-02
**Objective**: Add an explicit supply-chain verification gate before introducing Puppeteer or any other browser-automation dependency.
**Context**: The user flagged the April 1, 2026 Microsoft advisory for the compromised npm releases `axios@1.14.1` and `axios@0.30.4` and requested confirmation that `TASK-053` will not introduce insecure packages.
**Decision**: Require pinned-version resolution, lockfile-only inspection, and a hard stop if the resolved tree includes either compromised Axios version before any real install occurs.
**Execution**: Updated the task requirements, acceptance criteria, Phase 1 plan, and risk notes to make dependency-tree verification a mandatory prerequisite for browser automation setup.
**Output**: `TASK-053` now includes a documented npm supply-chain gate for browser-test tooling.
**Validation**: Current repo and global npm trees were checked separately and do not contain `axios@1.14.1`, `axios@0.30.4`, or an installed Puppeteer package at this time.
**Next**: Start Phase 1 by selecting the exact Puppeteer version, generating a lockfile-only resolution, and verifying the resolved tree before any install proceeds.

### TYPE C - TASK-053 PHASE 1 TOOLING BOOTSTRAP - 2026-04-02
**Objective**: Complete the dependency-reviewed browser-tooling bootstrap and scaffold a maintained live-workflow smoke harness.
**Context**: `TASK-053` Phase 1 required a pinned browser-automation dependency, npm script wiring, an untracked local AOI fixture path, and a maintained replacement for the dormant Stage 0 Puppeteer script before live runtime evidence could be collected.
**Decision**: Pin `puppeteer` to `24.19.0`, install it without bundled browser download, target a locally installed browser executable instead, and scaffold the smoke harness around a local AOI fixture plus artifact capture under `.agent_work/context/analysis/`.
**Execution**: Resolved the npm tree in lockfile-only mode, verified the resolved tree did not include Axios or the blocked `axios@1.14.1` / `axios@0.30.4` releases, installed `puppeteer@24.19.0` as a dev-only dependency using the local Edge browser path, added browser smoke scripts to `package.json`, ignored `tests/frontend/detection-workflow.local.json`, added `tests/frontend/detection-workflow.example.json`, and created `tests/frontend/test_detection_workflow_smoke.js`.
**Output**: The workspace now contains the Phase 1 harness scaffold and npm entrypoints for provider-specific detection runs.
**Validation**: `node --check tests/frontend/test_detection_workflow_smoke.js`, `node tests/frontend/test_detection_workflow_smoke.js --help`, and `npm.cmd run test:browser:detect -- --help` all passed. The local Flask dev server was then started successfully and responded on `http://localhost:5000`.
**Next**: Create or confirm the local untracked AOI fixture, run the first live smoke pass against the running Flask app, capture the first browser-run artifact, and then document the baseline findings in `DETECTION-WORKFLOW-LIVE-VALIDATION.md`.

### TYPE C - TASK-053 LIVE RUNTIME BASELINE AND BLOCKER ISOLATION - 2026-04-02
**Objective**: Capture the first real Google/Azure runtime evidence, preserve it in-repo, and clear the first obvious backend blocker without widening into speculative fixes.
**Context**: Static analysis had already identified structural issues, but `TASK-053` needed live browser evidence to confirm the actual order of operations, runtime failures, and provider differences before deeper stabilization work continued.
**Decision**: Record the baseline artifacts first, patch only the confirmed `ts_maps.py` missing-import defect in the codebase, extend the smoke harness to capture failed `/getobjects` response bodies, and stop once the live server state became ambiguous rather than continuing on unreliable evidence.
**Execution**: Created the local AOI fixture, ran Azure baseline `20260402-151701-azure` and confirmed `#estimate` could be hidden while `#find` remained available, ran Azure `20260402-152342-azure` and confirmed the hidden estimate preflight plus backend `500`, ran Google `20260402-152835-google` and confirmed a client-side runtime failure before the detection request, created `.agent_work/context/analysis/DETECTION-WORKFLOW-LIVE-VALIDATION.md`, patched `webapp/ts_maps.py` to import `MapProviderError` and `NetworkError`, updated `tests/frontend/test_detection_workflow_smoke.js` to record failed `/getobjects` response-body snippets, then reran Azure as `20260402-153806-azure`, `20260402-154432-azure`, and `20260402-155117-azure`.
**Output**: The repo now has a reproducible runtime baseline showing: hidden `Estimate tiles` visibility problems, duplicate estimate preflight behavior on `Find towers`, an Azure backend `500`, a Google frontend/runtime failure before detection POST, and a generic structured `InternalServerError` body captured from the failed Azure `/getobjects` response.
**Validation**: `python -m py_compile webapp\\ts_maps.py`, `node --check tests/frontend/test_detection_workflow_smoke.js`, real browser runs against `http://localhost:5000`, artifact inspection in `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/`, and `netstat -ano | findstr :5000`.
**Blocker**: `netstat` showed two separate Python listeners on port `5000` (PIDs `15784` and `30392`), so the active browser reruns can still reach a stale Flask instance and stale traceback path.
**Next**: Start the next session by stopping all Flask listeners, bringing up one clean instance on `5000`, verifying a single listener, rerunning Azure first to validate the `ts_maps.py` import fix and expose the true underlying backend failure, and only then continue to Google runtime diagnosis and workflow fixes.

### TYPE C - TASK-053 IMPLEMENTATION PASS LANDED, LIVE RERUNS PENDING - 2026-04-03
**Objective**: Land the bounded workflow-stabilization changes identified during the April 2 reality check and runtime baseline before resuming live browser reruns.
**Context**: The task already had enough static and live evidence to implement the dedicated estimate path, detection-run lifecycle cleanup, provider-aware geocoding/cache behavior, frontend request separation, and stronger pre-geocode dedupe without waiting for more speculative debugging.
**Decision**: Implement the planned workflow split and consistency fixes in-repo first, then return to Azure-first live reruns against the local Flask server to expose the next real blocker from the cleaned-up path.
**Execution**: Added `POST /api/detection/estimate`, routed `POST /getobjects` through a dedicated `_run_detection_request()` path with structured in-memory run tracking and unified cleanup, let `/abort` accept both `POST` and `GET`, made the geocoding cache provider-aware, propagated the active backend provider through reverse geocoding for both manual towers and detection-result address attachment, replaced adjacent-coordinate dedupe with score-ordered spatial dedupe before geocoding, updated the modular frontend so `Estimate tiles` and `Find towers` use separate request paths, enabled indeterminate progress when no cached estimate exists, reduced provider bootstrap drift in the frontend sync layer, updated the smoke harness to watch `/api/detection/estimate`, and rebuilt the frontend bundle.
**Output**: The core Task-053 implementation plan now exists in the repo and passes syntax/build validation, but none of the new runtime behavior is considered signed off until the Azure and Google live smoke flows pass on the local Flask app.
**Validation**: `python -m py_compile webapp\\towerscout.py webapp\\ts_geocache.py webapp\\ts_maps.py`; `node --check` on touched frontend modules plus `tests/frontend/test_detection_workflow_smoke.js`; `node webapp/build.js`; `node tests/frontend/test_debug_logging_contract.js`; `node tests/frontend/test_global_contract.js`.
**Next**: Run the Azure smoke harness against the currently responding local Flask server, fix the first real Azure failure from that run, rerun Azure to green, then rerun Google and document any remaining frontend/runtime issue before handing manual regression QA back to the user.

### TYPE C - TASK-053 ISOLATED 5001 VALIDATION AND FILE-WRITE BLOCKER - 2026-04-03
**Objective**: Remove stale `5000` listener ambiguity from Task-053 validation and isolate the first real Azure backend blocker from current workspace code.
**Context**: `5000` was confirmed to have multiple Python listeners, and a browser rerun intended for `5001` still produced an artifact with `baseUrl: http://localhost:5000`, so runtime evidence had to be separated into stale-target evidence and clean isolated-target evidence.
**Decision**: Introduce and use a helper launcher at `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py`, treat `localhost:5001` as the authoritative validation target, and verify the backend path directly with a multipart probe before spending more time on browser automation.
**Execution**: Added the isolated helper launcher for `5001`, started the helper server from current workspace code, confirmed the listener and startup log, inspected the suspicious Azure browser artifact `20260403-133540-azure`, then sent a direct multipart `curl.exe -F ... /getobjects` request to `http://localhost:5001/getobjects` using the same request shape as the browser. That probe reached the updated detection route, began YOLO model loading normally, initialized Azure Maps, and then failed during tile download with `Permission denied` while writing the downloaded JPEG into the session temp directory. As a bounded mitigation, session tempdirs were rerouted in-repo to `webapp/temp/session` using `SESSION_TMP_ROOT` and `_make_session_tmpdir()`.
**Output**: Task-053 now has a clean current-code backend failure isolated on `5001`: the remaining Azure blocker is the tile-download file-write path, not stale exception handling or stale-process ambiguity. The repo also now contains an isolated validation launcher plus a repo-local session-tempdir mitigation awaiting rerun confirmation.
**Validation**: `netstat -ano | findstr :5001`; startup log inspection for `task053-server-5001.log`; direct `curl.exe -F` multipart probe against `http://localhost:5001/getobjects`; backend traceback/log inspection showing `Detection pipeline error: Failed to download satellite maps: All map tile downloads failed` with an underlying `Permission denied` write failure.
**Next**: Restart the helper `5001` server so the repo-local session-tempdir mitigation is active, rerun the direct Azure multipart probe, and only if that clears the file-write failure, rerun the Azure browser smoke while explicitly verifying `summary.baseUrl` is `http://localhost:5001`.

### TYPE C - TASK-053 MKDTEMP ROOT-CAUSE FIX VERIFIED ON DIRECT AZURE PROBE - 2026-04-03
**Objective**: Verify whether the repo-local session-tempdir mitigation actually clears the clean isolated Azure backend failure before moving back to browser automation.
**Context**: The first isolated `5001` probe proved that `tempfile.mkdtemp(dir=...)` was creating session child directories that were immediately unwritable on this Windows setup. The same failure reproduced outside Flask with a standalone Python write test, while a normal `os.makedirs(...)` child directory in the same parent remained writable.
**Decision**: Replace `tempfile.mkdtemp(dir=SESSION_TMP_ROOT)` with explicit unique-directory creation under `webapp/temp/session`, restart only the helper `5001` server, and verify the fix first with a direct multipart Azure request.
**Execution**: Patched `_make_session_tmpdir()` to create unique session directories with `os.makedirs(...)` instead of `tempfile.mkdtemp(...)`, confirmed the patched file compiles, restarted the helper `5001` server without output-redirection plumbing, and reran the direct `curl.exe -F ... http://localhost:5001/getobjects` Azure probe.
**Output**: The direct Azure probe now returns detections instead of a tile-download `500`, which validates the tempdir root-cause fix at the backend-request level. The next remaining gate is end-to-end browser validation against `5001`.
**Validation**: `python -m py_compile webapp\\towerscout.py`; helper-server restart and `http://localhost:5001` health check; direct multipart probe returning a JSON detection payload from `POST /getobjects` instead of `Detection pipeline error: Failed to download satellite maps: All map tile downloads failed`.
**Next**: Run Azure browser smoke against `5001`, verify the artifact records `baseUrl: http://localhost:5001`, confirm the request sequence and detection count, then proceed to Google.

### TYPE C - TASK-053 AZURE BROWSER SMOKE GREEN ON ISOLATED 5001 TARGET - 2026-04-03
**Objective**: Prove the end-to-end Azure browser flow works against the isolated helper server rather than the stale `5000` environment.
**Context**: Earlier Azure browser reruns intended for `5001` still recorded `baseUrl: http://localhost:5000` because the smoke harness let the fixture-level `baseUrl` override the CLI/env target. That had to be corrected before the browser artifacts could be trusted again.
**Decision**: Fix the smoke harness so CLI/env target overrides win over the fixture default, then rerun Azure and treat the new artifact as authoritative only if it records `baseUrl: http://localhost:5001`.
**Execution**: Updated `tests/frontend/test_detection_workflow_smoke.js` so `options.baseUrl` takes precedence over `fixture.baseUrl`, reran the Azure smoke with both `TOWERSCOUT_BASE_URL=http://localhost:5001` and `--base-url=http://localhost:5001`, and inspected the resulting artifact.
**Output**: Azure browser smoke is now green against the isolated helper server. Artifact `20260403-142736-azure` records `baseUrl: http://localhost:5001`, `estimateCalls: 1`, `getobjectsCalls: 1`, `hiddenEstimatePreflightObserved: false`, `detectionCount: 14`, and `pageErrors: 0`.
**Validation**: `node --check tests/frontend/test_detection_workflow_smoke.js`; browser smoke artifact at `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-142736-azure/summary.json`.
**Next**: Run Google browser smoke against `5001`, then validate cancellation, then update the remaining task artifacts before handing browser-only manual QA back to the user.

### TYPE C - TASK-053 GOOGLE BROWSER SMOKE GREEN ON ISOLATED 5001 TARGET - 2026-04-03
**Objective**: Prove the end-to-end Google browser flow works against the isolated helper server and matches the corrected estimate/detect request sequencing.
**Context**: Azure was already green on `5001`, but provider parity still required a clean Google browser pass against current workspace code.
**Decision**: Reuse the corrected smoke harness target-selection logic, rerun Google against `http://localhost:5001`, and trust the artifact only if it records the isolated target plus the expected estimate/detect request sequence.
**Execution**: Ran the Google smoke harness against `5001` using the existing local AOI fixture and inspected the resulting summary artifact.
**Output**: Google browser smoke is now green against the isolated helper server. Artifact `20260403-143013-google` records `baseUrl: http://localhost:5001`, `estimateCalls: 1`, `getobjectsCalls: 1`, `hiddenEstimatePreflightObserved: false`, `detectionCount: 8`, and `pageErrors: 0`.
**Validation**: Browser smoke artifact at `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-143013-google/summary.json`.
**Next**: Validate cancellation against `5001`, then hand the remaining manual QA back to the user.

### TYPE C - TASK-053 CANCEL VALIDATION GREEN ON ISOLATED 5001 TARGET - 2026-04-03
**Objective**: Prove cancellation leaves the modular frontend and backend in a clean state so a second detection can start immediately on the isolated helper server.
**Context**: Earlier cancel reruns exposed three separate issues: a shared asyncio event loop in the active route, session-keyed abort events that could be overwritten by overlapping runs from the same browser session, and cancelled client responses that could still clear the rendered detections. Headless reruns also showed that the visible post-cancel `Find towers` click could occasionally be swallowed without changing app state.
**Decision**: Move the active detection route to request-local run tokens and event loops, abort and ignore stale in-flight `/getobjects` fetches in the modular frontend, and add a harness-side click fallback only when a visible control click produces no output/progress delta within `1s`.
**Execution**: Patched `webapp/towerscout.py` so the active detection route registers and signals per-run tokens, patched `webapp/js/src/ui/search.js` to abort the active detection fetch and ignore stale cancelled responses, rebuilt the frontend bundle, then reran the Azure cancel smoke against `5001`.
**Output**: Cancel validation is now green against the isolated helper server. Artifact `20260403-150354-azure-cancel` records `baseUrl: http://localhost:5001`, `abortStatus: 200`, `estimateCalls: 1`, `getobjectsCalls: 1`, `hiddenEstimatePreflightObserved: false`, `detectionCount: 14`, `listCount: 14`, and `mapVisibleCount: 9`. The follow-up detection used `triggerMode: click-fallback`, which documents the headless-only swallowed-click recovery in the harness rather than a backend/runtime blocker.
**Validation**: `python -m py_compile webapp\\towerscout.py`; `node --check webapp\\js\\src\\ui\\search.js`; `node --check tests/frontend/test_detection_workflow_smoke.js`; `node webapp\\build.js`; browser smoke artifact at `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-150354-azure-cancel/summary.json`.
**Next**: Hand the remaining browser-only manual QA back to the user, with special attention to real-browser click-after-cancel behavior.

### TYPE C - TASK-053 MANUAL-QA FOLLOW-UP FIXES LANDED ON ISOLATED 5001 TARGET - 2026-04-03
**Objective**: Resolve the first set of real-browser manual-QA regressions that appeared after the Azure/Google/cancel smoke runs were already green on `5001`.
**Context**: User manual QA on `http://localhost:5001` exposed three issues that the smoke harness did not cover: Azure-only confidence-slider invisibility on initial load, fresh/restored detections falling back to `Address unavailable ...`, and Azure restore inconsistencies around preserved selection state plus stale manual-drawing geometry.
**Decision**: Keep the isolated `5001` workflow, fix the helper-server environment first, then patch the geocoding cache, startup filter visibility, and restore identity/cleanup behavior in small bounded changes while preserving the export schema and `contents.txt` contract.
**Execution**: Patched `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py` to clear inherited proxy variables and force UTF-8 stdio before importing `towerscout`, patched `webapp/ts_geocache.py` so cached fallback strings beginning with `Address unavailable` are evicted on read and never cached on write, updated `webapp/js/src/towerscout.js` so active Google/Azure views force `#ffilter` to `display:flex` / `visibility:visible` and dataset restore clears stale drawn shapes and boundaries before loading restored detections, updated `webapp/towerscout.py` so dataset selection persistence uses stable `(tile, id_in_tile)` identity instead of flattened detection order, rebuilt the frontend bundle, and restarted the helper server on `5001`.
**Output**: The isolated helper server now returns real reverse-geocode addresses again, the Azure confidence slider is visible on initial page load, and dataset selection persistence no longer depends on fragile positional indexing. Restore also starts from a clean visual state instead of mixing restored detections with leftover session drawings.
**Validation**: `python -m py_compile webapp\\towerscout.py webapp\\ts_geocache.py .agent_work\\scripts\\task053_run_server_5001.py`; `node --check webapp\\js\\src\\towerscout.js`; `node webapp\\build.js`; live `Invoke-RestMethod` probe to `POST http://localhost:5001/api/geocode/reverse` returning `255 Murray Street, New York, NY 10282`; local Edge DOM probe on `http://localhost:5001` returning `provider: azure`, `display: flex`, `visibility: visible` for `#ffilter`; targeted backend identity test showing non-sequential tile IDs still preserve the intended selected detection via `(tile, id_in_tile)` matching.
**Next**: Have the user rerun the manual towers and export/restore checks on `5001`, then close Task-053 once that manual pass and the earlier setup/settings / real-browser cancel checks are confirmed.

### TYPE C - TASK-053 APRIL 6 GOOGLE FILTERING AND AZURE TILE-REVIEW FIXES - 2026-04-06
**Objective**: Resolve the two remaining regressions found in the next manual QA pass on `http://localhost:5001`: Google `Find`-mode list filtering and Azure tile-review framing.
**Context**: The April 3 follow-up fixes restored geocoding, slider visibility, and restore integrity, but the next user rerun still found that some Google detections inside the search radius disappeared from the list in `Find` mode, and Azure tile-by-tile review could show clipped/over-zoomed imagery after a detection run.
**Decision**: Keep both fixes narrow and local to the affected UI paths: correct grouped-address visibility in `DetectionList.adjustConfidence()` without changing detection scoring semantics, and change tile review to fit the selected tile bounds on the active provider instead of forcing a hardcoded center/zoom path.
**Execution**: Patched `webapp/js/src/detection/DetectionList.js` so address-group visibility is aggregated across the whole group before any header is shown or hidden, patched `webapp/js/src/detection/Tile.js` so tile review uses provider-aware `fitBounds(...)` when available and falls back to the legacy center/zoom path only if necessary, then rebuilt the frontend bundle.
**Output**: Google `Find` mode no longer lets an outside-radius detection hide an inside-radius detection at the same address, and Azure tile review now frames the full tile bounds instead of drifting into a clipped zoom state.
**Validation**: `node --check webapp\\js\\src\\detection\\DetectionList.js`; `node --check webapp\\js\\src\\detection\\Tile.js`; `node webapp\\build.js`; local Edge validation on `http://localhost:5001` showing grouped-address visibility calls remain `true` for the shared address when one child detection is inside, and a mocked tile-review call now drives `fitBounds(1, 2, 3, 4)` instead of the old hardcoded zoom path.
**Next**: Refresh the browser on `http://localhost:5001` and rerun the Azure tile review plus the Google `Find`/restore checks to confirm the remaining user-visible regressions are closed.

### TYPE C - TASK-053 FINAL GOOGLE TILE-REVIEW CONSOLE ERROR FIX - 2026-04-06
**Objective**: Eliminate the last live browser console errors still affecting Google tile-by-tile review on `http://localhost:5001`.
**Context**: After the grouped-address and tile-framing fixes landed, user QA confirmed Azure tile review and Google `Find` mode were working again, but Google tile review still threw `InvalidValueError: not a LatLngBounds or LatLngBoundsLiteral: not an Object`, followed by a secondary `Cannot read properties of null (reading 'message')` from the global critical-error handler.
**Decision**: Fix the real Google bounds-construction bug first, then harden the critical-error handler so future null-like runtime errors do not cascade into a second console failure.
**Execution**: Patched `webapp/js/src/providers/GoogleMap.js` so `fitBounds()` now passes a plain bounds-literal object to `this.map.fitBounds(...)` instead of calling `google.maps.LatLngBounds(...)` incorrectly, patched `webapp/js/src/managers/ErrorHandler.js` so `handleCriticalError()` safely derives an error message when `error` is null-like, then rebuilt the frontend bundle.
**Output**: Google tile review no longer feeds an invalid bounds value into the Maps API, and the error-reporting path no longer throws a secondary `null.message` exception when handling an unexpected runtime error.
**Validation**: `node --check webapp\\js\\src\\providers\\GoogleMap.js`; `node --check webapp\\js\\src\\managers\\ErrorHandler.js`; `node webapp\\build.js`; local Edge validation on `http://localhost:5001` showing `GoogleMap.fitBounds()` now emits `{north: 2, south: 4, east: 3, west: 1}` and `TowerScoutErrorHandler.handleCriticalError(null, ...)` now reports `Critical error: Unknown error occurred` without any page-level exceptions.
**Next**: Refresh `http://localhost:5001` and rerun Google tile-by-tile review. If that is clean, Task-053 should be down to the remaining user-owned signoff checks rather than active code regressions.

### TYPE C - TASK-053 GOOGLE-ONLY SETUP-WIZARD STARTUP FIX - 2026-04-06
**Objective**: Eliminate the remaining startup failure exposed when configuration is completed through the Setup Wizard with only a Google key configured.
**Context**: After the tile-review console errors were fixed, a setup-required rerun with only a Google provider configured still failed after the wizard completed and reloaded the main app. The browser reported `TowerScout initialization failed: Cannot read properties of undefined (reading 'Map')`, while the console also logged the expected Azure-missing warning because no Azure key was configured.
**Decision**: Keep the fix local to the initial-provider startup path rather than widening the wizard flow: make the Google default-provider branch use the same SDK-loading path as provider switching, and harden `initGoogleMap()` so future callers fail with a precise message if they skip the loader.
**Execution**: Patched `webapp/js/src/towerscout.js` so the initial Google-provider branch in `fillProviders()` now calls `loadGoogleMaps()` before requiring a Google map instance and only falls back to direct `initGoogleMap()` if the SDK is already present but the map instance is still missing, patched `webapp/js/src/providers/providerInit.js` so `initGoogleMap()` explicitly checks for `google.maps.Map` before constructing `GoogleMap`, then rebuilt the frontend bundle.
**Output**: The startup path that follows a Google-only Setup Wizard save/reload now uses the intended Google SDK loader instead of dereferencing an undefined Maps SDK object during initial provider setup.
**Validation**: `node --check webapp\\js\\src\\towerscout.js`; `node --check webapp\\js\\src\\providers\\providerInit.js`; `node webapp\\build.js`.
**Next**: Hard-refresh `http://localhost:5001`, rerun the Google-only setup-wizard flow, and confirm the main app loads without the previous `reading 'Map'` initialization error before closing the remaining setup/settings gate.

### TYPE C - TASK-053 GOOGLE-ONLY STARTUP READINESS AND GEOCODING AUTHORIZATION FIXES - 2026-04-06
**Objective**: Remove the last Google-only startup exception under the current single-provider config and prevent Setup Wizard false positives for Google keys that cannot perform reverse geocoding.
**Context**: After the earlier Google-only startup patch, the main app still logged `TowerScout initialization failed: Cannot read properties of undefined (reading 'getNorthEast')` during page load on `http://localhost:5001`, even though the Google map ultimately rendered. At the same time, direct reverse-geocode probes showed the current Google key loads the map path but returns `REQUEST_DENIED` from the Google Geocoding API, which explained the missing building addresses.
**Decision**: Keep the startup fix narrow by guarding the not-ready Google-bounds path during the initial provider switch, remove the redundant startup wrapper that mislabeled the failure as provider-sync noise, and tighten Google key validation so Setup Wizard acceptance requires Geocoding API authorization as well as map access.
**Execution**: Patched `webapp/js/src/towerscout.js` to initialize the configured app directly without the redundant `syncUIWithBackendProviders()` wrapper, tolerate missing initial Google bounds while preserving the current provider bootstrap, and skip stored provider preferences that are disabled; patched `webapp/js/src/providers/GoogleMap.js` so `getBounds()` falls back safely when Google has not published viewport bounds yet; patched `webapp/ts_config.py` so Google key validation now checks both the existing map/static path and the Google Geocoding API; patched `webapp/ts_geocoding.py` and `webapp/towerscout.py` so failed reverse-geocode results preserve the provider error reason and return coordinate fallbacks instead of a successful `Address unavailable ...` address; rebuilt the frontend bundle and restarted the helper `5001` server.
**Output**: The page-load console on `http://localhost:5001` no longer shows the previous startup initialization error, and the backend now correctly reports that the current Google key is not authorized for the Geocoding API. Setup Wizard validation will now reject that key instead of letting the app enter a half-working Google-only state.
**Validation**: `node --check webapp\\js\\src\\towerscout.js`; `node --check webapp\\js\\src\\providers\\GoogleMap.js`; `python -m py_compile webapp\\towerscout.py webapp\\ts_config.py webapp\\ts_geocoding.py`; `node webapp\\build.js`; helper-server restart on `5001`; live `POST http://localhost:5001/api/geocode/reverse` now returns `success:false` with coordinate fallback plus the Google authorization error; live `POST http://localhost:5001/api/config/validate-key` now reports the current Google key invalid for Geocoding API access; local headless Edge load on `http://localhost:5001` now shows only the favicon `404` as a page-load error.
**Next**: Clear API-key values again, restart the helper server, and rerun the Setup Wizard from a true blank-config state using a Google key that has Geocoding API authorization. Then recheck Google-only startup, reverse geocoding, and the remaining manual QA gates.

### TYPE C - TASK-053 GOOGLE-ONLY SETUP/RUNTIME CONFIRMED WITH GEOCODING-ENABLED KEY - 2026-04-06
**Objective**: Verify that the remaining Google-only setup/runtime blocker is resolved once the Google key actually has Geocoding API access.
**Context**: The previous live pass isolated the blocker to Google key authorization rather than a remaining code defect: the map path loaded, but reverse geocoding returned `REQUEST_DENIED` until the Geocoding API was enabled for the active key.
**Decision**: Treat this as a validation closure step rather than another code change. Reuse the current `5001` helper server, rerun the Setup Wizard with the corrected Google key, then confirm Google detections populate addresses normally in the right-hand panel.
**Execution**: User enabled Google Geocoding API access for the active Google key, reran the Google-only setup/runtime flow on `http://localhost:5001`, and then executed a detection run.
**Output**: Google-only setup/runtime now passes the previously failing path: the app loads, detections run, and addresses populate in the right-hand panel instead of falling back to `Address unavailable ...`.
**Validation**: User rerun confirmation on `http://localhost:5001` after enabling Geocoding API access on the active Google key.
**Next**: Finish the remaining user-owned signoff checks for manual towers, export/restore, settings/setup sanity, and real-browser click-after-cancel behavior, then close Task-053.
