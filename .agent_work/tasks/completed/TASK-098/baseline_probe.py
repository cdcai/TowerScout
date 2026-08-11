from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import psutil
from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
WEBAPP = ROOT / "webapp"
sys.path.insert(0, str(WEBAPP))

os.environ["TOWERSCOUT_DEVICE"] = "cpu"
os.environ["TOWERSCOUT_SAVE_EN_DEBUG_IMAGES"] = "0"
os.environ["TOWERSCOUT_LAZY_MODEL_INIT"] = "1"

from ts_en import EN_Classifier  # noqa: E402
from ts_yolov5 import YOLOv5_Detector  # noqa: E402


def median(values: list[float]) -> float:
    return round(statistics.median(values), 6)


def measure_import_startup() -> list[float]:
    command = [
        sys.executable,
        "-c",
        (
            "import os,sys;"
            "os.environ['TOWERSCOUT_LAZY_MODEL_INIT']='1';"
            f"sys.path.insert(0,{str(WEBAPP)!r});"
            "import towerscout"
        ),
    ]
    durations = []
    for _ in range(3):
        started = time.perf_counter()
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        durations.append(time.perf_counter() - started)
        if result.returncode != 0:
            raise RuntimeError(
                f"TowerScout import probe failed with exit code {result.returncode}."
            )
    return durations


def measure_models() -> dict[str, object]:
    image = Image.new("RGB", (640, 640), color=(127, 127, 127))
    process = psutil.Process()

    yolo_started = time.perf_counter()
    yolo = YOLOv5_Detector(
        str(WEBAPP / "model_params" / "yolov5" / "newest.pt")
    )
    yolo_load_seconds = time.perf_counter() - yolo_started

    yolo.model([image])
    yolo_durations = []
    yolo_counts = []
    for _ in range(3):
        started = time.perf_counter()
        result = yolo.model([image])
        yolo_durations.append(time.perf_counter() - started)
        yolo_counts.append(len(result.xyxyn[0]))

    en_started = time.perf_counter()
    classifier = EN_Classifier()
    en_load_seconds = time.perf_counter() - en_started

    classifier.classify(
        image,
        [[0.2, 0.2, 0.8, 0.8, 0.5, 0]],
    )
    en_durations = []
    en_scores = []
    for run_id in range(3):
        detections = [[0.2, 0.2, 0.8, 0.8, 0.5, 0]]
        started = time.perf_counter()
        classifier.classify(image, detections, batch_id=run_id)
        en_durations.append(time.perf_counter() - started)
        en_scores.append(round(float(detections[0][6]), 8))

    return {
        "device": "cpu",
        "fixture": {
            "kind": "generated-solid-rgb",
            "size": [640, 640],
            "rgb": [127, 127, 127],
            "yolo_detection_counts": yolo_counts,
            "efficientnet_scores": en_scores,
        },
        "yolo_load_seconds": round(yolo_load_seconds, 6),
        "yolo_inference_seconds": [round(value, 6) for value in yolo_durations],
        "yolo_inference_median_seconds": median(yolo_durations),
        "efficientnet_load_seconds": round(en_load_seconds, 6),
        "efficientnet_inference_seconds": [
            round(value, 6) for value in en_durations
        ],
        "efficientnet_inference_median_seconds": median(en_durations),
        "process_rss_bytes_after_probes": process.memory_info().rss,
    }


def main() -> None:
    startup_durations = measure_import_startup()
    output = {
        "python": sys.version,
        "executable": sys.executable,
        "startup_import_seconds": [
            round(value, 6) for value in startup_durations
        ],
        "startup_import_median_seconds": median(startup_durations),
        "models": measure_models(),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
