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
