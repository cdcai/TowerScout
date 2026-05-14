---
name: towerscout-provider-state-review
description: 'Primary skill for TowerScout provider-state and race-condition review:
  ProviderStateManager, provider switching, timers/listeners, cancellation, detection/tile
  state, map state, and Google/Azure parity. Use browser smoke skill only for live
  smoke execution or artifact triage.'
---

# TowerScout Provider State Review

Use this skill when a task touches provider switching, `ProviderStateManager`, timers, event listeners, cancellation, detection/tile arrays, map state, or race-condition-sensitive frontend code.

## Goal

Review stateful frontend behavior for race conditions, cleanup gaps, stuck locks, and Google/Azure parity issues.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for code review of provider state. Use `towerscout-browser-provider-smoke-triage` as a secondary skill only when live smoke execution or browser-run artifact interpretation is needed.

## First read

- `webapp/js/src/managers/ProviderStateManager.js`
- `webapp/js/src/managers/TimerManager.js`
- `webapp/js/src/managers/EventListenerManager.js`
- `webapp/js/src/providers/GoogleMap.js`
- `webapp/js/src/providers/AzureMap.js`
- `webapp/js/src/providers/providerSwitch.js`
- `tests/integration/test_task_064_provider_state_manager.js`

## Review checklist

1. Provider switches are serialized and rollback-safe.
2. Cleanup/restore behavior is provider-aware.
3. Lock flags are always cleared in `finally` paths.
4. Timer/listener lifecycle is explicit and cleaned up.
5. Detection/tile arrays are mutated through approved patterns, not replaced unexpectedly.
6. Google and Azure behavior stays equivalent unless divergence is intentional.
7. Cancelled/stale detection requests cannot update current UI state.

## Inspect commands (read-only)

```bash
git diff -- webapp/js/src/managers webapp/js/src/providers webapp/js/src/detection tests/integration/test_task_064_provider_state_manager.js
python .agents/skills/towerscout-frontend-bundle-guard/scripts/check_bundle_source_consistency.py .
```

## Build/update generated files (mutating)

Run only if frontend source changed and the generated bundle should be refreshed.

```bash
node webapp/build.js
```

## Validation commands

```bash
node tests/integration/test_task_064_provider_state_manager.js
node tests/frontend/test_global_contract.js
node tests/frontend/test_debug_logging_contract.js
npm run test:stage-0
```

Browser validation, when needed:

```bash
npm run test:browser:detect:google
npm run test:browser:detect:azure
```

## Output format

Return state surfaces touched, race/cleanup risks, tests run, bundle status, provider parity notes, and recommended browser smoke scope if needed.
