---
name: towerscout-frontend-bundle-guard
description: 'Primary skill for TowerScout frontend bundle discipline: webapp/js/src
  changes, webapp/build.js, generated webapp/js/towerscout.js, module order, Detection_detections,
  or Tile_tiles. Separates inspect-only checks from mutating rebuild commands.'
---

# TowerScout Frontend Bundle Guard

Use this skill when a task touches `webapp/js/src/`, `webapp/build.js`, generated `webapp/js/towerscout.js`, frontend module order, `Detection_detections`, or `Tile_tiles`.

## Goal

Protect the custom JavaScript bundle workflow and prevent accidental hand-edits to generated output.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for JavaScript source/build/bundle changes. If the same change affects ProviderStateManager behavior or map state, add `towerscout-provider-state-review` as a secondary review.

## First read

- `webapp/build.js`
- `webapp/js/src/`
- `webapp/js/towerscout.js`
- `validate_stage_0.sh`
- `package.json`

## Rules

1. Prefer editing `webapp/js/src/`; do not hand-edit `webapp/js/towerscout.js` except for emergency diagnosis.
2. Treat `webapp/js/towerscout.js` as generated build output.
3. If frontend source changes, rebuild the bundle intentionally and review the generated diff.
4. If `webapp/build.js` or `MODULE_ORDER` changes, treat it as load-order sensitive.
5. If `Detection_detections` or `Tile_tiles` changes, run Stage 0 validation.

## Inspect commands (read-only)

```bash
git diff -- webapp/js/src webapp/js/towerscout.js webapp/build.js validate_stage_0.sh
python .agents/skills/towerscout-frontend-bundle-guard/scripts/check_bundle_source_consistency.py .
```

## Build/update generated files (mutating)

Run only when source changes should update the generated bundle.

```bash
node webapp/build.js
```

After running, inspect the generated diff before proceeding.

```bash
git diff -- webapp/js/towerscout.js
```

## Validation commands

```bash
npm run test:stage-0
node tests/integration/test_task_064_provider_state_manager.js
node tests/frontend/test_global_contract.js
node tests/frontend/test_debug_logging_contract.js
```

## Output format

Return source files changed, whether generated bundle was changed, whether the bundle change is explained by source/build changes, Stage 0 result if applicable, and any module-order/load-order risk.
