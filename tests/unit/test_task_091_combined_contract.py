import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "scripts" / "task091_combined_contract.py"
PROBE_PATH = REPO_ROOT / "scripts" / "task098_ml_qualification.py"


def _load_contract_module():
    spec = importlib.util.spec_from_file_location(
        "task091_combined_contract",
        CONTRACT_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_probe_module():
    spec = importlib.util.spec_from_file_location(
        "task098_ml_qualification_w05_test",
        PROBE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _detection(**overrides):
    detection = {
        "x1": 0.1,
        "y1": 0.2,
        "x2": 0.3,
        "y2": 0.4,
        "conf": 0.5,
        "class": 0,
        "class_name": "cooling_tower",
        "secondary": 0.75,
    }
    detection.update(overrides)
    return detection


def _write_manifest(tmp_path, **overrides):
    tile_path = tmp_path / "tile.png"
    tile_path.write_bytes(b"fixed-permitted-fixture")
    manifest = {
        "schema_version": 1,
        "flow": "combined-production",
        "tiles": [
            {
                "path": tile_path.name,
                "sha256": hashlib.sha256(tile_path.read_bytes()).hexdigest(),
                "expected_detections": [_detection()],
            }
        ],
        "tolerances": {
            "coordinates": 0.000001,
            "confidence": 0.000001,
            "secondary": 0.000001,
        },
        "minimum_secondary_candidates": 1,
        "minimum_secondary_batches": 1,
    }
    manifest.update(overrides)
    manifest_path = tmp_path / "fixture-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def _performance(**metadata_overrides):
    metadata = {
        "model_device": "cpu",
        "secondary_classifier_enabled": True,
        "secondary_classifier_device": "cpu",
        "secondary_classifier_candidate_count": 1,
        "secondary_classifier_batches": 1,
    }
    metadata.update(metadata_overrides)
    return {
        "phase_timings": {
            "model_yolo_inference": 1.0,
            "model_secondary_classifier_inference": 0.5,
        },
        "runtime_metadata": metadata,
    }


def test_fixture_manifest_binds_relative_file_hash_and_expected_output(tmp_path):
    contract = _load_contract_module()
    manifest_path = _write_manifest(tmp_path)

    manifest = contract.load_fixture_manifest(manifest_path)

    assert manifest["schema_version"] == 1
    assert manifest["flow"] == "combined-production"
    assert manifest["tiles"][0]["resolved_path"] == str(tmp_path / "tile.png")
    assert manifest["tiles"][0]["expected_detections"] == [_detection()]


def test_fixture_manifest_allows_zero_detection_tiles_when_flow_is_positive(tmp_path):
    contract = _load_contract_module()
    first = tmp_path / "empty.png"
    second = tmp_path / "positive.png"
    first.write_bytes(b"empty-fixture")
    second.write_bytes(b"positive-fixture")
    manifest_path = _write_manifest(
        tmp_path,
        tiles=[
            {
                "path": first.name,
                "sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
                "expected_detections": [],
            },
            {
                "path": second.name,
                "sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
                "expected_detections": [_detection()],
            },
        ],
    )

    manifest = contract.load_fixture_manifest(manifest_path)

    assert manifest["tiles"][0]["expected_detections"] == []
    assert manifest["tiles"][1]["expected_detections"] == [_detection()]


def test_fixture_manifest_requires_enough_expected_detections(tmp_path):
    contract = _load_contract_module()
    manifest_path = _write_manifest(
        tmp_path,
        minimum_secondary_candidates=2,
    )

    with pytest.raises(ValueError, match="minimum_secondary_candidates"):
        contract.load_fixture_manifest(manifest_path)


@pytest.mark.parametrize(
    "tile_path,sha256",
    [
        ("../outside.png", "0" * 64),
        ("..\\outside.png", "0" * 64),
        ("tile.png", "0" * 64),
        ("C:/absolute/tile.png", "0" * 64),
    ],
)
def test_fixture_manifest_rejects_unsafe_or_hash_mismatched_tiles(
    tmp_path,
    tile_path,
    sha256,
):
    contract = _load_contract_module()
    manifest_path = _write_manifest(
        tmp_path,
        tiles=[
            {
                "path": tile_path,
                "sha256": sha256,
                "expected_detections": [_detection()],
            }
        ],
    )

    with pytest.raises(ValueError):
        contract.load_fixture_manifest(manifest_path)


def test_combined_report_passes_only_complete_expected_production_flow(tmp_path):
    contract = _load_contract_module()
    manifest = contract.load_fixture_manifest(_write_manifest(tmp_path))

    report = contract.evaluate_combined_report(
        manifest=manifest,
        results=[[_detection()]],
        performance=_performance(),
        selected_devices={"yolo": "cpu", "efficientnet": "cpu"},
        requested_device="cpu",
    )

    assert report["passed"] is True
    assert all(report["checks"].values())
    assert report["normalized_results"] == [[_detection()]]


@pytest.mark.parametrize(
    "results,performance,selected_devices,failed_check",
    [
        (
            [[_detection(conf=0.6)]],
            _performance(),
            {"yolo": "cpu", "efficientnet": "cpu"},
            "expected_outputs_match",
        ),
        (
            [[_detection()]],
            _performance(secondary_classifier_candidate_count=0),
            {"yolo": "cpu", "efficientnet": "cpu"},
            "secondary_candidates_sufficient",
        ),
        (
            [[_detection()]],
            _performance(secondary_classifier_batches=0),
            {"yolo": "cpu", "efficientnet": "cpu"},
            "secondary_batches_sufficient",
        ),
        (
            [[_detection()]],
            _performance(),
            {"yolo": "cuda", "efficientnet": "cpu"},
            "devices_match_request",
        ),
        (
            [[_detection()]],
            {"phase_timings": {}, "runtime_metadata": _performance()["runtime_metadata"]},
            {"yolo": "cpu", "efficientnet": "cpu"},
            "required_phases_recorded",
        ),
    ],
)
def test_combined_report_fails_closed_on_incomplete_evidence(
    tmp_path,
    results,
    performance,
    selected_devices,
    failed_check,
):
    contract = _load_contract_module()
    manifest = contract.load_fixture_manifest(_write_manifest(tmp_path))

    report = contract.evaluate_combined_report(
        manifest=manifest,
        results=results,
        performance=performance,
        selected_devices=selected_devices,
        requested_device="cpu",
    )

    assert report["passed"] is False
    assert report["checks"][failed_check] is False


def test_combined_report_rejects_invalid_detection_shape(tmp_path):
    contract = _load_contract_module()
    manifest = contract.load_fixture_manifest(_write_manifest(tmp_path))

    report = contract.evaluate_combined_report(
        manifest=manifest,
        results=[[_detection(x1=0.9, x2=0.1)]],
        performance=_performance(),
        selected_devices={"yolo": "cpu", "efficientnet": "cpu"},
        requested_device="cpu",
    )

    assert report["passed"] is False
    assert report["checks"]["detections_valid"] is False


def test_fixture_reverification_rejects_bytes_changed_after_load(tmp_path):
    contract = _load_contract_module()
    manifest = contract.load_fixture_manifest(_write_manifest(tmp_path))
    Path(manifest["tiles"][0]["resolved_path"]).write_bytes(b"changed")

    with pytest.raises(ValueError, match="changed after manifest validation"):
        contract.verify_fixture_files(manifest)


def test_combined_probe_wires_production_models_metrics_and_events(
    tmp_path,
    monkeypatch,
):
    probe = _load_probe_module()
    webapp = tmp_path / "webapp"
    yolo_path = webapp / "model_params" / "yolov5" / "newest.pt"
    en_path = webapp / "model_params" / "EN" / "b5_unweighted_best.pt"
    yolo_path.parent.mkdir(parents=True)
    en_path.parent.mkdir(parents=True)
    yolo_path.write_bytes(b"trusted-yolo")
    en_path.write_bytes(b"trusted-efficientnet")
    tile_path = tmp_path / "tile.png"
    tile_path.write_bytes(b"permitted-tile")
    manifest_path = tmp_path / "fixture-manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    manifest = {
        "flow": "combined-production",
        "tiles": [{"resolved_path": str(tile_path)}],
    }
    captured = {}

    class FakeContract:
        @staticmethod
        def load_fixture_manifest(path):
            assert path == manifest_path
            return manifest

        @staticmethod
        def evaluate_combined_report(**kwargs):
            captured["evaluation"] = kwargs
            return {"checks": {"combined": True}, "passed": True}

        @staticmethod
        def verify_fixture_files(verified_manifest):
            assert verified_manifest is manifest
            captured["fixture_verifications"] = (
                captured.get("fixture_verifications", 0) + 1
            )

    class FakeClassifier:
        device_label = "cpu"

    class FakeDetector:
        device_label = "cpu"

        def __init__(self, path):
            assert path == str(yolo_path)

        def detect(
            self,
            tiles,
            events,
            run_id,
            crop_tiles=False,
            secondary=None,
            perf_metrics=None,
        ):
            assert tiles == [{"filename": str(tile_path)}]
            assert events.query(run_id) is False
            assert crop_tiles is False
            assert isinstance(secondary, FakeClassifier)
            perf_metrics.add_phase_duration("model_yolo_inference", 1.0)
            perf_metrics.add_phase_duration(
                "model_secondary_classifier_inference",
                0.5,
            )
            perf_metrics.set_runtime_metadata(
                model_device="cpu",
                secondary_classifier_enabled=True,
                secondary_classifier_device="cpu",
                secondary_classifier_candidate_count=1,
                secondary_classifier_batches=1,
            )
            captured["events"] = events
            captured["run_id"] = run_id
            return [[_detection()]]

    monkeypatch.setattr(probe, "WEBAPP", webapp)
    monkeypatch.setattr(probe, "_load_combined_contract", lambda: FakeContract)
    monkeypatch.setattr(probe, "YOLOv5_Detector", FakeDetector)
    monkeypatch.setattr(probe, "EN_Classifier", FakeClassifier)
    monkeypatch.setattr(
        probe,
        "verify_trusted_model",
        lambda _path: {"source": "release_manifest"},
    )
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cpu")

    report = probe._combined_probe(manifest_path)

    assert report["passed"] is True
    assert captured["evaluation"]["selected_devices"] == {
        "yolo": "cpu",
        "efficientnet": "cpu",
    }
    assert captured["evaluation"]["performance"]["runtime_metadata"][
        "secondary_classifier_candidate_count"
    ] == 1
    assert captured["events"].query(captured["run_id"]) is None
    assert captured["fixture_verifications"] == 2


def _set_probe_identity_environment(probe, monkeypatch):
    monkeypatch.setenv(
        "TASK098_EXPECTED_TORCH",
        probe.torch.__version__.split("+", 1)[0],
    )
    monkeypatch.setenv(
        "TASK098_EXPECTED_TORCHVISION",
        probe.torchvision.__version__.split("+", 1)[0],
    )
    monkeypatch.setenv("TASK098_SOURCE_COMMIT", "a" * 40)
    monkeypatch.setenv("TASK098_IMAGE", "towerscout:test")
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cpu")


def test_combined_main_skips_legacy_startup_probe(tmp_path, monkeypatch):
    probe = _load_probe_module()
    output_path = tmp_path / "combined.json"
    manifest_path = tmp_path / "fixture-manifest.json"
    _set_probe_identity_environment(probe, monkeypatch)
    monkeypatch.setattr(
        probe,
        "_parse_args",
        lambda: SimpleNamespace(
            fixture_manifest=manifest_path,
            output=output_path,
        ),
    )
    monkeypatch.setattr(
        probe,
        "_startup_probe",
        lambda: pytest.fail("combined mode must not run the startup probe"),
    )
    monkeypatch.setattr(
        probe,
        "_model_probe",
        lambda: pytest.fail("combined mode must not run the synthetic probe"),
    )
    monkeypatch.setattr(
        probe,
        "_combined_probe",
        lambda path: {
            "checks": {"combined_flow_passed": path == manifest_path},
            "passed": True,
        },
    )

    probe.main()

    output = json.loads(output_path.read_text(encoding="utf-8"))
    assert output["schema_version"] == 2
    assert output["task"] == "TASK-091-W05"
    assert output["mode"] == "combined-production"
    assert output["passed"] is True


def test_no_argument_main_preserves_legacy_task098_report(tmp_path, monkeypatch):
    probe = _load_probe_module()
    output_path = tmp_path / "legacy.json"
    _set_probe_identity_environment(probe, monkeypatch)
    monkeypatch.setattr(
        probe,
        "_parse_args",
        lambda: SimpleNamespace(fixture_manifest=None, output=output_path),
    )
    monkeypatch.setattr(probe, "_startup_probe", lambda: [1.0, 2.0, 3.0])
    monkeypatch.setattr(
        probe,
        "_model_probe",
        lambda: {
            "output_matches_declared_tolerance": True,
            "selected_devices_match_request": True,
        },
    )
    monkeypatch.setattr(
        probe,
        "_combined_probe",
        lambda _path: pytest.fail("legacy mode must not run combined probe"),
    )

    probe.main()

    output = json.loads(output_path.read_text(encoding="utf-8"))
    assert output["schema_version"] == 1
    assert output["task"] == "TASK-098"
    assert output["startup_import_seconds"] == [1.0, 2.0, 3.0]
    assert output["startup_import_median_seconds"] == 2.0
    assert output["passed"] is True