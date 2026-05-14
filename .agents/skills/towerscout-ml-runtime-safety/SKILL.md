---
name: towerscout-ml-runtime-safety
description: 'Primary skill for TowerScout ML runtime safety: ts_yolov5.py, ts_en.py,
  model loading, asset manifests, confidence thresholds, tiling, inference behavior,
  CPU/GPU behavior, and ML performance changes.'
---

# TowerScout ML Runtime Safety

Use this skill when a task touches `ts_yolov5.py`, `ts_en.py`, model loading, asset manifests, confidence thresholds, tiling, inference behavior, CPU/GPU behavior, or ML performance.

## Goal

Protect TowerScout detection behavior and model-loading safety while allowing focused runtime improvements.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## First read

- `webapp/ts_yolov5.py`
- `webapp/ts_en.py`
- `webapp/ts_imgutil.py`
- `webapp/ts_paths.py`
- `webapp/asset_manifest.v1.json` if present
- `tests/unit/test_yolov5_local_loader.py`
- `tests/integration/test_end_to_end.py`
- `.github/copilot-instructions.md` ML guardrails

## Review checklist

1. Preserve detection behavior unless the user explicitly asked to change it.
2. Flag confidence threshold, tiling, coordinate precision, or NMS changes.
3. Check CPU-only release compatibility before CUDA/GPU assumptions.
4. Check model file path and asset manifest assumptions.
5. Check `torch.load` trust boundaries and whether `weights_only=True` is viable for any touched load path.
6. Confirm debug-image capture remains opt-in.
7. Confirm export/restore/manual tower semantics are not affected.

## Inspect commands (read-only)

```bash
git diff -- webapp/ts_yolov5.py webapp/ts_en.py webapp/ts_imgutil.py webapp/ts_paths.py webapp/asset_manifest.v1.json tests/unit/test_yolov5_local_loader.py tests/integration/test_end_to_end.py
```

## Build/update generated files (mutating)

No standard mutating command. Do not update model weights, assets, or generated release files unless the task explicitly requests it.

## Validation commands

```bash
python -m py_compile webapp/ts_en.py webapp/ts_yolov5.py
python -m pytest tests/unit/test_yolov5_local_loader.py -q -p no:cacheprovider
python -m pytest tests/integration/test_end_to_end.py -q -p no:cacheprovider
```

## Output format

Return ML files changed, behavior-sensitive findings, model/asset path findings, CPU/GPU compatibility notes, tests run, and validation gaps.
