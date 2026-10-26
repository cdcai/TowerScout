# TowerScout YOLOv5 Local Runtime

This directory vendors the YOLOv5 runtime snapshot that TowerScout uses for
model initialization and inference.

Source provenance:
- Upstream repo: `ultralytics/yolov5`
- Validated commit: `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`

Vendored contents:
- `models/`
- `utils/`
- `data/ImageNet.yaml`
- `LICENSE`

TowerScout-specific local patches:
The following modifications are present in TowerScout's October 23, 2026
source revision; this is the notice reconciliation date, not an assertion
that every patch was first authored on that date. Modified runtime sources
remain under AGPL-3.0 with upstream notices retained.

- Removed upstream `pip install -U ultralytics` fallback from
  `models/common.py` and `utils/general.py`
- Trimmed non-runtime upstream surface before Docker work, including sample
  assets, deployment helpers, training-only helpers, and cache artifacts
- TowerScout loads this snapshot through the packaged
  `vendor.yolov5_local` contract in `webapp/ts_yolov5_local.py` instead of
  `torch.hub`
- `models/common.py` `AutoShape.forward` synchronizes CUDA after the forward
  pass and before `non_max_suppression` (TASK-103). The upstream `Profile()`
  timers do not synchronize, so the NMS wall-clock time limit
  (`0.5 + 0.05 * batch` seconds) also counted pending asynchronous forward work
  and silently dropped detections for the rest of the batch on slower GPUs
  (observed on an NVIDIA T1000 at batch 8). Detection semantics are unchanged.

This runtime is intentionally local to eliminate Torch Hub cache and GitHub
bootstrap dependence during YOLO model initialization.

## Additional modification notice reconciliation — October 25, 2026

The modified runtime files are `models/common.py`, `models/experimental.py`,
`models/yolo.py`, `utils/__init__.py`, `utils/augmentations.py`,
`utils/autoanchor.py`, `utils/dataloaders.py`, `utils/downloads.py`,
`utils/general.py`, `utils/metrics.py`, `utils/plots.py`, and `utils/torch_utils.py`.
Their per-file notices identify the source snapshot/notice reconciliation date,
not a newly claimed original authorship date. Upstream copyright/license notices
and the full AGPL text are preserved.

Compared with the pinned upstream commit, local runtime integration also uses
package-relative imports and removes upstream `sys.path` bootstrap changes.
`models/common.py` replaces the training/export module's `export_formats`
dependency with a local runtime format list. The import/path changes, removed
dependency-install fallbacks, trimmed training/export surface and CUDA timing
patch above are the local integration changes; this notice does not claim that
the vendored files are unmodified upstream source.
