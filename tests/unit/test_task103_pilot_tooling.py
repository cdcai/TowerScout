"""TASK-103 pilot qualification tooling: probe helpers, reporting, and manifest builder."""

import importlib.util
import json
import logging
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_PATH = REPO_ROOT / "scripts" / "task103_pilot_probe.py"
MANIFEST_PATH = REPO_ROOT / "scripts" / "task103_make_manifest.py"
GATES_PATH = REPO_ROOT / "scripts" / "task103_gates.v1.json"
HARNESS_PATH = REPO_ROOT / "scripts" / "task098-qualify-ml.ps1"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def probe():
    return _load(PROBE_PATH, "task103_pilot_probe_test")


@pytest.fixture(scope="module")
def manifest_builder():
    return _load(MANIFEST_PATH, "task103_make_manifest_test")


@pytest.mark.parametrize(
    ("arch", "capability", "expected"),
    [
        ("sm_75", (7, 5), True),
        ("sm_90", (12, 0), False),
        ("sm_120", (12, 0), True),
        ("sm_120", (12, 1), True),
        ("sm_86", (8, 9), True),
        ("compute_90", (12, 0), True),
        ("compute_90a", (12, 0), False),
        ("compute_90a", (9, 0), True),
        ("sm_100f", (10, 3), True),
        ("sm_100f", (12, 0), False),
        ("compute_100f", (12, 0), False),
        ("sm_foo", (12, 0), None),
    ],
)
def test_arch_code_rules_respect_suffix_restrictions(probe, arch, capability, expected):
    assert probe.arch_code_covers_device(arch, *capability) is expected


def test_arch_support_aggregates_known_and_unknown_entries(probe):
    cu126 = ["sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90"]
    cu128 = ["sm_70", "sm_75", "sm_80", "sm_86", "sm_90", "sm_100", "sm_120"]
    assert probe.arch_supported(cu126, 12, 0) is False
    assert probe.arch_supported(cu126, 7, 5) is True
    assert probe.arch_supported(cu128, 12, 0) is True
    assert probe.arch_supported(["sm_foo"], 12, 0) is None
    assert probe.arch_supported([], 12, 0) is None


def test_counting_classifier_records_work_injection_and_forwarding(probe):
    class Inner:
        device_label = "cuda"
        batch_size = 8

        def classify(self, img, detections, **kwargs):
            return {"candidate_count": 2, "batches": 1}

    counting = probe.CountingClassifier(Inner(), inject_error_on_call=2)
    assert counting.device_label == "cuda"
    assert counting.batch_size == 8
    counting.classify(None, [])
    with pytest.raises(RuntimeError, match="injected"):
        counting.classify(None, [])
    counting.classify(None, [])
    snapshot = counting.snapshot()
    assert counting.injected is True
    assert snapshot["calls"] == 3
    assert snapshot["candidates"] == 4
    assert snapshot["batches"] == 2
    assert len(snapshot["errors"]) == 1


def test_log_capture_counts_propagated_records_once(probe):
    logger = logging.getLogger("task103.test.capture")
    logger.propagate = True
    capture = probe._attach_log_capture()
    logger.addHandler(capture)
    try:
        logger.error("Secondary classifier failed: boom")
        logger.warning("WARNING NMS time limit 2.1s exceeded")
        logger.warning("unrelated warning")
    finally:
        logger.removeHandler(capture)
        logging.getLogger().removeHandler(capture)
        for other in logging.Logger.manager.loggerDict.values():
            if isinstance(other, logging.Logger):
                other.removeHandler(capture)
    assert capture.counts == {"secondary_classifier_failed": 1, "nms_time_limit": 1}


def test_main_always_writes_structured_failure_evidence(probe, tmp_path, monkeypatch):
    def failing_phase(_args):
        raise RuntimeError("no kernel image is available for execution on the device")

    monkeypatch.setitem(probe.PHASES, "identity", failing_phase)
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cuda")
    output = tmp_path / "identity.json"

    exit_code = probe.main(["--phase", "identity", "--output", str(output)])

    report = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert report["ok"] is False
    assert report["error"]["type"] == "RuntimeError"
    assert "no kernel image" in report["error"]["message"]
    assert report["profile"] == "cuda"


def test_main_passes_only_when_every_check_passes(probe, tmp_path, monkeypatch):
    monkeypatch.setitem(probe.PHASES, "startup", lambda _args: {"checks": {"a": True, "b": False}})
    output = tmp_path / "startup.json"
    assert probe.main(["--phase", "startup", "--output", str(output)]) == 1
    monkeypatch.setitem(probe.PHASES, "startup", lambda _args: {"checks": {"a": True}})
    assert probe.main(["--phase", "startup", "--output", str(output)]) == 0


def _capture_report(gates):
    tiles = gates["fixture"]["tiles"]
    detection = {
        "x1": 0.1, "y1": 0.1, "x2": 0.2, "y2": 0.2, "conf": 0.4,
        "class": 0, "class_name": "ct", "secondary": 0.3,
    }
    results = [[] for _ in tiles]
    results[2] = [detection]
    return {
        "phase": "combined",
        "mode": "capture",
        "ok": True,
        "stage": "A",
        "profile": "cpu",
        "run_id": "run-a",
        "tile_hashes_verified": True,
        "tiles": [{"name": tile["name"], "sha256": tile["sha256"]} for tile in tiles],
        "runs": [
            {"index": 0, "warmup": True, "results": results, "en": {"candidates": 1, "batches": 1, "errors": []}},
            {"index": 1, "warmup": False, "results": results, "en": {"candidates": 1, "batches": 1, "errors": []}},
        ],
    }


def test_manifest_builder_uses_gates_tolerances_and_last_measured_run(manifest_builder):
    gates = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    manifest = manifest_builder.build_manifest(gates, _capture_report(gates), "f" * 64)
    assert manifest["flow"] == "combined-production"
    assert manifest["tolerances"] == {
        "coordinates": gates["tolerances"]["box"],
        "confidence": gates["tolerances"]["conf"],
        "secondary": gates["tolerances"]["secondary"],
    }
    assert manifest["minimum_secondary_candidates"] == 1
    assert manifest["provenance"]["per_tile_counts"][2] == 1
    assert [tile["path"] for tile in manifest["tiles"]] == [tile["name"] for tile in gates["fixture"]["tiles"]]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda report: report.update(ok=False),
        lambda report: report.update(mode="compare"),
        lambda report: report.update(tile_hashes_verified=False),
        lambda report: report["tiles"][0].update(sha256="0" * 64),
        lambda report: report["runs"][0]["en"]["errors"].append("RuntimeError: boom"),
        lambda report: report["runs"][1]["en"].update(candidates=0),
    ],
)
def test_manifest_builder_refuses_untrustworthy_captures(manifest_builder, mutation):
    gates = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    report = _capture_report(gates)
    mutation(report)
    with pytest.raises(ValueError):
        manifest_builder.build_manifest(gates, report, "f" * 64)


def test_gates_file_declares_every_pilot_threshold():
    gates = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    assert gates["target_flavor"] == "cuda128"
    assert gates["fixture"]["historical_count_vector"] == [0, 0, 13, 8, 0, 4, 6, 11, 2, 4, 5, 0]
    assert len(gates["fixture"]["tiles"]) == 12
    assert gates["memory"]["relative_max"] == 1.10
    assert gates["performance"]["relative_max"] == 1.10
    assert gates["precision"] == {"conv": "ieee", "matmul": "ieee", "applies_to_stages": ["B", "C"]}
    assert set(gates["required_phases"]) == {"identity", "startup", "synthetic", "combined", "memory", "inject"}


def test_harness_pilot_mode_never_overwrites_and_keeps_legacy_contract():
    harness = HARNESS_PATH.read_text(encoding="utf-8")
    assert "evidence is never overwritten" in harness
    assert "-EvidenceRoot must be outside the repository" in harness
    assert "task103_pilot_probe.py" in harness
    assert "[ValidatePattern('^cu1[0-9]{2}$')]" in harness
    assert '"cuda" + $CudaWheelTag.Substring(2)' in harness
    # the original Task-098 path is preserved for existing users
    assert "Task-098 $Profile qualification passed." in harness
