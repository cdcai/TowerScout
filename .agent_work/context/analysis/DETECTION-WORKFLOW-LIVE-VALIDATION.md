# Detection Workflow Live Validation

**Task**: `TASK-053`  
**Date Started**: April 2, 2026  
**Scope**: Runtime validation of the full detection workflow on the live local Flask app using the Phase 1 Puppeteer smoke harness.

---

## Purpose

This document captures live runtime evidence that complements the static trace in [DETECTION-WORKFLOW-REALITY-CHECK.md](./DETECTION-WORKFLOW-REALITY-CHECK.md). The goal is to verify what the application is actually doing in-browser and through Flask when a user moves from `Estimate tiles` to `Find towers`, and to separate confirmed runtime failures from static suspicions.

---

## Test Environment

- Local app base URL: `http://localhost:5000`
- Browser harness: `tests/frontend/test_detection_workflow_smoke.js`
- Browser executable: local Microsoft Edge
- AOI fixture: `tests/frontend/detection-workflow.local.json`
- Validation mode: real provider integrations, not mocked flows

AOI used for the first baseline:

- Center: `[-74.008206, 40.710838]`
- Bounds: approximately `40.71055,-74.00855,40.7111,-74.00785`
- Expected minimum detections: `1`

---

## Baseline Runs

### Run 1: Azure Smoke Attempt Before Harness Fallback

- Run ID: `20260402-151701-azure`
- Artifact directory: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-151701-azure`
- Outcome: failed before estimate request could be triggered normally

Observed behavior:

- `#find` was visible and clickable
- `#estimate` existed but was hidden with `display: none` and zero-size layout metrics
- Puppeteer failed with `Node is either not clickable or not an Element`

Confirmed finding:

- The current UI/CSS state can hide `Estimate tiles` while `Find towers` remains available.
- The harness needed a fallback path to call the estimate workflow directly because the visible button state is not reliable in headless runtime.

Notes:

- This failure was not a provider API failure. It exposed a UI-state inconsistency.
- Earlier inspection tied the hidden state to `webapp/css/ts_styles_mobile.css`, which is still being applied in the headless test environment.

### Run 2: Azure Smoke Attempt With Harness Fallback

- Run ID: `20260402-152342-azure`
- Artifact directory: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-152342-azure`
- Outcome: estimate succeeded, detection failed server-side

Observed behavior:

- Estimate completed successfully
- Estimated tile count: `1`
- Estimate duration: approximately `16.7s`
- Detection never completed in-browser and timed out at `180000ms`

Network evidence:

- Three `POST /getobjects` calls were observed in the run:
  - first request: estimate path, `200`
  - second request: another `200` immediately after `Find towers`
  - third request: detection request, `500`

Confirmed findings:

- `Find towers` is still causing an estimate-style preflight before the actual detection request.
- The backend detection path is failing with a server error before results can render.
- The `500` is being masked by broken exception handling in `webapp/ts_maps.py`.

Flask error evidence:

- `File write failed for C:\Users\bg90\AppData\Local\Temp\1\...jpg: [Errno 13] Permission denied`
- `NameError: name 'MapProviderError' is not defined`
- `NameError: name 'NetworkError' is not defined`

Interpretation:

- There is likely a real lower-level map-download or temp-file failure in the Azure path.
- `ts_maps.py` cannot currently surface that failure correctly because it references `MapProviderError` and `NetworkError` without importing them.
- The current exception path therefore crashes while trying to report the original error.

### Run 3: Google Smoke Attempt With Harness Fallback

- Run ID: `20260402-152835-google`
- Artifact directory: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-152835-google`
- Outcome: estimate succeeded, detection did not reach Flask

Observed behavior:

- Estimate completed successfully
- Estimated tile count: `1`
- Estimate duration: approximately `284ms`
- Detection timed out at `180000ms`

Network evidence:

- The run showed only one `POST /getobjects` request, which matched the estimate call
- No detection request reached Flask during the captured run

Browser-console evidence:

- `google bounds error`
- `Google Maps bounds not ready, but allowing switch to proceed`
- `Global JavaScript error`
- `Critical error from JavaScript Runtime Error`

Confirmed findings:

- The Google path is failing client-side before the actual detection request is sent.
- This is a different failure mode than Azure. Azure currently crosses into backend failure; Google is currently blocked earlier by frontend/provider-switch/runtime logic.

### Run 4-6: Azure Follow-Up Attempts After In-Repo `ts_maps.py` Import Fix

- Run IDs: `20260402-153806-azure`, `20260402-154432-azure`, `20260402-155117-azure`
- Artifact directories:
  - `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-153806-azure`
  - `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-154432-azure`
  - `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260402-155117-azure`
- Outcome: estimate still succeeds, detection still times out in-browser, and the backend still returns a structured `500`

Observed behavior:

- Estimate completed quickly and returned `1` tile
- Detection still produced the same `200`, `200`, `500` `/getobjects` pattern
- The browser artifact now includes the failed response body for `/getobjects`

Latest failed response body evidence:

- `{"error":true,"message":"An internal error occurred. Please try again or contact support.","timestamp":"2026-04-02T19:51:24.791004Z","type":"InternalServerError"}`

Important environment finding:

- `netstat -ano | findstr :5000` showed two different Python listeners bound to port `5000`
- The active listener set included PIDs `15784` and `30392`

Interpretation:

- The in-repo `ts_maps.py` import fix is on disk, but the live reruns are still capable of hitting a stale Flask process
- That makes the repeated `MapProviderError` / `NetworkError` `NameError` tracebacks unreliable as verification of the current codebase
- The underlying Azure backend problem is still very likely the tile-download / temp-file path, but it cannot be isolated confidently until the server state is cleaned up first

Harness improvement captured during this pass:

- The smoke harness now records `responseBodySnippet` for failed `/getobjects` responses so browser artifacts retain the server's returned error body even when terminal access is ambiguous

---

## Confirmed Runtime Issues So Far

1. `Estimate tiles` visibility is not reliable in the live UI state under headless execution, while `Find towers` remains available.
2. `Find towers` still performs an estimate-style preflight instead of starting a clean detection-only request.
3. `webapp/ts_maps.py` has broken exception handling because `MapProviderError` and `NetworkError` are referenced but not imported.
4. The Azure detection path is currently hitting a lower-level file or download failure that is not yet fully exposed because of the broken exception path.
5. The Google detection path is currently hitting a frontend runtime error before detection reaches Flask.
6. Multiple Flask listeners on `localhost:5000` can invalidate rerun evidence by routing requests to a stale server process.

---

## Immediate Priorities

1. Start the next session by stopping all Flask listeners and bringing up one clean server instance on `localhost:5000`.
2. Re-run the Azure smoke flow against that single clean listener to verify the `ts_maps.py` import fix and isolate the true underlying backend failure.
3. Capture the exact Google client-side runtime error stack once the Azure backend path is no longer masked by stale-server ambiguity.
4. After the first blockers are cleared, move to the structural workflow fixes already identified in the static analysis:
   - dedicated estimate contract
   - removal of hidden estimate preflight on `Find towers`
   - cancel lifecycle cleanup
   - provider-aware geocoding and cache isolation
   - stronger duplicate suppression

---

## Current Assessment

The live runtime evidence confirms that the current detection workflow is not just structurally bloated on paper; it is failing in distinct ways across both providers:

- Azure currently reaches the backend but fails during satellite-image retrieval / file handling, with error handling itself broken.
- Google currently fails earlier in frontend/provider initialization and does not reliably reach the detection request.
- The local runtime environment can also invalidate rerun confidence when more than one Flask process is listening on the same port, so clean server-state control is now part of the validation protocol.

This validates the decision to pause `TASK-047` Phase 4. Adding more progress-overlay UX before these failures are stabilized would layer UI polish on top of an unreliable execution path.

---

## April 3 Implementation Milestone Before Reruns

The April 2 runtime evidence was sufficient to land the first full stabilization pass before resuming the browser reruns. The following behavior is now implemented in-repo but still needs live signoff:

- `POST /api/detection/estimate` now owns estimate-only tiling and returns `{ tileCount, estimatedSeconds }`
- `POST /getobjects` now routes through a dedicated detection path with in-memory run-state tracking and unified cleanup
- `/abort` now accepts both `POST` and `GET`, with the modular frontend using `POST`
- geocoding cache lookups are now provider-aware, so Google-preferred and Azure-preferred results do not silently share the same cache entry
- reverse geocoding now sends the active backend provider for manual towers and for detection-result address attachment
- adjacent-coordinate dedupe was replaced with score-ordered spatial dedupe before geocoding
- the modular frontend now keeps `Estimate tiles` and `Find towers` on separate request paths, and detection can run with an indeterminate overlay if no fresh estimate is cached
- the smoke harness now watches `/api/detection/estimate` explicitly instead of treating estimate and detect as the same route

Static/build validation completed for this implementation pass:

- `python -m py_compile webapp\towerscout.py webapp\ts_geocache.py webapp\ts_maps.py`
- `node --check` on the touched frontend files and `tests/frontend/test_detection_workflow_smoke.js`
- `node webapp/build.js`
- `node tests/frontend/test_debug_logging_contract.js`
- `node tests/frontend/test_global_contract.js`

Current runtime state before the next rerun:

- `http://localhost:5000` responded with `200` on April 3, 2026
- the next live step is still Azure first
- this document should not treat any of the new workflow behavior as validated until the new smoke artifacts confirm it

---

## April 3 Isolated `5001` Validation Pass

After the stale `5000` listener ambiguity persisted, Task-053 validation shifted to an isolated helper server on `localhost:5001` driven by `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py`.

Important environment correction:

- The browser artifact `20260403-133540-azure` was intended to target `5001`
- Its `summary.json` still recorded `baseUrl: http://localhost:5000`
- That artifact therefore cannot be treated as proof that the isolated helper path was actually exercised end-to-end

Authoritative current-code evidence from the isolated path instead comes from a direct multipart backend probe:

- Command shape: `curl.exe -F ... http://localhost:5001/getobjects`
- Request matched the browser's multipart form flow for `bounds`, `engine`, `provider`, and `polygons`
- The request reached the updated Task-053 detection route on current workspace code
- YOLO model loading began normally
- Azure Maps provider initialization began normally
- The backend then failed during satellite tile download while writing the downloaded JPEG to the detection session temp directory

Observed backend error:

- surfaced error: `Detection pipeline error: Failed to download satellite maps: All map tile downloads failed`
- underlying log evidence: `Permission denied` while writing the downloaded tile JPEG into the session temp directory

Mitigation now landed in-repo but not yet validated live:

- `towerscout.py` now routes session tempdirs through a repo-local temp root at `webapp/temp/session`
- This is implemented via `SESSION_TMP_ROOT` and `_make_session_tmpdir()`
- The isolated helper server must be restarted before that mitigation can be verified against Azure reruns

Current assessment after the isolated probe:

- stale `5000` listener ambiguity is no longer the primary blocker for Azure diagnosis
- the first clean current-code Azure blocker is the tile-download file-write path
- the next bounded step is to restart the helper `5001` server, rerun the direct multipart Azure probe, and only if that clears the file-write failure, rerun the Azure browser smoke while verifying the artifact records `baseUrl: http://localhost:5001`

### Follow-Up: `mkdtemp()` Root Cause Confirmed and Direct Azure Probe Recovered

The repo-local tempdir mitigation itself exposed the remaining root cause more clearly:

- on this Windows setup, `tempfile.mkdtemp(dir=...)` was creating per-run session child directories that were immediately unwritable
- that behavior reproduced outside Flask in a standalone Python test:
  - `tempfile.mkdtemp(dir=root)` created the child directory
  - opening a file inside that child directory immediately failed with `PermissionError`
- a control test in the same parent directory using explicit `os.makedirs(...)` plus a normal file write succeeded

Fix now landed in-repo:

- `_make_session_tmpdir()` no longer calls `tempfile.mkdtemp(dir=SESSION_TMP_ROOT)`
- it now creates a unique child directory under `webapp/temp/session` with explicit `os.makedirs(...)`

Verification result:

- the helper `5001` server was restarted after the fix
- the direct multipart Azure probe to `http://localhost:5001/getobjects` now returns a JSON detection payload instead of a tile-download `500`
- this validates the backend recovery path through tile download and model inference on current workspace code

What remains unverified:

- the end-to-end Azure browser smoke still needs to prove that the harness is truly targeting `http://localhost:5001`
- Google and cancel-path browser validation still remain open

### Follow-Up: Azure Browser Smoke Recovered on `5001`

The final Azure browser blocker was not the backend anymore; it was the smoke harness target selection:

- the local AOI fixture hard-coded `baseUrl: http://localhost:5000`
- the harness still resolved `fixture.baseUrl` before the CLI/env override
- that caused the earlier "isolated" Azure browser reruns to hit stale `5000` even when `--base-url=http://localhost:5001` was supplied

Fix now landed in-repo:

- `tests/frontend/test_detection_workflow_smoke.js` now resolves `options.baseUrl` before `fixture.baseUrl`
- the run was launched with both `TOWERSCOUT_BASE_URL=http://localhost:5001` and `--base-url=http://localhost:5001`

Passing artifact:

- Run ID: `20260403-142736-azure`
- Artifact: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-142736-azure/summary.json`

Confirmed results from the passing artifact:

- `baseUrl: http://localhost:5001`
- `estimateCalls: 1`
- `getobjectsCalls: 1`
- `hiddenEstimatePreflightObserved: false`
- `detectionCount: 14`
- `pageErrors: 0`

Current assessment after Azure recovery:

- Azure now passes both the direct backend probe and the end-to-end browser smoke on the isolated helper server
- the remaining live-browser gates are Google on `5001` and cancel-path validation on `5001`

### Follow-Up: Google Browser Smoke Green on `5001`

Provider parity is now confirmed on the isolated helper server as well:

- the Google smoke run targeted `http://localhost:5001`
- the resulting artifact is `20260403-143013-google`
- artifact path: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-143013-google/summary.json`

Confirmed results from the passing artifact:

- `baseUrl: http://localhost:5001`
- `estimateCalls: 1`
- `getobjectsCalls: 1`
- `hiddenEstimatePreflightObserved: false`
- `detectionCount: 8`
- `pageErrors: 0`

Current assessment after Google recovery:

- both Azure and Google now pass end-to-end browser smoke against current workspace code on `5001`
- the remaining live-browser gate is cancel-path validation on `5001`

### Follow-Up: Cancel Validation Recovered on `5001`

The cancel path needed both backend and frontend hardening before it became stable:

- the active Flask route now uses request-local run tokens instead of relying on a session-keyed abort event that could be overwritten by a second detection from the same browser session
- the active Flask route also uses request-local asyncio loops, so overlapping detection attempts no longer collide on a shared event loop
- the modular frontend now aborts the in-flight `/getobjects` fetch on cancel and ignores stale cancelled responses so an empty cancelled payload cannot clear a newer detection run
- the smoke harness now falls back to `window.getObjects()` only if a visible post-cancel `Find towers` click produces no output/progress change within `1s` in headless mode

Passing artifact:

- Run ID: `20260403-150354-azure-cancel`
- Artifact: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/20260403-150354-azure-cancel/summary.json`

Confirmed results from the passing artifact:

- `baseUrl: http://localhost:5001`
- `abortStatus: 200`
- `estimateCalls: 1`
- `getobjectsCalls: 1`
- `hiddenEstimatePreflightObserved: false`
- `detectionCount: 14`
- `listCount: 14`
- `mapVisibleCount: 9`
- follow-up detection trigger mode: `click-fallback`

Current assessment after cancel recovery:

- automated Azure, Google, and cancel validation are all green on the isolated helper server
- the remaining Task-053 verification work is user-owned manual QA for manual towers, export/restore, setup/settings, and a real-browser click-after-cancel confirmation

### Follow-Up: Manual-QA Regression Fixes Landed on `5001`

The first real-browser manual-QA pass on `http://localhost:5001` exposed issues that were not covered by the earlier smoke harness:

- Azure-only: the confidence slider row was missing on initial load
- Azure and Google: detections and restored datasets could still show `Address unavailable ...`
- Azure restore: preserved checkbox state could drift, and stale manual-drawing geometry could remain on-screen during restore

Root causes isolated during the follow-up pass:

- the isolated helper launcher inherited placeholder proxy variables from the tool environment, which could blackhole outbound reverse-geocoding requests
- the file geocoding cache treated cached fallback strings like `Address unavailable - 40.714857, -74.015066` as valid successful addresses and reused them
- the filter row had its inline `display:none` cleared, but the active stylesheet could still compute it hidden, so `style.display = null` was not strong enough
- dataset selection persistence still depended on flattened detection order instead of stable `(tile, id_in_tile)` identity
- dataset restore did not clear stale drawn shapes or boundaries before loading restored detections

Fixes now landed in the workspace:

- `.agent_work/tasks/completed/TASK-053/task053_run_server_5001.py`
  - clears inherited proxy env vars before importing `towerscout`
  - forces UTF-8 stdio so helper-server startup is stable under the local shell
- `webapp/ts_geocache.py`
  - removes cached `Address unavailable ...` entries on read
  - skips writing unsuccessful/fallback geocode results into the cache
- `webapp/js/src/towerscout.js`
  - forces `#ffilter` to `display:flex` / `visibility:visible` for active Google/Azure views
  - clears stale shapes and boundaries before dataset restore
- `webapp/towerscout.py`
  - preserves restored selection state using stable `(tile, id_in_tile)` identity instead of flattened positional indexing

Bounded validation completed after the follow-up fixes:

- live reverse-geocode probe on `5001`:
  - `Invoke-RestMethod -Method Post http://localhost:5001/api/geocode/reverse`
  - returned `255 Murray Street, New York, NY 10282`
- local Edge DOM probe on `http://localhost:5001`:
  - `provider: azure`
  - `display: flex`
  - `visibility: visible`
  - `height: 20`
- targeted backend restore-identity test:
  - a non-sequential tile-ID scenario preserved the intended selected detection using `(tile, id_in_tile)` matching

Current assessment after the follow-up fixes:

- fresh reverse geocoding is working again on the isolated helper server
- Azure initial-load slider visibility is corrected on the live page
- restore identity and stale-geometry handling are patched in-repo
- the remaining verification work is a user rerun of manual towers and export/restore on `5001`, followed by the earlier setup/settings and real-browser cancel checks

### Follow-Up: April 6 Google Filtering and Azure Tile Review Fixes

The next manual QA rerun on `http://localhost:5001` surfaced two narrower issues after the earlier follow-up fixes:

- Google `Find` mode could still hide detections that were inside the search radius when another detection at the same address was outside the radius
- Azure tile-by-tile review could show a clipped or over-zoomed section of the search area instead of framing the full selected tile

Root causes isolated in the current workspace:

- `webapp/js/src/detection/DetectionList.js` was still toggling each address header once per child detection, so the last child in an address group could hide the entire group even if an earlier child was inside the radius
- `webapp/js/src/detection/Tile.js` still routed tile review through the inherited center-and-zoom path, which hard-forced `zoom=19` instead of fitting the actual tile bounds on the active provider

Fixes now landed in the workspace:

- `webapp/js/src/detection/DetectionList.js`
  - computes address-group visibility across the whole group first
  - then applies the shared header visibility once using the aggregated result
- `webapp/js/src/detection/Tile.js`
  - uses provider-aware `fitBounds(...)` for tile review when available
  - falls back to the legacy center/zoom path only if the active provider does not expose bounds fitting

Bounded validation completed after the April 6 fixes:

- `node --check webapp\\js\\src\\detection\\DetectionList.js`
- `node --check webapp\\js\\src\\detection\\Tile.js`
- `node webapp\\build.js`
- local Edge validation on `http://localhost:5001` showing:
  - grouped-address visibility calls remain `true` for the shared address block when one child detection is inside and another is outside
  - tile review now drives `fitBounds(1, 2, 3, 4)` on the active provider instead of the old hardcoded zoom path

Current assessment after the April 6 fixes:

- the Google grouped-address filtering bug is patched in-repo
- the Azure tile-review framing bug is patched in-repo
- the remaining verification work is a user refresh-and-rerun of the affected workflows on `5001`, followed by the broader manual signoff already pending for Task-053

### Follow-Up: Final Google Tile-Review Console Error Fix

After the grouped-address and tile-framing fixes landed, the next user rerun confirmed that Azure tile review, Google `Find` mode, Google dataset restore, and Azure dataset restore were all working again. The remaining live issue was isolated to Google tile-by-tile review console errors:

- `InvalidValueError: not a LatLngBounds or LatLngBoundsLiteral: not an Object`
- followed by a secondary `Cannot read properties of null (reading 'message')` from the global critical-error path

Root causes isolated in the current workspace:

- `webapp/js/src/providers/GoogleMap.js` constructed the tile-review bounds via `google.maps.LatLngBounds(...)` incorrectly instead of passing a valid bounds-literal or instantiated bounds object
- `webapp/js/src/managers/ErrorHandler.js` assumed `error.message` existed in `handleCriticalError()` and threw again when the original error object was null-like

Fixes now landed in the workspace:

- `webapp/js/src/providers/GoogleMap.js`
  - `fitBounds()` now passes a valid bounds-literal object `{ north, south, east, west }` into `this.map.fitBounds(...)`
- `webapp/js/src/managers/ErrorHandler.js`
  - `handleCriticalError()` now safely derives an error message even when `error` is null-like

Bounded validation completed after the final Google tile-review fix:

- `node --check webapp\\js\\src\\providers\\GoogleMap.js`
- `node --check webapp\\js\\src\\managers\\ErrorHandler.js`
- `node webapp\\build.js`
- local Edge validation on `http://localhost:5001` showing:
  - `GoogleMap.fitBounds()` now emits a valid bounds payload `{north: 2, south: 4, east: 3, west: 1}`
  - `TowerScoutErrorHandler.handleCriticalError(null, ...)` reports `Critical error: Unknown error occurred`
  - no page-level exceptions were emitted during the validation probe

Current assessment after the final Google tile-review fix:

- the last known Google tile-review console error is patched in-repo
- Task-053 appears to be down to user rerun confirmation rather than an active reproduced code defect

### Follow-Up: Google-Only Setup Wizard Startup Regression

The next setup-required validation pass exposed one more startup issue outside the earlier smoke harness scope:

- with both provider keys removed from `webapp/config/.env`, the Setup Wizard was shown correctly
- after validating and saving only a Google key, the wizard completed and reloaded into the main app
- the main app then showed `TowerScout initialization failed: Cannot read properties of undefined (reading 'Map')`
- the browser console also logged the expected Azure-missing warning because no Azure key was configured for that rerun

Root cause isolated in the current workspace:

- `webapp/js/src/towerscout.js` still had an initial Google-provider startup path inside `fillProviders()` that called `initGoogleMap()` directly
- unlike the normal Google provider-switch path, that startup branch did not first call `loadGoogleMaps()`
- when Google was the only configured provider after Setup Wizard completion, startup therefore tried to construct `GoogleMap` before the Google Maps SDK had been loaded

Fix now landed in-repo:

- `webapp/js/src/towerscout.js`
  - the initial Google-provider branch in `fillProviders()` now calls `loadGoogleMaps()` before requiring a Google map instance
  - if the SDK is already loaded but the map instance is still missing, it then falls back to a direct `initGoogleMap()` call
- `webapp/js/src/providers/providerInit.js`
  - `initGoogleMap()` now explicitly checks for `google.maps.Map` and throws a precise SDK-not-loaded error instead of failing later with an undefined `.Map` dereference

Bounded validation completed after the startup fix:

- `node --check webapp\\js\\src\\towerscout.js`
- `node --check webapp\\js\\src\\providers\\providerInit.js`
- `node webapp\\build.js`

Current assessment after the startup fix:

- the Google-only Setup Wizard startup regression is patched in-repo
- user rerun confirmation is still required because the full setup/save/reload path depends on a real configured Google key and browser reload state

### Follow-Up: Google-Only Runtime Authorization and Bounds-Readiness Gap

The next live pass on the current single-provider config exposed two separate Google-only realities:

- the page-load console no longer hit the earlier `reading 'Map'` failure, but startup still logged `TowerScout initialization failed: Cannot read properties of undefined (reading 'getNorthEast')`
- direct reverse-geocode probes on `http://localhost:5001` returned fallback coordinates instead of building addresses

Authoritative live evidence from the current helper-server state:

- `POST http://localhost:5001/api/geocode/reverse` with `provider: "google"` returned:
  - `success: false`
  - coordinate fallback address
  - Google provider metadata
  - an explicit Google error explaining that the current key is not authorized for the Geocoding API
- `POST http://localhost:5001/api/config/validate-key` now reports the same configured Google key as invalid because Geocoding API authorization is missing
- a local headless Edge load against `http://localhost:5001` confirmed that, after the final startup patch, the previous initialization error is gone and the only page-load error left is the favicon `404`

Root causes isolated in the current workspace:

- the configured Google key is sufficient for the Google Maps JavaScript load path but not authorized for the Google Geocoding API, which is why addresses could not be attached
- the remaining startup exception came from asking Google for viewport bounds before `map.getBounds()` was populated during the initial provider-switch bookkeeping

Fixes now landed in-repo:

- `webapp/js/src/towerscout.js`
  - the configured-app startup path no longer routes through the redundant backend-sync wrapper
  - initial provider switching now tolerates not-yet-ready map state instead of failing startup
- `webapp/js/src/providers/GoogleMap.js`
  - `getBounds()` now falls back safely when Google has not published viewport bounds yet
- `webapp/ts_config.py`
  - Google key validation now checks the Geocoding API as well as the existing map/static path
- `webapp/ts_geocoding.py` and `webapp/towerscout.py`
  - failed reverse-geocode results now preserve the underlying provider error message
  - reverse-geocode API responses now return `success:false` with coordinate fallback instead of a successful `Address unavailable ...` address
  - detection/manual address attachment now treats unsuccessful geocodes as fallback coordinates or empty manual addresses rather than caching/displaying failed pseudo-addresses

Bounded validation completed after the final Google-only fixes:

- `python -m py_compile webapp\\towerscout.py webapp\\ts_config.py webapp\\ts_geocoding.py`
- `node --check webapp\\js\\src\\towerscout.js`
- `node --check webapp\\js\\src\\providers\\GoogleMap.js`
- `node webapp\\build.js`
- helper-server restart on `5001`
- live reverse-geocode probe and live config-validation probe on `5001`
- local headless Edge page-load verification on `http://localhost:5001`

Current assessment after the final Google-only fixes:

- the current configured Google key is not suitable for TowerScout’s address workflow because Google Geocoding API authorization is missing
- the startup exception is patched in-repo and no longer appears on page load
- the next meaningful rerun should start from a blank config state so the Setup Wizard can be revalidated with a geocoding-authorized Google key

### Follow-Up: Google-Only Setup/Runtime Passes With Geocoding-Authorized Key

The next live rerun confirmed that the remaining Google-only blocker was key authorization, not a leftover code defect:

- the active Google key was updated so Geocoding API access was actually enabled
- the user reran the Google-only setup/runtime flow on `http://localhost:5001`
- the app loaded successfully, detections ran, and building addresses populated in the right-hand panel

Current assessment after that rerun:

- the Google-only setup/runtime path is now behaving correctly when the Google key has the required API access
- the remaining open work for Task-053 is down to the broader manual signoff items rather than an active Google-only startup/geocoding defect

### Follow-Up: Final Manual Signoff Pass

The final user-owned signoff pass on `http://localhost:5001` is now complete:

- manual tower workflows worked as expected
- export / restore worked as expected
- Azure key entry through the Settings screen worked as expected
- a real browser `Find towers` click immediately after cancel worked as expected

Final assessment for Task-053:

- Azure and Google smoke automation are green
- cancel-path validation is green
- the Google-only setup/runtime path is green when the key has Geocoding API access
- the broader manual regression pass is green
- Task-053 can now be considered closed
