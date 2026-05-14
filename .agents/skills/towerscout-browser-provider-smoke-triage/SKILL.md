---
name: towerscout-browser-provider-smoke-triage
description: 'Primary skill for TowerScout browser smoke tests and provider workflow
  triage: Google/Azure readiness, Puppeteer detection workflow failures, progress
  overlay, cancel flow, and browser-run artifacts.'
---

# TowerScout Browser Provider Smoke Triage

Use this skill when a task changes or investigates the browser detection workflow, Google Maps, Azure Maps, provider switching, setup/settings startup state, progress overlay, cancellation, detection list rendering, or browser smoke artifacts.

## Goal

Run or interpret TowerScout browser smoke tests consistently, distinguish local setup issues from application regressions, and produce sanitized evidence that reviewers can trust.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for live smoke execution or smoke artifact triage. Use `towerscout-provider-state-review` as primary when the task is code review of state management without running browser smoke.

## First read

- `tests/frontend/test_detection_workflow_smoke.js`
- `tests/frontend/detection-workflow.example.json`
- `tests/frontend/detection-workflow.local.json` if present
- `webapp/js/src/providers/*`
- `webapp/js/src/managers/ProviderStateManager.js`
- `.agent_work/context/analysis/browser-runs/` summaries, if relevant

## Inspect commands (read-only)

```bash
python .agents/skills/towerscout-browser-provider-smoke-triage/scripts/summarize_browser_run.py .agent_work/context/analysis/browser-runs/<run-id>/summary.json
git diff -- tests/frontend webapp/js/src/providers webapp/js/src/managers/ProviderStateManager.js
```

## Build/update generated files (mutating)

Run only if frontend source changed and the task includes updating the generated bundle.

```bash
node webapp/build.js
```

## Validation commands

Choose the smallest set that matches the task.

```bash
npm run test:browser:detect:google
npm run test:browser:detect:azure
node tests/frontend/test_detection_workflow_smoke.js --provider=azure --cancel-smoke
node tests/frontend/test_detection_workflow_smoke.js --provider=google --headed
```

Useful environment variables:

```bash
TOWERSCOUT_BASE_URL=http://localhost:5000
TOWERSCOUT_AOI_FILE=tests/frontend/detection-workflow.local.json
TOWERSCOUT_EXECUTABLE_PATH=/path/to/chrome-or-edge
```

## Triage checklist

1. Confirm app reachability and setup-required state.
2. Confirm requested provider appears in `availableProviders`.
3. For Azure, look for style/data source/drawing manager readiness and SDK/CORS errors.
4. For Google, look for script loading, map instance, bounds, center, drawing/search issues.
5. Confirm fixture polygon is safe, small, and valid.
6. Confirm `/api/detection/estimate` returns numeric tile count.
7. Confirm `/getobjects`, `Detection_detections`, list entries, selected count, and map-visible count meet fixture minimums.
8. Do not commit raw screenshots, network payloads, or local AOI coordinates unless explicitly approved.

## Output format

Return provider tested, base URL, smoke status, command used, estimate/detection/cancel summary, console/page/network red flags, likely failure category, and next focused check.
