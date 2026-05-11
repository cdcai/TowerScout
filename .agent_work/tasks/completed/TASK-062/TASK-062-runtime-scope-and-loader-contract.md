# TASK-062 Runtime Scope and Loader Contract

**Date**: 2026-04-14  
**Owner**: Codex  
**Task**: `TASK-062`

## Chosen Loader Approach

- Keep the vendored runtime rooted at `webapp/vendor/yolov5_local/`.
- Replace the temporary `sys.path` injection pattern with explicit imports under
  `vendor.yolov5_local`.
- Add package markers where needed so the active loader can import:
  - `vendor.yolov5_local.models.*`
  - `vendor.yolov5_local.utils.*`
- Rewrite retained vendored imports to package-relative or package-qualified
  imports so the runtime no longer depends on `sys.modules` caching of top-level
  `models` and `utils` names.
- Preserve the caller-facing `load_local_yolov5_model(filename, autoshape=True,
  verbose=False, device=None)` interface used by `ts_yolov5.py`.

## Bounded `UT-009` Cleanup Scope

This task only replaces raw `print()` calls in active runtime paths that still
matter for current workflows:

- custom image detection helper path
- model upload
- dataset export and label-writing flow
- manual-tower addition during dataset export
- dataset restore / upload
- startup banner logging
- `ts_imgutil.make_boundary()` parse-failure path

Anything broader stays with `TASK-059`.

## Explicit Out of Scope

- background detection jobs and durable run state
- filesystem-session redesign
- broad `towerscout.py` decomposition
- repo-wide logging consolidation
- frontend build modernization
- `UT-012` cleanup unless a required edit unexpectedly touches the served JS
  tree
- speculative runtime dependency pruning beyond anything made obviously safe by
  the vendored-runtime trim

## Expected Validation Reuse

- `tests/unit/test_yolov5_local_loader.py`
- `tests/unit/test_flask_routes.py`
- `tests/integration/test_end_to_end.py`
- `pytest --collect-only tests -q -p no:cacheprovider`

