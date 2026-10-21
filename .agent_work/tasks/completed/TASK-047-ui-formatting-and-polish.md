# TASK-047: UI Formatting and Polish

**Status**: COMPLETED
**Priority**: MEDIUM  
**Type**: A (UI/UX Polish)  
**Estimated Effort**: 6-10 hours  
**Created**: April 1, 2026  
**Last Updated**: April 6, 2026
**Target Sprint**: Sprint 04

---

## Objective

Implement the approved set of main-screen polish, settings-screen readability fixes, and bounded process-flow improvements for detection progress feedback without introducing meaningful runtime overhead or changing core detection behavior.

This pass includes the 10 user-approved adjustments discussed on April 1, 2026. The hard item remains in scope, but it is explicitly narrowed to lightweight phase-status plus counts on the existing detection progress overlay rather than raw Flask terminal log streaming.

---

## Current Status Snapshot

- Phase 1: Implemented and user-reviewed.
- Phase 1 refinement: `Settings` button width increased so it better matches the `Estimate tiles` button footprint while remaining right-aligned in `div#fversion`.
- Phase 2: Implemented and user-reviewed.
- Phase 3: Longer `9000ms` polygon-complete timeout implemented in both providers and rebuilt into the frontend bundle.
- Phase 3 follow-up from April 2 was closed during `TASK-053`: Azure Maps now preserves the intended drawing context for custom search boundaries, so the completion message no longer falls back to the manual-tower `Save Towers` guidance.
- April 2 sequencing decision paused `TASK-047` before Phase 4 while `TASK-053` stabilized the detection workflow and added live browser validation.
- April 6 resume decision: Phase 4 implementation is now in-repo using the `TASK-053` detection-run plumbing as the backend foundation rather than treating that earlier work as a full substitute for the Task-047 overlay.
- Phase 4 implementation is complete in code: the app now has a lightweight in-memory progress tracker, `GET /api/detection/progress`, batch/coarse-count progress updates, progress-overlay title/detail text, and throttled frontend polling.
- Phase 5 is complete: static validation, targeted automated coverage, manual happy-path verification, and live browser cancel-smoke/runtime verification are all complete.
- Runtime validation note: the stale helper server on `http://localhost:5001` was not used for closeout because it was serving pre-Phase-4 markup; final Task-047 smoke evidence was gathered against the current local app on `http://localhost:5000`.

---

## Scope For This Pass

**Included**:
- Main UI header alignment and emphasis for `div.fheader`
- Removal of the `About TowerScout` link from `div#fversion`
- Balanced same-row button spacing refinements for `#fadd` and `#fsave`
- Hover hint text for export buttons in `#fsave`
- Corner-radius consistency for `Circle`, `Custom shape`, and `Clear` search controls
- Settings modal copy and link-contrast refinements for the resource section
- Longer timeout for polygon-complete notifications only
- Detection progress overlay enhancements using structured phase status plus counts

**Explicitly Excluded**:
- Raw Flask terminal output mirroring in the browser
- Per-tile or per-detection UI log spam during active detection
- Frequent progress writes into Flask cookie-backed session state
- Broad notification-duration changes outside the polygon-complete messages
- New workflow redesign outside the listed adjustments
- Any change to model thresholds, model weights, or detection-selection behavior

---

## Key Decisions

1. Keep TASK-047 as a Type A polish task, but use a dedicated task document because the approved scope now spans UI, UX, and bounded backend progress plumbing.
2. Use an impact-first sequence: low-risk visual polish first, then notification timing, then the bounded progress-overlay enhancement.
3. Preserve equal-width, single-row button layouts for both `#fadd` and `#fsave`; create spacing by reducing visual bulk and adding explicit gaps rather than switching to content-width buttons or wrapping.
4. Extend only the two polygon-complete notifications. Leave the global notification default unchanged.
5. Implement item 10 as coarse phase-status plus counts with lightweight polling and in-memory tracking, not raw backend log streaming.
6. Add performance guardrails to item 10: no disk-backed live progress logging, no cookie-session writes for progress, no per-tile DOM updates, and no poll interval tighter than `750ms`.

---

## Requirements (EARS Notation)

**R-047-001**: WHEN the main UI renders on desktop, THE SYSTEM SHALL center the `TowerScout` label within `div.fheader` and present it with stronger visual emphasis than the current header styling.

**R-047-002**: WHEN the top-right utility area renders, THE SYSTEM SHALL remove the `About TowerScout` link from `div#fversion` and leave the `Settings` button as the only control in that container.

**R-047-003**: WHEN the manual tower action row renders, THE SYSTEM SHALL keep `Add Towers`, `Save Towers`, `Clear`, and `Clear all` on a single line with balanced equal-width buttons and increased spacing between buttons.

**R-047-004**: WHEN the export action row renders, THE SYSTEM SHALL keep `Download results`, `Download dataset`, and `Restore dataset` on a single line with balanced equal-width buttons and increased spacing between buttons.

**R-047-005**: WHEN users hover the export action buttons, THE SYSTEM SHALL show button-specific hint text explaining each button's purpose.

**R-047-006**: WHEN the search-area controls render in `div.fsearch`, THE SYSTEM SHALL give `Circle`, `Custom shape`, and `Clear` corner radii visually consistent with the rest of the button system without breaking same-row alignment.

**R-047-007**: WHEN the Settings modal renders, THE SYSTEM SHALL rename the `Resources` section heading to `Resource Links`.

**R-047-008**: WHEN resource links render in the Settings modal, THE SYSTEM SHALL display readable white text with accessible hover and focus states against the existing dark modal background.

**R-047-009**: WHEN a polygon-complete notification is shown for either custom search boundaries or manual tower additions, THE SYSTEM SHALL keep that notification visible longer than the default app-notification timeout.

**R-047-010**: WHEN a tower-detection run is active, THE SYSTEM SHALL show structured progress feedback in `div#progress_div` for the current workflow phase and available counts, including at minimum tile preparation, imagery download, model detection, result filtering, geocoding, and finalization.

**R-047-011**: WHEN item 10 is implemented, THE SYSTEM SHALL source progress state from lightweight in-memory tracking keyed to the active session and SHALL NOT stream raw terminal output into the browser.

**R-047-012**: IF live progress data is temporarily unavailable during a detection run, THEN THE SYSTEM SHALL preserve the existing progress bar and cancel workflow instead of blocking the detection request.

**R-047-013**: WHEN the progress overlay updates during detection, THE SYSTEM SHALL avoid meaningful degradation of application responsiveness by using coarse updates, throttled polling, and natural batch/phase boundaries.

---

## Acceptance Criteria

- [x] `TowerScout` is centered and visibly bolder in `div.fheader` on the desktop main screen.
- [x] `About TowerScout` is removed from `div#fversion`, leaving only the `Settings` button there.
- [x] The `#fadd` action row remains a single line with equal-width buttons and clearly increased spacing.
- [x] The `#fsave` action row remains a single line with equal-width buttons and clearly increased spacing.
- [x] Each export button shows a meaningful hover title: results export, dataset export, and dataset restore.
- [x] `Circle`, `Custom shape`, and `Clear` use rounded corners consistent with the rest of the UI button language.
- [x] The Settings modal section heading reads `Resource Links`.
- [x] Resource links in Settings are white and remain readable in default, hover, visited, and keyboard-focus states.
- [x] The polygon-complete notifications for search-area drawing and manual tower drawing use an explicit longer timeout than the default notification timeout.
- [x] The default global notification timeout remains unchanged for unrelated messages.
- [x] `div#progress_div` shows a status title and supporting detail text in addition to the existing progress bar and Cancel button.
- [x] Detection progress feedback covers at least these phases: tile preparation/filtering, imagery download, model detection, boundary/result filtering, geocoding, and finalization.
- [x] Model-detection progress reports counts at batch level, not raw tile-by-tile console messages.
- [x] Geocoding progress reports coarse counts and does not flood the UI with per-address updates.
- [x] Progress polling is throttled to a bounded interval of about `750ms` and stops when detection completes, fails, or is cancelled.
- [x] Existing detection cancel behavior continues to work.
- [x] No model thresholds, model outputs, export formats, or review-mode behavior regress as part of this pass.

Validation note: implementation/build validation is complete, the user manually verified the new loading/progress messages on both Google Maps and Azure Maps, and current-code cancel smoke passed on both providers with runtime artifacts at `tasks/completed/TASK-053/evidence/browser-runs/20260406-151929-google-cancel/summary.json` and `tasks/completed/TASK-053/evidence/browser-runs/20260406-151958-azure-cancel/summary.json`.

---

## Dependencies

- Sprint 04 sequencing and active-task tracking in `.agent_work/current-tasks.md`
- Existing setup/settings UI from `TASK-046`
- Existing notification system in `webapp/js/src/managers/ErrorHandler.js`
- Existing progress overlay and detection workflow in `webapp/js/src/ui/search.js`
- Existing detection batch processing in `webapp/ts_yolov5.py`

---

## Files Likely To Change

- `webapp/templates/towerscout.html`
- `webapp/css/ts_styles.css`
- `webapp/css/ts_styles_mobile.css` if any shared selector change creates a mobile regression
- `webapp/js/src/providers/GoogleMap.js`
- `webapp/js/src/providers/AzureMap.js`
- `webapp/js/src/ui/search.js`
- `webapp/towerscout.py`
- `webapp/ts_yolov5.py`
- `webapp/ts_events.py` or a new lightweight progress-tracking module if a separate file is cleaner

---

## Implementation Plan

### Phase 1: Main UI Polish (Implemented)
- Center and strengthen `div.fheader` styling in desktop CSS without changing the existing grid layout.
- Remove the `About TowerScout` link markup from `div#fversion` and keep the Settings button right-aligned.
- Refine `#fadd` and `#fsave` rows so their buttons stay equal-width on one line, but use slightly lighter padding and explicit `gap` spacing between buttons.
- Add descriptive `title` attributes to each export button in `#fsave`.
- Apply rounded-corner styling to the `Circle`, `Custom shape`, and `Clear` buttons so they visually match the other action buttons while preserving the current same-row search layout.
- Refinement completed: widened the `Settings` button while preserving its right-aligned placement in `div#fversion`.

### Phase 2: Settings Readability Polish (Implemented)
- Rename the Settings section header from `Resources` to `Resource Links` in `webapp/templates/towerscout.html`.
- Add resource-link color styling in `webapp/css/ts_styles.css` for normal, visited, hover, and focus-visible states so link text remains white/readable against the modal background.
- Reduce resource-link font weight so the link list visually matches the surrounding settings content instead of reading as overly bold.
- Keep the existing modal structure and save flow unchanged.

### Phase 3: Notification Timing Adjustment (Implemented and Signed Off)
- Update only the polygon-complete notifications in `webapp/js/src/providers/GoogleMap.js` and `webapp/js/src/providers/AzureMap.js` to use an explicit longer timeout.
- Default assumption for this pass: use `9000ms` for those two completion notices.
- Leave all other `TowerScoutErrorHandler.showUserNotification(...)` calls at their current timing unless they are the two approved polygon-complete messages.
- Validation follow-up was closed in `TASK-053`: the Azure Maps custom search-area workflow now preserves the intended drawing context and no longer falls back to the manual-tower `Save Towers` guidance.

### Phase 4: Detection Progress Overlay Enhancement
- Add a lightweight, thread-safe progress tracker keyed by session ID.
- Preferred implementation shape:
  - either extend `webapp/ts_events.py` with progress-state storage in a separate structure
  - or add a small dedicated module such as `webapp/ts_progress.py` if that keeps the responsibilities cleaner
- Add a read-only backend endpoint such as `GET /api/detection/progress` that returns the current structured state for the active session.
- Update `webapp/towerscout.py` to set coarse-grained status transitions at natural points in `/getobjects`:
  - `preparing_tiles`
  - `tiles_filtered`
  - `downloading_imagery`
  - `running_model`
  - `filtering_results`
  - `geocoding`
  - `finalizing`
  - `complete`
  - `cancelled`
  - `error`
- Include counts where naturally available:
  - candidate and retained tile counts after filtering
  - model batches completed / total batches and processed tile count
  - raw detection count after model output
  - inside / outside / retained counts after filtering and dedupe
  - geocoding processed / total counts, updated only every 10 detections and at completion
- Update `webapp/ts_yolov5.py` to accept an optional progress callback so model status can advance once per completed batch rather than once per tile.
- Extend `div#progress_div` in `webapp/templates/towerscout.html` with status-title and detail-text placeholders beneath the existing progress bar.
- Update `webapp/js/src/ui/search.js` so:
  - `enableProgress()` starts a throttled poll loop against the new progress endpoint
  - `disableProgress()` stops that poll loop on success, cancel, or failure
  - the existing estimated progress bar remains intact
  - the overlay shows structured phase text and counts rather than raw console output
- Preserve the Cancel button and existing `/abort` flow.

### Phase 5: Validation
- Rebuild the frontend bundle with `node webapp/build.js`.
- Run `node --check` on touched frontend source files.
- Run `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m py_compile` on touched backend modules.
- Add or update targeted automated coverage for the progress-tracker state transitions if a new module or callback path is introduced.
- Perform browser smoke checks for:
  - desktop main-screen header/button/layout changes
  - Settings modal heading and link contrast
  - polygon-complete notices for both Google and Azure drawing workflows
  - detection start, live phase updates, cancellation, and successful completion
- Confirm item 10 does not visibly slow tile estimation or full detection in ordinary use.

### Post-Phase-4 Follow-On: Lightweight Browser Smoke Automation
- After Phase 4 is stable, set up the recommended lightweight Puppeteer smoke suite with simple `npm` scripts for headless and headed browser checks.
- Initial smoke coverage should verify main-screen UI polish, Settings modal copy/contrast, polygon-complete notifications, and progress-overlay rendering.
- Keep this follow-on narrowly scoped to repeatable smoke validation rather than a broad end-to-end test framework rollout.

---

## Performance Guardrails For Item 10

- Do not write live progress into Flask `session`, because TowerScout uses signed cookie-backed sessions.
- Do not write progress updates to disk or reuse raw Flask console output as the browser payload.
- Do not update progress UI more frequently than the polling interval.
- Update model progress at batch boundaries only.
- Update geocoding progress only at coarse checkpoints (`every 10 detections`, plus final update).
- If the live-status path fails, fall back to the current progress bar and finish the request normally.

---

## Risks And Watchpoints

- The progress-overlay enhancement is the only meaningful regression risk in this task because it touches backend/frontend coordination instead of pure CSS.
- `div#progress_div` currently contains only the progress bar and Cancel button, so markup and JS changes must preserve the current cancel affordance.
- Any status-tracking implementation that writes into cookie-backed sessions or emits per-tile UI updates would violate the performance intent of this task.
- Main-screen spacing changes must be checked on both Google and Azure providers because the right-column layout already has several tightly packed action rows.
- Manual QA found an Azure Maps drawing-context mismatch during custom search-area definition: the completion notification can incorrectly instruct the user to click `Save Towers` instead of continuing with `Custom Shape` / `Estimate Tiles`. Resolve this before finalizing Phase 3 or closing the task.
- There is not yet a repeatable browser automation harness in the active workflow, so interim UI verification still depends on manual smoke checks until the post-Phase-4 Puppeteer follow-on lands.

---

## Implementation Log

### TYPE A - TASK-047 DOCUMENTATION AND SCOPE LOCK - 2026-04-01 11:00 EDT
**Objective**: Translate the approved April 1 adjustment list into a dedicated, implementation-ready TASK-047 document without starting code changes.
**Context**: TASK-047 was still open-ended in Sprint 04 tracking. The user then supplied 10 concrete requests across Main UI Screen, Settings Screen, and Process Flow/User Experience, including one harder progress-feedback enhancement.
**Decision**: Keep TASK-047 scoped to the approved list, treat item 10 as structured phase-status plus counts instead of raw log streaming, and add explicit performance guardrails so the later implementation does not harm model responsiveness.
**Execution**: Created `.agent_work/tasks/completed/TASK-047-ui-formatting-and-polish.md` with scope, requirements, acceptance criteria, implementation phases, and validation guidance. Synced `.agent_work/current-tasks.md` so Sprint 04 tracking points to this task document.
**Output**: TASK-047 now has a dedicated task file and a decision-complete implementation scope.
**Validation**: Documentation review only; no code or runtime behavior changed in this step.
**Next**: Start implementation when ready, beginning with the low-risk main-screen and settings-screen polish before the bounded progress-overlay enhancement.

### TYPE A - TASK-047 PHASE 1 MAIN-SCREEN POLISH - 2026-04-01
**Objective**: Implement the requested main-screen visual refinements before touching the riskier progress-overlay work.
**Execution**: Updated `webapp/templates/towerscout.html` and `webapp/css/ts_styles.css` to center and strengthen the `TowerScout` header, remove the `About TowerScout` link, convert the manual/export action rows to CSS-driven equal-width button layouts with explicit gaps, add export-button hover titles, and align the `Circle`, `Custom shape`, and `Clear` controls with the broader button styling. Follow-up refinement widened the `Settings` button while preserving its placement in `div#fversion`.
**Output**: The main screen now has the approved header treatment, cleaner top-right utility area, more balanced button spacing, tooltip hints for export actions, and visually consistent search controls.
**Validation**: User-reviewed and accepted in-browser. No JavaScript rebuild was required for the HTML/CSS-only portion.
**Next**: Move to Settings-screen readability polish.

### TYPE A - TASK-047 PHASE 2 SETTINGS READABILITY POLISH - 2026-04-02
**Objective**: Improve the Settings modal copy clarity and link contrast without changing modal behavior.
**Execution**: Updated `webapp/templates/towerscout.html` so the section heading reads `Resource Links`, then added scoped styles in `webapp/css/ts_styles.css` for white/default/visited link states, accessible hover/focus states, and lighter font weight for the resource list items.
**Output**: The Settings modal resource section now reads `Resource Links`, and the linked items remain readable against the dark modal background without visually overpowering the surrounding text.
**Validation**: User-reviewed and accepted after refresh/manual verification.
**Next**: Adjust polygon-complete notification timing.

### TYPE A - TASK-047 PHASE 3 NOTIFICATION TIMING ADJUSTMENT - 2026-04-02
**Objective**: Extend only the approved polygon-complete notifications without changing the global notification default.
**Execution**: Updated the polygon-complete success notifications in `webapp/js/src/providers/GoogleMap.js` and `webapp/js/src/providers/AzureMap.js` from `6000ms` to `9000ms`, ran `node --check` on both provider modules, and rebuilt `webapp/js/towerscout.js`.
**Output**: The targeted completion messages now stay visible longer in both provider code paths, and the rebuilt frontend bundle contains the updated `9000ms` timeout.
**Validation**: Source-level verification and bundle rebuild succeeded. Manual QA then found an Azure Maps custom search-area workflow bug where the completion message still surfaces the manual-tower guidance (`Save Towers`) instead of the search-boundary guidance (`Custom Shape` / `Estimate Tiles`).
**Next**: Correct the Azure Maps completion-message context mismatch before treating Phase 3 as signed off, then continue to Phase 4.

### TYPE A - TASK-047 PHASE 4 PROGRESS OVERLAY IMPLEMENTATION - 2026-04-06
**Objective**: Land the bounded progress-overlay enhancement using lightweight in-memory tracking and throttled polling instead of raw terminal streaming.
**Context**: `TASK-053` completed the detection-workflow stabilization and added request/run-state plumbing, but the user-facing Task-047 overlay still only exposed the legacy progress bar plus Cancel button with no structured phase/count detail.
**Decision**: Implement Phase 4 as a dedicated `ts_progress.py` tracker plus `GET /api/detection/progress`, reuse the current detection route as the source of truth for coarse phase transitions, add model/geocoding callbacks only at natural batch/checkpoint boundaries, and keep the existing progress bar while layering in throttled status polling.
**Execution**: Added `webapp/ts_progress.py` and `tests/unit/test_progress_tracker.py`; updated `webapp/towerscout.py` to publish progress phases/counts for tile preparation, filtering, imagery download, model batches, result filtering, geocoding, finalization, completion, cancellation, and errors; updated `webapp/ts_yolov5.py` with an optional batch progress callback; extended `webapp/templates/towerscout.html` with progress title/detail placeholders; updated `webapp/js/src/config.js` and `webapp/js/src/ui/search.js` so the overlay polls `GET /api/detection/progress` at `750ms` while preserving the existing progress-bar lifecycle and cancel flow; then rebuilt `webapp/js/towerscout.js`.
**Output**: The detection overlay now has structured status text and coarse counts, the backend exposes a live progress contract for the active session, model progress advances once per completed batch, geocoding progress advances every 10 detections plus completion, and the served bundle includes the new overlay behavior.
**Validation**: `python -m py_compile webapp\\towerscout.py webapp\\ts_yolov5.py webapp\\ts_progress.py`; `pytest tests\\unit\\test_progress_tracker.py -q`; `node --check webapp\\js\\src\\config.js`; `node --check webapp\\js\\src\\ui\\search.js`; `node webapp\\build.js`; `node tests\\frontend\\test_debug_logging_contract.js`; `node tests\\frontend\\test_global_contract.js`. Note: pytest emitted the existing non-blocking `.pytest_cache` permission warning in this workspace.
**Next**: Run live browser smoke against a real detection flow to confirm the new overlay text/phase/count updates behave correctly during start, cancellation, success, and error paths before closing `TASK-047`.

### TYPE A - TASK-047 PHASE 5 VALIDATION AND CLOSEOUT - 2026-04-06
**Objective**: Close the remaining runtime-validation gaps for the progress overlay and cancellation flow, then synchronize the Task-047 records.
**Context**: After Phase 4 landed, the only open acceptance items were proving cancel still worked and confirming the overlay changes had not regressed the broader detection workflow. The user had already manually verified the new loading/progress messages on both Google Maps and Azure Maps.
**Decision**: Reuse the existing Puppeteer smoke harness from `TASK-053`, tighten it to record overlay title/detail snapshots during detection and cancel flows, run current-code cancel smoke against the active local app on `http://localhost:5000` rather than the stale helper server on `5001`, and guard the frontend against stale terminal progress snapshots from a previous run.
**Execution**: Updated `tests/frontend/test_detection_workflow_smoke.js` so provider selection no longer blocks on a transient map object and progress-overlay snapshots record title/detail text during detection/cancel flows. Confirmed `5001` was serving stale pre-Phase-4 markup. Updated `webapp/js/src/ui/search.js` to ignore terminal `/api/detection/progress` states older than the active request start time, rebuilt `webapp/js/towerscout.js`, and reran current-code cancel smoke against `5000` for both Google and Azure.
**Output**: The smoke harness now captures overlay text evidence alongside the existing request-sequence/runtime assertions, and the frontend no longer risks briefly rendering stale terminal progress text at the start of a fresh detection request. Browser artifacts `20260406-151929-google-cancel` and `20260406-151958-azure-cancel` both passed with non-empty overlay title/detail text before cancel, hidden overlay state after cancel, `abortStatus: 200`, no hidden estimate preflight, and successful follow-up detections/list/map rendering.
**Validation**: `node --check tests/frontend/test_detection_workflow_smoke.js`; `node --check webapp\\js\\src\\ui\\search.js`; `node webapp\\build.js`; `node tests/frontend/test_detection_workflow_smoke.js --provider=google --cancel-smoke --base-url=http://localhost:5000`; `node tests/frontend/test_detection_workflow_smoke.js --provider=azure --cancel-smoke --base-url=http://localhost:5000`; user manual verification that the progress/loading messages looked good on both providers during real detections.
**Next**: Mark Task-047 complete and sync Sprint 04 bookkeeping in `.agent_work/current-tasks.md`.
