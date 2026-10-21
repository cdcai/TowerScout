# UT-019: Temporary `sys.path` YOLO Loader Contract Is Fragile

**Status**: READY-FOR-RETEST
**Severity**: HIGH
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-14
**Last Updated**: 2026-04-14

## Summary

`webapp/ts_yolov5_local.py` currently prepends `webapp/vendor/yolov5_local/` to `sys.path`, imports `models.*` and `utils.*`, and then removes that path in a `finally` block. The loader works today because the imported modules remain cached in `sys.modules`, but that makes the active runtime contract implicit rather than explicit. It also means the loader is sensitive to import order and future naming collisions around top-level `models` or `utils` packages. No current runtime failure has been reproduced from this, but it is a correctness and maintainability risk that would be hard to diagnose if it surfaced under Docker or future dependency changes.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: both

## Reproduction

1. Inspect `_prepend_local_yolov5_path()` and `load_local_yolov5_model()` in `webapp/ts_yolov5_local.py`.
2. Observe that the vendored path is inserted into `sys.path` only for the duration of the import block.
3. Observe that the returned model continues to depend on modules imported from `models.*` and `utils.*` after that path has been removed.

## Expected Result

The local YOLO loader should use an explicit, long-lived import contract that does not depend on temporary `sys.path` mutation and `sys.modules` caching behavior.

## Actual Result

The current loader path:

- inserts the vendored root into `sys.path`
- imports `models.common`, `models.experimental`, `models.yolo`, `utils.general`, and `utils.torch_utils`
- removes the vendored root from `sys.path` before the returned model is used later in the process

That means the loader depends on Python module caching to keep those imports alive, and future import-order changes could silently bind the wrong `models` or `utils` package if a collision is introduced.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/ts_yolov5_local.py`
  - `tests/unit/test_yolov5_local_loader.py`

## Triage Notes

- This captures the April 13 senior review's new issue B.
- Current repo inspection on April 14 did not find another active TowerScout package named `models` or `utils`, so this is a latent contract risk rather than a confirmed current failure.
- Even so, the loader contract should be made explicit before Docker work begins so import behavior stays predictable across environments.
- This is separate from `UT-018`, which is about trimming the vendored tree rather than fixing the import mechanism.

## Retest Notes

- Retest owner: teammate tester or reviewer
- Retest date: pending
- Retest result: pending

## Resolution

`TASK-062` replaced the temporary vendored-root `sys.path` prepend/remove logic
in `webapp/ts_yolov5_local.py` with explicit packaged imports under
`vendor.yolov5_local`. To keep existing `.pt` checkpoints loadable, the loader
now exposes targeted legacy `models.*` / `utils.*` aliases in `sys.modules`
only while unpickling YOLO weights; `sys.path` is no longer mutated.

Validation:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_local_loader.py -q -p no:cacheprovider`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\integration\\test_end_to_end.py -q -p no:cacheprovider`

Retest by confirming `ts_yolov5_local.py` contains no temporary `sys.path`
mutation and that real YOLO initialization still succeeds before the bounded
imagery failure in the maintained smoke path.
