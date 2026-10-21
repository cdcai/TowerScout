# UT-018: Vendored YOLOv5 Tree Includes Non-Runtime Upstream Surface

**Status**: READY-FOR-RETEST
**Severity**: MEDIUM
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-14
**Last Updated**: 2026-04-14

## Summary

`TASK-057` correctly removed the active Torch Hub dependency, but the vendored snapshot under `webapp/vendor/yolov5_local/` is broader than TowerScout's runtime actually needs. On commit `a2160dc`, the tree includes 39 Python files plus sample images, docs, `__pycache__` files, and directories for AWS, Docker, Flask REST API examples, loggers, and other training or deployment surfaces that TowerScout does not call during inference. This is not a confirmed runtime break today, but it expands the Docker image footprint, leaves more accidental-import surface in the repo, and blurs the intended contract of the local YOLO ownership change.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: both

## Reproduction

1. Inspect `webapp/vendor/yolov5_local/`.
2. Count the vendored Python files and directories.
3. Compare that tree with the subset TowerScout actually imports through `webapp/ts_yolov5_local.py`.

## Expected Result

The vendored runtime should contain only the inference-time files and assets TowerScout actually needs, plus the minimum provenance documentation required to explain the snapshot.

## Actual Result

The current vendored tree contains broad upstream surface area that TowerScout does not use at runtime, including examples such as:

- `utils/aws/`
- `utils/docker/`
- `utils/flask_rest_api/`
- `utils/loggers/`
- `data/images/`
- `__pycache__/` artifacts

The current repo state includes 39 vendored Python files even though the active loader path is centered on a much smaller inference subset.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/vendor/yolov5_local/`
  - `webapp/ts_yolov5_local.py`

## Triage Notes

- This captures the April 13 senior review's new issue A.
- The runtime behavior delivered by `TASK-057` is still the right direction; this issue is about scoping the vendored footprint more tightly.
- Treat this as a pre-Docker follow-up so `TASK-025` does not build image contents around a broader-than-necessary upstream snapshot.
- This is separate from `UT-019`, which is about the loader import contract rather than tree size and scope.

## Retest Notes

- Retest owner: teammate tester or reviewer
- Retest date: pending
- Retest result: pending

## Resolution

`TASK-062` trimmed the vendored YOLO snapshot from the broader upstream tree
down to the retained inference subset plus provenance files. The cleanup
removed the issue's named non-runtime surfaces such as `utils/aws/`,
`utils/docker/`, `utils/flask_rest_api/`, `utils/loggers/`, `data/images/`,
training helpers, and `__pycache__/` artifacts. The retained tree now contains
23 files anchored around the packaged runtime under `vendor.yolov5_local`.

Validation:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_local_loader.py -q -p no:cacheprovider`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\integration\\test_end_to_end.py -q -p no:cacheprovider`

Retest by re-inspecting `webapp/vendor/yolov5_local/` and confirming the tree
still matches the retained inference/runtime scope before Docker image work
continues.
