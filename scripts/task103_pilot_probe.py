"""TASK-103 pilot qualification probe (runs inside a TowerScout image).

Each invocation runs exactly one phase and always writes one JSON report,
including when the phase fails, so failed runs still leave structured evidence.
The probe must work against images built from accepted main (stage A, which
predates the TASK-103 ts_device changes) as well as later stages, so every
optional ts_device capability is feature-detected.

Phases:
  identity   versions, wheel tag, CUDA build, arch coverage, kernel probe,
             FP32 precision read-back (after model-module imports), pip check
  startup    cold start plus warm-up-discarded startup import timings
  synthetic  the Task-098 synthetic model probe plus a torchvision NMS probe
  combined   production YOLOv5 -> EfficientNet detect() over frozen fixture
             tiles; "capture" without a manifest, "compare" with the Task-091
             combined contract when --fixture-manifest is given
  memory     production-batch workload with both models resident
  inject     controlled EfficientNet failure, then a clean follow-up run

Environment (set by scripts/task098-qualify-ml.ps1): TOWERSCOUT_DEVICE,
TASK103_EXPECTED_TORCH, TASK103_EXPECTED_TORCHVISION,
TASK103_EXPECTED_CUDA_BUILD, TASK103_EXPECTED_WHEEL_TAG, TASK103_STAGE,
TASK103_RUN_ID.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import logging
import os
import re
import statistics
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

APP_ROOT = Path("/app")
WEBAPP = APP_ROOT / "webapp"
QUALIFICATION_DIR = Path(__file__).resolve().parent
YOLO_PATH = WEBAPP / "model_params" / "yolov5" / "newest.pt"
EN_PATH = WEBAPP / "model_params" / "EN" / "b5_unweighted_best.pt"
LOG_PATTERNS = {
    "secondary_classifier_failed": "Secondary classifier failed",
    "nms_time_limit": "NMS time limit",
}
_ARCH_RE = re.compile(r"^(sm|compute)_(\d+)([af]?)$")

sys.path.insert(0, str(WEBAPP))
os.environ.setdefault("TOWERSCOUT_SAVE_EN_DEBUG_IMAGES", "0")
os.environ.setdefault("TOWERSCOUT_LAZY_MODEL_INIT", "1")

import psutil  # noqa: E402
import torch  # noqa: E402
import torchvision  # noqa: E402
from PIL import Image  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _requested_device() -> str:
    device = os.environ.get("TOWERSCOUT_DEVICE", "")
    if device not in ("cpu", "cuda"):
        raise RuntimeError(f"TOWERSCOUT_DEVICE must be cpu or cuda for qualification; got {device!r}")
    return device


def _cuda_sync() -> None:
    if torch.cuda.is_available() and torch.cuda.is_initialized():
        torch.cuda.synchronize()


def _load_module(name: str, filename: str):
    path = QUALIFICATION_DIR / filename
    if not path.is_file():
        raise RuntimeError(f"Required qualification module was not found: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 6) if values else None


# --------------------------------------------------------------------------
# Architecture and precision helpers (independent of ts_device so stage A,
# which predates the TASK-103 ts_device changes, is measured the same way)
# --------------------------------------------------------------------------

def arch_code_covers_device(arch: str, major: int, minor: int) -> bool | None:
    """None = unknown syntax; 'a' = exact arch only; 'f' = same family only."""
    match = _ARCH_RE.match(arch)
    if not match:
        return None
    kind, number, suffix = match.group(1), int(match.group(2)), match.group(3)
    code_major, code_minor = divmod(number, 10)
    if suffix == "a":
        return code_major == major and code_minor == minor
    if suffix == "f" or kind == "sm":
        return code_major == major and code_minor <= minor
    return (code_major, code_minor) <= (major, minor)


def arch_supported(arch_list: list[str], major: int, minor: int) -> bool | None:
    verdicts = [arch_code_covers_device(arch, major, minor) for arch in arch_list]
    if any(verdict is True for verdict in verdicts):
        return True
    if verdicts and all(verdict is False for verdict in verdicts):
        return False
    return None


def _kernel_probe() -> tuple[bool, str | None]:
    """Run elementwise, cuDNN conv, and cuBLAS GEMM kernels on the GPU."""
    try:
        zeros = torch.zeros(1, device="cuda")
        zeros.cpu()
        x = torch.ones((1, 3, 8, 8), device="cuda")
        w = torch.ones((4, 3, 3, 3), device="cuda")
        y = torch.nn.functional.conv2d(x, w, padding=1).flatten(1)
        result = (y @ torch.ones((y.shape[1], 2), device="cuda")).cpu()
    except Exception as exc:  # noqa: BLE001 - evidence must capture any failure
        return False, f"{exc.__class__.__name__}: {exc}"
    if not torch.equal(result, torch.full((1, 2), 5808.0)):
        return False, f"kernel probe returned {result.tolist()}"
    return True, None


def _precision_readback(ts_device_module: Any) -> dict[str, Any]:
    override = os.environ.get("TORCH_ALLOW_TF32_CUBLAS_OVERRIDE")
    if hasattr(ts_device_module, "current_fp32_precision"):
        readback = dict(ts_device_module.current_fp32_precision())
    else:
        conv_module = getattr(torch.backends.cudnn, "conv", None)
        if conv_module is not None and hasattr(conv_module, "fp32_precision"):
            readback = {
                "api": "fp32_precision",
                "conv": str(conv_module.fp32_precision),
                "matmul": str(torch.backends.cuda.matmul.fp32_precision),
            }
        else:
            readback = {
                "api": "allow_tf32",
                "conv": "tf32" if torch.backends.cudnn.allow_tf32 else "ieee",
                "matmul": "tf32" if torch.backends.cuda.matmul.allow_tf32 else "ieee",
            }
    readback["override_env"] = override
    readback["cudnn_benchmark"] = bool(torch.backends.cudnn.benchmark)
    return readback


# --------------------------------------------------------------------------
# Phases
# --------------------------------------------------------------------------

def phase_identity(args: argparse.Namespace) -> dict[str, Any]:
    requested = _requested_device()
    import ts_device  # noqa: WPS433 - after sys.path setup
    import ts_en  # noqa: F401  (import model modules before precision read-back)
    import ts_yolov5  # noqa: F401

    local_tag = torch.__version__.partition("+")[2]
    try:
        cudnn_version = torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None
    except Exception:  # noqa: BLE001
        cudnn_version = None
    cuda: dict[str, Any] = {
        "available": bool(torch.cuda.is_available()),
        "device_name": None,
        "capability": None,
        "arch_list": [],
        "arch_supported": None,
        "kernel_probe_ok": None,
        "kernel_probe_error": None,
    }
    if cuda["available"]:
        cuda["arch_list"] = [str(arch) for arch in torch.cuda.get_arch_list()]
        try:
            cuda["device_name"] = torch.cuda.get_device_name(0)
            major, minor = torch.cuda.get_device_capability(0)
            cuda["capability"] = f"sm_{major}{minor}"
            cuda["arch_supported"] = arch_supported(cuda["arch_list"], major, minor)
        except Exception as exc:  # noqa: BLE001
            cuda["kernel_probe_error"] = f"{exc.__class__.__name__}: {exc}"
        if requested == "cuda":
            cuda["kernel_probe_ok"], cuda["kernel_probe_error"] = _kernel_probe()

    pip_check = subprocess.run(
        [sys.executable, "-m", "pip", "check"], capture_output=True, text=True, timeout=180, check=False
    )
    pip_freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=180, check=False
    )
    expected_cuda_build = os.environ.get("TASK103_EXPECTED_CUDA_BUILD", "") or None
    report: dict[str, Any] = {
        "versions": {
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "torchvision": torchvision.__version__,
            "torch_local_tag": local_tag,
            "torch_cuda_build": torch.version.cuda,
            "cudnn_version": cudnn_version,
        },
        "cuda": cuda,
        "precision": _precision_readback(ts_device),
        "ml_runtime": ts_device.build_runtime_diagnostics(),
        "model_sha256": {"yolo": _sha256(YOLO_PATH), "efficientnet": _sha256(EN_PATH)},
        "pip_check": {"ok": pip_check.returncode == 0, "output": (pip_check.stdout + pip_check.stderr)[-4000:]},
        "pip_freeze": pip_freeze.stdout.splitlines(),
        "env": {
            "TOWERSCOUT_PYTORCH_FLAVOR": os.environ.get("TOWERSCOUT_PYTORCH_FLAVOR"),
            "TOWERSCOUT_VERSION": os.environ.get("TOWERSCOUT_VERSION"),
            "torch_num_threads": torch.get_num_threads(),
        },
    }
    report["checks"] = {
        "versions_match": (
            torch.__version__.split("+", 1)[0] == os.environ.get("TASK103_EXPECTED_TORCH")
            and torchvision.__version__.split("+", 1)[0] == os.environ.get("TASK103_EXPECTED_TORCHVISION")
        ),
        "cuda_build_matches": (torch.version.cuda or None) == expected_cuda_build,
        "wheel_tag_matches": local_tag == os.environ.get("TASK103_EXPECTED_WHEEL_TAG"),
        "pip_check_ok": pip_check.returncode == 0,
    }
    return report


def phase_startup(args: argparse.Namespace) -> dict[str, Any]:
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
    total = 1 + args.warmup + args.measured
    for _ in range(total):
        started = time.perf_counter()
        result = subprocess.run(command, cwd=WEBAPP, capture_output=True, text=True, timeout=300, check=False)
        durations.append(round(time.perf_counter() - started, 6))
        if result.returncode != 0:
            raise RuntimeError(f"startup import failed ({result.returncode}): {result.stderr[-2000:]}")
    measured = durations[1 + args.warmup:]
    return {
        "cold_start_seconds": durations[0],
        "warmup_seconds": durations[1:1 + args.warmup],
        "measured_seconds": measured,
        "median_seconds": _median(measured),
    }


def _nms_probe(device: str) -> dict[str, Any]:
    boxes = torch.tensor(
        [[0.0, 0.0, 10.0, 10.0], [1.0, 1.0, 11.0, 11.0], [50.0, 50.0, 60.0, 60.0]], device=device
    )
    scores = torch.tensor([0.9, 0.8, 0.7], device=device)
    keep = torchvision.ops.nms(boxes, scores, 0.45).cpu().tolist()
    return {"device": device, "keep": keep, "ok": keep == [0, 2]}


def phase_synthetic(args: argparse.Namespace) -> dict[str, Any]:
    requested = _requested_device()
    legacy = _load_module("task098_ml_qualification_task103", "task098_ml_qualification.py")
    models = legacy._model_probe()
    nms = _nms_probe(requested)
    report = {
        "yolo": models["yolo"],
        "efficientnet": models["efficientnet"],
        "selected_devices": models["selected_devices"],
        "trust": models["trust"],
        "process_rss_bytes": models["process_rss_bytes"],
        "cuda_peak_memory_allocated_bytes": models["cuda_peak_memory_allocated_bytes"],
        "nms_probe": nms,
    }
    report["checks"] = {
        "output_matches_declared_tolerance": bool(models["output_matches_declared_tolerance"]),
        "selected_devices_match_request": bool(models["selected_devices_match_request"]),
        "nms_probe_ok": bool(nms["ok"]),
    }
    return report


class CountingClassifier:
    """Wraps EN_Classifier to observe real work and errors independent of
    detect()'s fail-open handling of secondary-classifier exceptions."""

    def __init__(self, inner: Any, inject_error_on_call: int | None = None):
        self._inner = inner
        self._inject = inject_error_on_call
        self.calls = 0
        self.candidates = 0
        self.batches = 0
        self.errors: list[str] = []
        self.injected = False

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def classify(self, img: Any, detections: Any, **kwargs: Any) -> Any:
        self.calls += 1
        try:
            if self._inject is not None and self.calls == self._inject:
                self.injected = True
                raise RuntimeError("TASK103 injected secondary classifier failure")
            stats = self._inner.classify(img, detections, **kwargs)
        except Exception as exc:
            self.errors.append(f"{exc.__class__.__name__}: {exc}")
            raise
        if isinstance(stats, dict):
            self.candidates += int(stats.get("candidate_count") or 0)
            self.batches += int(stats.get("batches") or 0)
        return stats

    def snapshot(self) -> dict[str, Any]:
        return {"calls": self.calls, "candidates": self.candidates, "batches": self.batches, "errors": list(self.errors)}


class _LogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.counts = {key: 0 for key in LOG_PATTERNS}

    def emit(self, record: logging.LogRecord) -> None:
        # The handler is attached to several loggers, so a propagating record can
        # arrive more than once; mark it rather than tracking id(), which is reused.
        if getattr(record, "_task103_seen", False):
            return
        record._task103_seen = True
        message = record.getMessage()
        for key, pattern in LOG_PATTERNS.items():
            if pattern in message:
                self.counts[key] += 1


def _attach_log_capture() -> _LogCapture:
    handler = _LogCapture()
    logging.getLogger().addHandler(handler)
    for logger in list(logging.Logger.manager.loggerDict.values()):
        if isinstance(logger, logging.Logger):
            logger.addHandler(handler)
    return handler


class _DeviceRecorder:
    def __init__(self) -> None:
        self.devices: dict[str, set[str]] = {"yolo": set(), "efficientnet": set()}
        self.forward_calls: dict[str, int] = {"yolo": 0, "efficientnet": 0}

    def hook(self, label: str) -> Callable[..., None]:
        def record(module: Any, inputs: Any) -> None:
            self.forward_calls[label] += 1
            parameter = next(module.parameters(), None)
            if parameter is not None:
                self.devices[label].add(str(parameter.device))
            for value in inputs:
                if hasattr(value, "device"):
                    self.devices[label].add(str(value.device))
                    break
        return record

    def as_dict(self) -> dict[str, Any]:
        return {
            "yolo": sorted(self.devices["yolo"]),
            "efficientnet": sorted(self.devices["efficientnet"]),
            "forward_calls": dict(self.forward_calls),
        }


def _yolo_torch_module(yolo: Any) -> Any:
    for module in yolo.model.modules():
        if module.__class__.__name__ in ("DetectionModel", "Model"):
            return module
    return yolo.model


def _load_models() -> tuple[Any, Any, dict[str, float]]:
    from ts_en import EN_Classifier  # noqa: WPS433
    from ts_yolov5 import YOLOv5_Detector  # noqa: WPS433

    started = time.perf_counter()
    yolo = YOLOv5_Detector(str(YOLO_PATH))
    yolo_seconds = time.perf_counter() - started
    started = time.perf_counter()
    classifier = EN_Classifier()
    en_seconds = time.perf_counter() - started
    return yolo, classifier, {"yolo": round(yolo_seconds, 6), "efficientnet": round(en_seconds, 6)}


def _fixture_tiles(args: argparse.Namespace, contract: Any) -> tuple[list[Path], Any]:
    if args.fixture_manifest:
        manifest = contract.load_fixture_manifest(args.fixture_manifest)
        return [Path(tile["resolved_path"]) for tile in manifest["tiles"]], manifest
    if not args.fixture_dir:
        raise RuntimeError("combined/memory/inject phases need --fixture-manifest or --fixture-dir")
    tiles = sorted(Path(args.fixture_dir).glob("*.png"))
    if not tiles:
        raise RuntimeError(f"No .png fixture tiles in {args.fixture_dir}")
    return tiles, None


def _normalize_results(results: Any) -> list[list[dict[str, Any]]]:
    normalized = []
    for tile in results:
        rows = []
        for detection in tile:
            rows.append(
                {
                    "x1": float(detection["x1"]),
                    "y1": float(detection["y1"]),
                    "x2": float(detection["x2"]),
                    "y2": float(detection["y2"]),
                    "conf": float(detection["conf"]),
                    "class": int(detection["class"]),
                    "class_name": str(detection["class_name"]),
                    "secondary": float(detection["secondary"]),
                }
            )
        normalized.append(rows)
    return normalized


def _run_detect(yolo: Any, secondary: Any, tiles: list[Path], run_id: str) -> tuple[Any, Any, float]:
    from ts_events import ExitEvents  # noqa: WPS433
    from ts_performance import PerformanceMetrics  # noqa: WPS433

    events = ExitEvents()
    events.alloc(run_id)
    metrics = PerformanceMetrics(run_id)
    metrics.tile_count = len(tiles)
    metrics.detection_engine = "YOLOv5+EfficientNet-B5"
    _cuda_sync()
    started = time.perf_counter()
    try:
        results = yolo.detect(
            [{"filename": str(path)} for path in tiles],
            events,
            run_id,
            crop_tiles=False,
            secondary=secondary,
            perf_metrics=metrics,
        )
    finally:
        _cuda_sync()
        events.free(run_id)
    seconds = time.perf_counter() - started
    metrics.detection_count = sum(len(tile) for tile in results)
    metrics.finalize()
    performance = metrics.to_dict()
    performance["phase_timings"] = dict(metrics.phase_timings)
    return results, performance, seconds


def phase_combined(args: argparse.Namespace) -> dict[str, Any]:
    requested = _requested_device()
    contract = _load_module("task091_combined_contract", "task091_combined_contract.py")
    tiles, manifest = _fixture_tiles(args, contract)
    hashes_before = {path.name: _sha256(path) for path in tiles}
    yolo, classifier, load_seconds = _load_models()
    recorder = _DeviceRecorder()
    hooks = [
        _yolo_torch_module(yolo).register_forward_pre_hook(recorder.hook("yolo")),
        classifier.model.register_forward_pre_hook(recorder.hook("efficientnet")),
    ]
    capture = _attach_log_capture()
    runs = []
    last_performance: dict[str, Any] = {}
    try:
        for index in range(args.warmup + args.measured):
            counting = CountingClassifier(classifier)
            results, performance, seconds = _run_detect(yolo, counting, tiles, f"task103-combined-{index}")
            runs.append(
                {
                    "index": index,
                    "warmup": index < args.warmup,
                    "seconds": round(seconds, 6),
                    "results": _normalize_results(results),
                    "en": counting.snapshot(),
                }
            )
            last_performance = performance
    finally:
        for hook in hooks:
            hook.remove()
    hashes_after = {path.name: _sha256(path) for path in tiles}
    selected_devices = {"yolo": yolo.device_label, "efficientnet": classifier.device_label}
    observed = recorder.as_dict()
    contract_report = None
    if manifest is not None:
        evaluated = contract.evaluate_combined_report(
            manifest=manifest,
            results=runs[-1]["results"],
            performance=last_performance,
            selected_devices=selected_devices,
            requested_device=requested,
        )
        contract_report = {"checks": evaluated["checks"], "passed": evaluated["passed"]}
    measured = [run["seconds"] for run in runs if not run["warmup"]]
    report = {
        "mode": "compare" if manifest is not None else "capture",
        "tiles": [{"name": name, "sha256": digest} for name, digest in hashes_before.items()],
        "tile_hashes_verified": hashes_before == hashes_after,
        "runs": runs,
        "measured_median_seconds": _median(measured),
        "model_load_seconds": load_seconds,
        "observed_devices": observed,
        "log_findings": dict(capture.counts),
        "selected_devices": selected_devices,
        "last_run_runtime_metadata": last_performance.get("runtime_metadata", {}),
        "last_run_phase_timings": last_performance.get("phase_timings", {}),
        "contract": contract_report,
        "process_rss_bytes": psutil.Process().memory_info().rss,
    }
    device_prefix = "cuda" if requested == "cuda" else "cpu"
    report["checks"] = {
        "tile_hashes_verified": report["tile_hashes_verified"],
        "en_errors_zero": all(not run["en"]["errors"] for run in runs),
        "en_candidates_positive": runs[-1]["en"]["candidates"] > 0,
        "log_findings_zero": all(count == 0 for count in capture.counts.values()),
        "selected_devices_match": all(value == requested for value in selected_devices.values()),
        "observed_devices_match": bool(observed["yolo"]) and bool(observed["efficientnet"]) and all(
            value.startswith(device_prefix) for value in observed["yolo"] + observed["efficientnet"]
        ),
    }
    if contract_report is not None:
        report["checks"]["contract_passed"] = bool(contract_report["passed"])
    return report


def _peak_host_rss_bytes() -> int:
    try:
        with open("/proc/self/status", encoding="ascii") as status:
            for line in status:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return 0


class _DeviceFreeSampler(threading.Thread):
    """Samples device-level free memory (includes non-PyTorch allocations)."""

    def __init__(self, interval: float = 0.1) -> None:
        super().__init__(daemon=True)
        self.interval = interval
        self.stop_event = threading.Event()
        self.min_free: int | None = None
        self.total: int | None = None
        self.samples = 0
        self.error: str | None = None

    def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                free, total = torch.cuda.mem_get_info(0)
            except Exception as exc:  # noqa: BLE001
                self.error = f"{exc.__class__.__name__}: {exc}"
                return
            self.samples += 1
            self.total = total
            self.min_free = free if self.min_free is None else min(self.min_free, free)
            self.stop_event.wait(self.interval)


def phase_memory(args: argparse.Namespace) -> dict[str, Any]:
    requested = _requested_device()
    contract = _load_module("task091_combined_contract", "task091_combined_contract.py")
    tiles, _manifest = _fixture_tiles(args, contract)
    yolo, classifier, load_seconds = _load_models()
    sampler = None
    if requested == "cuda":
        torch.cuda.reset_peak_memory_stats()
        sampler = _DeviceFreeSampler()
        sampler.start()
    job_tiles = list(itertools.islice(itertools.cycle(tiles), args.memory_tiles))
    counting = CountingClassifier(classifier)
    job_seconds = []
    try:
        for job in range(args.memory_jobs):
            _results, _performance, seconds = _run_detect(yolo, counting, job_tiles, f"task103-memory-{job}")
            job_seconds.append(round(seconds, 6))
        synthetic_boxes = [
            [0.05 + 0.055 * (i % 8), 0.1 + 0.4 * (i // 8), 0.1 + 0.055 * (i % 8), 0.35 + 0.4 * (i // 8), 0.5, 0]
            for i in range(args.memory_en_candidates)
        ]
        with Image.open(tiles[min(2, len(tiles) - 1)]) as tile_image:
            en_stats = counting.classify(tile_image.convert("RGB"), synthetic_boxes)
        _cuda_sync()
    finally:
        if sampler is not None:
            sampler.stop_event.set()
            sampler.join(timeout=5)
    cuda_report = None
    if requested == "cuda":
        cuda_report = {
            "min_free_bytes": sampler.min_free if sampler else None,
            "total_bytes": sampler.total if sampler else None,
            "samples": sampler.samples if sampler else 0,
            "sampler_error": sampler.error if sampler else None,
            "max_allocated_bytes": torch.cuda.max_memory_allocated(),
            "max_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
    report = {
        "workload": {
            "tiles_per_job": args.memory_tiles,
            "jobs": args.memory_jobs,
            "synthetic_en_candidates": args.memory_en_candidates,
            "yolo_batch_size": getattr(yolo, "batch_size", None),
            "en_batch_size": getattr(classifier, "batch_size", None),
        },
        "model_load_seconds": load_seconds,
        "job_seconds": job_seconds,
        "synthetic_en_stats": {k: en_stats.get(k) for k in ("candidate_count", "batches", "batch_size", "device")},
        "host": {"vmhwm_bytes": _peak_host_rss_bytes(), "final_rss_bytes": psutil.Process().memory_info().rss},
        "cuda": cuda_report,
        "en": counting.snapshot(),
    }
    report["checks"] = {
        "en_errors_zero": not counting.errors,
        "synthetic_en_batches_full": (en_stats.get("batches") or 0) >= 2,
        "device_memory_sampled": requested != "cuda" or bool(cuda_report and cuda_report["samples"] > 0),
    }
    return report


def phase_inject(args: argparse.Namespace) -> dict[str, Any]:
    requested = _requested_device()
    contract = _load_module("task091_combined_contract", "task091_combined_contract.py")
    tiles, manifest = _fixture_tiles(args, contract)
    yolo, classifier, _load_seconds = _load_models()
    capture = _attach_log_capture()

    injected = CountingClassifier(classifier, inject_error_on_call=args.inject_on_call)
    detect_raised = None
    try:
        _run_detect(yolo, injected, tiles, "task103-inject")
    except Exception as exc:  # noqa: BLE001 - a propagating failure is also "detected"
        detect_raised = f"{exc.__class__.__name__}: {exc}"
    injected_logs = dict(capture.counts)

    followup = CountingClassifier(classifier)
    results, performance, _seconds = _run_detect(yolo, followup, tiles, "task103-inject-followup")
    followup_logs = {key: capture.counts[key] - injected_logs[key] for key in capture.counts}
    contract_passed = None
    if manifest is not None:
        evaluated = contract.evaluate_combined_report(
            manifest=manifest,
            results=_normalize_results(results),
            performance=performance,
            selected_devices={"yolo": yolo.device_label, "efficientnet": classifier.device_label},
            requested_device=requested,
        )
        contract_passed = bool(evaluated["passed"])
    report = {
        "injected": {
            "on_call": args.inject_on_call,
            "triggered": injected.injected,
            "en": injected.snapshot(),
            "detect_raised": detect_raised,
            "log_findings": injected_logs,
        },
        "followup": {
            "en": followup.snapshot(),
            "log_findings": followup_logs,
            "contract_passed": contract_passed,
        },
    }
    report["checks"] = {
        "injected_failure_detected": injected.injected and (
            bool(injected.errors) or detect_raised is not None
        ),
        "followup_clean": (
            not followup.errors
            and followup.candidates > 0
            and all(count == 0 for count in followup_logs.values())
            and contract_passed is not False
        ),
    }
    return report


PHASES: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "identity": phase_identity,
    "startup": phase_startup,
    "synthetic": phase_synthetic,
    "combined": phase_combined,
    "memory": phase_memory,
    "inject": phase_inject,
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixture-manifest", type=Path)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--measured", type=int, default=3)
    parser.add_argument("--memory-tiles", type=int, default=100)
    parser.add_argument("--memory-jobs", type=int, default=3)
    parser.add_argument("--memory-en-candidates", type=int, default=16)
    parser.add_argument("--inject-on-call", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    report: dict[str, Any] = {
        "schema_version": 1,
        "phase": args.phase,
        "ok": False,
        "error": None,
        "profile": os.environ.get("TOWERSCOUT_DEVICE"),
        "stage": os.environ.get("TASK103_STAGE"),
        "run_id": os.environ.get("TASK103_RUN_ID"),
        "started_utc": _utc_now(),
    }
    try:
        report.update(PHASES[args.phase](args))
        report["ok"] = all(report.get("checks", {}).values())
    except BaseException as exc:  # noqa: BLE001 - always emit structured failure evidence
        report["ok"] = False
        report["error"] = {
            "type": exc.__class__.__name__,
            "message": str(exc)[:4000],
            "traceback": traceback.format_exc()[-8000:],
        }
    finally:
        report["finished_utc"] = _utc_now()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(f"TASK-103 phase {args.phase} ok={report['ok']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
