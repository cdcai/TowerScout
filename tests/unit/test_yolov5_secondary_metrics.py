from pathlib import Path
import shutil
import uuid
from unittest.mock import Mock, patch

import torch
from PIL import Image

from ts_yolov5 import YOLOv5_Detector


class _FakeEvents:
    def query(self, _run_id):
        return False


class _FakePerfMetrics:
    def __init__(self):
        self.phases = {}
        self.metadata = {}

    def add_phase_duration(self, name, duration):
        self.phases[name] = self.phases.get(name, 0.0) + duration

    def update_memory_usage(self):
        pass

    def set_runtime_metadata(self, **metadata):
        for key, value in metadata.items():
            if value is not None:
                self.metadata[key] = value


class _FakeResult:
    names = {0: "cooling_tower"}

    def __init__(self):
        self.xyxyn = [
            torch.tensor(
                [
                    [0.1, 0.1, 0.2, 0.2, 0.5, 0.0],
                    [0.3, 0.3, 0.4, 0.4, 0.9, 0.0],
                ]
            )
        ]


class _FakeModel:
    def __call__(self, _images):
        return _FakeResult()


class _FakeSecondary:
    device_label = "cpu"
    batch_size = 8

    def classify(self, _img, detections, batch_id=0):
        detections[0].append(0.75)
        detections[1].append(1)
        return {
            "detections_total": 2,
            "candidate_count": 1,
            "batch_size": self.batch_size,
            "device": self.device_label,
            "batches": 1,
            "crop_seconds": 0.01,
            "transform_seconds": 0.02,
            "stack_seconds": 0.03,
            "forward_seconds": 0.04,
            "attach_seconds": 0.05,
            "debug_image_seconds": 0.0,
            "total_seconds": 0.15,
        }


def test_detect_records_secondary_classifier_subphase_metrics():
    scratch_dir = Path(".agent_work/pytest-temp") / f"ts-yolo-secondary-{uuid.uuid4().hex}"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    tile_path = scratch_dir / "tile.jpg"
    Image.new("RGB", (8, 8), "white").save(tile_path)

    try:
        detector = object.__new__(YOLOv5_Detector)
        detector.model = _FakeModel()
        detector.batch_size = 4
        detector.device_label = "cpu"
        detector.semaphore = type(
            "NoOpSemaphore",
            (),
            {
                "__enter__": lambda self: self,
                "__exit__": lambda self, exc_type, exc, traceback: False,
            },
        )()

        perf_metrics = _FakePerfMetrics()

        results = detector.detect(
            [{"filename": str(tile_path)}],
            _FakeEvents(),
            "test-run",
            crop_tiles=False,
            secondary=_FakeSecondary(),
            perf_metrics=perf_metrics,
        )

        assert results[0][0]["secondary"] == 0.75
        assert results[0][1]["secondary"] == 1
        assert perf_metrics.phases["model_secondary_crop"] == 0.01
        assert perf_metrics.phases["model_secondary_transform"] == 0.02
        assert perf_metrics.phases["model_secondary_stack"] == 0.03
        assert perf_metrics.phases["model_secondary_forward"] == 0.04
        assert perf_metrics.phases["model_secondary_attach"] == 0.05
        assert perf_metrics.metadata["secondary_classifier_detection_count"] == 2
        assert perf_metrics.metadata["secondary_classifier_candidate_count"] == 1
        assert perf_metrics.metadata["secondary_classifier_batches"] == 1
        assert perf_metrics.metadata["secondary_classifier_batch_size"] == 8
        assert perf_metrics.metadata["secondary_classifier_device"] == "cpu"
        assert perf_metrics.metadata["secondary_classifier_seconds_per_candidate"] == 0.15
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)


def test_detector_uses_configured_cpu_batch_size(monkeypatch):
    scratch_dir = Path(".agent_work/pytest-temp") / f"ts-yolo-batch-{uuid.uuid4().hex}"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    model_path = scratch_dir / "newest.pt"
    model_path.write_bytes(b"fake-model")
    monkeypatch.setenv("TOWERSCOUT_YOLO_CPU_BATCH_SIZE", "3")

    try:
        with patch("ts_yolov5._validate_runtime_dependencies"), \
             patch("ts_yolov5._load_local_yolov5_model", return_value=Mock()), \
             patch("ts_yolov5.torch.cuda.is_available", return_value=False):
            detector = YOLOv5_Detector(str(model_path))

        assert detector.batch_size == 3
        assert detector.device_label == "cpu"
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)
