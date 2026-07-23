# UT-014: YOLO Loading Still Depends On Torch Hub And GitHub At Runtime

**Status**: READY-FOR-RETEST
**Severity**: HIGH
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The original concern was valid when this issue was opened, but the active loader contract has since changed. On commit `a2160dc`, TowerScout no longer uses `torch.hub.load(...)` in the active YOLO path and instead loads from the vendored local snapshot under `webapp/vendor/yolov5_local/` via `webapp/ts_yolov5_local.py`. That resolves the original Torch Hub and GitHub bootstrap dependency. The April 13 review did identify two new follow-up risks with the vendored implementation, but those are narrower and are now tracked separately in `UT-018` and `UT-019`.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: both

## Reproduction

1. Inspect the active YOLO load path in `webapp/ts_yolov5.py`.
2. Observe that TowerScout now imports `load_local_yolov5_model` from `webapp/ts_yolov5_local.py`.
3. Confirm that the active path no longer calls `torch.hub.load(...)`.

## Expected Result

TowerScout should own the exact inference code it depends on locally, so first-run behavior does not rely on GitHub availability or upstream Hub bootstrap behavior.

## Actual Result

The current code now shows:

- `webapp/ts_yolov5.py` importing `load_local_yolov5_model`
- `webapp/ts_yolov5_local.py` pointing at the vendored local source tree
- targeted loader tests that patch `torch.hub.load` to fail while confirming the active loader path still succeeds

The original Hub and GitHub bootstrap dependency is gone from the active runtime. The remaining follow-up questions are about the shape and import contract of the vendored tree, not about continuing to depend on Torch Hub.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log:
  - related first-run mutation evidence in `C:\Users\bg90\Downloads\console_output_20260406_0241p.txt`
- Other evidence:
  - `webapp/ts_yolov5.py`
  - `webapp/ts_yolov5_local.py`
  - `tests/unit/test_yolov5_local_loader.py`
  - `UT-001`
  - `UT-006`

## Triage Notes

- This captures senior engineer critique item 8.
- `TASK-057` delivered the intended end-state fix for this issue by moving to a vendored local loader.
- The senior review on April 13 surfaced two follow-up items in the new local-loader implementation:
  - `UT-018` vendored tree scope is broader than necessary
  - `UT-019` the temporary `sys.path` import contract is fragile

## Retest Notes

- Retest owner: not applicable
- Retest date: pending
- Retest result: pending

## Resolution

Engineering review on April 14, 2026 found that commit `a2160dc` resolves the original Torch Hub and GitHub runtime dependency. Keep this issue in `READY-FOR-RETEST` for one more clean validation pass, and route the remaining vendored-loader follow-up work to `UT-018` and `UT-019`.
