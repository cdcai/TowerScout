"""TASK-103 negative control N3: TOWERSCOUT_DEVICE=auto must fall back to CPU and still detect.

Runs inside a TowerScout image with a GPU visible (``docker run --gpus all``) in a
situation where CUDA is ineligible, for example:
  * an image whose PyTorch build has no kernels for the GPU (an older CUDA build on Blackwell), or
  * TORCH_ALLOW_TF32_CUBLAS_OVERRIDE=1, which violates the IEEE FP32 policy.

Before the TASK-103 loader fix, the vendored YOLOv5 loader moved the model to cuda:0
before the device policy ran, so this situation failed the YOLO load instead of
falling back. The check passes only if both models select CPU with a recorded
fallback reason and the combined detection over the frozen tiles produces the
expected per-tile counts.

Usage (inside the image):
  python /qualification/task103_auto_fallback_check.py /evidence/n3-auto-fallback.json \
      --expect-counts 0,0,12,8,0,4,6,9,4,6,5,0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, "/app/webapp")
os.environ.setdefault("TOWERSCOUT_SAVE_EN_DEBUG_IMAGES", "0")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--fixtures", type=Path, default=Path("/fixtures"))
    parser.add_argument("--expect-counts", required=True)
    args = parser.parse_args()
    expected = [int(value) for value in args.expect_counts.split(",")]
    report: dict = {"requested_policy": os.environ.get("TOWERSCOUT_DEVICE"), "passed": False}
    try:
        import ts_device
        from ts_en import EN_Classifier
        from ts_events import ExitEvents
        from ts_yolov5 import YOLOv5_Detector

        report["diagnostics"] = ts_device.build_runtime_diagnostics()
        yolo = YOLOv5_Detector("/app/webapp/model_params/yolov5/newest.pt")
        classifier = EN_Classifier()
        report["devices"] = {
            "yolo": yolo.device_label,
            "yolo_fallback_reason": yolo.device_fallback_reason,
            "efficientnet": classifier.device_label,
            "efficientnet_fallback_reason": getattr(classifier, "device_fallback_reason", None),
        }
        tiles = sorted(args.fixtures.glob("tile_*.png"))
        events = ExitEvents()
        events.alloc("task103-n3")
        results = yolo.detect(
            [{"filename": str(path)} for path in tiles], events, "task103-n3", crop_tiles=False, secondary=classifier
        )
        report["counts"] = [len(tile) for tile in results]
        report["passed"] = (
            report["requested_policy"] == "auto"
            and report["devices"]["yolo"] == "cpu"
            and report["devices"]["efficientnet"] == "cpu"
            and bool(report["devices"]["yolo_fallback_reason"])
            and report["counts"] == expected
        )
    except BaseException as exc:  # noqa: BLE001 - evidence must record the failure
        report["error"] = {"type": exc.__class__.__name__, "message": str(exc)[:2000], "traceback": traceback.format_exc()[-6000:]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: report.get(k) for k in ("requested_policy", "devices", "counts", "passed")}, default=str))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
