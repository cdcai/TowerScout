"""Sanitized, deterministic Task-098 CPU/GPU model qualification probe."""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import psutil
import torch
import torchvision
from PIL import Image

APP_ROOT = Path("/app")
WEBAPP = APP_ROOT / "webapp"
EVIDENCE_PATH = Path("/evidence/qualification.json")
RUNS = 3
EXPECTED_EN_SCORE = 0.8266443
EN_SCORE_TOLERANCE = 0.0001

sys.path.insert(0, str(WEBAPP))
os.environ["TOWERSCOUT_SAVE_EN_DEBUG_IMAGES"] = "0"
os.environ["TOWERSCOUT_LAZY_MODEL_INIT"] = "1"

from ts_assets import verify_trusted_model  # noqa: E402
from ts_en import EN_Classifier  # noqa: E402
from ts_yolov5 import YOLOv5_Detector  # noqa: E402


def _median(values: list[float]) -> float:
    return round(statistics.median(values), 6)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _startup_probe() -> list[float]:
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
    for _ in range(RUNS):
        started = time.perf_counter()
        result = subprocess.run(
            command,
            cwd=WEBAPP,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        durations.append(time.perf_counter() - started)
        if result.returncode != 0:
            raise RuntimeError(
                f"TowerScout startup import failed with exit code {result.returncode}."
            )
    return durations


def _device_details() -> dict[str, object]:
    details: dict[str, object] = {
        "requested": os.environ["TOWERSCOUT_DEVICE"],
        "torch_cuda_build": torch.version.cuda,
        "torch_cuda_available": bool(torch.cuda.is_available()),
    }
    if torch.cuda.is_available():
        properties = torch.cuda.get_device_properties(0)
        details.update(
            {
                "name": properties.name,
                "compute_capability": [
                    properties.major,
                    properties.minor,
                ],
                "total_memory_bytes": properties.total_memory,
            }
        )
    return details


def _model_probe() -> dict[str, object]:
    image = Image.new("RGB", (640, 640), color=(127, 127, 127))
    yolo_path = WEBAPP / "model_params" / "yolov5" / "newest.pt"
    en_path = WEBAPP / "model_params" / "EN" / "b5_unweighted_best.pt"
    yolo_trust = verify_trusted_model(yolo_path)
    en_trust = verify_trusted_model(en_path)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    yolo_load_started = time.perf_counter()
    yolo = YOLOv5_Detector(str(yolo_path))
    yolo_load_seconds = time.perf_counter() - yolo_load_started
    yolo.model([image])
    yolo_durations = []
    yolo_counts = []
    for _ in range(RUNS):
        started = time.perf_counter()
        result = yolo.model([image])
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        yolo_durations.append(time.perf_counter() - started)
        yolo_counts.append(len(result.xyxyn[0]))

    en_load_started = time.perf_counter()
    classifier = EN_Classifier()
    en_load_seconds = time.perf_counter() - en_load_started
    classifier.classify(image, [[0.2, 0.2, 0.8, 0.8, 0.5, 0]])
    en_durations = []
    en_scores = []
    for run_id in range(RUNS):
        detections = [[0.2, 0.2, 0.8, 0.8, 0.5, 0]]
        started = time.perf_counter()
        classifier.classify(image, detections, batch_id=run_id)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        en_durations.append(time.perf_counter() - started)
        en_scores.append(round(float(detections[0][6]), 8))

    requested_device = os.environ["TOWERSCOUT_DEVICE"]
    output_matches = yolo_counts == [0, 0, 0] and all(
        abs(score - EXPECTED_EN_SCORE) <= EN_SCORE_TOLERANCE for score in en_scores
    )
    selected_devices_match = (
        yolo.device_label == requested_device
        and classifier.device_label == requested_device
    )
    return {
        "fixture": {
            "kind": "generated-solid-rgb",
            "size": [640, 640],
            "rgb": [127, 127, 127],
        },
        "trust": {
            "yolo": {
                "source": yolo_trust["source"],
                "bytes": yolo_path.stat().st_size,
                "sha256": _sha256(yolo_path),
            },
            "efficientnet": {
                "source": en_trust["source"],
                "bytes": en_path.stat().st_size,
                "sha256": _sha256(en_path),
            },
        },
        "selected_devices": {
            "yolo": yolo.device_label,
            "efficientnet": classifier.device_label,
        },
        "yolo": {
            "load_seconds": round(yolo_load_seconds, 6),
            "inference_seconds": [round(value, 6) for value in yolo_durations],
            "inference_median_seconds": _median(yolo_durations),
            "detection_counts": yolo_counts,
        },
        "efficientnet": {
            "load_seconds": round(en_load_seconds, 6),
            "inference_seconds": [round(value, 6) for value in en_durations],
            "inference_median_seconds": _median(en_durations),
            "scores": en_scores,
            "expected_score": EXPECTED_EN_SCORE,
            "score_tolerance": EN_SCORE_TOLERANCE,
        },
        "process_rss_bytes": psutil.Process().memory_info().rss,
        "cuda_peak_memory_allocated_bytes": (
            torch.cuda.max_memory_allocated() if torch.cuda.is_available() else 0
        ),
        "output_matches_declared_tolerance": output_matches,
        "selected_devices_match_request": selected_devices_match,
    }


def main() -> None:
    expected_torch = os.environ["TASK098_EXPECTED_TORCH"]
    expected_torchvision = os.environ["TASK098_EXPECTED_TORCHVISION"]
    startup_durations = _startup_probe()
    models = _model_probe()
    versions_match = (
        torch.__version__.split("+", 1)[0] == expected_torch
        and torchvision.__version__.split("+", 1)[0] == expected_torchvision
    )
    output = {
        "schema_version": 1,
        "task": "TASK-098",
        "source_commit": os.environ["TASK098_SOURCE_COMMIT"],
        "image": os.environ["TASK098_IMAGE"],
        "profile": os.environ["TOWERSCOUT_DEVICE"],
        "versions": {
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "torchvision": torchvision.__version__,
        },
        "device": _device_details(),
        "startup_import_seconds": [round(value, 6) for value in startup_durations],
        "startup_import_median_seconds": _median(startup_durations),
        "models": models,
        "checks": {
            "versions_match": versions_match,
            "output_matches_declared_tolerance": models[
                "output_matches_declared_tolerance"
            ],
            "selected_devices_match_request": models["selected_devices_match_request"],
        },
    }
    output["passed"] = all(output["checks"].values())
    EVIDENCE_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Task-098 qualification passed={output['passed']}")
    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
